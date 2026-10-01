import os

import MetaTrader5 as mt5
from dotenv import load_dotenv


class MT5Connector:
    def __init__(self):
        load_dotenv()

        self.symbol = os.getenv("MT5_SYMBOL", "XAUUSD")
        self.mt5_path = os.getenv(
            "MT5_PATH",
            r"C:\Program Files\MetaTrader 5\terminal64.exe"
        )

    def connect(self):
        if not mt5.initialize(
            path=self.mt5_path,
            timeout=60000
        ):
            error = mt5.last_error()
            raise ConnectionError(
                f"Connessione MT5 fallita: {error}"
            )

        account = mt5.account_info()

        if account is None:
            error = mt5.last_error()
            mt5.shutdown()
            raise ConnectionError(
                f"Account non disponibile: {error}"
            )

        return account

    def get_tick(self):
        if not mt5.symbol_select(self.symbol, True):
            error = mt5.last_error()
            raise RuntimeError(
                f"Impossibile selezionare {self.symbol}: {error}"
            )

        tick = mt5.symbol_info_tick(self.symbol)

        if tick is None:
            error = mt5.last_error()
            raise RuntimeError(
                f"Prezzo {self.symbol} non disponibile: {error}"
            )

        return tick

    def disconnect(self):
        mt5.shutdown()
