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
        self.session_id = ""
        self.user = dict()

    def __repr__(self):
        return "Depyro()"

    def init_client():
        client = requests.Session()
        client.headers.update({"Content-Type": "application/json"})
        return client

    def login(self, auth_type="basic"):
        payload = {
            "username": os.environ["username"],
            "password": os.environ["password"],
            "isPassCodeReset": False,
            "isRedirectToMobile": False,
        }
        if auth_type == "2fa":
            url = f"{constant.BASE}/{constant.LOGIN}/{constant.MFA}"
            payload["oneTimePassword"] = getpass("Enter authenticator token... ")
        else:
            url = f"{constant.BASE}/{constant.LOGIN}"

        response = self.client.post(url, data=json.dumps(payload))

        logger.debug(f"Login response: {response}")

        if response.status_code == 200:
            r = response.json()
            self.session_id = r["sessionId"]

            logger.debug("Login succeeded")

        return response

    def get_account_info(self):
        url = f"{constant.BASE}/{constant.ACCOUNT}"
        params = {"sessionId": self.session_id}
        r = self.client.get(url, params=params)
        response = r.json()
        data = response["data"]

        logger.debug(f"Data: {data}")

        self.user["account_ref"] = data["intAccount"]
        self.user["name"] = data["displayName"]

        return data

    def get_portfolio_info(self):
        url = f'{constant.BASE}/{constant.PF_DATA}/{self.user["account_ref"]}\
            ;jsessionid={self.session_id}?portfolio=0'
        response = self.client.get(url)
        r = response.json()

        keys = ["positionType", "size", "price", "value", "plBase", "breakEvenPrice"]

        products = []
        for product in r["portfolio"]["value"]:
            product_dict = {"id": product["id"]}
            for metric in product["value"]:
                if metric["name"] in keys:
                    if isinstance(metric["value"], dict):
                        product_dict[metric["name"]] = next(
                            iter(metric["value"].values())
                        )
                    else:
                        product_dict[metric["name"]] = metric["value"]
            product_name = self.get_product_info(product["id"])
            products.append({**product_dict, **product_name})
        return products

    def get_product_info(self, product_id):
        url = f"{constant.BASE}/{constant.PRODUCT_INFO}"
        params = {"intAccount": self.user["account_ref"], "sessionId": self.session_id}
        response = self.client.post(
            url, params=params, data=json.dumps([str(product_id)])
        )
        r = response.json()
        data = r["data"][next(iter(r["data"]))]  # skip a level in the dict

        keys = ["name", "isin", "symbol", "productType"]

        product = {k: v for k, v in data.items() if k in keys}
        return product


x = Depyro()
x.login()
# data = x.get_account_info()
# portfolio = x.get_portfolio_info()
# product = x.get_product_info(10280893)
# print(portfolio)
