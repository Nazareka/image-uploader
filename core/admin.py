from django.contrib import admin
from . import models

class UserAdmin(admin.ModelAdmin):
    pass

class PlanAdmin(admin.ModelAdmin):
    pass

class ImageAdmin(admin.ModelAdmin):
    pass



admin.site.register(models.User, UserAdmin)
admin.site.register(models.Plan, PlanAdmin)
admin.site.register(models.Image, ImageAdmin)
