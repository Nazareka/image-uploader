
import os
import uuid

from typing import Optional, Any
import PIL.Image

from django.db.models import (
    Model, IntegerField, ForeignKey, CASCADE, CharField, BooleanField, ImageField, DateTimeField, UUIDField,
    URLField
)
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.db.models.fields import URLField
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from . import validators



class User(AbstractUser):
    plan = ForeignKey(
        "Plan", 
        verbose_name=_("plan"),
        on_delete=CASCADE,
        null=True
    )
    class Meta:
        db_table = 'auth_user'

class Image(Model):
    """ Image Model """


    user = ForeignKey(
        "User", 
        verbose_name=_("user"), 
        on_delete=CASCADE
    )

    image = ImageField(
        _("image link"), 
        upload_to='static/images',
        validators=[
            FileExtensionValidator(allowed_extensions=['PNG', 'JPG']),
            validators.validate_file_size
        ],
        max_length=50
    )
    
    def __str__(self) -> str:
        return f'image object name="{self.image_name}"'
    
    def get_image_file(self, height: Optional[int]) -> Any:
        img = PIL.Image.open(self.image)
        if height:
            img_format = img.format
            new_height = height
            new_width  = int(new_height * self.image.height / self.image.width)
            img = img.resize((new_height, new_width), PIL.Image.ANTIALIAS)
            img.format = img_format
        return img

    def get_link_to_file(self, height: Optional[int]) -> str:
        url = f'/uploads/{self.image_name}'
        url += f'/thumbnail-{str(height)}px' if height else ''
        return url
    
    def get_link_to_fetch_expiring_link(self, height: Optional[int]) -> str:
        url = f'/fetch_expiring_link'
        url += f'/{self.image_name}'
        url += f'/thumbnail-{str(height)}px' if height else ''
        url += '{/seconds}'
        return url
    
    def create_image_dict(self, height: Optional[int], is_expiring_link_generation_provided: bool) -> dict:
        image_dict = {}
        image_dict["url"] = "{}{}".format(settings.HOSTNAME, self.get_link_to_file(height))
        if height:
            image_dict["height"] = height
        if is_expiring_link_generation_provided:
            image_dict["expired_url"] = "{}{}".format(settings.HOSTNAME, self.get_link_to_fetch_expiring_link(height))
        
        return image_dict

    @property
    def image_name(self) -> str:
        return os.path.basename(self.image.name)
    
    class Meta:
        verbose_name = "image"
        verbose_name_plural = "images"
        ordering = ["image",]
    

class Plan(Model):
    """ Plan Model """

    name = CharField(
        _("name of plan"), 
        max_length=50,
        blank=False,
        unique=True
    )
    thumbnail_heights = ArrayField(
        IntegerField(
            _("height in pixels"),
            validators=(
                MinValueValidator(1),
                MaxValueValidator(1000)
            ),
            default=200
        ), 
        size=1000,
        blank=False
    )

    is_link_to_original_provided = BooleanField(
        _("is a link to originally uploaded image provided by the plan"),
        default=False
    )
    is_expiring_link_generation_provided = BooleanField(
        _("is expiring link generation provided by the plan"),
        default=False
    )

    def __str__(self) -> str:
        return f'image object name="{self.name}"'
    
    class Meta:
        verbose_name = "plan"
        verbose_name_plural = "plans"
        ordering = ["name",]

class ExpiringLink(Model):
    """ ExpiringLink Model """

    id = UUIDField(
        _("universally unique identifiers for expiring links"),
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    link_to_image = URLField(
        _("link to image"),
        blank=False
    )
    created_at = DateTimeField()
    expired_at = DateTimeField()
 
    def get_expiring_link_to_image(self, height: Optional[int]) -> str:
        url = f'{self.link_to_image}'
        url += f'/thumbnail-{height}px' if height else ''
        url += f'/expiring-link-{self.id}'
        return url
    
    class Meta:
        verbose_name = "expiring_link"
        verbose_name_plural = "expiring_links"
        ordering = ["created_at",]

    

