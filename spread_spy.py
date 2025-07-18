#!/usr/bin/env python3
"""
SpreadSpy — мониторинг спреда между двумя Uniswap‑совместимыми пулами
для обнаружения арбитражных возможностей.
"""

import os
import time
from decimal import Decimal
from web3 import Web3

# Параметры из окружения
RPC_URL           = os.getenv("ETH_RPC_URL")
PAIR_A_ADDRESS    = os.getenv("PAIR_A_ADDRESS")    # пул A (например UniswapV2)
PAIR_B_ADDRESS    = os.getenv("PAIR_B_ADDRESS")    # пул B (например Sushiswap)
TOKEN_DECIMALS    = int(os.getenv("TOKEN_DECIMALS", "18"))
CHECK_AMOUNT      = Decimal(os.getenv("CHECK_AMOUNT", "1"))  # в единицах токена0
THRESHOLD_PERCENT = Decimal(os.getenv("THRESHOLD_PERCENT", "1.0"))  # %
POLL_INTERVAL     = int(os.getenv("POLL_INTERVAL", "10"))  # сек

if not all([RPC_URL, PAIR_A_ADDRESS, PAIR_B_ADDRESS]):
    print("❗ Не заданы ETH_RPC_URL, PAIR_A_ADDRESS, PAIR_B_ADDRESS")
    exit(1)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print("❗ Не удалось подключиться к RPC‑узлу")
    exit(1)

# ABI для UniswapV2‑пула: getReserves()
PAIR_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "_reserve0", "type": "uint112"},
            {"name": "_reserve1", "type": "uint112"},
            {"name": "_blockTimestampLast", "type": "uint32"}
        ],
        "type": "function"
    }
]

def fetch_price(pair_addr):
    pair = w3.eth.contract(address=pair_addr, abi=PAIR_ABI)
    r0, r1, _ = pair.functions.getReserves().call()
    # Цена token1 в токен0: price = reserve0 / reserve1
    if r1 == 0:
        return None
    return Decimal(r0) / Decimal(r1)

def main():
    print("🚀 SpreadSpy запущен. Отслеживаем спред:")
    print(f" • пул A: {PAIR_A_ADDRESS}")
    print(f" • пул B: {PAIR_B_ADDRESS}")
    print(f" • объём для оценки: {CHECK_AMOUNT} токен0")
    print(f" • порог спреда: {THRESHOLD_PERCENT}%\n")

    while True:
        try:
            price_a = fetch_price(PAIR_A_ADDRESS)
            price_b = fetch_price(PAIR_B_ADDRESS)
            if price_a is None or price_b is None:
                print("⚠️ Ошибка получения резервов — повтор через", POLL_INTERVAL, "с")
            else:
                # расчёт относительного спреда
                spread = abs(price_a - price_b) / min(price_a, price_b) * 100
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                if spread >= THRESHOLD_PERCENT:
                    direction = "A→B" if price_a < price_b else "B→A"
                    print(f"[{ts}] 🟢 Арбитраж: {spread:.2f}% ({direction})")
                    print(f"    price A = {price_a:.6f}, price B = {price_b:.6f}")
                else:
                    print(f"[{ts}] — спред {spread:.2f}% < {THRESHOLD_PERCENT}%")
        except Exception as e:
            print("❗ Ошибка:", e)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
