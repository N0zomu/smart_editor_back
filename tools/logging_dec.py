from django.http import JsonResponse
import jwt
from django.conf import settings
from user.models import User


def logging_check(func):
    def wrap(request, *args, **kwargs):

        # token
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            result = {'code': 403, 'error': 'Please login'}
            return JsonResponse(result)
        # jwt
        try:
            res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
        except Exception as e:
            print(e)
            result = {'code': 403, 'error': 'Please login'}
            return JsonResponse(result)

        # decode的返回值是字典
        email = res['email']

        user = User.objects.get(email=email)
        request.myuser = user
        # 视图中可以用request.myuser获取当前用户

        return func(request, *args, **kwargs)


    return wrap