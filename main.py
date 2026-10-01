from src.mt5_connector import MT5Connector
from src.trade_executor import TradeExecutor


def print_positions(executor, symbol):
    positions = executor.get_positions(symbol)

    print()
    print("================================")
    print("          POSITIONS")
    print("================================")

    if not positions:
        print("Nessuna posizione aperta.")
        return positions

    for position in positions:
        side = "BUY" if position.type == 0 else "SELL"

        print(f"Ticket:   {position.ticket}")
        print(f"Side:     {side}")
        print(f"Symbol:   {position.symbol}")
        print(f"Volume:   {position.volume}")
        print(f"Open:     {position.price_open}")
        print(f"Current:  {position.price_current}")
        print(f"Profit:   {position.profit:.2f} USD")
        print()

    return positions


def main():
    connector = MT5Connector()

    try:
        account = connector.connect()
        executor = TradeExecutor(connector)

        print("================================")
        print("          MT5 BOT")
        print("================================")
        print(f"Login:   {account.login}")
        print(f"Server:  {account.server}")
        print(f"Balance: {account.balance:.2f} {account.currency}")
        print(f"Equity:  {account.equity:.2f} {account.currency}")

        while True:
            print()
            print("================================")
            print("             MENU")
            print("================================")
            print("1. BUY  0.01 XAUUSD")
            print("2. SELL 0.01 XAUUSD")
            print("3. Mostra posizioni")
            print("4. Chiudi posizione")
            print("5. Chiudi tutte le posizioni XAUUSD")
            print("0. Esci")
            print()

            choice = input("Scelta: ").strip()

            if choice == "1":
                print()
                print("=== BUY 0.01 XAUUSD ===")

                result = executor.buy(
                    volume=0.01,
                    symbol=connector.symbol
                )

                if hasattr(result, "retcode"):
                    print(f"Retcode: {result.retcode}")
                    print(f"Comment: {result.comment}")

                    if hasattr(result, "order"):
                        print(f"Order ticket: {result.order}")

                    if hasattr(result, "deal"):
                        print(f"Deal ticket: {result.deal}")

            elif choice == "2":
                print()
                print("=== SELL 0.01 XAUUSD ===")

                result = executor.sell(
                    volume=0.01,
                    symbol=connector.symbol
                )

                if hasattr(result, "retcode"):
                    print(f"Retcode: {result.retcode}")
                    print(f"Comment: {result.comment}")

                    if hasattr(result, "order"):
                        print(f"Order ticket: {result.order}")

                    if hasattr(result, "deal"):
                        print(f"Deal ticket: {result.deal}")

            elif choice == "3":
                print_positions(
                    executor,
                    connector.symbol
                )

            elif choice == "4":
                positions = print_positions(
                    executor,
                    connector.symbol
                )

                if positions:
                    ticket = input(
                        "Inserisci il ticket da chiudere: "
                    ).strip()

                    if ticket.isdigit():
                        result = executor.close_position(
                            int(ticket)
                        )

                        print()
                        print(
                            f"Retcode: {result.retcode}"
                        )
                        print(
                            f"Comment: {result.comment}"
                        )
                    else:
                        print("Ticket non valido.")

            elif choice == "5":
                positions = executor.get_positions(
                    connector.symbol
                )

                if not positions:
                    print("Nessuna posizione da chiudere.")
                    continue

                print(
                    f"Posizioni da chiudere: "
                    f"{len(positions)}"
                )

                confirmation = input(
                    "Confermi la chiusura di TUTTE? "
                    "[si/no]: "
                ).strip().lower()

                if confirmation != "si":
                    print("Operazione annullata.")
                    continue

                for position in positions:
                    try:
                        result = executor.close_position(
                            position.ticket
                        )

                        print(
                            f"Ticket {position.ticket}: "
                            f"{result.retcode} - "
                            f"{result.comment}"
                        )

                    except Exception as e:
                        print(
                            f"Errore chiusura "
                            f"{position.ticket}: {e}"
                        )

            elif choice == "0":
                print("Uscita...")
                break

            else:
                print("Scelta non valida.")

    except Exception as e:
        print(f"ERRORE: {e}")

    finally:
        connector.disconnect()
        print("MT5 disconnesso.")


if __name__ == "__main__":
    main()
