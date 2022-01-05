import requests
import json
import os
import logging
from getpass import getpass
from dotenv import load_dotenv
from src.depyro.constants import Constants as c

logging.basicConfig(format=c.LOGGING_FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)


class Depyro:
    def __init__(self):
        load_dotenv()
        self.client = Depyro.init_client()
        self.session_id = ""
        self.user = dict()
        self.auth_type = "basic"

    def __repr__(self):
        return __class__.__name__

    def init_client():
        client = requests.Session()
        client.headers.update({"Content-Type": "application/json"})
        return client

    def request(self, url, method, *, data={}, params={}, recurse=True):
        if method == "get":
            r = self.client.get(url, data=json.dumps(data), params=params)
        elif method == "post":
            r = self.client.post(url, data=json.dumps(data), params=params)

        if r.status_code == 200:
            try:
                return r.json()
            except AttributeError:
                return "No data"
        elif r.status_code in [400, 401]:
            logger.warning("Request not authorized, refreshing session token.")
            if recurse:
                self.login()  # refresh session token
                return self.request(
                    url, method, data=data, params=params, recurse=False
                )  # recurse once
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
        if auth_type == "2fa" or self.auth_type == "2fa":
            url = f"{c.BASE}/{c.LOGIN}/{c.MFA}"
            payload["oneTimePassword"] = getpass("Enter authenticator token... ")
        else:
            url = f"{c.BASE}/{c.LOGIN}"

        response = self.request(url, "post", data=payload)

        try:
            self.session_id = response["sessionId"]
            logger.info("Login succeeded")
        except TypeError:
            logger.error("Login failed")

        return response

    def get_account_info(self):
        url = f"{c.BASE}/{c.ACCOUNT}"
        params = {"sessionId": self.session_id}
        response = self.request(url, "get", params=params)
        try:
            data = response["data"]
            self.user["account_ref"] = data["intAccount"]
            self.user["name"] = data["displayName"]
            logger.info("Fetched account info")
        except TypeError:
            logger.error("Could not fetch account data")

    def get_portfolio_info(self):
        if not self.session_id:  # if not logged in: login
            self.login()
        if not self.user:  # if not account info: get account info
            self.get_account_info()

        url = f'{c.BASE}/{c.PF_DATA}/{self.user["account_ref"]}\
            ;jsessionid={self.session_id}?portfolio=0'
        response = self.request(url, "get")

        keys = ["positionType", "size", "price", "value", "plBase", "breakEvenPrice"]

        products = []
        for product in response["portfolio"]["value"]:
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
        if not self.session_id:
            self.login()
        if not self.user:
            self.get_account_info()

        url = f"{c.BASE}/{c.PRODUCT_INFO}"
        params = {"intAccount": self.user["account_ref"], "sessionId": self.session_id}
        response = self.request(url, "post", params=params, data=[str(product_id)])
        data = response["data"][
            next(iter(response["data"]))
        ]  # skip a level in the dict
        keys = ["name", "isin", "symbol", "productType"]  # keys to extract
        product = {k: v for k, v in data.items() if k in keys}

        return product
