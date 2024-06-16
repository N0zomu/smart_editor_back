import json

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from doc.models import Doc, Document, Collection
from team.models import Teammate
from tools.logging_dec import logging_check
from user.models import User


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
            if not is_folder:
                document = Document(doc_id=doc.doc_id)
                document.save()
            return JsonResponse({
                'code': 1,
                'message': '创建文档成功!',
                'result': {
                    'doc_id': doc.doc_id,
                    'doc_name': doc.doc_name,
                    'doc_creator': request.myuser.nickname,
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

        # if is_folder:
        #     for c in doc.get_descendants(include_self=False):
        #         c.is_delete = True
        #         c.save()
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

        for c in doc.get_ancestors(include_self=False):
            if c.is_delete:
                doc.parent = None
                doc.save()
                return JsonResponse({
                    'code': 1,
                    'message': '无法恢复到原路径，已恢复到桌面'
                })

        # if is_folder:
        #     for c in doc.get_descendants(include_self=False):
        #         c.is_delete = False
        #         c.save()
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
        for c in doc.get_ancestors(include_self=True):
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
        collections = Collection.objects.filter(user=request.myuser.id)
        res = []
        id_group = []
        for c in collections:
            id_group.append(c.doc)
        for c in docs:
            res.append({"doc_id": c.doc_id,
                        "doc_name": c.doc_name,
                        "doc_creator": request.myuser.nickname,
                        "created_time": c.created_time,
                        "update_time": c.update_time,
                        "is_folder": c.is_folder,
                        "is_collect": c.doc_id in id_group,
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

        collections = Collection.objects.filter(user=request.myuser.id)
        res = []
        id_group = []
        for c in collections:
            id_group.append(c.doc)
        for c in docs:
            res.append({"doc_id": c.doc_id,
                        "doc_name": c.doc_name,
                        "doc_creator": User.objects.get(id=c.doc_creator).nickname,
                        "created_time": c.created_time,
                        "update_time": c.update_time,
                        "is_folder": c.is_folder,
                        "is_collect": c.doc_id in id_group,
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

        collections = Collection.objects.filter(user=request.myuser.id)
        res = []
        id_group = []
        for c in collections:
            id_group.append(c.doc)
        for c in docs:
            res.append({"doc_id": c.doc_id,
                        "doc_name": c.doc_name,
                        "doc_creator": User.objects.get(id=c.doc_creator).nickname,
                        "created_time": c.created_time,
                        "update_time": c.update_time,
                        "is_folder": c.is_folder,
                        "is_collect": c.doc_id in id_group,
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

@logging_check
def add_collect(request):
    if request.method == 'POST':

        json_str = request.body
        data = json.loads(json_str)
        doc_id = data.get('doc_id')

        try:
            doc = Doc.objects.get(doc_id=doc_id)
        except Exception as e:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '对应文档不存在！'
                }
            )

        try:
            c = Collection.objects.get(user=request.myuser.id, doc=doc_id)
            return JsonResponse(
                {
                    'code': 0,
                    'error': '已收藏！'
                }
            )
        except Exception as e:
            print(e)
            collection = Collection(user=request.myuser.id, doc=doc_id)
            collection.save()

            return JsonResponse({
                'code': 1,
                'message': '收藏成功！'
            })

@logging_check
def remove_collect(request):
    if request.method == 'POST':

        json_str = request.body
        data = json.loads(json_str)
        doc_id = data.get('doc_id')
        print(request.myuser.id, doc_id)
        try:
            c = Collection.objects.get(user=request.myuser.id, doc=doc_id)
        except Exception as e:
            print(e)
            return JsonResponse(
                {
                    'code': 0,
                    'error': '未收藏！'
                }
            )

        c.delete()

        return JsonResponse({
            'code': 1,
            'message': '取消收藏成功！'
        })

@logging_check
def get_collection(request):
    if request.method == 'GET':
        collections = Collection.objects.filter(user=request.myuser.id)

        res = []
        id_group = []
        for c in collections:
            id_group.append(c.doc)
            doc = Doc.objects.get(doc_id=c.doc)
            res.append({
                'doc_id': doc.doc_id,
                'doc_name': doc.doc_name,
                "doc_creator": User.objects.get(id=c.user).nickname,
                'is_in_team': doc.is_in_team,
                'team_id': doc.team_id,
                "created_time": doc.created_time,
                "update_time": doc.update_time,
            })

        return JsonResponse({
            'code': 1,
            'res': res,
            'id_group': id_group,
            'count': len(res)
        })

@logging_check
def update_time(request):
    if request.method == 'POST':

        json_str = request.body
        data = json.loads(json_str)
        doc_id = data.get('doc_id')

        try:
            doc = Doc.objects.get(doc_id=doc_id)
        except Exception as e:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '对应文档不存在！'
                }
            )
        doc.update_time = timezone.now()
        doc.save()

        return JsonResponse({
            'code': 1,
            'message': '更新成功！',
            'update_time': doc.update_time
        })