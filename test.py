import erniebot

erniebot.api_type = 'aistudio'
erniebot.access_token = '45dbd1155454209811e8b451c2a2fa8743fe8234'

response = erniebot.ChatCompletion.create(
    model='ernie-3.5',
    messages=[{'role': 'user', 'content': "你是?"}],
)
print(response.get_result())
