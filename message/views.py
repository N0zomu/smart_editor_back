from django.shortcuts import render
from django.http import JsonResponse
import json
from user.models import User
from team.models import Teammate, Team
from doc.models import *
from tools.logging_dec import logging_check
from message.models import Message



# Create your views here.
@logging_check
def create_message(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        rec_id = data.get('rec_id')

        is_team = data.get('is_team')
        team_id = data.get('team_id')

        ref_type = data.get('ref_type') if data.get('ref_type') else ''
        ref_id = data.get('ref_id') if data.get('ref_id') else 0

        if rec_id == request.myuser.id:
            return JsonResponse(
                {
                    'code': 11002,
                    'error': '不可给自己发送消息！'
                }
            )
        try:
            rec_user = User.objects.get(id=rec_id)
        except Exception as e:
            print(e)
            return JsonResponse(
                {
                    'code': 11001,
                    'error': '接收者不存在！'
                }
            )
        if ref_type == 'team':
            try:
                team = Team.objects.get(team_id=ref_id)
            except Exception as e:
                print(e)
                return JsonResponse(
                    {
                        'code': 11003,
                        'error': '团队获取错误！'
                    }
                )
        elif ref_type == 'doc':
            try:
                team = Team.objects.get(team_id=team_id)
            except Exception as e:
                print(e)
                return JsonResponse(
                    {
                        'code': 11003,
                        'error': '团队获取错误！'
                    }
                )
            try:
                relation = Teammate.objects.get(user_id=rec_id, team_id=team_id)
            except Exception as e:
                print(e)
                return JsonResponse(
                    {
                        'code': 11004,
                        'error': '接收者不在团队中！'
                    }
                )
            try:
                doc = Doc.objects.get(doc_id=ref_id, is_delete=False)
            except Exception as e:
                return JsonResponse({
                    'code': 11201,
                    'error': '该文档不存在！'
                })

        msg = Message.objects.create(receiver=rec_user, sender=request.myuser, is_team=is_team, team_id=team_id if is_team else 0,
                                     ref_type=ref_type, ref_id=ref_id)
        msg.save()
        return JsonResponse({
            'code': 200,
            'message': '消息发送成功！',
            'msg_id': msg.msg_id,
            'receiver': msg.receiver_id,
            'sender': msg.sender_id,
            'is_team': msg.is_team,
            'team': msg.team_id,
            'send_time': msg.created_time,
            'ref_type': msg.ref_type,
            'ref_id': msg.ref_id
        })

# 查看所有消息
@logging_check
def all_messages(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        status = data.get('status')

        if status is not None:
            all_msg = Message.objects.filter(receiver_id=request.myuser.id, status=status, is_deleted=False).order_by('-created_time')
            messages = [{
                'msg_id': x.msg_id,
                'sender': User.objects.get(id=x.sender_id).nickname,
                'is_team': x.is_team,
                'team_id': x.team_id,
                'send_time': x.created_time,
                'ref_type': x.ref_type,
                'ref_id': x.ref_id,
                'ref_name': Team.objects.get(team_id=x.ref_id).teamName if x.ref_type=='team' else Doc.objects.get(doc_id=x.ref_id).doc_name
            } for x in all_msg]

        else:
            all_msg = Message.objects.filter(receiver_id=request.myuser.id, is_deleted=False).order_by('-created_time')
            messages = [{
                'msg_id': x.msg_id,
                'sender': User.objects.get(id=x.sender_id).nickname,
                'is_team': x.is_team,
                'team_id': x.team_id,
                'send_time': x.created_time,
                'ref_type': x.ref_type,
                'ref_id': x.ref_id
            } for x in all_msg]

        return JsonResponse({
            'code': 200,
            'status': status,
            'messages': messages,
            'count': all_msg.count()
        })

# 修改状态
@logging_check
def change_message(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        msg_id = data.get('msg_id')

        try:
            msg = Message.objects.get(msg_id=msg_id, receiver_id=request.myuser.id, is_deleted=False)
        except Exception as e:
            print(e)
            return JsonResponse(
                {
                    'code': 11101,
                    'error': '该消息不存在！'
                }
            )

        if msg.status == 1:
            return JsonResponse(
                {
                    'code': 11102,
                    'error': '该消息已处理！'
                }
            )

        msg.status = 1
        msg.save()
        return JsonResponse({
            'code': 200,
            'msg': '消息状态修改成功！'
        })

@logging_check
def delete_message(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        msg_id = data.get('msg_id')

        try:
            msg = Message.objects.get(msg_id=msg_id, receiver_id=request.myuser.id, is_deleted=False)
        except Exception as e:
            print(e)
            return JsonResponse(
                {
                    'code': 11101,
                    'error': '该消息不存在！'
                }
            )

        msg.is_deleted = True
        msg.save()
        return JsonResponse({
            'code': 200,
            'msg': '消息删除成功！'
        })

# 一键设置所有已读 一键删除所有已读消息
@logging_check
def change_all(request):
    json_str = request.body
    data = json.loads(json_str)
    team_id = data.get('team_id')
    all_msg = Message.objects.filter(team_id=team_id, is_deleted=False)
    # 未读消息一键设置所有已读
    if request.method == 'PUT':
        messages = all_msg.filter(receiver_id=request.myuser.id, is_read=False)
        count = 0
        for m in messages:
            m.is_read = True
            m.save()
            count += 1

        return JsonResponse({
            'code': 200,
            'num': count,
            'msg': '消息已读状态修改成功！'
        })

    # 一键删除所有已读消息
    if request.method == 'POST':
        messages = all_msg.filter(receiver_id=request.myuser.id, is_read=True)
        count = 0
        for m in messages:
            m.is_deleted = True
            m.save(),
            count += 1

        return JsonResponse({
            'code': 200,
            'num': count,
            'msg': '消息删除成功！'
        })

@logging_check
def message_info(request, msg_id):
    if request.method == 'GET':
        try:
            msg = Message.objects.get(msg_id=msg_id, is_deleted=False)
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 11101,
                'error': '消息不存在！'
            })

        return JsonResponse({
            'code': 200,
            'message': "返回成功！",
            'msg_id': msg.msg_id,
            'status': msg.status,
            'is_team': msg.is_team,
            'team': msg.team_id,
            'sender_id': msg.sender_id,
            'created_time': msg.created_time,
            'update_time': msg.updated_time,
            'ref_type': msg.ref_type,
            'ref_id': msg.ref_id
        })