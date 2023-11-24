import requests
from constant import CVAT_PROTO, CVAT_DOMAIN, CVAT_MAIL, CVAT_PASS, CVAT_USER

# all tasks between the ID s will be deleted
START_ID = 2772
END_ID = 2777


def login():
    try:
        url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/auth/login'
        payload = {'username': CVAT_USER, 'email': CVAT_MAIL, 'password': CVAT_PASS}
        response = requests.post(url, json=payload)
        result = response.json()
        return result['key']
    except KeyError as e:
        print('Unable to login into CVAT',e)
        return None


token = login()

for i in range(START_ID, END_ID):
    url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks/{i}'
    response = requests.delete(url, headers={'Authorization': f'Token {token}'})
