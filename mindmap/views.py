from django.shortcuts import render
import json
from tools.logging_dec import logging_check
from django.http import JsonResponse
from mindmap.models import MindMap

# Create your views here.


@logging_check
def get_mindmap(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        doc_id = data.get('doc_id')
        try:
            mp = MindMap.objects.get(doc_id=doc_id)
        except Exception:
            return JsonResponse(
                {
                    'code': 0,
                    'message': "该文档没有思维导图！",
                }
            )

        return JsonResponse(
            {
                'code': 1,
                'content': mp.content,
            }
        )

@logging_check
def store_mindmap(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        doc_id = data.get('doc_id')
        content = data.get('content')


        try:
            mp = MindMap.objects.get(doc_id=doc_id)
        except Exception:
            mp = MindMap.objects.create(doc_id=doc_id, content=content)
            mp.save()
            return JsonResponse(
                {
                    'code': 1,
                    'message': '创建成功！',
                    'doc_id': mp.doc_id,
                    'content': mp.content,
                }
            )
        return JsonResponse(
            {
                'code': 1,
                'doc_id': mp.doc_id,
                'content': mp.content,
            }
        )