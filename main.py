import json
from notion_requests import read_database, update_page

database_id_1 = 'd866a45662f240bdbdcb2668e29a0d4f' #Потреби
database_id_2 = '748a8405acb34452b65ec4128c8a7ce6' #Товари
database_id_3 = '346bb62ba6584dc9ac704c02aa966344' #Асортимент

def main():
    # transition = {}
    addition = {}
    subtraction = {}
    sum = {}

    with open(read_database(database_id_1), 'r') as f:
        data = json.loads(f.read())

        for result in data['results']:
            for relation in result['properties']['Назва в асортименті']['relation']:
                key = relation['id']
                # transition[result['id']] = key
                value = result['properties']['Видано']['number']

                if value is not None:
                    subtraction[key] = value


    with open(read_database(database_id_2), 'r') as f:
        data = json.loads(f.read())

        for result in data['results']:
            for relation in result['properties']['Асортимент (в наявності)']['relation']:
                key = relation['id']
                value = result['properties']['Кількість']['number']

                if value is not None:
                    addition[key] = value

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

        print(update_page(key.replace('-', ''), update_data))
    

if __name__ == "__main__":
    main()
