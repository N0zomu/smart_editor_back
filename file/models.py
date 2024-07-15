from django.db import models
from django.conf import settings
import urllib.parse


def upload_to(instance, filename):
    return '/'.join([settings.MEDIA_ROOT, 'file', instance.doc_id, filename])
# Create your models here.
class File(models.Model):  # 用户表
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=512, default='default file')
    content = models.TextField(default='')
    doc_id = models.IntegerField(default=0)
    file = models.FileField(upload_to=upload_to, default='')
    type = models.CharField(max_length=50, default='img')
    @property
    def file_url(self):
        if self.file and hasattr(self.file, 'url'):
            return urllib.parse.unquote(self.file.url)
        else:
            return ""
    class Meta:
        db_table = 'files'