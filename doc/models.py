from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.

class Doc(MPTTModel):
    doc_id = models.AutoField(primary_key=True)
    doc_name = models.CharField(max_length=1024)
    doc_creator = models.IntegerField(default=0)

    is_in_team = models.BooleanField(default=False)
    team_id = models.IntegerField(default=0)

    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    is_folder = models.BooleanField(default=False)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    # class MPTTMeta:
    #     order_insertion_by = ['created']

class Document(models.Model):
    doc_id = models.IntegerField(default=0)
    content = models.TextField(default='')

    class Meta:
        db_table = 'Document'

class Collection(models.Model):  # 团队成员表
    user = models.IntegerField(default=0)
    doc = models.IntegerField(default=0)
    class Meta:
        db_table = 'Collection'