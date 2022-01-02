# depyro :money_with_wings:
A wrapper for De Giro API, specifically for portfolio analysis. If you have ETFs in your portfolio, use in conjunction with `pyholdings` to discover ETF compositions.

### Get started
1. Set `username` and `password` as environment variables or in an `.env` file in the root of your project.
2. Instantiate the client and fetch portfolio information.

```
from depyro.core import Depyro
client = Depyro(auth_type="2fa")
>>> Enter authenticator token...
client.get_portfolio_info()
>>>
[
  {
    id: int,
    positionType: str,
    size: int,
    price: float,
    value: float,
    plBase: float,
    breakEvenPrice: float,
    name: str,
    isin: str,
    symbol: str,
    productType: str
  },
]
```
