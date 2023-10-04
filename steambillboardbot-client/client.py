from telethon import TelegramClient, events
import configparser
import zmq
import datetime
import json

print("Launching resend_messages")
config = configparser.ConfigParser()
config.read('../config.ini')

save_path = "C:/Users/falle/PycharmProjects/SteamBillboardBot/static/photos/"
socket_config = config['Socket']

socket_host = socket_config['host']
print(socket_host)
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect(f"tcp://{socket_host}:5556")

telegram_config = config['Telegram']

api_id = telegram_config['api_id']
api_hash = telegram_config['api_hash']
phone_number = telegram_config['phone_number']

client = TelegramClient('session_name', api_id, api_hash, system_version="4.16.30-vxCUSTOM")


def text_processing(text_orig):
    text = text_orig.split('\n')[:-2]
    text = '\n'.join(text)
    text += "\n\nИсточник: https://t.me/MarketSteamBot\nДанное объявление мы взяли из сторонней рассылки." \
            "\nОбращайте на это внимание если совершаете сделку вне нашего сервиса. Не попадитесь на уловки " \
            "мошенников. "

    return text


async def send_to_index(message):
    new_data = message.to_dict()
    uid = str(int(datetime.datetime.now().timestamp())) + "_" + str(new_data['id'])
    new_data['uid'] = uid
    photo = False

    if message and getattr(message, 'photo') is not None:
        try:
            photo = True
            await client.download_media(message, file=save_path + uid)
        except Exception as e:
            print(e)

    entities = {index: str(value) for index, value in enumerate(message.entities)}

    data = {'id': new_data['id'],
            'picture': new_data['uid'],
            'date': str(new_data['date']),
            'message_text': text_processing(new_data['message']),
            'entities': json.dumps(entities),
            'photo': getattr(message, 'photo') is not None,
            'source': 'tg_MSB'
            }

    data_json = json.dumps(data).encode('utf-8')
    print(data_json)
    print()
    socket.send(data_json)


@client.on(events.NewMessage)
async def handle_new_message(event):
    resend_id = int(telegram_config['resend_id'])
    print("New message")
    if event.message.sender_id == int(telegram_config['listen_id']):  # int(telegram_config['chat_id']): # 6171309331
        message_str = event.message.message
  
        if 'Объявление №' in message_str:
            a = event.message
            print(event.message)
            print('Sending message to index')
            await send_to_index(event.message)


# -1001976215330 - steambillboard channel p.s. add @tst2552bot and give permission to send messages into steambillboard
# -1001630538061 - my test channel
client.start(phone=phone_number)

client.run_until_disconnected()
#bot.run_until_disconnected()
