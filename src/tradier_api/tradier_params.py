from typing import Optional

class BaseParams:
    def to_query_params(self) -> dict:
        """
        Converts the parameters to a dictionary, filtering out any None values.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}

class AccountParams(BaseParams):
    def __init__(self, account_id: str):
        self.account_id = account_id

class OrderParams(BaseParams):
    def __init__(self, account_id: str, order_id: str):
        self.account_id = account_id
        self.order_id = order_id

class WatchlistParams(BaseParams):
    def __init__(self, watchlist_id: str, symbol: Optional[str] = None):
        self.watchlist_id = watchlist_id
        self.symbol = symbol
