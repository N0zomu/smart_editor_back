from django.db import models
from user.models import User
from team.models import Team
# Create your models here.
class Message(models.Model):  # 消息表
    msg_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='senders')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receivers')
    is_deleted = models.BooleanField(default=False)

    is_team = models.BooleanField(default=False)
    team_id = models.IntegerField(default=0)

    ref_type = models.CharField(max_length=128, default='')
    ref_id = models.IntegerField(default=0)

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    status = models.IntegerField(default=0)

    class Meta:
        db_table = 'message'