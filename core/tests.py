from django.conf import settings

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient, APITestCase

from . import models


client = APIClient()

class ListImagesWithoutSendingImageTestCase(APITestCase):
    def test_not_found_list_images_views(self):
        response = client.get(settings.HOSTNAME + "/list_images")
        self.assertEqual(response.status_code, 404)

class ListImagesViewTestCase(APITestCase):
    def setUp(self):
        user = models.User.objects.create_user(username="testName", email="testemail@gmail.com", password="test")  
    def create_image(self, user):
        image = SimpleUploadedFile(
            name='test_image.jpg', 
            content=open('./static/test_images/valid_image.jpg', 'rb').read(), 
            content_type='image/jpeg'
        )
        image_obj = models.Image.objects.create(user_id=user.id, image=image)
        image_obj.save()
        
        return image_obj
    
    def test_basic_plan_list_images_views(self):
        user = models.User.objects.get(username="testName")

        image_obj = self.create_image(user)
        response = client.get(settings.HOSTNAME + "/list_images")
        self.assertEqual(response.data, 
            [
                {
                    'thumbnails': [
                        {
                            'url': settings.HOSTNAME + '/uploads/' + image_obj.image_name + '/thumbnail-200px',
                            'height': 200
                        }
                    ]
                }
            ]
        )
    
    def test_premium_plan_list_images_views(self):
        user = models.User.objects.get(username="testName")
        plan_obj = models.Plan.objects.get(name="Premium")
        user.plan_id = plan_obj.id
        user.save()
        client.force_authenticate(user=user)
        image_obj = self.create_image(user)
        response = client.get(settings.HOSTNAME + "/list_images")
        self.assertEqual(response.data, 
            [
                {
                    'thumbnails': [
                        {
                            'url': settings.HOSTNAME + '/uploads/' + image_obj.image_name + '/thumbnail-200px',
                            'height': 200
                        },
                        {
                            'url': settings.HOSTNAME + '/uploads/' + image_obj.image_name + '/thumbnail-400px',
                            'height': 400
                        }
                    ],
                    'original': 
                    {
                        'url': settings.HOSTNAME + '/uploads/' + image_obj.image_name
                    }
                }
            ]
        )
    
    def test_enterprise_plan_list_images_views(self):
        user = models.User.objects.get(username="testName")
        plan_obj = models.Plan.objects.get(name="Enterprise")
        user.plan_id = plan_obj.id
        user.save()
        client.force_authenticate(user=user)
        image_obj = self.create_image(user)
        response = client.get(settings.HOSTNAME + "/list_images")
        print(response.data)
        self.assertEqual(response.data, 
            [
                {
                    'thumbnails': [
                        {
                            'url': settings.HOSTNAME + '/uploads/' + image_obj.image_name + '/thumbnail-200px',
                            'height': 200,
                            'expired_url': settings.HOSTNAME + '/fetch_expiring_link/' + image_obj.image_name + '/thumbnail-200px{/seconds}'
                        },
                        {
                            'url': settings.HOSTNAME + '/uploads/' + image_obj.image_name + '/thumbnail-400px',
                            'height': 400,
                            'expired_url': settings.HOSTNAME + '/fetch_expiring_link/' + image_obj.image_name + '/thumbnail-400px{/seconds}'
                        }
                    ],
                    'original': 
                    {
                        'url': settings.HOSTNAME + '/uploads/' + image_obj.image_name,
                        'expired_url': settings.HOSTNAME + '/fetch_expiring_link/' + image_obj.image_name + '{/seconds}'
                    }
                }
            ]
        )

