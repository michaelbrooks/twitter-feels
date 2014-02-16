from django.contrib import admin

# Register your models here.
import models

admin.site.register(models.FeelingGroup)
admin.site.register(models.FeelingPrefix)
admin.site.register(models.FeelingWord)
admin.site.register(models.TimeFrame)
