import json
import erniebot
from django.http import JsonResponse
from django.shortcuts import render

from tools.logging_dec import logging_check
from django.conf import settings

# Create your views here.
@logging_check
def polish(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        key = settings.AI_TOKEN
        quescont = data.get('cont')
        askcont="帮我润色下面这段话:"+quescont

        erniebot.api_type = 'aistudio'
        erniebot.access_token = key

        try:
            response = erniebot.ChatCompletion.create(
                model='ernie-bot',
                messages=[{'role': 'user', 'content': askcont}],
            )
            restext = response['result']
            return JsonResponse({
                'code': 1,
                'answer': restext,
                'message': '返回成功！'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 0,
                'message': 'something goes wrong...',
            })

@logging_check
def continuation(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        key = settings.AI_TOKEN
        quescont = data.get('cont')
        askcont="帮我续写下面这段话:"+quescont

        erniebot.api_type = 'aistudio'
        erniebot.access_token = key

        try:
            response = erniebot.ChatCompletion.create(
                model='ernie-bot',
                messages=[{'role': 'user', 'content': askcont}],
            )
            restext = response['result']
            return JsonResponse({
                'code': 1,
                'answer': restext,
                'message': '返回成功！'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 0,
                'message': 'something goes wrong...',
            })