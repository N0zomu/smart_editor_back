from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
import hashlib
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
                'message': '不合法的邮箱！'
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
                        'message': 'Unexpected Error'
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
                    'message': '用户未注册！'
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
                'token': token
            }
        )

@csrf_exempt
@logging_check
def self_info(request):
    if request.method == 'GET':
        return JsonResponse({
            'code': 1,
            'user_id': request.myuser.id,
            'nickname': request.myuser.nickname,
            'email': request.myuser.email,
        })

@csrf_exempt
@logging_check
def change_nickname(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        nickname = data.get('nickname')

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
        old_password = data.get('old_password')
        old_hash_value = hashlib.sha256(old_password.encode('utf-8')).hexdigest()
        new_password = data.get('new_password')
        new_hash_value = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
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

@csrf_exempt
@logging_check
def get_icon(request):
    if request.method == 'GET':

        if not request.myuser.icon:
            return JsonResponse({
                'code': 0,
                'error': '用户未上传头像！'
            })
        print(request.myuser.icon.url)
        return JsonResponse({
            'code': 1,
            'icon_url': request.myuser.icon.url,
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
            'user_id': user.id,
            'nickname': user.nickname,
            'email': user.email,
            'icon_url': user.icon.url
        })


@csrf_exempt
@logging_check
def user_email_search(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        user_email = data.get('email')

        try:
            user = User.objects.get(email=user_email)
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 0,
                'error': '查询用户不存在！'
            })

        return JsonResponse({
            'code': 1,
            'user_id': user.id,
            'nickname': user.nickname,
            'email': user.email,
            'icon_url': user.icon.url
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
            'user_id': user.id,
            'nickname': user.nickname,
            'email': user.email,
            'icon_url': user.icon.url
        } for user in users]

        return JsonResponse({
            'code': 1,
            'users': res,
            'count': len(res)
        })