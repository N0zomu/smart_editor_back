from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
import hashlib

from message.models import Message
from team.models import Teammate
from user.models import User
from django.http import JsonResponse
import jwt
from django.conf import settings
import time
from tools.logging_dec import *




# Create your views here.
@csrf_exempt
def register(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)

        nickname = data.get('nickname')
        password = data.get('password')
        email = data.get('email')

        hash_value = hashlib.sha256(password.encode('utf-8')).hexdigest()
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'code': 0,
                'error': '不合法的邮箱！'
            })
        try:
            old_user = User.objects.get(email=email)
        except User.DoesNotExist:
            try:
                user = User.objects.create(email=email, password=hash_value ,nickname=nickname)
                user.save()
            except Exception as e:
                print(e)
                return JsonResponse(
                    {
                        'code': 0,
                        'error': 'Unexpected Error'
                    }
                )
            return JsonResponse({
                'code': 1,
                'message': '恭喜您，注册成功！'
            })
        return JsonResponse(
            {
                'code': 0,
                'error': '用户已存在！'
            }
        )

def make_token(email, expire=3600 * 24):
    key = settings.JWT_TOKEN_KEY
    now_t = time.time()
    payload_data = {'email': email, 'exp': now_t + expire}
    return jwt.encode(payload_data, key, algorithm='HS256')

@csrf_exempt
def login(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        email = data.get('email')
        password = data.get('password')
        hash_value = hashlib.sha256(password.encode('utf-8')).hexdigest()
        try:
            user = User.objects.get(email=email)
        except Exception as e:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '用户未注册！'
                }
            )
        if hash_value != user.password:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '用户名或密码错误！'
                }
            )
        token = make_token(email)

        return JsonResponse(
            {
                'code': 1,
                'message': '登录成功！',
                'id': user.id,
                'email': user.email,
                'nickname': user.nickname,
                'icon': user.icon_url,
                'is_VIP': user.isVIP,
                'token': token
            }
        )

@csrf_exempt
@logging_check
def self_info(request):
    if request.method == 'GET':
        return JsonResponse({
            'code': 1,
            'id': request.myuser.id,
            'email': request.myuser.email,
            'nickname': request.myuser.nickname,
            'icon': request.myuser.icon_url,
            'is_VIP': request.myuser.isVIP
        })

@csrf_exempt
@logging_check
def change_nickname(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        nickname = data.get('newNick')

        request.myuser.nickname = nickname
        request.myuser.save()

        return JsonResponse({
            'code': 200,
            'message': '个人信息修改成功！'
        })

@csrf_exempt
@logging_check
def change_password(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        old_password = data.get('oldPWD')
        old_hash_value = hashlib.sha256(old_password.encode('utf-8')).hexdigest()
        new_password = data.get('newPWD')
        new_hash_value = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
        c_password = data.get('cPWD')

        if new_password != c_password:
            return JsonResponse({
                'code': 0,
                'error': '确认密码与新密码不一致！'
            })

        user = User.objects.get(id = request.myuser.id)
        if user.password != old_hash_value:
            return JsonResponse({
                'code': 0,
                'error': '密码错误！'
            })
        user.password = new_hash_value
        user.save()
        return JsonResponse({
            'code': 1,
            'message': '修改成功'
        })

@csrf_exempt
@logging_check
def change_icon(request):
    if request.method == 'POST':
        icon = request.FILES['icon']

        request.myuser.icon = icon
        request.myuser.save()

        return JsonResponse({
            'code': 1,
            'msg': '修改成功'
        })

@logging_check
def upgrade(request):
    if request.method == 'POST':
        request.myuser.isVIP = True
        request.myuser.save()

        return JsonResponse({
            'code': 1,
            'msg': '修改成功'
        })

@csrf_exempt
@logging_check
def get_icon(request):
    if request.method == 'GET':

        # if not request.myuser.icon:
        #     return JsonResponse({
        #         'code': 0,
        #         'error': '用户未上传头像！'
        #     })
        # print(request.myuser.icon.url)
        return JsonResponse({
            'code': 1,
            'icon_url': request.myuser.icon_url,
            'msg': '返回头像成功！'
        })

@csrf_exempt
@logging_check
def user_info(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        user_id = data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 0,
                'error': '查询用户不存在！'
            })

        return JsonResponse({
            'code': 1,
            'id': user.id,
            'email': user.email,
            'nickname': user.nickname,
            'icon': user.icon_url,
            'is_VIP': user.isVIP,
        })


@csrf_exempt
@logging_check
def user_email_search(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        user_email = data.get('email')
        team_id = data.get('team_id')
        has_in_team = False

        try:
            user = User.objects.get(email=user_email)
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 0,
                'error': '查询用户不存在！'
            })
        for x in Teammate.objects.filter(user_id=user.id):
            if x.team_id == team_id:
                has_in_team = True
                break
        try:
            msg = Message.objects.get(sender_id=request.myuser.id, receiver_id=user.id, ref_type="team", ref_id=team_id, status=0)
        except Exception as e:
            return JsonResponse({
                'code': 1,
                'id': user.id,
                'email': user.email,
                'nickname': user.nickname,
                'icon': user.icon_url,
                'is_VIP': user.isVIP,
                'has_in_team': has_in_team,
                'has_send': False,
            })
        return JsonResponse({
            'code': 1,
            'id': user.id,
            'email': user.email,
            'nickname': user.nickname,
            'icon': user.icon_url,
            'is_VIP': user.isVIP,
            'has_in_team': has_in_team,
            'has_send': True,
        })

@csrf_exempt
@logging_check
def user_name_search(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        key = data.get('key')

        users = User.objects.filter(nickname__contains=key)

        res = [{
            'id': user.id,
            'email': user.email,
            'nickname': user.nickname,
            'icon': user.icon_url,
            'is_VIP': user.isVIP,
        } for user in users]

        return JsonResponse({
            'code': 1,
            'users': res,
            'count': len(res)
        })