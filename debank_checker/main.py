import threading

from queue import Queue
from time import time

from alive_progress import alive_bar

from app.json import *
from app.questions import *
from app.config import *
from app.utils import *

from app.config import file_json
from app.json import save_full_to_json, save_selected_to_json

from termcolor import colored
import os
import sys
# 确保可以从任何路径运行时都能正确引用本地 app 目录下的模块
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

def print_banner():
    """打印精美的横幅"""
    print(colored("✨", "yellow") + colored("─"*75, "light_blue") + colored("✨", "yellow"))
    custom_art = [
        "    ▗▄▄▄  ▗▄▄▄▖▗▄▄▖  ▗▄▖ ▗▖  ▗▖▗▖ ▗▖     ▗▄▄▖▗▖ ▗▖▗▄▄▄▖ ▗▄▄▖▗▖ ▗▖▗▄▄▄▖▗▄▄▖",
        "    ▐▌  █ ▐▌   ▐▌ ▐▌▐▌ ▐▌▐▛▚▖▐▌▐▌▗▞▘    ▐▌   ▐▌ ▐▌▐▌   ▐▌   ▐▌▗▞▘▐▌   ▐▌ ▐▌",
        "    ▐▌  █ ▐▛▀▀▘▐▛▀▚▖▐▛▀▜▌▐▌ ▝▜▌▐▛▚▖     ▐▌   ▐▛▀▜▌▐▛▀▀▘▐▌   ▐▛▚▖ ▐▛▀▀▘▐▛▀▚▖",
        "    ▐▙▄▄▀ ▐▙▄▄▖▐▙▄▞▘▐▌ ▐▌▐▌  ▐▌▐▌ ▐▌    ▝▚▄▄▖▐▌ ▐▌▐▙▄▄▖▝▚▄▄▖▐▌ ▐▌▐▙▄▄▖▐▌ ▐▌",
        "",
    ]
    
    # 打印自定义艺术字
    for line in custom_art:
        if line.strip():  # 只打印非空行
            print(colored(line, 'light_blue', attrs=["bold"]))
        else:
            print()  # 空行保持间距
    
    # 功能特色展示
    features = [
        "⛓️ 支持EVM链查询 (Ethereum, BSC, Polygon, Arbitrum, Optimism...)",
        "💎 实时价格获取 (DeBank-Cloud API)",
        "📊 详细余额统计 (代币 + 流动性池)",
        "⚡ 多线程并发处理 (提升查询速度)",
    ]
    
    print(colored("🌟 功能特色:", "yellow", attrs=["bold"]))
    for feature in features:
        print(colored(f"   {feature}", "white"))
    print()
    
    # 版本信息
    print(colored("📋 版本信息:", "magenta", attrs=["bold"]))
    print(colored("   🐍 Python 3.8+ | 🛜 DeBank—Cloud API | 🎯 支持批量EVM地址查询", "light_blue"))
    print()
    
    # 底部装饰
    print(colored("✨", "yellow") + colored("─"*75, "light_blue") + colored("✨", "yellow"))
    print()

def print_separator(title=None):
    """打印分隔线"""
    if title:
        print(colored("╭" + "─"*24 + f" {title} " + "─"*24 + "╮", "magenta", attrs=["bold"]))
    else:
        print(colored("╭" + "─"*58 + "╮", "magenta", attrs=["bold"]))

def print_end_separator():
    """打印结束分隔线"""
    print(colored("╰" + "─"*58 + "╯", "magenta", attrs=["bold"]))

