import os
import json
import sys
from art import text2art
from termcolor import colored
from alive_progress import alive_bar

# 确保可以从任何路径运行时都能正确引用同目录下的 main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import get_chains, setup_session, chain_balance, edit_session_headers, send_request

def print_banner():
    print(colored("-"*60, "magenta", attrs=["bold"]))
    print(colored("🚀 钱包代币分析工具🚀\n", "green", attrs=["bold", "reverse"]))
    art = text2art(text="DEBANK   CHECKER", font="standart")
    print(colored(art,'light_blue'))

def print_section_header(title):
    """打印章节标题"""
    print(colored(f"\n{'='*60}", "magenta", attrs=["bold"]))
    print(colored(f"  {title}", "cyan", attrs=["bold"]))
    print(colored(f"{'='*60}", "magenta", attrs=["bold"]))

def print_success(message):
    """打印成功信息"""
    print(colored(f"✅ {message}", "green", attrs=["bold"]))

def print_info(message):
    """打印信息"""
    print(colored(f"ℹ️  {message}", "blue"))

def print_warning(message):
    """打印警告信息"""
    print(colored(f"⚠️  {message}", "yellow"))

def print_error(message):
    """打印错误信息"""
    print(colored(f"❌ {message}", "red", attrs=["bold"]))

def print_progress(message):
    """打印进度信息"""
    print(colored(f"🔄 {message}", "cyan"))

def get_chain_token_addresses(node_process, session, wallets, chain):
    """
    获取指定链上所有钱包持有的代币地址列表
    """
    token_addresses = set()
    
    for wallet in wallets:
        try:
            # 直接调用 DeBank API 获取代币余额列表
            payload = {
                'user_addr': wallet,
                'chain': chain
            }
            edit_session_headers(node_process, session, payload, 'GET', '/token/balance_list')
            resp = send_request(
                node_process, 
                session=session,
                method='GET',
                url=f'https://api.debank.com/token/balance_list?user_addr={wallet}&chain={chain}',
            )
            data = resp.json()
            
            # 从响应中提取代币地址
            for coin in data.get('data', []):
                if 'id' in coin:  # 代币合约地址通常在 'id' 字段中
                    token_addresses.add(coin['id'])
                elif 'address' in coin:  # 或者可能在 'address' 字段中
                    token_addresses.add(coin['address'])
                    
        except Exception as e:
            print_error(f"获取 {wallet} 在 {chain} 的代币地址时出错: {e}")
            continue
    
    return list(token_addresses)

def get_chain_tokens(node_process, session, wallets, chain):
    """
    获取指定链上所有钱包持有的代币合约地址、余额和名称列表
    返回: [{"address": ..., "amount": ..., "name": ...}, ...]
    """
    tokens = {}
    for wallet in wallets:
        try:
            payload = {
                'user_addr': wallet,
                'chain': chain
            }
            edit_session_headers(node_process, session, payload, 'GET', '/token/balance_list')
            resp = send_request(
                node_process, 
                session=session,
                method='GET',
                url=f'https://api.debank.com/token/balance_list?user_addr={wallet}&chain={chain}',
            )
            data = resp.json()
            for coin in data.get('data', []):
                name = coin.get('name', '')
                address = coin.get('id') or coin.get('address')
                amount = coin.get('amount', 0)
                if address:
                    if address in tokens:
                        tokens[address]['amount'] += amount
                    else:
                        tokens[address] = {'name': name, 'address': address, 'amount': amount}
        except Exception as e:
            print_error(f"获取 {wallet} 在 {chain} 的代币信息时出错: {e}")
            continue
    # 转为列表
    return list(tokens.values())

def print_summary_table(used_chain_data):
    """打印汇总表格"""
    print_section_header("📊 分析结果汇总")
    
    # 表格头部
    print(colored(f"{'链名称':<12} {'链ID':<10} {'币种数量':<8} {'状态'}", "yellow", attrs=["bold"]))
    print(colored("-" * 50, "yellow"))
    
    # 表格内容
    for chain_data in used_chain_data:
        name = chain_data['name']
        chain_id = chain_data['chain_id'] or 'N/A'
        token_count = chain_data['token_count']
        
        # 根据代币数量选择颜色
        if token_count > 10:
            status_color = "green"
            status = "丰富"
        elif token_count > 5:
            status_color = "yellow"
            status = "中等"
        else:
            status_color = "blue"
            status = "较少"
        
        print(f"{name:<12} {chain_id:<10} {token_count:<8} {colored(status, status_color)}")
    
    print(colored("-" * 50, "yellow"))

