from src.mt5_connector import MT5Connector


def main():
    connector = MT5Connector()

    try:
        account = connector.connect()

        print("================================")
        print("       MT5 CONNECTION")
        print("================================")
        print(f"Login:   {account.login}")
        print(f"Server:  {account.server}")
        print(f"Name:    {account.name}")
        print(f"Balance: {account.balance:.2f} {account.currency}")
        print(f"Equity:  {account.equity:.2f} {account.currency}")
        print()

        tick = connector.get_tick()

        print("================================")
        print("        MARKET DATA")
        print("================================")
        print(f"Symbol: {connector.symbol}")
        print(f"Bid:    {tick.bid}")
        print(f"Ask:    {tick.ask}")
        print()

        print("Connection successful.")

    except Exception as e:
        print(f"ERRORE: {e}")

    finally:
        connector.disconnect()
        print("MT5 disconnesso.")


if __name__ == "__main__":
    main()
