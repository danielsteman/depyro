# base
BASE = "https://trader.degiro.nl"

# login
LOGIN = "login/secure/login"
MFA = "totp"

#account
TRADER = "trader/secure/profile"
ACCOUNT = "pa/secure/client"
PF_DATA = "trading/secure/v5/update/"

# product
PRODUCT_INFO = "https://trader.degiro.nl/product_search/secure/v5/products/info"

HEADERS = {
    "access-control-allow-credentials": "true",
    "cache-control": "no-cache, no-store, must-revalidate",
    "content-encoding": "br",
    "content-security-policy": "block-all-mixed-content;",
    "content-type": "application/json",
    "date": "Thu, 09 Dec 2021 16:58:07 GMT",
    "expires": "0",
    "pragma": "no-cache",
    "server": "openresty",
    "strict-transport-security": "max-age=31536000; includeSubDomains",
    "vary": "Accept-Encoding",
}