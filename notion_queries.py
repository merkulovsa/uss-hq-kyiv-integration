import os
import json
from notion_requests import read_database, update_page

def stock_update_query() -> None:
    database_id_1 = 'd866a45662f240bdbdcb2668e29a0d4f'
    database_id_2 = '748a8405acb34452b65ec4128c8a7ce6'

    addition = {}
    subtraction = {}
    sum = {}

    with open(read_database(database_id_1), 'r') as f:
        data = json.loads(f.read())

        for result in data['results']:
            for relation in result['properties']['Назва в асортименті']['relation']:
                key = relation['id']
                amount = result['properties']['Видано']['number']

                if amount is not None:
                    if key in subtraction:
                        subtraction[key] += amount
                    else:
                        subtraction[key] = amount
        
        f.close()
        os.remove(f.name)

    with open(read_database(database_id_2), 'r') as f:
        data = json.loads(f.read())

        for result in data['results']:
            for relation in result['properties']['Асортимент (в наявності)']['relation']:
                key = relation['id']
                amount = result['properties']['Кількість']['number']
                status = result['properties']['Статус']['select']

                if amount is not None and status != None and status['name'] == 'На складі':
                    if key in addition:
                        addition[key] += amount
                    else:
                        addition[key] = amount

        f.close()
        os.remove(f.name)

    for key in addition:
        if key not in subtraction:
            subtraction[key] = 0

    for key in subtraction:
        if key not in addition:
            addition[key] = 0

    for key in addition.keys():
        sum[key] = addition[key] - subtraction[key]

        update_data = {
            "properties": {
                "Запас": {
                    "number": sum[key],
                }        
            }
        }

        update_page(key.replace('-', ''), update_data)
