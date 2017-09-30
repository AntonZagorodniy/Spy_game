import time; time.time()
import json
from time import sleep

import requests


try:
    with open('config.json', encoding='utf-8-sig') as f:
        data = json.load(f)
except FileNotFoundError:
    print('Файл не найден')


def get_data():
    app_id = data[1]['APP_ID']
    version_res = data[2]['VERSION']
    user_id = data[3]['USER_ID']
    token_res = data[4]['TOKEN']

    # Словарь с ключами
    auth_data = {
        'client_id': app_id,
        'redirect_uri': 'https://oauth.vk.com/blank.html',
        'access_token': 'status',
        'response_type': token_res,
        'v': version_res,
        'user_id': user_id
    }

    # print('?'.join((AUTHORIZE_URL, urlencode(auth_data))))
    return auth_data


def get_friends_list():
    information = get_data()
    token_res = information['response_type']
    version_res = information['v']

    params = {
        'access_token': token_res,
        'v': version_res
    }
    response = requests.get('https://api.vk.com/method/friends.get', params)
    users_list = list(response.json()['response']['items'])
    return users_list


def create_json():
    with open('response.json', 'w', encoding='utf8') as file:
        file.write('[\n')


def write_json(data_res):
    with open('response.json', 'a', encoding='utf8') as file:
        json.dump(data_res, file, indent=2, ensure_ascii=False)


def append_json(text):
    with open('response.json', 'a', encoding='utf8') as file:
        file.write(text)


def get_groups():
    information = get_data()
    user_id = information['user_id']
    offset = 0
    token_res = information['response_type']

    user_groups = []

    params = {
        'access_token': token_res,
        'user_id': user_id,
        'offset': offset,
        'count': 1000,
    }

    # - получение списка групп пользователя
    r = requests.get('https://api.vk.com/method/groups.get', params)
    groups = r.json()['response']
    user_groups.extend(groups)
    del user_groups[0]
    return user_groups


def check_for_presence():
    information = get_data()
    offset = 0
    token_res = information['response_type']
    user_groups = get_groups()
    len_groups = (len(user_groups))
    friends_list = get_friends_list()
    ind = 0
    for friend in friends_list:
        sleep(0.4)  # VK ставит ограничение на кол-во запросов в секунду
        params = {
            'access_token': token_res,
            'user_id': friend,
            'offset': offset,
            'count': 1000,
        }
        try:
            r = requests.get('https://api.vk.com/method/groups.get', params)
            groups = r.json()['response']
            user_groups = list(set(user_groups) - set(groups))
            ind += 1
            print("Обработано значений {} из {}".format(ind, len_groups))
        except:
            continue
    return user_groups


def get_groups_info():
    information = get_data()
    token_res = information['response_type']
    groups = check_for_presence()
    len_groups = (len(groups))
    ind = 0
    for group in groups:
        sleep(0.4)
        params = {
            'access_token': token_res,
            'group_id': group
        }
        try:
            r = requests.get('https://api.vk.com/method/groups.getById', params)
            group_info = r.json()
            write_json(group_info['response'])
            ind += 1
            if ind != len_groups:
                append_json(",\n")
            else:
                append_json("\n")
            print("Записано в файл: {} из {}".format(ind, len_groups))
        except:
            continue


def main():
    create_json()
    get_groups_info()
    append_json("]")

if __name__ == '__main__':
    main()