class ImageViewTestCase(APITestCase):

    def save_plan(self, plan_name: str):
        user = models.User.objects.get(username="testName")
        plan_obj = models.Plan.objects.get(name=plan_name)
        user.plan_id = plan_obj.id
        user.save()
        client.force_authenticate(user=user)
        return user
    
    def create_image(self, user):
        image = SimpleUploadedFile(
            name='test_image.jpg', 
            content=open('./static/test_images/valid_image.jpg', 'rb').read(), 
            content_type='image/jpeg'
        )
        image_obj = models.Image.objects.create(user_id=user.id, image=image)
        image_obj.save()
        
        return image_obj

    def test_valid_original_image_view(self):
        user = self.save_plan("Enterprise")
        image_obj = self.create_image(user)
        response = client.get(settings.HOSTNAME + image_obj.get_link_to_file(height=None))
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_name_original_image_view(self):
        user = self.save_plan("Enterprise")
        response = client.get(settings.HOSTNAME + '/uploads/aasdasdasd')
        self.assertEqual(response.status_code, 404)
    
    def test_is_not_provided_original_image_view(self):
        user = self.save_plan("Basic")
        image_obj = self.create_image(user)
        response = client.get(settings.HOSTNAME + image_obj.get_link_to_file(height=None))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"].code, 'permission_denied')
    
    def test_is_not_provided_original_image_view(self):
        user = self.save_plan("Enterprise")
        image_obj = self.create_image(user)
        response = client.get(settings.HOSTNAME + image_obj.get_link_to_file(height=None))
        print(response.data["detail"].code)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"].code, 'permission_denied')

    def test_valid_thumbnail_image_view(self):
        user = self.save_plan("Basic")
        image_obj = self.create_image(user)
        response = client.get(settings.HOSTNAME + image_obj.get_link_to_file(height=200))
        self.assertEqual(response.status_code, 200)
    
    def test_height_is_not_provided_thumbnail_image_view(self):
        user = self.save_plan("Basic")
        image_obj = self.create_image(user)
        response = client.get(settings.HOSTNAME + image_obj.get_link_to_file(height=500))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"].code, 'permission_denied')
    
    def test_invalid_height_thumbnail_image_view(self):
        user = self.save_plan("Basic")
        image_obj = self.create_image(user)
        response = client.get(settings.HOSTNAME + image_obj.get_link_to_file(height=50213123120))
        print(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data[0].code, 'invalid')

# class UploadImageTestCase(APITestCase):
#     def setUp(self):
#         # basic_plan = models.Plan.objects.create(
#         #     name="Basic",
#         #     thumbnail_heights=[200]
#         # )
#         # basic_plan.save()
#         # premium_plan = models.Plan.objects.create(
#         #     name="Premium", 
#         #     is_link_to_original_provided=True,
#         #     thumbnail_heights=[200, 400]
#         # )
#         # premium_plan.save()
#         # enterprise_plan = models.Plan.objects.create(
#         #     name="Enterprise", 
#         #     thumbnail_heights=[200, 400],
#         #     is_link_to_original_provided=True, 
#         #     is_expiring_link_generation_provided=True
#         # )
#         # enterprise_plan.save()

#         user = models.User.objects.create_user(username="testName", email="testemail@gmail.com", password="test", plan=basic_plan)
#         # basic_plan.users.add(user)
#         client.force_authenticate(user=user)
#         # new_plan = models.Plan.objects.create()
#         # new_plan_id = new_plan.id
#         # new_plan.save()
#         # new_thumb = models.Thumbnail.objects.create(height=300, plan_id=new_plan_id)
#         # new_thumb.save()
#         # print(models.Plan.objects.get(id=new_plan_id).thumbnails.all())

#     # def test_valid_image(self):
#     #     user = models.User.objects.get(username="testName")
#     #     is_image_created = True 
#     #     try:
#     #         image = SimpleUploadedFile(
#     #             name='test_image.jpg', 
#     #             content=open('./static/test_images/valid_image.jpg', 'rb').read(), 
#     #             content_type='image/jpeg'
#     #         )
#     #         image_obj = models.Image.objects.create(user_id=user.id, image=image)
#     #         image_obj.save()
#     #     except ValidationError as e:
#     #         logger.error("there was an exception %s", str(e))
#     #         is_image_created = False
#     #     self.assertEqual(is_image_created, True)
    
#     # def test_invalid_size_image(self):
#     #     user = models.User.objects.get(username="testName")
#     #     is_image_created = True 
#     #     try:
#     #         image = SimpleUploadedFile(
#     #             name='test_image.jpg', 
#     #             content=open('./static/test_images/invalid_size_image.jpg', 'rb').read(), 
#     #             content_type='image/jpeg'
#     #         )
#     #         context = {"request": TestRequest(user=user)}
#     #         data = {
#     #             "user_id": user.id,
#     #             "image": image
#     #         }
#     #         ser = serializers.ImageSerializer(data=data, context=context)
#     #         ser.is_valid(raise_exception=True)
#     #         ser.save()
#     #     except ValidationError as e:
#     #         logger.debug("there was an exception %s", str(e))
#     #         is_image_created = False
#     #     self.assertEqual(is_image_created, False)
    
