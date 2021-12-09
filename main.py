import requests
import json
import os
from getpass import getpass
from dotenv import load_dotenv
import constant
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Depyro:
    def __init__(self):
        load_dotenv()
        self.client = Depyro.init_client()
        self.session_id = ''
        self.user = dict()

    def __repr__(self):
        return 'Depyro()'

    def init_client():
        client = requests.Session()
        client.headers.update({"Content-Type": "application/json"})
        return client

    def login(self):
        url = f'{constant.BASE}/{constant.LOGIN}/{constant.MFA}'
        payload = {
            'username': os.environ['username'], 
            'password': os.environ['password'],
            'isPassCodeReset': False,
            'isRedirectToMobile': False,
            'oneTimePassword': getpass('Enter authenticator token... '),
        }
        response = self.client.post(url, data=json.dumps(payload))

        logger.debug(f'Login response: {json.dumps(response)}')

        if response.get('status_code') == 200:
            self.session_id = response['sessionId']

            logger.debug('Login succeeded')

        return response

    def get_account_data(self):
        url = f'{constant.BASE}/{constant.ACCOUNT}'
        params = {
            'sessionId': self.session_id,
        }
        r = self.client.get(url, params=params)
        response = r.json()
        print(response)
        # data = response['data']
        # self.user['account_ref'] = data['intAccount']
        # self.user['name'] = data['displayName']
        # self.user['country'] = data['nationality']
        # return data

    def get_portfolio(self):
        url = f'{constant.BASE}/{constant.DATA}/{self.user["account_ref"]};jsessionid={self.session_id}'
        response = self.request(url)
        return response

client = Depyro()
client.login()
client.get_account_data()