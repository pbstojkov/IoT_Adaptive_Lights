# import urllib.request
from urllib2 import urlopen
import json

class Persons:
    def __init__(self):
        self.dict_json = None
        self.person_list = []

    def load_json(self, url):
        # url1 = 'https://iot-test.000webhostapp.com/OwnershipPriority.json'
        response = urlopen(url)
        data = response.read()
        text = data.decode('utf-8')
        for p in json.loads(text):
            self.person_list.append(Person(p['user_type'], p['user_id'], p['sensor_id'], p['light_color'], p['low_light'],
                                           p['user_location_x'], p['user_location_y']))

    def get_owners(self):
        return self.person_list

    def find_user_id_change_values(self, user_id, **kwargs):
        person_searched = None
        for p in self.person_list:
            if p.user_id == user_id:
                person_searched = p
                break
        for i, j in kwargs.items():
            if i == 'user_type':
                person_searched.user_type = j
            elif i == 'user_id':
                person_searched.user_id = j
            elif i == 'sensor_id':
                person_searched.sensor_id = j
            elif i == 'light_color':
                person_searched.light_color = j
            elif i == 'low_light':
                person_searched.low_light = j
            elif i == 'user_location_x':
                person_searched.user_location_x = j
            elif i == 'user_location_y':
                person_searched.user_location_y = j
        return person_searched.user_type


class Person:
    def __init__(self, user_type, user_id, sensor_id, light_color, low_light, user_location_x, user_location_y):
        self.user_type = user_type
        self.user_id = user_id
        self.sensor_id = sensor_id
        self.light_color = light_color
        self.low_light = low_light
        self.user_location_x = user_location_x
        self.user_location_y = user_location_y


#Example

# owner = Persons()
# owner.load_json('https://iot-test.000webhostapp.com/OwnershipPriority.json')
# for p in owner.get_owners():
#     print(p.user_location_x)
#
# print('-------------')
#
# owner.find_user_id_change_values('Office-Worker-1', user_type='RODRO', user_location_x = True)
#
# for p in owner.get_owners():
#     print(p.user_location_x)



