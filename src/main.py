import requests
import json
import os
from getpass import getpass
from dotenv import load_dotenv
import constant
import logging

logging.basicConfig(level=logging.WARN)
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

    def login(self, auth_type='basic'):
        url = f'{constant.BASE}/{constant.LOGIN}/{constant.MFA}'
        payload = {
            'username': os.environ['username'], 
            'password': os.environ['password'],
            'isPassCodeReset': False,
            'isRedirectToMobile': False,
        }
        if auth_type == "2fa":
            payload['oneTimePassword'] = getpass('Enter authenticator token... ')
        
        response = self.client.post(url, data=json.dumps(payload))

        logger.debug(f'Login response: {response}')

        if response.status_code == 200:
            r = response.json()
            self.session_id = r['sessionId']

            logger.debug('Login succeeded')

        return response

    def get_account_data(self):
        url = f'{constant.BASE}/{constant.ACCOUNT}'
        params = {
            'sessionId': self.session_id,
        }
        r = self.client.get(url, params=params)
        response = r.json()
        data = response['data']

        logger.debug(f'Data: {data}')

        self.user['account_ref'] = data['intAccount']
        self.user['name'] = data['displayName']

        return data

    def get_portfolio(self):
        url = f'{constant.BASE}/{constant.PF_DATA}/{self.user["account_ref"]};jsessionid={self.session_id}?portfolio=0'
        response = self.client.get(url)
        r = response.json()

        keys = [
            'positionType',
            'size',
            'price',
            'value',
            'plBase',
            'breakEvenPrice',
        ]

        products = []
        for product in r['portfolio']['value']:
            product_dict = {product['id']: {}}
            for metric in product['value']:
                if metric['name'] in keys:
                    product_dict[product['id']][metric['name']] = metric['value']
            products.append(product_dict)
        return products

    def get_product_info(self, product_id):
        url = f'{constant.BASE}/{constant.PRODUCT_INFO}'
        params = {
            'intAccount': self.user['account_ref'],
            'sessionId': self.session_id
        }
        response = self.client.post(
            url, 
            params=params, 
            data=json.dumps([str(product_id)])
        )
        r = response.json()
        data = r['data'][next(iter(r['data']))]  # skip a level in the dict
        
        keys = [
            'id',
            'name',
            'isin',
            'symbol',
            'productType',
            'currency',
            'closePrice',
        ]

        product = {k: v for k, v in data.items() if k in keys}
        return product

x = Depyro()
x.login(auth_type='2fa')
data = x.get_account_data()
portfolio = x.get_portfolio()
product = x.get_product_info(10280893)
print(product)