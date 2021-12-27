from typing import Type
import requests
import json
import os
from getpass import getpass
from dotenv import load_dotenv
from constant import *
import logging

logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)


class Depyro:
    def __init__(self):
        load_dotenv()
        self.client = Depyro.init_client()
        self.session_id = ""
        self.user = dict()

    def __repr__(self):
        return __class__.__name__

    def init_client():
        client = requests.Session()
        client.headers.update({"Content-Type": "application/json"})
        return client

    def request(self, url, method, *, data={}, params={}):
        if method == "get":
            r = self.client.get(url, data=json.dumps(data), params=params)
        elif method == "post":
            r = self.client.post(url, data=json.dumps(data), params=params)

        if r.status_code == 200:
            try:
                return r.json()
            except AttributeError:
                return "No data"
        elif r.status_code == 401:
            logger.warning("Request not authorized, refreshing session token.")
            self.login()  # to remedy expired session
            return self.request(url, method, data=data, params=params)  # recurse
        else:
            logger.error("Could not process request")
            return "Could not process request"

    def login(self, auth_type="basic"):
        payload = {
            "username": os.environ["username"],
            "password": os.environ["password"],
            "isPassCodeReset": False,
            "isRedirectToMobile": False,
        }
        if auth_type == "2fa":
            url = f"{BASE}/{LOGIN}/{MFA}"
            payload["oneTimePassword"] = getpass("Enter authenticator token... ")
        else:
            url = f"{BASE}/{LOGIN}"

        response = self.request(url, "post", data=payload)

        try:
            self.session_id = response["sessionId"]
            logger.info("Login succeeded")
        except:
            logger.error("Login failed")

        return response

    def get_account_info(self):
        url = f"{BASE}/{ACCOUNT}"
        params = {"sessionId": self.session_id}
        response = self.request(url, "get", params=params)

        try:
            data = response["data"]
            self.user["account_ref"] = data["intAccount"]
            self.user["name"] = data["displayName"]
        except TypeError:
            logger.error("Could not fetch account data")

    def get_portfolio_info(self):
        url = f'{BASE}/{PF_DATA}/{self.user["account_ref"]};jsessionid={self.session_id}?portfolio=0'
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
        url = f"{BASE}/{PRODUCT_INFO}"
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
data = x.get_account_info()
portfolio = x.get_portfolio_info()
product = x.get_product_info(10280893)
print(portfolio)
