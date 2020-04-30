from django.db import models
from datetime import datetime
from django.conf import settings



def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/raw_csv/{1}'.format(instance.user.username, filename)

# class DataSet(models.Model):
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     Dataset = models.FileField(upload_to=user_directory_path)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='documents', on_delete=models.CASCADE)


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    dataset = models.FileField(upload_to=user_directory_path)
    label = models.CharField(max_length=200,blank=True)
    date = models.CharField(max_length=200, blank=True)
    ratio = models.IntegerField(blank=True, default=75)
    clean_data = models.FileField(upload_to=user_directory_path, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='documents', on_delete=models.CASCADE)

    def __str__(self):
        return self.title