#     # def test_invalid_extention_image(self):
#     #     user = models.User.objects.get(username="testName")
#     #     is_image_created = True 
#     #     try:
#     #         image = SimpleUploadedFile(
#     #             name='test_image.gif', 
#     #             content=open('./static/test_images/invalid_extention_image.gif', 'rb').read(), 
#     #             content_type='image/gif'
#     #         )
#     #         context = {"request": TestRequest(user=user)}
#     #         data = {
#     #             "user_id": user.id,
#     #             "image": image
#     #         }
#     #         ser = serializers.ImageSerializer(data=data, context=context)
#     #         ser.is_valid(raise_exception=True)
#     #         ser.save()
#     #     except ValidationError as e:
#     #         logger.error("there was an exception %s", str(e))
#     #         is_image_created = False
#     #     self.assertEqual(is_image_created, False)
    
#     # def test_invalid_name_image(self):
#     #     user = models.User.objects.get(username="testName")
#     #     is_image_created = True 
#     #     try:
#     #         image = SimpleUploadedFile(
#     #             name='asdasdasdasdasdasdsadsadasdsadasdsadsadasdsadasdasdasdasdasd.jpg', 
#     #             content=open('./static/test_images/asdasdasdasdasdasdsadsadasdsadasdsadsadasdsadasdasdasdasdasd.jpg', 'rb').read(), 
#     #             content_type='image/jpg '
#     #         )
#     #         context = {"request": TestRequest(user=user)}
#     #         data = {
#     #             "user_id": user.id,
#     #             "image": image
#     #         }
#     #         ser = serializers.ImageSerializer(data=data, context=context)
#     #         ser.is_valid(raise_exception=True)
#     #         ser.save()
#     #     except ValidationError as e:
#     #         logger.error("there was an exception %s", str(e))
#     #         is_image_created = False
#     #         self.assertEqual(e.detail["image"][0].code, 'max_length') # type: ignore
#     #     self.assertEqual(is_image_created, False)

#     # def test_create_valid_expiring_link(self):
#     #     user = models.User.objects.get(username="testName")
#     #     image = SimpleUploadedFile(
#     #         name='test_image.jpg', 
#     #         content=open('./static/test_images/valid_image.jpg', 'rb').read(), 
#     #         content_type='image/jpeg'
#     #     )
#     #     image_obj = models.Image.objects.create(user_id=user.id, image=image)
#     #     image_obj.save()
#     #     response = client.get('http://127.0.0.1:8000/fetch_expiring_link/' + image_obj.image_name + '/original/300')
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertContains(response, 'http://127.0.0.1:8000' + image_obj.get_link_to_original())
    
#     # def test_create_invalid_seconds_expiring_link(self):
#     #     user = models.User.objects.get(username="testName")
#     #     image = SimpleUploadedFile(
#     #         name='test_image.jpg', 
#     #         content=open('./static/test_images/valid_image.jpg', 'rb').read(), 
#     #         content_type='image/jpeg'
#     #     )
#     #     image_obj = models.Image.objects.create(user_id=user.id, image=image)
#     #     image_obj.save()
#     #     response = client.get('http://127.0.0.1:8000/fetch_expiring_link/' + image_obj.image_name + '/original/10000000')
#     #     self.assertEqual(response.status_code, 400)
    
#     # def test_create_invalid_seconds_expiring_link(self):
#     #     user = models.User.objects.get(username="testName")
#     #     image = SimpleUploadedFile(
#     #         name='test_image.jpg', 
#     #         content=open('./static/test_images/valid_image.jpg', 'rb').read(), 
#     #         content_type='image/jpeg'
#     #     )
#     #     image_obj = models.Image.objects.create(user_id=user.id, image=image)
#     #     image_obj.save()
#     #     response = client.get('http://127.0.0.1:8000/fetch_expiring_link/' + image_obj.image_name + '/original/10000000')
#     #     self.assertEqual(response.status_code, 400)
    