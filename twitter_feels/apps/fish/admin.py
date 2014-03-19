from django.contrib import admin

# Register your models here.
import models

admin.site.register(models.Emotion)
admin.site.register(models.ExampleTweet)
admin.site.register(models.TimeFrame)
