import json

import requests


def post_json(url, json_data):
    return requests.post(url, data=json.dumps(json_data), headers={'Content-Type': 'application/json'})


def put_binary(url, header, file_path):
    with open(file_path, 'rb') as file_obj:
        resp = requests.put(url, headers=header, data=file_obj)
        return resp










