import socketio
import requests
import g4f
from g4f.client import Client


client = Client()
http_session = requests.Session()
http_session.verify = False
sio = socketio.Client(http_session=http_session)

BOT_TAG = 'chatgpt'
BOT_PASSWORD = 'gptpass'

def send_message(chat_id, content, reply_to=None, type='default'):
    response = requests.post('https://coffeetox.ru/sendmsgapi', json={
        'tag': BOT_TAG,
        'password': BOT_PASSWORD,
        'content': content,
        'chat_id': chat_id,
        'reply_to': reply_to,
        'type': type
    }, verify=False)

    try:
        json = response.json()

        if 'success' not in json:
            print('There was an error!')
        if 'error' in json:
            print(json['error'])
    except:
        print('Unknown error!')

def ask_gpt(prompt):
    response = client.chat.completions.create(
        model=g4f.models.default,
        provider=g4f.Provider.FlowGpt,
        max_tokens=100000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def ammend(text):
    return text + '''

    --------------------------------------------
    Поддержите нас, задонатив ебалл данному боту!
'''

@sio.event
def message(data):
    send_message(data['chat_id'], ammend(ask_gpt(data['content'])), data['id'])

@sio.on('error')
def handle_server_error(err):
    print('There was an error:', err)
    sio.disconnect()
    exit()

sio.connect('https://coffeetox.ru')
sio.emit('activate_bot_api', {'tag': BOT_TAG, 'password': BOT_PASSWORD})

sio.wait()
