from django.shortcuts import render
from tools.logging_dec import logging_check
from team.models import Team, Teammate
from user.models import User
import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# 建立团队
@csrf_exempt
@logging_check
def create_team(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        team_name = data.get('team_name')

        team = Team.objects.create(teamName = team_name, creator=request.myuser.id)
        team.save()

        team_id = team.team_id
        teamMate = Teammate.objects.create(team=team, perm=settings.TEAM_CREATOR, user=request.myuser)
        teamMate.save()

        return JsonResponse(
            {
                'code': 1,
                'message': '团队创建成功！',
                'team_id': team_id
            }
        )

@csrf_exempt
@logging_check
def all_team(request):
    if request.method == 'GET':
        teams = []
        for x in Teammate.objects.order_by('perm').filter(user_id=request.myuser.id):
            team = Team.objects.get(team_id=x.team_id)
            teams.append({
                'team_id': team.team_id,
                'team_name': team.teamName,
                'creator_id': team.creator,
                'creator': request.myuser.nickname if x.perm else User.objects.get(id=team.creator).nickname,
                'created_time': team.created_time,
                'updated_time': team.updated_time,
                'perm': x.perm
            })
        return JsonResponse(
            {
                'code': 1,
                'message': '返回成功！',
                'res': teams,
                'count': len(teams)
            }
        )

@csrf_exempt
@logging_check
def add_member(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        team_id = data.get('team_id')
        user_id = data.get('user_id')

        old_relation = Teammate.objects.filter(team_id=team_id)
        for r in old_relation:

            if r.user_id == user_id:
                return JsonResponse(
                    {
                        'code': 0,
                        'error': '该成员已在团队中！'
                    }
                )

        teamMate = Teammate.objects.create(team_id=team_id, perm=settings.TEAM_MEMBER, user_id=user_id)
        teamMate.save()

        return JsonResponse(
            {
                'code': 1,
                'message': '添加队员成功！',
                'team_id': team_id,
                'user_id': user_id,
            }
        )

@csrf_exempt
@logging_check
def quit_member(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        team_id = data.get('team_id')
        user_id = data.get('user_id')

        try:
            u = Teammate.objects.get(team_id=team_id, user_id=user_id)
        except Exception as e:
            print('delete member error %s' % e)
            return JsonResponse(
                {
                    'code': 0,
                    'error': '该用户不存在！'
                }
            )
        if u.perm == 1:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '不可删除管理员！'
                }
            )
        u.delete()
        return JsonResponse(
            {
                'code': 1,
                'message': '删除队员成功！'
            }
        )

@csrf_exempt
@logging_check
def delete_team(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        team_id = data.get('team_id')


        try:
            u = Teammate.objects.get(team_id=team_id, user_id=request.myuser.id)
        except Exception as e:
            print('delete member error %s' % e)
            return JsonResponse(
                {
                    'code': 0,
                    'error': '用户不在团队中！'
                }
            )
        if u.perm != 1:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '用户没有解散团队的权限！'
                }
            )
        try:
            t = Team.objects.get(team_id=team_id)
        except Exception as e:
            print('delete team error %s' % e)
            return JsonResponse(
                {
                    'code': 0,
                    'error': '不存在该团队！'
                }
            )
        # t.is_delete = True
        # t.save()
        t.delete()

        #################### delete? #########################
        old_relation = Teammate.objects.filter(team_id=team_id)

        for r in old_relation:
            r.delete()

        return JsonResponse(
            {
                'code': 1,
                'message': '解散队伍成功！'
            }
        )

@logging_check
def regain_team(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        team_id = data.get('team_id')


        try:
            u = Teammate.objects.get(team_id=team_id, user_id=request.myuser.id)
        except Exception as e:
            print('delete member error %s' % e)
            return JsonResponse(
                {
                    'code': 0,
                    'error': '用户不在团队中！'
                }
            )
        if u.perm != 1:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '用户没有恢复团队的权限！'
                }
            )
        try:
            t = Team.objects.get(team_id=team_id)
        except Exception as e:
            print('delete team error %s' % e)
            return JsonResponse(
                {
                    'code': 0,
                    'error': '不存在该团队！'
                }
            )
        t.is_delete = False
        t.save()

        ##################### delete? #########################
        # old_relation = Teammate.objects.filter(team_id=team_id)
        #
        # for r in old_relation:
        #     r.delete()

        return JsonResponse(
            {
                'code': 1,
                'message': '恢复队伍成功！'
            }
        )

# 查看团队里的所有成员的信息
@csrf_exempt
@logging_check
def see_members(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        flag = 0
        team_id = data.get('team_id')
        for x in Teammate.objects.filter(user_id=request.myuser):
            if x.team_id == team_id:
                flag = 1
                break
        if flag == 0:
            return JsonResponse({
                'code': 0,
                'error': '你无法查看你没有加入的团队信息'
            })
        team_mates = []
        for x in Teammate.objects.filter(team_id=team_id):
            user = User.objects.get(id=x.user_id)
            team_mates.append({
                'user_id': x.user_id,
                'perm': x.perm,
                'nickname': user.nickname,
                'email': user.email,
                'icon': user.icon_url
            })

        return JsonResponse({
                'code': 1,
                'message': '查询成功！',
                'res': team_mates,
                'count': len(team_mates)
            })

@csrf_exempt
@logging_check
def team_info(request, team_id):
    if request.method == 'GET':
        try:
            tm = Teammate.objects.get(team_id=team_id, user_id=request.myuser.id)
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 0,
                'error': '未加入该团队！'
            })

        try:
            team = Team.objects.get(team_id=team_id)
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 0,
                'error': '团队不存在！'
            })

        return JsonResponse({
            'code': 200,
            'message': "返回成功！",
            'team_id': team.team_id,
            'team_name': team.teamName,
            'creator': User.objects.get(id=team.creator).nickname,
            'created_time': team.created_time,
            'update_time': team.updated_time
        })

@logging_check
def search_team(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        key = data.get('key')

        # teams = Team.objects.filter(teamName__contains=key, is_delete=False)
        #
        # res = [{
        #     'team_id': team.team_id,
        #     'team_name': team.teamName,
        #     'creator': User.objects.get(id=team.creator).nickname,
        #     'created_time': team.created_time,
        #     'updated_time': team.updated_time,
        # } for team in teams]

        res = []
        for x in Teammate.objects.order_by('perm').filter(user_id=request.myuser.id):
            team = Team.objects.get(team_id=x.team_id)
            if key in team.teamName:
                res.append({
                    'team_id': team.team_id,
                    'team_name': team.teamName,
                    'creator_id': team.creator,
                    'creator': request.myuser.nickname if x.perm else User.objects.get(id=team.creator).nickname,
                    'created_time': team.created_time,
                    'updated_time': team.updated_time,
                    'perm': x.perm
                })

        return JsonResponse({
            'code': 1,
            'users': res,
            'count': len(res)
        })

@logging_check
def quit_team(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        team_id = data.get('team_id')
        try:
            tm = Teammate.objects.get(team_id=team_id, user_id=request.myuser.id)
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 0,
                'error': '未加入该团队！'
            })

        tm.delete()

        return JsonResponse({
            'code': 1,
            'message': "退出成功！",
        })