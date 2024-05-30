from django.db import models
from user.models import User
# Create your models here.

class Team(models.Model):  # 团队表
    team_id = models.AutoField(primary_key=True)
    teamName = models.CharField(max_length=20)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    creator = models.IntegerField()

    class Meta:
        db_table = 'team'


class Teammate(models.Model):  # 团队成员表
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    perm = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Teammate'