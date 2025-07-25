import threading

from queue import Queue
from time import time

from art import text2art
from alive_progress import alive_bar

from app.json import *
from app.questions import *
from app.config import *
from app.utils import *

from app.config import file_json
from app.json import save_full_to_json, save_selected_to_json

from termcolor import colored

def choose_output_mode():
    print(colored("-"*50 + "\n", "magenta", attrs=["bold"]))
    print(colored("🌿  请选择输出模式：", "cyan", attrs=["bold"]))
    print(colored("1. 各链和池子余额（详细模式）", "green"))
    print(colored("2. 仅总余额（简单模式）", "green"))
    print()
    while True:
        mode = input(colored("💁‍♀️  请输入 1 或 2 并回车：", "yellow", attrs=["bold"])).strip()
        if mode in ("1", "2"):
            print(colored(f"➡️  你选择了模式 {mode}\n", "cyan"))
            print(colored("-"*50 + "\n", "magenta", attrs=["bold"]))
            return mode
        print(colored("⚠️  输入有误，请重新输入 1 或 2。", "red", attrs=["bold"]))

def chain_balance(node_process, session, address, chain, ticker, min_amount):
    coins = []

    payload = {
        'user_addr': address,
        'chain': chain
    }
    try:
        edit_session_headers(node_process, session, payload, 'GET', '/token/balance_list')
        resp = send_request(
            node_process, 
            session=session,
            method='GET',
            url=f'https://api.debank.com/token/balance_list?user_addr={address}&chain={chain}',
        )
        data = resp.json()
    except Exception as e:
        logger.error(f"获取 {address} 在 {chain} 的余额时出错: {e}")
        return coins

    for coin in data.get('data', []):
        if (ticker == None or coin['optimized_symbol'] == ticker):
            coin_in_usd = '?' if (coin["price"] is None) else coin["amount"] * coin["price"]
            if (type(coin_in_usd) is str or (type(coin_in_usd) is float and coin_in_usd > min_amount)):
                coins.append({
                    'amount': coin['amount'],
                    'name': coin['name'],
                    'ticker': coin['optimized_symbol'],
                    'price': coin['price'],
                    'logo_url': coin['logo_url']
                })
    
    return coins


def show_help():
    from termcolor import colored
    print(colored("--------------------- 📖  帮助 📖 ---------------------", "yellow", attrs=["bold"]))
    print(colored("❓ 最小代币金额（美元）是什么意思？", "red", attrs=["bold"]))
    print("🔊  如果某个代币的美元金额小于设定的最小值，则不会被写入 balance.json。\n")
    print(colored("❓ 工作线程数是什么意思？", "red", attrs=["bold"]))
    print("🔊  这是同时获取钱包信息的“工作进程”数量。线程数越多，被 Cloudflare 限制的风险越高。推荐 3 个线程。\n")
    print(colored("❓ 余额进度条不动怎么办？", "red", attrs=["bold"]))
    print("🔊  减少线程数/检查网络连接。\n")
    print(colored("❓ 为什么获取钱包已用链列表很慢？", "red", attrs=["bold"]))
    print("🔊  因为该请求容易被 Cloudflare 限制，所以只能单线程处理。\n")
    print(colored("❓ 其他问题？", "red", attrs=["bold"]))
    print("🔊  欢迎交流 🔗 https://t.me/cryptostar210 \n")

def get_used_chains(node_process, session, address):
    payload = {
        'id': address,
    }
    try:
        edit_session_headers(node_process, session, payload, 'GET', '/user/used_chains')
        resp = send_request(
            node_process, 
            session=session,
            method='GET',
            url=f'https://api.debank.com/user/used_chains?id={address}',
        )
        data = resp.json()
        chains = data['data']['chains']
    except Exception as e:
        logger.error(f"获取 {address} 已用链时出错: {e}")
        chains = []
    return chains


def get_chains(node_process, session, wallets):
    chains = set()

    with alive_bar(len(wallets)) as bar:
        for wallet in wallets:
            chains = chains.union(get_used_chains(node_process, session, wallet))
            bar()

    print()
    return chains


def get_wallet_balance(node_process, session, address):
    payload = {
        'user_addr': address,
    }
    try:
        edit_session_headers(node_process, session, payload, 'GET', '/asset/net_curve_24h')
        resp = send_request(
            node_process,
            session=session,
            method='GET',
            url=f'https://api.debank.com/asset/net_curve_24h?user_addr={address}',
        )
        data = resp.json()
        usd_value = data['data']['usd_value_list'][-1][1]
    except Exception as e:
        logger.error(f"获取 {address} 总余额时出错: {e}")
        usd_value = 0.0
    return usd_value


