import json
import os

import erniebot
from django.http import JsonResponse
from django.shortcuts import render

from file.models import File
from tools.logging_dec import logging_check
from django.conf import settings
import requests
import base64
import pathlib

# Create your views here.
@logging_check
def polish(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        key = settings.AI_TOKEN
        env = data.get('env')
        details = data.get('detail')
        quescont = data.get('cont')
        function = data.get('func')

        prompt = ''
        if function == 'summary':
            prompt = '请给出下面这段话的摘要:'
        elif function == 'polish':
            prompt = '请帮我润色下面这段话:'
        elif function == 'continue':
            prompt = '请帮我续写下面这段话:'
        elif function == 'revise':
            prompt = '下面这段话包含病句，请修改:'
        elif function == 'translateE':
            prompt = '请将下面这段话翻译为英语:'
        elif function == 'translateC':
            prompt = '请将下面这段话翻译为中文:'


        askcont = ''
        if env != '':
            askcont = "我正在撰写一份"+env+"，这份文档的具体要求为："+details+"。"

        askcont += prompt + quescont
        askcont += "请注意，我给出的段落可能是一个json对象，这是因为该段落的来源为tiptap编辑器。你只需要阅读并理解其中text字段的内容。"
        askcont += "无论我提供的段落的格式是什么，请直接给出你的文本结果（不需包含其他格式）"

        print(askcont)

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
def mindmap(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        key = settings.AI_TOKEN

        quescont = data.get('cont')

        example = [{
          "name":"如何学习D3",
          "children": [
            {
              "name":"预备知识",
              "children": [
                { "name":"HTML & CSS" },
                { "name":"JavaScript" },
              ]
            },
            {
              "name":"安装",
              "children": [ { "name": "折叠节点" } ]
            },
            { "name":"进阶"},
          ]
        }]

        prompt = "请你用我提供的格式，返回这篇文章的树形结构。\n"
        prompt += "树形结构中，每一个节点都是一个js对象。\n"
        prompt += "树形结构的父节点格式为：{\"name\":\"节点内容\",\"children\": [{}, {}, {}]}\n"
        prompt += "树形结构的叶子节点格式为：{\"name\":\"节点内容\"} \n"
        prompt += "一个可以参考的格式为：" + json.dumps(example, indent=2, ensure_ascii=False)
        prompt += "请确保你的输出与参考格式保持一致。\n"
        prompt += "我提供的文章为："
        prompt += quescont
        prompt += "注意：你的返回应该是能直接被解析的json字符串！为了保证返回的完整性，你返回的字符串长度应不超过200个词。"

        print(prompt)

        erniebot.api_type = 'aistudio'
        erniebot.access_token = key
        restext = ''
        try:
            response = erniebot.ChatCompletion.create(
                model='ernie-bot',
                messages=[{'role': 'user', 'content': prompt}],
                stream=True
            )
            for r in response:
                print(r)
                restext+=r.result

            restext = restext.replace('```json\n', '')
            restext = restext.replace('```', '')
            restext = restext.replace('\n', '')
            restext = restext.replace('\\n', '')
            restext = restext.replace(' ', '')
            print(restext)
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
def typeset(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        key = settings.AI_TOKEN
        quescont = data.get('cont')
        askcont=("以下是一段文本内容，请你根据内容分析将其进行合理的排版，包括但不限于缩进、调整字号、标题等级调整、去掉无意义的空白字符"
                 "设置或者取消有序列表、无序列表等，"
                 "请直接返回你的回答，以HTML格式，并转换为纯文本字符串的形式，不要包括其他内容,也不用换行:")+quescont
        askcont+="注意：请保证你输出的正确性。"
        erniebot.api_type = 'aistudio'
        erniebot.access_token = key

        try:
            response = erniebot.ChatCompletion.create(
                model='ernie-bot',
                messages=[{'role': 'user', 'content': askcont}],
                stream=True
            )
            restext = ''

            for r in response:
                print(r)
                restext+=r.result

            restext = restext.replace('```html\n', '')
            restext = restext.replace('```','')
            restext = restext.replace('\n','')
            restext = restext.replace('\\n', '')
            restext = restext.replace(' ', '')
            print(restext)
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
def get_ocr(request):
    if request.method == 'POST':
        json_str = request.body
        data = json.loads(json_str)
        file_id = data.get('file_id')
        key_word = data.get('key_word')

        try:
            file = File.objects.get(id=file_id)
        except Exception:
            return JsonResponse(
                {
                    'code': 0,
                    'error': '该文件不存在！',
                }
            )
        # 參數
        # 基礎ORC
        file_path = file.file_url[5:]
        file_type = 0  # 0表示pdf，1表示圖像
        if file.type == 'img':
            file_type = 1
        elif file.type == 'pdf':
            file_type = 0

        # llm解析ORC結果，建議做成兩個接口
        queryKey = key_word  # 输入想要查询的字段名称，字段名称间需用半角逗号（,）分隔

        CHATOCR_VISUAL_URL = "https://zav2r0lfa2k2y344.aistudio-hub.baidu.com/chatocr_visual"
        CHATOCR_LLM_URL = "https://zav2r0lfa2k2y344.aistudio-hub.baidu.com/chatocr_llm"
        # 请前往 https://aistudio.baidu.com/index/accessToken 查看 访问令牌 并替换
        TOKEN = "914eba8ce3de692244b1eb2d2e22513eeb77e50c"

        # 设置鉴权信息
        headers = {
            "Authorization": f"token {TOKEN}",
            "Content-Type": "application/json"
        }

        file_bytes = pathlib.Path(file_path).read_bytes()
        file_base64 = base64.b64encode(file_bytes).decode('ascii')

        chatocr_visual_payload = {
            "file": file_base64,  # Base64编码的文件内容或者文件链接
            "fileType": file_type,  # 本地文件类型，0:pdf,1:图片，此参数在上传本地文件时必须设置，使用文件链接时可省略
            "aistudioToken": TOKEN,
            "inferenceParams": {
                "maxLongSide": 960  # 文本检测长边的最大值，当大分辨率图片漏检严重时，可调大该值
            }
        }

        chatocr_visual_response = requests.post(CHATOCR_VISUAL_URL, json=chatocr_visual_payload, headers=headers)
        chatocr_visual_response_data = chatocr_visual_response.json()

        strs = chatocr_visual_response_data["result"]["tableOcrResult"]["filter_rec_res"]
        if key_word=='':
            return JsonResponse({
                'code': 1,
                'res': strs,
                'message': '识别成功！',
            })
        # 到這裡 strs 就是識別出的文本，是一個字符串數組，接下來的部分是大模型分析

        # 设置 chatocr_llm 接口请求体
        chatocr_llm_payload = {
            "queryKey": queryKey,
            "aistudioToken": TOKEN,
            "documentType": chatocr_visual_response_data['result']['documentType'],
            "ocrAllResult": chatocr_visual_response_data['result']['ocrAllResult'],
            "tableOcrResult": chatocr_visual_response_data['result']['tableOcrResult'],
            "rules": "",  # 提示词规则（可以留空）
            "fewShot": "",  # 提示词示例（可以留空）
        }

        # # 获取大模型信息抽取的返回结果
        chatocr_chat_response = requests.post(CHATOCR_LLM_URL, json=chatocr_llm_payload, headers=headers)
        chatocr_chat_response_data = chatocr_chat_response.json()
        print(chatocr_chat_response_data)

        return JsonResponse({
            'code': 1,
            'res': chatocr_chat_response_data['result'],
            'message': '识别成功！',
        })