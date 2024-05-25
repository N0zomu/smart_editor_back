from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from doc.models import Doc, Document
from team.models import Teammate
from tools.logging_dec import logging_check

# Create your views here.
@logging_check
@csrf_exempt
def create_doc(request):
    if request.method == 'POST':

        data_json = json.loads(request.body)

        doc_name = data_json['doc_name']
        doc_creator = request.myuser.id
        is_in_team = data_json['ifteam']
        team_id = data_json.get('team_id')

        parent_id = data_json.get('parent_id')

        is_folder = data_json.get('is_folder')

        doc = Doc(doc_name=doc_name, doc_creator=doc_creator, is_in_team=is_in_team, is_folder=is_folder)

        if is_in_team:
            doc.team_id = team_id
        parent_doc = None
        if parent_id:
            try:
                parent_doc = Doc.objects.get(doc_id=parent_id, is_delete=False)
            except Exception as e:
                return JsonResponse({
                    'code': 0,
                    'message': '父节点文件不存在!'
                })
            doc.parent = parent_doc

        if "/" in doc_name:
            return JsonResponse({
                'code': 0,
                'message': '含有不合法字符!'
            })
        try:
            old_doc = Doc.objects.get(doc_name=doc_name, team_id=doc.team_id, is_delete=False, is_folder=is_folder, parent=parent_doc)
        except Exception as e:
            doc.save()
            document = Document(doc_id=doc.doc_id)
            document.save()
            return JsonResponse({
                'code': 1,
                'message': '创建文档成功!',
                'result': {
                    'doc_id': doc.doc_id,
                    'doc_name': doc.doc_name,
                    'doc_creator': doc.doc_creator,
                    'is_in_team': doc.is_in_team,
                    'team_id': doc.team_id,
                    "created_time": doc.created_time
                }
            })
        return JsonResponse({
            'code': 0,
            'message': '存在同名文件'
        })