def get_pools(node_process, session, wallets):
    def get_pool(session, address):
        pools = {}
        payload = {
            'user_addr': address,
        }
        try:
            edit_session_headers(node_process, session, payload, 'GET', '/portfolio/project_list')
            resp = send_request(
                node_process,
                session=session,
                method='GET',
                url=f'https://api.debank.com/portfolio/project_list?user_addr={address}',
            )
            data = resp.json()
        except Exception as e:
            logger.error(f"获取 {address} 池子信息时出错: {e}")
            return pools

        for pool in data.get('data', []):
            pools[f"{pool['name']} ({pool['chain']})"] = []
            for item in pool.get('portfolio_item_list', []):
                for coin in item.get('asset_token_list', []):
                    pools[f"{pool['name']} ({pool['chain']})"].append({
                        'amount': coin['amount'],
                        'name': coin['name'],
                        'ticker': coin['optimized_symbol'],
                        'price': coin['price'],
                        'logo_url': coin['logo_url']
                    })

        return pools
    
    all_pools = {}

    with alive_bar(len(wallets)) as bar:
        for wallet in wallets:
            pools = get_pool(session, wallet)
            for pool in pools:
                if (pool not in all_pools):
                    all_pools[pool] = {}
                all_pools[pool][wallet] = pools[pool]
            bar()

    for pool in all_pools:
        for wallet in wallets:
            if (wallet not in all_pools[pool]):
                all_pools[pool][wallet] = []
    print()

    return all_pools


def worker(queue_tasks, queue_results):
    session, node_process = setup_session()

    while True:
        try:
            task = queue_tasks.get()
            if (task[0] == 'chain_balance'):
                balance = chain_balance(node_process, session, task[1], task[2], task[3], task[4])
                queue_results.put((task[2], task[1], balance))
            elif (task[0] == 'get_wallet_balance'):
                balance = get_wallet_balance(node_process, session, task[1])
                queue_results.put((task[1], balance))
            elif (task[0] == 'done'):
                queue_tasks.put(('done',))
                break
        except Exception as e:
            logger.error(f"线程任务执行出错: {e}")

