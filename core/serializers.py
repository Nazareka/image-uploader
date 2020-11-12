from datetime import timedelta

import django.utils.timezone

from rest_framework.fields import DurationField
from rest_framework.serializers import ModelSerializer, CurrentUserDefault, HiddenField

from . import models

class CreateImageSerializer(ModelSerializer):
    user = HiddenField(
        default=CurrentUserDefault()
    )

    class Meta:
        model = models.Image
        fields = ('image', 'user')

class ImageSerializer(ModelSerializer):

    class Meta:
        model = models.Image
        fields = ('image',)

class CreateExpiringLinkSerializer(ModelSerializer):

    seconds = DurationField(
        min_value=timedelta(seconds=300), 
        max_value=timedelta(seconds=30000)
    )

    def create(self, validated_data):
        validated_data["created_at"] = django.utils.timezone.now()
        validated_data["expired_at"] = validated_data["created_at"] + validated_data["seconds"]
        validated_data.pop("seconds")

        return models.ExpiringLink.objects.create(**validated_data)

    class Meta:
        model = models.ExpiringLink
        fields = ('id', 'link_to_image', 'seconds')
