"""
Chain Summary — сводная статистика по блокам Bitcoin.
"""

import requests
import argparse

def get_block(block_height):
    url = f"https://api.blockchair.com/bitcoin/raw/block/{block_height}"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"❌ Не удалось получить блок {block_height}")
    return r.json()["data"][str(block_height)]["decoded_raw_block"]

def summarize_range(start, end):
    total_fees = 0
    total_txs = 0
    block_count = 0

    print(f"📊 Анализ блоков с {start} по {end}")
    for height in range(start, end + 1):
        try:
            block = get_block(height)
            txs = block.get("tx", [])
            if not txs:
                continue

            fees = 0
            for tx in txs[1:]:  # exclude coinbase
                vin_sum = sum(inp.get("prevout", {}).get("value", 0) for inp in tx.get("vin", []) if "prevout" in inp)
                vout_sum = sum(out.get("value", 0) for out in tx.get("vout", []))
                fees += vin_sum - vout_sum

            print(f"⛏️ Блок {height}: {len(txs)} TX | Комиссии: {fees} сатоши")
            total_fees += fees
            total_txs += len(txs)
            block_count += 1
        except Exception as e:
            print(f"⚠️ {e}")

    if block_count == 0:
        print("❌ Нет данных.")
        return

    print("\n📈 ИТОГО:")
    print(f"🧱 Блоков: {block_count}")
    print(f"📦 Транзакций: {total_txs}")
    print(f"💰 Общие комиссии: {total_fees} сатоши")
    print(f"📊 Среднее TX/блок: {total_txs // block_count}")
    print(f"💸 Средняя комиссия/блок: {total_fees // block_count} сатоши")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chain Summary — обзор статистики блоков.")
    parser.add_argument("start_block", type=int, help="Номер начального блока")
    parser.add_argument("end_block", type=int, help="Номер конечного блока")
    args = parser.parse_args()

    summarize_range(args.start_block, args.end_block)
