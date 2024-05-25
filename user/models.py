from django.db import models

# Create your models here.

class User(models.Model):  # 用户表
    id = models.AutoField(primary_key=True)
    nickname = models.CharField(max_length=32, default='default user')  # nickname
    password = models.CharField(max_length=256)
    email = models.EmailField(max_length=32)
    icon = models.FileField(upload_to='icon', default='')
    isVIP = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'