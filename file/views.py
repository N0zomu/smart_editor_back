from django.http import JsonResponse
from django.shortcuts import render
from tools.logging_dec import logging_check
from file.models import File
import json
import os

# Create your views here.

@logging_check
def upload_file(request):
    if request.method == 'POST':
        f = request.FILES['file']
        doc_id = request.POST.get('doc_id')
        last = f.name.split('.')[-1]
        t = ''
        if last in ['jpeg', 'jpg', 'gif', 'png', 'svg']:
            t = 'img'
        if last == 'pdf':
            t = 'pdf'
        if last in ['mp3', 'wav', 'flac']:
            t = 'voice'

        file = File.objects.create(file_name=f.name, file=f, doc_id=doc_id, type=t)
        file.save()
        return JsonResponse(
            {
                'code': 1,
                'message': '文件上传成功！',
                'file_id': file.id,
                'file_name': file.file_name,
                'file_type': file.type,
                'url': file.file_url,
            }
        )


@logging_check
def all_file(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        doc_id = data.get('doc_id')

        files = File.objects.filter(doc_id=doc_id)
        res = []
        for f in files:
            res.append({
                'file_id': f.id,
                'name': f.file_name,
                'url': f.file_url,
                'content': f.content,
                'type': f.type
            })
        return JsonResponse(
            {
                'code': 1,
                'res': res,
            }
        )

@logging_check
def delete_file(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        file_id = data.get('file_id')

        try:
            file = File.objects.get(id=file_id)
        except Exception:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '该文件不存在！',
                }
            )
        p = file.file_url[5:]
        if os.path.exists(p):
            os.remove(p)
            file.delete()
            return JsonResponse(
                {
                    'code': 1,
                    'message': '删除成功！',
                }
            )
        else:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '该文件不存在！',
                }
            )

@logging_check
def update_file(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        file_id = data.get('file_id')
        new = data.get('content')

        try:
            file = File.objects.get(id=file_id)
        except Exception:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '该文件不存在！',
                }
            )
        file.content = new
        file.save()

        return JsonResponse(
            {
                'code': 1,
                'message': '修改成功！',
            }
        )