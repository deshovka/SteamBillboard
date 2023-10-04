import configparser
from telethon import TelegramClient, events
import psycopg2
import json
import zmq
import asyncio
print("Launching index")

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.bind("tcp://*:5556")

socket.setsockopt(zmq.SUBSCRIBE, b"")

config = configparser.ConfigParser()
config.read('../config.ini')

telegram_config = config['Telegram']

api_id = telegram_config['api_id']
api_hash = telegram_config['api_hash']
phone_number = telegram_config['phone_number']

resend_id = int(telegram_config['resend_id'])

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=telegram_config['bot_token'])
client = TelegramClient('session_name', api_id, api_hash, system_version="4.16.30-vxCUSTOM")


db_config = config['Database']
conn = psycopg2.connect(
    host=db_config['host'],
    database=db_config['database'],
    user=db_config['user'],
    password=db_config['password'],
    port=db_config['port']
)


async def send_to_channel(mes_data):
    print(mes_data)
    if mes_data['photo']:
        await bot.send_message(entity=resend_id, message=mes_data['message_text'],
                               file=f"C:/Users/falle/PycharmProjects/SteamBillboardBot/static/photos/{mes_data['picture']}.jpg")
    else:
        await bot.send_message(entity=resend_id, message=mes_data['message_text'])

conn.autocommit = True
cursor = conn.cursor()
print('listening messages from socket')

async def listening_server():
    while True:
        data = socket.recv().decode('utf-8')
        print("Recieved message from socket")
        json_acceptable_string = data.replace("'", "\"")
        data_dict = json.loads(json_acceptable_string)

        source = data_dict['source']

        await send_to_channel(data_dict)
        cursor.execute(f"""INSERT INTO posts (message_id, uid, date, message_text, tg_entities, photo, source) 
            VALUES ({data_dict['id']}, '{data_dict['picture']}', '{str(data_dict['date'])}', '{data_dict['message_text']}',
             '{data_dict['entities']}', '{data_dict['photo']}', '{data_dict['source']}')""")


async def main():
    await bot.start()
    task_bot = asyncio.create_task(bot.run_until_disconnected())
    task_server = asyncio.create_task(listening_server())

    await asyncio.gather(task_bot, task_server)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


