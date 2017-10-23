import sys
import time; time.time()
import json

import requests

TOO_MANY_REQUESTS = 6
USER_IS_BANNED = 18

try:
    with open('config.json', encoding='utf-8-sig') as f:
        config = json.load(f)
except FileNotFoundError:
    print('Файл не найден')
    sys.exit(1)


def call_api(requests_api_vk, params):
    try:
        while True:
            r = requests.get(requests_api_vk, params)
            res = r.json()
            if 'error' in res:
                if res['error']['error_code'] == USER_IS_BANNED:
                    print("Страница пользователя была удалена или заблокирована")
                    return None
                elif res['error']['error_code'] == TOO_MANY_REQUESTS:
                    time.sleep(1)
            else:
                return r
    except ValueError:
        print('Получено некоректное значение')
        sys.exit(1)
    except TypeError:
        print('Операция применена к объекту несоответствующего типа')
        sys.exit(1)


def get_friends_list():
    params = {
        'access_token': config['TOKEN'],
        'user_id': config['USER_ID'],
        'v': config['VERSION'],
    }
    r = call_api('https://api.vk.com/method/friends.get', params)
    users_list = list(r.json()['response']['items'])
    return users_list


def create_json(data_res):
    with open('groups.json', 'w', encoding='utf8') as file:
        json.dump(data_res, file, indent=2, ensure_ascii=False)


def get_groups():

    offset = 0
    user_groups = []

    params = {
        'access_token': config['TOKEN'],
        'user_id': config['USER_ID'],
        'offset': offset,
        'count': 1000,
        'v': config['VERSION'],
    }

    # - получение списка групп пользователя
    r = call_api('https://api.vk.com/method/groups.get', params)
    groups = r.json()['response']['items']
    user_groups.extend(groups)
    return user_groups


def check_for_presence():
    offset = 0
    user_groups = get_groups()
    friends_list = get_friends_list()

    for i, friend in enumerate(friends_list, 1):
        params = {
            'access_token': config['TOKEN'],
            'user_id': friend,
            'offset': offset,
            'count': 1000,
            'v': config['VERSION'],
        }
        r = call_api('https://api.vk.com/method/groups.get', params)

        if not r:
            continue
        else:
            groups = r.json()['response']['items']
            user_groups = list(set(user_groups) - set(groups))
            print("Обработано значений {} из {}".format(i, len(friends_list)))
    return user_groups


def get_info_groups(group_info):
    name = group_info[0]['name']
    gid = group_info[0]['gid']
    members_count = group_info[0]['members_count']
    return {'name': name, 'gid': gid, 'members_count': members_count}  #groups_info


def get_groups_info():
    groups = check_for_presence()
    len_groups = len(groups)
    list_json = []
    for i, group in enumerate(groups, 1):
        params = {
            'access_token': config['TOKEN'],
            'group_id': group,
            'fields': 'members_count'
        }
        r = call_api('https://api.vk.com/method/groups.getById', params)
        group_info = r.json()
        new_group_info = get_info_groups(group_info['response'])
        list_json.append(new_group_info)
        print("Записано в файл: {} из {}".format(i, len_groups))
    create_json(list_json)


def main():
    get_groups_info()

if __name__ == '__main__':
    main()
