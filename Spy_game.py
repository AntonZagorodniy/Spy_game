import sys
import time; time.time()
import json
from time import sleep

import requests

try:
    with open('config.json', encoding='utf-8-sig') as f:
        config = json.load(f)
except FileNotFoundError:
    print('Файл не найден')
    sys.exit(1)


def call_api(requests_api_vk, params):
    a = 0
    err = False
    try:
        while(True) and not err:
            r = requests.get(requests_api_vk, params)
            if int(r.json()['error']['error_code']) != 18:
                if int(r.json()['error']['error_code']) == 6:
                    time.sleep(6)
                else:
                    a += 1
                    print(a)
                    # print("+")
                    break
            else:
                print("Страница пользователя была удалена или заблокирована")
                err = True

    finally:
        print(r.json())
        if not err:
            print("OK")
            return r
        # else:
        #     print("NO")


def get_friends_list():

    params = {
        'access_token': config['TOKEN'],
        'v': config['VERSION']
    }
    r = call_api('https://api.vk.com/method/friends.get', params)
    users_list = list(r.json()['response']['items'])
    return users_list


def create_json(data_res):
    with open('response.json', 'w', encoding='utf8') as file:
        json.dump(data_res, file, indent=2, ensure_ascii=False)


def get_groups():

    offset = 0
    user_groups = []

    params = {
        'access_token': config['TOKEN'],
        'user_id': config['USER_ID'],
        'offset': offset,
        'count': 1000,
    }

    # - получение списка групп пользователя
    r = call_api('https://api.vk.com/method/groups.get', params)
    groups = r.json()['response']
    user_groups.extend(groups)
    del user_groups[0]
    return user_groups


def check_for_presence():
    offset = 0
    user_groups = get_groups()
    friends_list = get_friends_list()
    ind = 0
    all_groups = []
    for friend in friends_list:

        params = {
            'access_token': config['TOKEN'],
            'user_id': friend,
            'offset': offset,
            'count': 1000,
        }
        r = call_api('https://api.vk.com/method/groups.get', params)
        if not r:
            continue
        else:
            groups = r.json()['response']
            user_groups = list(set(user_groups) - set(groups))
            # params = {
            #     'access_token': config['TOKEN'],
            #     'user_id': friend,
            #     'offset': offset,
            #     'count': 1000,
            # }
            # r = call_api('https://api.vk.com/method/groups.get', params)
            # if not r:
            #     continue
            # else:
            #     print("euu")
            #     groups = r.json()['response']
            #     all_groups.extend(groups)
            #     if int(offset) < (r.json()['response'][0]):
            #         print("да")
            #         break
            #     else:
            #         offset += 1000
            # user_groups = list(set(user_groups) - set(all_groups))
            ind += 1
            print("Обработано значений {} из {}".format(ind, len(friends_list)))
    return user_groups


def get_groups_info():
    groups = check_for_presence()
    len_groups = (len(groups))
    ind = 0
    list_json = []
    for group in groups:
        params = {
            'access_token': config['TOKEN'],
            'group_id': group
        }
        r = call_api('https://api.vk.com/method/groups.getById', params)
        group_info = r.json()
        ind += 1
        list_json.extend(group_info['response'])
        create_json(list_json)
        print("Записано в файл: {} из {}".format(ind, len_groups))


def main():
    get_groups_info()

if __name__ == '__main__':
    main()
