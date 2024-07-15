from django.db import models

# Create your models here.

class MindMap(models.Model):  # 用户表
    id = models.AutoField(primary_key=True)
    content = models.TextField(default='')
    doc_id = models.IntegerField(default=0)

    class Meta:
        db_table = 'mind_map'