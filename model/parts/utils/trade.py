"""
Trade class implementing trading logic with buy and sell feature
"""
from model.types import TokenBalance

class Trade:
    """
    Class for trades happening in the buy and sell feature.
    Trades are always given from the perspective of the trader, i.e. if sell_gold=True then the
    trader sells CELO to the reserve. Amounts are always positive, deltas
    can be negative or positive
    """

    def __init__(self, sell_gold, sell_amount, buy_amount):
        # TODO: Add trader account id and checks against the respective balances
        self.sell_gold: bool = sell_gold
        self.sell_amount: TokenBalance = sell_amount
        self.buy_amount: TokenBalance = buy_amount

    @property
    def delta_trader_celo(self):
        """
        Celo delta from the perspective of the trader,
        i.e. if trader_delta_celo is negative, then the trader is
        selling CELO to the reserve for stables
        """
        if self.sell_gold:
            return -self.sell_amount
        return self.buy_amount

    @property
    def delta_trader_cusd(self):
        """
        cUSD delta from the perspective of the trader,
        i.e. if trader_delta_cusd is negative, then the trader is
        selling cUSD to the reserve for stables
        """
        if self.sell_gold:
            return self.buy_amount
        return -self.sell_amount

    @property
    def delta_reserve_celo(self):
        """
        Celo delta from the perspective of the reserve
        """
        return -self.delta_trader_celo

    @property
    def delta_reserve_cusd(self):
        """
        cUSD delta from the perspective of the reserve
        """
        return -self.delta_trader_celo

    @property
    def delta_float_celo(self):
        """
        Changes in float CELO
        """
        return self.delta_trader_celo

    @property
    def delta_float_cusd(self):
        """
        Changes in float cUSD
        """
        return self.delta_trader_cusd

    @property
    def delta_mento_bucket_celo(self):
        """
        Changes in float CELO
        """
        return -self.delta_trader_celo

    @property
    def delta_mento_bucket_cusd(self):
        """
        Changes in float cUSD
        """
        return -self.delta_trader_cusd
