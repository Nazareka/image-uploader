import uuid
from typing import Sequence, Union, Optional

from django.utils import timezone
from django.http import Http404
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.conf import settings

from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404

from . import models, serializers, utils

class UploadImageView(CreateAPIView):
    """ 
        View for uploading an image and then 
        return data about the image that provided by a plan
    """

    permission_classes = [IsAuthenticated,]
    
    serializer_class = serializers.CreateImageSerializer

    def create(self, request: Request) -> Union[Response, ValidationError]:
        plan_obj: models.Plan = request.user.plan # type: ignore 

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        img_obj: models.Image = serializer.save() # type: ignore 

        data = utils.create_image_data_dict(
            plan_obj.thumbnail_heights,
            img_obj,
            plan_obj.is_expiring_link_generation_provided,
            plan_obj.is_link_to_original_provided,
        )

        return Response(data, status=HTTP_201_CREATED)
    
class ListImagesView(ListAPIView):
    """ 
        View that return a list of data about the image that provided by a plan
    """
    permission_classes = [IsAuthenticated,]

    serializer_class = serializers.ImageSerializer

    def get_queryset(self):
        user_id: int = self.request.user.id # type: ignore
        return models.Image.objects.filter(user_id=user_id).order_by('image')

    def list(self, request: Request) -> Union[Response, NotFound]:
        images_qs: QuerySet[models.Image] = self.get_queryset()
        plan_obj: models.Plan = request.user.plan # type: ignore 

        if not images_qs:
            raise NotFound("You haven't sent any pictures yet")

        paginated_images_qs: Sequence[models.Image] = self.paginate_queryset(images_qs) # type: ignore 
        response_data = []
        for img_obj in paginated_images_qs:
            data = utils.create_image_data_dict(
                plan_obj.thumbnail_heights,
                img_obj,
                plan_obj.is_expiring_link_generation_provided,
                plan_obj.is_link_to_original_provided,
            )
            response_data.append(data)
        return Response(response_data, status=HTTP_200_OK)

class ImageView(APIView):
    """ 
        View that return an original of image or thumbnail as file
    """
    permission_classes = [IsAuthenticated,]

    def get(self, request: Request, image_title: str, **kwargs) -> Union[HttpResponse, Http404, PermissionDenied]:
        height: Optional[int] = kwargs.get("height", None)
        plan_obj: models.Plan = request.user.plan # type: ignore
        user_id: int = request.user.id # type: ignore

        if height:
            if not height in range(1, 1001):
                raise ValidationError("thumbnail's height must be in range 1 to 1000")
            if not height in plan_obj.thumbnail_heights:
                raise PermissionDenied("Your plan doesn't provide this thumbnail height")
        else:
            if not plan_obj.is_expiring_link_generation_provided:
                raise PermissionDenied("Your plan doesn't provide fetch original image")

        image_queryset: QuerySet[models.Image] = models.Image.objects.all()
        image_obj = get_object_or_404(queryset=image_queryset, user_id=user_id, image="static/images/" + image_title)

        height: Optional[int] = kwargs.get("height", None)

        image_file = image_obj.get_image_file(height=height)

        response = HttpResponse(content_type="image/" + image_file.format)
        response['Content-Disposition'] = 'filename="{}.{}"'.format(
            image_obj.image_name, 
            image_file.format
        )
        image_file.save(response, image_file.format)
        # print(response.code)
        return response



class FetchExpiringLinkView(APIView):
    """ 
        View that return a link to expiring a originall of image or thumbnail
    """
    permission_classes = [IsAuthenticated,]

    def get(
        self, request: Request, image_title: str, seconds: int, **kwargs
    ) -> Union[Response, Http404, PermissionDenied, ValidationError]:

        height: Optional[int] = kwargs.get("height", None)
        plan_obj: models.Plan = request.user.plan # type: ignore
        user_id: int = request.user.id # type: ignore
        
        if height:
            if not height in range(1, 1001):
                raise ValidationError("thumbnail's height must be in range 1 to 1000")
            if not height in plan_obj.thumbnail_heights:
                raise PermissionDenied("Your plan doesn't provide this thumbnail height")
        else:
            if not plan_obj.is_link_to_original_provided:
                raise PermissionDenied("Your plan doesn't provide fetch original image")
        
        if not plan_obj.is_expiring_link_generation_provided:
            raise PermissionDenied("Your plan doesn't provide generation expiring links")

        queryset: QuerySet[models.Image] = models.Image.objects.all()
        image_obj = get_object_or_404(queryset=queryset, user_id=user_id, image="static/images/" + image_title)

        exp_link_ser = serializers.CreateExpiringLinkSerializer(
            data={
                "id": uuid.uuid4,
                "link_to_image": settings.HOSTNAME + "/uploads/" + image_obj.image_name,
                "seconds": seconds
            } 
        )
        exp_link_ser.is_valid(raise_exception=True)

        exp_link_obj: models.ExpiringLink = exp_link_ser.save() # type: ignore

        return Response({"url": exp_link_obj.get_expiring_link_to_image(height)}, status=HTTP_200_OK)
        
class ExpiringLinkView(APIView):

    permission_classes = [IsAuthenticated,]

    def get(self, request: Request, image_title: str, uuid: str, **kwargs) -> Union[HttpResponse, Http404, PermissionDenied]:
        height: Optional[int] = kwargs.get("height", None)
        plan_obj: models.Plan = request.user.plan # type: ignore
        user_id: int = request.user.id # type: ignore
        
        if height:
            if not height in range(1, 1001):
                raise ValidationError("thumbnail's height must be in range 1 to 1000")
            if not height in plan_obj.thumbnail_heights:
                raise PermissionDenied("Your plan doesn't provide this thumbnail height")
        else:
            if not plan_obj.is_link_to_original_provided:
                raise PermissionDenied("Your plan doesn't provide fetch original image")
        
        if not plan_obj.is_expiring_link_generation_provided:
            raise PermissionDenied("Your plan doesn't provide generation expiring links")

        image_queryset: QuerySet[models.Image] = models.Image.objects.all()
        image_obj = get_object_or_404(queryset=image_queryset, user_id=user_id, image="static/images/" + image_title)

        exp_link_queryset: QuerySet[models.ExpiringLink] = models.ExpiringLink.objects.all()
        exp_link_obj = get_object_or_404(queryset=exp_link_queryset, id=uuid)
        
        if exp_link_obj.expired_at < timezone.now():
            raise PermissionDenied("Link is expired")

        image_file = image_obj.get_image_file(height=height)

        response = HttpResponse(content_type="image/" + image_file.format)
        response['Content-Disposition'] = 'filename="{}.{}"'.format(
            image_obj.image_name, 
            image_file.format
        )
        image_file.save(response, image_file.format)
        return response
