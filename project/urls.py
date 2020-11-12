from django.contrib import admin
from django.urls import path
from core.views import ( # type: ignore
    UploadImageView, ListImagesView, ImageView, FetchExpiringLinkView,
    ExpiringLinkView
)

urlpatterns = [
    path('admin', admin.site.urls),

    # url for uploading image and then get a dict with links
    path('upload_image', UploadImageView.as_view(), name="upload_image"),

    # url for fetch a list of images that user uploaded
    path('list_images', ListImagesView.as_view(), name="list_images"),

    # urls for fetch an image as file
    path(
        'uploads/<image_title>', 
        ImageView.as_view(),
        name="list_images"
    ),
    path(
        'uploads/<image_title>/thumbnail-<int:height>px', 
        ImageView.as_view(), 
        name="list_images"
    ),
    
    # urls for fetch expiring links to original image or thumbnail
    path(
        'fetch_expiring_link/<str:image_title>/<int:seconds>', 
        FetchExpiringLinkView.as_view(), 
        name="list_images"
    ),
    path(
        'fetch_expiring_link/<str:image_title>/thumbnail-<int:height>px/<int:seconds>', 
        FetchExpiringLinkView.as_view(), 
        name="list_images"
    ),

    # urls for fetch expiring original image or thumbnail as file
    path(
        'uploads/<image_title>/expiring-link-<str:uuid>', 
        ExpiringLinkView.as_view(), 
        name="list_images"
    ),
    path(
        'uploads/<image_title>/thumbnail-<int:height>px/expiring-link-<str:uuid>', 
        ExpiringLinkView.as_view(), 
        name="list_images"
    )

]