@csrf_exempt
def delete_doc(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        doc_id = data.get('doc_id')
        is_folder = data.get('is_folder')

        print(doc_id, is_folder)
        try:
            doc = Doc.objects.get(doc_id=doc_id, is_delete=False, is_folder=is_folder)
        except Exception as e:
            return JsonResponse({
                'code': 0,
                'message': '该文件不存在！'
            })

        doc.is_delete = True
        doc.save()

        if is_folder:
            for c in doc.get_descendants(include_self=False):
                c.is_delete = True
                c.save()
        return JsonResponse({
            'code': 1,
            'message': '删除成功！'
        })

@csrf_exempt
def regain_doc(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        doc_id = data.get('doc_id')
        is_folder = data.get('is_folder')

        try:
            doc = Doc.objects.get(doc_id=doc_id, is_delete=True, is_folder=is_folder)
        except Exception as e:
            return JsonResponse({
                'code': 0,
                'message': '该文件不存在！'
            })

        doc.is_delete = False
        doc.save()

        if is_folder:
            for c in doc.get_descendants(include_self=False):
                c.is_delete = False
                c.save()
        return JsonResponse({
            'code': 1,
            'message': '恢复成功！'
        })

@csrf_exempt
def get_path(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        doc_id = data.get('doc_id')

        try:
            doc = Doc.objects.get(doc_id=doc_id, is_delete=False)
        except Exception as e:
            return JsonResponse({
                'code': 0,
                'message': '该文件不存在！'
            })

        res = []
        for c in doc.get_ancestors(include_self=False):
            res.append({"id": c.doc_id,
                        "name": c.doc_name})

        return JsonResponse({
            'code': 1,
            'res': res,
            'count': len(res)
        })

@logging_check
def root_doc(request):
    if request.method == 'GET':

        docs = Doc.objects.filter(doc_creator=request.myuser.id, parent=None, is_delete=False, team_id=0)

        res = []
        for c in docs:
            res.append({"doc_id": c.doc_id,
                        "doc_name": c.doc_name,
                        "doc_creator": c.doc_creator,
                        "created_time": c.created_time,
                        "update_time": c.update_time,
                        "is_folder": c.is_folder,
                        })

        return JsonResponse({
            'code': 1,
            'res': res,
            'count': len(res)
        })

@logging_check
def team_root_doc(request):
    if request.method == 'POST':

        json_str = request.body
        data = json.loads(json_str)
        team_id = data.get('team_id')

        try:
            u = Teammate.objects.get(team_id=team_id, user_id=request.myuser.id)
        except Exception as e:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '用户不在团队中！'
                }
            )

        docs = Doc.objects.filter(parent_id=None, is_delete=False, team_id=team_id)

        res = []
        for c in docs:
            res.append({"doc_id": c.doc_id,
                        "doc_name": c.doc_name,
                        "doc_creator": c.doc_creator,
                        "created_time": c.created_time,
                        "update_time": c.update_time,
                        "is_folder": c.is_folder,
                        })

        return JsonResponse({
            'code': 1,
            'res': res,
            'count': len(res)
        })

@logging_check
def folder_doc(request):
    if request.method == 'POST':

        json_str = request.body
        data = json.loads(json_str)
        doc_id = data.get('doc_id')

        try:
            doc = Doc.objects.get(doc_id=doc_id, is_delete=False, doc_creator=request.myuser.id)
        except Exception as e:
            return JsonResponse({
                'code': 0,
                'message': '该文件不存在！'
            })
        if doc.is_folder is not True:
            return JsonResponse({
                'code': 0,
                'message': '该文件不是文件夹！'
            })

        docs = Doc.objects.filter(parent_id=doc_id, is_delete=False)

        res = []
        for c in docs:
            res.append({"doc_id": c.doc_id,
                        "doc_name": c.doc_name,
                        "doc_creator": c.doc_creator,
                        "created_time": c.created_time,
                        "update_time": c.update_time,
                        "is_folder": c.is_folder,
                        })

        return JsonResponse({
            'code': 1,
            'res': res,
            'count': len(res)
        })

@logging_check
def move_doc(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        src_doc = data.get('src_doc')
        dst_doc = data.get('dst_doc')

        try:
            src = Doc.objects.get(doc_id=src_doc, is_delete=False)
        except Exception as e:
            return JsonResponse({
                'code': 0,
                'message': '源文件不存在！'
            })
        if dst_doc is not None:
            try:
                dst = Doc.objects.get(doc_id=dst_doc, is_delete=False, is_folder=True)
                src.parent = dst
                src.save()
            except Exception as e:
                return JsonResponse({
                    'code': 0,
                    'message': '目标文件夹不存在！'
                })
        else:
            src.parent = None
            src.save()

        return JsonResponse({
            'code': 1,
            'message': '移动成功！'
        })

# 删除团队中所有文件
@logging_check
def team_doc_delete(request):
    if request.method == 'POST':

        json_str = request.body
        data = json.loads(json_str)
        team_id = data.get('team_id')

        try:
            u = Teammate.objects.get(team_id=team_id, user_id=request.myuser.id, perm=1)
        except Exception as e:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '用户无此权限！'
                }
            )

        docs = Doc.objects.filter(parent_id=None, is_delete=False, team_id=team_id)

        for c in docs:
            c.is_delete = True
            c.save()
            if c.is_folder:
                for d in c.get_descendants(include_self=False):
                    d.is_delete = True
                    d.save()


        return JsonResponse({
            'code': 1,
            'message': '删除成功！'
        })


# 恢复团队中所有文件
@logging_check
def team_doc_regain(request):
    if request.method == 'POST':

        json_str = request.body
        data = json.loads(json_str)
        team_id = data.get('team_id')

        try:
            u = Teammate.objects.get(team_id=team_id, user_id=request.myuser.id, perm=1)
        except Exception as e:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '用户无此权限！'
                }
            )

        docs = Doc.objects.filter(parent_id=None, is_delete=False, team_id=team_id)

        for c in docs:
            c.is_delete = False
            c.save()
            if c.is_folder:
                for d in c.get_descendants(include_self=False):
                    d.is_delete = False
                    d.save()

        return JsonResponse({
            'code': 1,
            'message': '恢复成功！'
        })