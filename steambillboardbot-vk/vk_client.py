import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
import zmq
import configparser
import json
import asyncio

config = configparser.ConfigParser()
config.read('../config.ini')

save_path = "static/photos/"
socket_config = config['Socket']

socket_host = socket_config['host']
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect(f"tcp://{socket_host}:5556")

vk_config = config['Vk']

vk = vk_api.VkApi(
    token=vk_config['token'])
longpoll = VkLongPoll(vk)
vk_upload = VkUpload(vk)


def text_processing(text_orig):
    text = text_orig.split('\n')[:-2]
    text = '\n'.join(text)
    text += "\n\nИсточник: https://vk.com/steamtrade\nДанное объявление мы взяли из сторонней рассылки." \
            "\nОбращайте на это внимание если совершаете сделку вне нашего сервиса. Не попадитесь на уловки " \
            "мошенников. "

    return text

async def listen_for_messages():
    while True:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                message = event
                if event.group_id == 221560941:
                    message = event

                    text = text_processing(message.text)

                    data = {'id': message.message_id,
                            'picture': 'null',
                            'date': str(message.datetime),
                            'message_text': text,
                            'entities': 'null',
                            'photo': False,
                            'source': 'vk_ST'
                            }

                    data_json = json.dumps(data).encode('utf-8')
                    print(data_json)
                    socket.send(data_json)


asyncio.run(listen_for_messages())
