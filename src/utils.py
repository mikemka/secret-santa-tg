from asyncio import run
from database.actions import init_db, shutdown_db
from database.models import User, Message
import logging
import settings
import sys
from pathlib import Path
from csv import reader
from datetime import datetime


async def add_users() -> None:
    users_str = ''
    
    for user_str in users_str.strip().split('\n\n'):
        data_str_list = user_str.strip().split('\n')
        
        data = [
            data_str_list[6],
            data_str_list[3],
            data_str_list[4],
            data_str_list[5],
            data_str_list[0],
            data_str_list[1],
            data_str_list[2],
        ]

    
        user, _ = await User.update_or_create(
            defaults={
                'tg_username': data[1] if data[1] != 'None' else None,
                'tg_first_name': data[2],
                'tg_last_name': data[3] if data[3] != 'None' else None,
                'name': data[4],
                'surname': data[5],
                'additional_info': data[6],
                'confirmed': True,
                'status': 'registration-moderation-confirmed',
            },
            tg_id=int(data[0]),
        )

        from pprint import pprint
        pprint(data)
        pprint(user)


async def add_messages_from_csv() -> None:
    _file = Path(__file__).resolve().parent.parent / 'messages.csv'
    
    fields = []
    
    with _file.open('r', encoding='utf-8') as _data:
        for row in reader(_data):
            if not fields:
                fields = row
                continue
            # "id","text","created_at","from_user_id","to_user_id"

            message_payload = {}

            for field, data in zip(fields, row):
                if field == 'id':
                    message_payload[field] = int(data)
                    continue
                if field == 'created_at':                 
                    message_payload[field] = datetime.fromisoformat(data)
                    continue
                if field in ('from_user_id', 'to_user_id'):
                    message_payload[field[:-3]] = await User.get(id=int(data))
                    continue

                message_payload[field] = data
            
            message = await Message.create(**message_payload)
            print(message)


async def main() -> None:
    await init_db()
    
    try:
        await add_messages_from_csv()
    finally:
        await shutdown_db()



if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO if settings.DEBUG else logging.WARNING,
        stream=sys.stdout,
    )
    run(main())
