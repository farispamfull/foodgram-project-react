import json

pre_result = []
with open("ingredients.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)
    i = 1
    for item in data:
        pre_item = dict()
        pre_item['model'] = 'api.ingredient'
        pre_item['pk'] = i
        pre_item['field'] = {
            'name': item['name'],
            'measurement_unit': item['measurement_unit']
        }
        pre_result.append(pre_item)
        i += 1

with open("ingredients_data.json", "w", encoding='utf-8') as write_file:
    json.dump(pre_result, write_file, indent=4, ensure_ascii=False)