def get_balances(wallets, ticker=None, output_mode="1"):
    session, node_process = setup_session()

    logger.info('🔍  正在获取钱包已使用的 EVM 链列表以及钱包在其中的余额...')
    chains = list(get_chains(node_process, session, wallets))
    logger.info('🔍  正在获取池子列表以及钱包在其中的余额...')
    pools = get_pools(node_process, session, wallets)
    logger.success(f'🔆  完成！已使用的 EVM 链和池子的合计数量为: {len(chains) + len(pools)}\n')

    min_amount = get_minimal_amount_in_usd()
    num_of_threads = get_num_of_threads()
    if output_mode == "1":
        selected_chains = chains + [pool for pool in pools]
    else:
        selected_chains = []

    coins = {chain: dict() for chain in selected_chains}
    coins.update(pools)
    pools_names = [pool for pool in pools]

    queue_tasks = Queue()
    queue_results = Queue()

    threads = []
    for _ in range(num_of_threads):
        th = threading.Thread(target=worker, args=(queue_tasks, queue_results))
        threads.append(th)
        th.start()

    start_time = time()
    for chain_id, chain in enumerate(selected_chains):
        if (chain not in pools_names):
            logger.info(f'[{chain_id + 1}/{len(selected_chains) - len(set(selected_chains) & set(pools_names))}] 正在获取 {chain.upper()} 网络的余额...')

            for wallet in wallets:
                queue_tasks.put(('chain_balance', wallet, chain, ticker, min_amount))

            with alive_bar(len(wallets)) as bar:
                for wallet in wallets:
                    result = queue_results.get()
                    coins[result[0]][result[1]] = result[2]
                    bar()

    print()
    logger.info('🔍  正在获取每个钱包在所有 EVM 链上的余额')
    for wallet in wallets:
        queue_tasks.put(('get_wallet_balance', wallet))

    balances = {}
    with alive_bar(len(wallets)) as bar:
        for wallet in wallets:
            result = queue_results.get()
            balances[result[0]] = result[1]
            bar()

    queue_tasks.put(('done',))
    for th in threads:
        th.join()

    if (ticker is None):
        if output_mode == "1":
            save_full_to_json(wallets, selected_chains, coins, balances, file_json)
        else:
            save_full_to_json(wallets, [], {}, balances, file_json)
    else:
        if output_mode == "1":
            save_selected_to_json(wallets, selected_chains, coins, balances, ticker, file_json)
        else:
            save_selected_to_json(wallets, [], {}, balances, ticker, file_json)

    # 统计输出（美化版+表格）
    from termcolor import colored
    try:
        from tabulate import tabulate
        use_tabulate = True
    except ImportError:
        use_tabulate = False
        logger.warning("未安装 tabulate 库，表格美化功能不可用。可通过 pip install tabulate 安装。")

    print(colored("\n" + "-"*50, "magenta", attrs=["bold"]))
    print(colored("\U0001F4CA 统计结果 SUMMARY ", "white", attrs=["bold", "reverse"]).center(50))
    print()
    total_wallets = len(wallets)
    total_balance = sum(balances.values())
    nonzero_wallets = [w for w, v in balances.items() if v > 0]
    print(colored(f"\U0001F4B0 钱包总数: ", "yellow", attrs=["bold"]) + colored(f"{total_wallets}", "white", attrs=["bold"]))
    print(colored(f"\U0001F4B5 总余额: ", "yellow", attrs=["bold"]) + colored(f"{total_balance:.2f} USD", "magenta", attrs=["bold"]))
    print(colored(f"\U0001F911 余额大于0的钱包数: ", "yellow", attrs=["bold"]) + colored(f"{len(nonzero_wallets)}", "white", attrs=["bold"]))

    # 表格输出
    table_data = []
    for w, v in balances.items():
        table_data.append([
            w,
            f"{v:.2f}",
            "✅" if v > 0 else "❌"
        ])
    headers = [colored("钱包地址", "cyan", attrs=["bold"]), colored("余额(USD)", "cyan", attrs=["bold"]), colored("状态", "cyan", attrs=["bold"])]
    if use_tabulate:
        print(tabulate(
            table_data,
            headers=headers,
            tablefmt="fancy_grid",
            stralign="right",
            numalign="right"
        ))
    else:
        print(colored(f"{'钱包地址':^44}{'余额(USD)':^15}{'状态':^8}", "cyan", attrs=["bold"]))
        for row in table_data:
            addr_str = colored(f"{row[0]:>44}", "white", attrs=["bold"]) if float(row[1]) > 0 else colored(f"{row[0]:>44}", "grey")
            bal_str = colored(f"{row[1]:>15}", "green", attrs=["bold"]) if float(row[1]) > 0 else colored(f"{row[1]:>15}", "red")
            status_str = colored(f"{row[2]:>8}", "green") if float(row[1]) > 0 else colored(f"{row[2]:>8}", "red")
            print(addr_str + bal_str + status_str)

    print()
    logger.success(f'🔆  完成！查询结果已生成至 {file_json}')
    logger.info(f'⏱️  耗时: {round((time() - start_time) / 60, 1)} 分钟.\n')
    print(colored("="*50 + "\n", "magenta", attrs=["bold"]))

def main():
    art = text2art(text="DEBANK   CHECKER", font="standart")
    print(colored(art,'light_blue'))
    print(colored('💬  Telegram: t.me/cryptostar210','light_cyan'))
    print(colored('☕  请我喝杯咖啡：0xd328426a8e0bcdbbef89e96a91911eff68734e84','light_cyan'))
    print(colored("-"*50 + "\n", "magenta", attrs=["bold"]))

    print(colored("📝  请输入 EVM 钱包地址列表（每行一个地址，输入完后回车确认）：", "yellow", attrs=["bold"]))
    input_lines = []
    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            print("\n输入中断，程序退出。")
            exit()
        if line.strip() == '':
            break
        input_lines.append(line)
    wallets = [addr.strip().lower() for addr in input_lines if addr.strip()]

    logger.success(f'🔆  成功加载 {len(wallets)} 个地址\n')

    output_mode = choose_output_mode()

    while True:
        action = get_action()

        match action:
            case '💲 -获取钱包中所有EVM链的代币余额':
                get_balances(wallets, output_mode=output_mode)
            case '🪙 -仅获取特定代币的余额':
                ticker = get_ticker()
                get_balances(wallets, ticker, output_mode=output_mode)
            case '📖 -帮助':
                show_help()
            case '📤 -退出':
                exit()
            case _:
                pass


if (__name__ == '__main__'):
    main()