def run_with_wallets(wallets: list[str]):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chainid_path = os.path.join(base_dir, 'evm_scavenger/conf/chain_index.json')
    used_chain_path = os.path.join(base_dir, 'evm_scavenger/conf/used_chains.json')
    
    # 然后进行错误检查
    if not wallets:
        print_error("未输入任何钱包地址，程序退出。")
        exit()
    if len(wallets) > 1:
        print_error("只支持查询一个钱包地址，请重新运行并只输入一个地址！")
        exit()
    print_success(f"查询钱包地址：{wallets[0]}")
    print_section_header("🔧 系统初始化")
    print_progress("正在初始化 DeBank 会话...")
    session, node_process = setup_session()
    print_success("DeBank 会话初始化完成")
    print_progress("正在获取钱包使用的链列表...")
    chains = list(get_chains(node_process, session, wallets))
    print_success(f"发现 {len(chains)} 条链")
    print_section_header("🔍 链余额分析")
    print(colored("正在分析各链余额并收集代币地址信息...", "cyan", attrs=["bold"]))
    min_usd = 0
    filtered_chains = []
    chain_tokens = {}
    with alive_bar(len(chains), title="分析链余额", bar="smooth") as bar:
        for chain in chains:
            total_usd = 0.0
            for wallet in wallets:
                coins = chain_balance(node_process, session, wallet, chain, None, 0)
                for coin in coins:
                    if coin['price'] is not None:
                        total_usd += coin['amount'] * coin['price']
            if total_usd > min_usd:
                filtered_chains.append(chain)
                bar.text(f"收集 {chain} 链代币信息...")
                tokens = get_chain_tokens(node_process, session, wallets, chain)
                chain_tokens[chain] = tokens
            bar()
    chains = filtered_chains
    print_section_header("🗺️ 链ID映射")
    print_progress("正在加载链ID映射表...")
    try:
        with open(chainid_path, 'r', encoding='utf-8') as f:
            chainid_list = json.load(f)
        chainid_map = {c['name']: c['chain_id'] for c in chainid_list}
        print_success(f"成功加载 {len(chainid_map)} 个链ID映射")
    except Exception as e:
        print_warning(f"加载链ID映射失败: {e}")
        chainid_map = {}
    print_section_header("📊 数据生成")
    print_progress("正在生成链数据...")
    used_chain_data = []
    for chain in chains:
        chain_id = chainid_map.get(chain)
        tokens = chain_tokens.get(chain, [])
        chain_data = {
            'name': chain,
            'chain_id': chain_id,
            'tokens': tokens,
            'token_count': len(tokens)
        }
        used_chain_data.append(chain_data)
    print_progress("正在保存数据到文件...")
    with open(used_chain_path, 'w', encoding='utf-8') as f:
        json.dump(used_chain_data, f, ensure_ascii=False, indent=2)
    print_success(f"数据已保存到: {used_chain_path}")
    print_summary_table(used_chain_data)
    print_section_header("🎉 任务完成")
    print_success(f"成功生成 used_chains.json，共 {len(used_chain_data)} 条链")
    print_info("每条链现在包含以下信息：")
    print()
    print(colored("   📝 name: 链名称", "yellow"))
    print(colored("   🔢 chain_id: 链ID", "yellow"))
    print(colored("   🪙 tokens: 代币详情", "yellow"))
    print(colored("   📊 token_count: 币种数量", "yellow"))
    print()

# 输入阶段
if __name__ == "__main__":
    print_banner()
    print_section_header("✍️ 钱包地址输入")
    print(colored("请输入 EVM 钱包地址（只支持单个地址，输入完后两次回车确认）：", "yellow", attrs=["bold"]))
    print(colored("💡 只允许输入一个钱包地址", "blue"))
    input_lines = []
    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            print_error("输入中断，程序退出。")
            exit()
        if line.strip() == '':
            break
        input_lines.append(line)
    wallets = [addr.strip().lower() for addr in input_lines if addr.strip()]
    run_with_wallets(wallets)