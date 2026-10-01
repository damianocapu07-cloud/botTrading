import os

import MetaTrader5 as mt5
from dotenv import load_dotenv


class TradeExecutor:
    def __init__(self, connector):
        load_dotenv()

        self.connector = connector
        self.trading_enabled = (
            os.getenv("TRADING_ENABLED", "false").lower() == "true"
        )

        self.magic = 100001

    def get_positions(self, symbol=None):
        positions = (
            mt5.positions_get(symbol=symbol)
            if symbol
            else mt5.positions_get()
        )

        if positions is None:
            raise RuntimeError(
                f"Errore lettura posizioni: {mt5.last_error()}"
            )

        return list(positions)

    def buy(
        self,
        volume,
        symbol=None,
        stop_loss=None,
        take_profit=None,
        deviation=20,
    ):
        return self._open_position(
            mt5.ORDER_TYPE_BUY,
            volume,
            symbol,
            stop_loss,
            take_profit,
            deviation,
        )

    def sell(
        self,
        volume,
        symbol=None,
        stop_loss=None,
        take_profit=None,
        deviation=20,
    ):
        return self._open_position(
            mt5.ORDER_TYPE_SELL,
            volume,
            symbol,
            stop_loss,
            take_profit,
            deviation,
        )

    def _get_filling_mode(self, symbol_info):
        mode = symbol_info.filling_mode

        if mode & mt5.ORDER_FILLING_FOK:
            return mt5.ORDER_FILLING_FOK

        if mode & mt5.ORDER_FILLING_IOC:
            return mt5.ORDER_FILLING_IOC

        return mt5.ORDER_FILLING_RETURN

    def _open_position(
        self,
        order_type,
        volume,
        symbol,
        stop_loss,
        take_profit,
        deviation,
    ):
        if symbol is None:
            symbol = self.connector.symbol

        symbol_info = mt5.symbol_info(symbol)

        if symbol_info is None:
            raise RuntimeError(
                f"Simbolo non trovato: {symbol}"
            )

        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                raise RuntimeError(
                    f"Impossibile selezionare {symbol}"
                )

        if volume < symbol_info.volume_min:
            raise ValueError(
                f"Volume troppo basso. Minimo: "
                f"{symbol_info.volume_min}"
            )

        if volume > symbol_info.volume_max:
            raise ValueError(
                f"Volume troppo alto. Massimo: "
                f"{symbol_info.volume_max}"
            )

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            raise RuntimeError(
                f"Prezzo non disponibile per {symbol}"
            )

        if order_type == mt5.ORDER_TYPE_BUY:
            price = tick.ask
            side = "BUY"
        else:
            price = tick.bid
            side = "SELL"

        filling_mode = self._get_filling_mode(symbol_info)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": stop_loss or 0.0,
            "tp": take_profit or 0.0,
            "deviation": deviation,
            "magic": self.magic,
            "comment": "botTrading",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }

        print("=== ORDER REQUEST ===")
        print(f"Side:    {side}")
        print(f"Symbol:  {symbol}")
        print(f"Volume:  {volume}")
        print(f"Price:   {price}")
        print(f"SL:      {stop_loss}")
        print(f"TP:      {take_profit}")
        print(f"Filling: {filling_mode}")

        check = mt5.order_check(request)

        if check is None:
            raise RuntimeError(
                f"order_check fallito: {mt5.last_error()}"
            )

        print()
        print("=== ORDER CHECK ===")
        print(f"Retcode: {check.retcode}")
        print(f"Comment: {check.comment}")

        if check.retcode != 0:
            raise RuntimeError(
                f"Ordine non approvato da order_check: "
                f"{check.retcode} - {check.comment}"
            )

        if not self.trading_enabled:
            print()
            print(
                "TRADING_ENABLED=false: "
                "ordine NON inviato."
            )
            return check

        print()
        print("=== INVIO ORDINE ===")

        result = mt5.order_send(request)

        if result is None:
            raise RuntimeError(
                f"order_send fallito: {mt5.last_error()}"
            )

        print(f"Retcode: {result.retcode}")
        print(f"Comment: {result.comment}")

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(
                f"Ordine rifiutato: "
                f"{result.retcode} - {result.comment}"
            )

        print(f"Order ticket: {result.order}")
        print(f"Deal ticket:  {result.deal}")

        return result

    def close_position(self, ticket):
        positions = mt5.positions_get(ticket=ticket)

        if positions is None or len(positions) == 0:
            raise RuntimeError(
                f"Posizione non trovata: {ticket}"
            )

        position = positions[0]

        symbol = position.symbol
        volume = position.volume

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            raise RuntimeError(
                f"Prezzo non disponibile per {symbol}"
            )

        symbol_info = mt5.symbol_info(symbol)

        if symbol_info is None:
            raise RuntimeError(
                f"Simbolo non trovato: {symbol}"
            )

        filling_mode = self._get_filling_mode(symbol_info)

        if position.type == mt5.POSITION_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
            side = "SELL / CLOSE BUY"
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
            side = "BUY / CLOSE SELL"

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "position": position.ticket,
            "price": price,
            "deviation": 20,
            "magic": self.magic,
            "comment": "botTrading close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }

        print("=== CLOSE REQUEST ===")
        print(f"Side:     {side}")
        print(f"Position: {position.ticket}")
        print(f"Symbol:   {symbol}")
        print(f"Volume:   {volume}")
        print(f"Price:    {price}")
        print(f"Filling:  {filling_mode}")

        check = mt5.order_check(request)

        if check is None:
            raise RuntimeError(
                f"order_check fallito: {mt5.last_error()}"
            )

        print()
        print("=== CLOSE CHECK ===")
        print(f"Retcode: {check.retcode}")
        print(f"Comment: {check.comment}")

        if check.retcode != 0:
            raise RuntimeError(
                f"Chiusura non approvata: "
                f"{check.retcode} - {check.comment}"
            )

        if not self.trading_enabled:
            print()
            print(
                "TRADING_ENABLED=false: "
                "chiusura NON inviata."
            )
            return check

        print()
        print("=== CHIUSURA POSIZIONE ===")

        result = mt5.order_send(request)

        if result is None:
            raise RuntimeError(
                f"order_send fallito: {mt5.last_error()}"
            )

        print(f"Retcode: {result.retcode}")
        print(f"Comment: {result.comment}")

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(
                f"Chiusura rifiutata: "
                f"{result.retcode} - {result.comment}"
            )

        print(f"Deal ticket: {result.deal}")

        return result
