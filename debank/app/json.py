import json

from .config import file_json

def save_full_to_json(wallets, chains, coins, balances, file_json):
    # 简洁模式：只输出wallet和total_all_chains
    if not chains:
        data = []
        for wallet in wallets:
            data.append({
                'wallet': wallet,
                'total_all_chains': balances.get(wallet, 0)
            })
        with open(file_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return
        
    # 详细模式    
    data = []
    for wallet in wallets:
        wallet_data = {
            'wallet': wallet,
            'chains': {},
            'total_in_usd': 0,
            'total_all_chains': balances.get(wallet, 0)
        }
        total_in_wallet = 0
        for chain in chains:
            chain_coins = coins.get(chain, {}).get(wallet, [])
            chain_list = []
            total_in_chain_for_wallet = 0.0
            for coin in chain_coins:
                coin_in_usd = 0 if coin["price"] is None else round(coin["amount"] * coin["price"], 2)
                chain_list.append({
                    'ticker': coin['ticker'],
                    'amount': coin['amount'],
                    'price': coin['price'],
                    'name': coin['name'],
                    'usd': coin_in_usd
                })
                if isinstance(coin_in_usd, (int, float)):
                    total_in_wallet += coin_in_usd
                    total_in_chain_for_wallet += coin_in_usd
            wallet_data['chains'][chain] = {
                'coins': chain_list,
                'total_usd_in_chain': round(total_in_chain_for_wallet, 2)
            }
        wallet_data['total_in_usd'] = round(total_in_wallet, 2)
        data.append(wallet_data)
    with open(file_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_selected_to_json(wallets, chains, coins, balances, ticker, file_json):
    # 简洁模式：只输出wallet和total_all_chains
    if not chains:
        data = []
        for wallet in wallets:
            data.append({
                'wallet': wallet,
                'total_all_chains': balances.get(wallet, 0)
            })
        with open(file_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return
    
    # 详细模式
    data = []
    for wallet in wallets:
        wallet_data = {
            'wallet': wallet,
            'chains': {},
            'total_in_usd': 0,
            'total_all_chains': balances.get(wallet, 0)
        }
        total_in_wallet = 0
        for chain in chains:
            chain_coins = coins.get(chain, {}).get(wallet, [])
            chain_list = []
            for coin in chain_coins:
                if coin['ticker'] == ticker:
                    coin_in_usd = 0 if coin["price"] is None else round(coin["amount"] * coin["price"], 2)
                    chain_list.append({
                        'ticker': coin['ticker'],
                        'amount': coin['amount'],
                        'price': coin['price'],
                        'name': coin['name'],
                        'usd': coin_in_usd
                    })
                    total_in_wallet += coin_in_usd
            wallet_data['chains'][chain] = chain_list
        wallet_data['total_in_usd'] = total_in_wallet
        data.append(wallet_data)
    with open(file_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