def choose_output_mode():
    print_separator("模式选择")
    print(colored("🎨  请选择输出模式：", "cyan", attrs=["bold"]))
    print()
    print(colored("  📊  1. 各链和池子余额（详细模式）", "green", attrs=["bold"]))
    print(colored("     └─ 显示每个钱包在所有链和池子中的详细余额", "white"))
    print()
    print(colored("  📈  2. 仅总余额（简单模式）", "green", attrs=["bold"]))
    print(colored("     └─ 只显示每个钱包的总余额汇总", "white"))
    print()
    
    while True:
        mode = input(colored("💫  请输入选择 (1 或 2): ", "yellow", attrs=["bold"])).strip()
        if mode in ("1", "2"):
            mode_name = "详细模式" if mode == "1" else "简单模式"
            print(colored(f"✅  已选择: {mode_name}", "cyan", attrs=["bold"]))
            print_end_separator()
            print()
            return mode
        print(colored("❌  输入有误，请输入 1 或 2", "red", attrs=["bold"]))

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
    print()
    print_separator("帮助信息")
    print(colored("📚  常见问题解答", "yellow", attrs=["bold", "reverse"]))
    print()
    
    questions = [
        ("❓ 最小代币金额（美元）是什么意思？", "如果某个代币的美元金额小于设定的最小值，则不会被写入 balances.json。"),
        ("❓ 工作线程数是什么意思？", "这是同时获取钱包信息的'工作进程'数量。线程数越多，被 Cloudflare 限制的风险越高。推荐 3 个线程。"),
        ("❓ 余额进度条不动怎么办？", "减少线程数/检查网络连接。"),
        ("❓ 为什么获取钱包已用链列表很慢？", "因为该请求容易被 Cloudflare 限制，所以只能单线程处理。"),
        ("❓ 其他问题？", "欢迎交流 🔗 https://t.me/cryptostar210")
    ]
    
    for i, (q, a) in enumerate(questions, 1):
        print(colored(f"  {q}", "red", attrs=["bold"]))
        print(colored(f"     💡  {a}", "white"))
        if i < len(questions):
            print()
    
    print_end_separator()

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

    with alive_bar(len(wallets), title='⛓️ 链列表', bar='smooth') as bar:
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

    with alive_bar(len(wallets), title='🏊 池子信息', bar='smooth') as bar:
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
    print()

    print_separator("数据获取")
    logger.info('🔍  正在获取钱包已使用的 EVM 链列表以及钱包在其中的余额...')
    chains = list(get_chains(node_process, session, wallets))
    logger.info('🔍  正在获取池子列表以及钱包在其中的余额...')
    pools = get_pools(node_process, session, wallets)
    logger.success(f'🎉  完成！已使用的 EVM 链和池子的合计数量为: {len(chains) + len(pools)}')
    print()

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
            logger.info(f'🌐  [{chain_id + 1}/{len(selected_chains) - len(set(selected_chains) & set(pools_names))}] 正在获取 {chain.upper()} 网络的余额...')

            for wallet in wallets:
                queue_tasks.put(('chain_balance', wallet, chain, ticker, min_amount))

            with alive_bar(len(wallets), title=f'📊 {chain.upper()}', bar='smooth') as bar:
                for wallet in wallets:
                    result = queue_results.get()
                    coins[result[0]][result[1]] = result[2]
                    bar()

    print()
    logger.info('💰  正在获取每个钱包在所有 EVM 链上的余额')
    for wallet in wallets:
        queue_tasks.put(('get_wallet_balance', wallet))

    balances = {}
    with alive_bar(len(wallets), title='💳 钱包余额', bar='smooth') as bar:
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
    print()

    print_separator("统计结果")
    print()
    
    total_wallets = len(wallets)
    total_balance = sum(balances.values())
    nonzero_wallets = [w for w, v in balances.items() if v > 0]
    
    # 统计信息卡片
    print(colored("╭" + "─"*25 + "╮" + " " + "╭" + "─"*25 + "╮", "magenta"))
    print(colored("│", "magenta") + colored(f"  💼 钱包总数", "yellow", attrs=["bold"]) + colored(" "*12, "magenta") + colored("│", "magenta") + 
          colored(" │", "magenta") + colored(f"  💰 总余额", "yellow", attrs=["bold"]) + colored(" "*14, "magenta") + colored("│", "magenta"))
    print(colored("│", "magenta") + colored(f"  {total_wallets:>8}", "white", attrs=["bold"]) + colored(" "*15, "magenta") + colored("│", "magenta") + 
          colored(" │", "magenta") + colored(f"  ${total_balance:>10.2f}", "magenta", attrs=["bold"]) + colored(" "*12, "magenta") + colored("│", "magenta"))
    print(colored("╰" + "─"*25 + "╯" + " " + "╰" + "─"*25 + "╯", "magenta"))
    print()
    
    print(colored("╭" + "─"*25 + "╮", "magenta"))
    print(colored("│", "magenta") + colored(f"  🎯 有余额钱包", "yellow", attrs=["bold"]) + colored(" "*10, "magenta") + colored("│", "magenta"))
    print(colored("│", "magenta") + colored(f"  {len(nonzero_wallets):>8}", "white", attrs=["bold"]) + colored(" "*15, "magenta") + colored("│", "magenta"))
    print(colored("╰" + "─"*25 + "╯", "magenta"))
    print()

    # 表格输出
    print(colored("📋  详细余额列表", "cyan", attrs=["bold"]))
    print()
    
    table_data = []
    for w, v in balances.items():
        status_icon = "✅" if v > 0 else "❌"
        status_color = "green" if v > 0 else "red"
        table_data.append([
            w,
            f"${v:.2f}",
            colored(status_icon, status_color)
        ])
    
    headers = [
        colored("钱包地址", "cyan", attrs=["bold"]), 
        colored("余额(USD)", "cyan", attrs=["bold"]), 
        colored("状态", "cyan", attrs=["bold"])
    ]
    
    if use_tabulate:
        # 为tabulate创建带颜色的数据
        colored_table_data = []
        for row in table_data:
            addr_color = "yellow" if float(row[1].replace('$', '')) > 0 else "grey"
            bal_color = "magenta" if float(row[1].replace('$', '')) > 0 else "red"
            colored_table_data.append([
                colored(row[0], addr_color, attrs=["bold"]),
                colored(row[1], bal_color, attrs=["bold"]),
                row[2]  # 状态已经是colored的
            ])
        
        print(tabulate(
            colored_table_data,
            headers=headers,
            tablefmt="grid",
            stralign="left",
            numalign="right"
        ))
    else:
        # 自定义表格格式
        print(colored("┌" + "─"*44 + "┬" + "─"*15 + "┬" + "─"*8 + "┐", "cyan"))
        print(colored("│", "cyan") + colored(f"{'钱包地址':^44}", "cyan", attrs=["bold"]) + 
              colored("│", "cyan") + colored(f"{'余额(USD)':^15}", "cyan", attrs=["bold"]) + 
              colored("│", "cyan") + colored(f"{'状态':^8}", "cyan", attrs=["bold"]) + colored("│", "cyan"))
        print(colored("├" + "─"*44 + "┼" + "─"*15 + "┼" + "─"*8 + "┤", "cyan"))
        
        for row in table_data:
            # 地址设置为黄色，余额设置为紫色
            addr_str = colored(f"{row[0]:^44}", "yellow", attrs=["bold"]) if float(row[1].replace('$', '')) > 0 else colored(f"{row[0]:^44}", "grey")
            bal_str = colored(f"{row[1]:^15}", "magenta", attrs=["bold"]) if float(row[1].replace('$', '')) > 0 else colored(f"{row[1]:^15}", "red")
            status_str = colored(f"{row[2]:^8}", "green") if float(row[1].replace('$', '')) > 0 else colored(f"{row[2]:^8}", "red")
            print(colored("│", "cyan") + addr_str + colored("│", "cyan") + bal_str + colored("│", "cyan") + status_str + colored("│", "cyan"))
        
        print(colored("└" + "─"*44 + "┴" + "─"*15 + "┴" + "─"*8 + "┘", "cyan"))

    print()
    logger.success(f'🎉  完成！查询结果已生成至 {file_json}')
    logger.info(f'⏱️  耗时: {round((time() - start_time) / 60, 1)} 分钟')
    print_end_separator()
    print()

def main():
    print_banner()

    print(colored("📝  请输入 EVM 钱包地址列表（每行一个地址，输入完后两次回车确认）：", "yellow", attrs=["bold"]))
    print(colored("💡  提示：可以复制粘贴多个地址，每行一个", "blue", attrs=["bold"]))
    print()
    
    input_lines = []
    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            print(colored("\n❌ 输入中断，程序退出。", "red", attrs=["bold"]))
            exit()
        if line.strip() == '':
            break
        input_lines.append(line)
    wallets = [addr.strip().lower() for addr in input_lines if addr.strip()]

    if not wallets:
        print(colored("❌ 未输入任何有效地址，程序退出。", "red", attrs=["bold"]))
        exit()

    logger.success(f'✅  成功加载 {len(wallets)} 个地址')
    print()

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
                print("\n" + colored("👋 感谢使用，再见！", "green", attrs=["bold", "reverse"]))
                exit()
            case _:
                pass


if (__name__ == '__main__'):
    main()
