import os
import json
import logging
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
from colorama import Fore, Style, init

# ========== 初始化 ==========
init(autoreset=True)

# 获取脚本文件所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 指定 .env 文件的完整路径加载环境变量
load_dotenv(dotenv_path=os.path.join(script_dir, '.env'))

# Dry-run 模式开关
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# 日志记录开关
ENABLE_LOG = os.getenv("ENABLE_LOG", "true").lower() == "true"
if ENABLE_LOG:
    logging.basicConfig(filename='/home/lighthouse/work/工具/钱包资产迁移/EVM系/transfer.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# ========== 读取环境变量 ==========
private_key = os.getenv('PRIVATE_KEY')
to_address = Web3.to_checksum_address(os.getenv('TO_ADDRESS'))

account = Account.from_key(private_key)
from_address = account.address

# ========== 加载链信息与 ABI ==========
# 加载 RPC URL 和 ERC20 token 地址
rpc_lists_path = '/home/lighthouse/work/工具/钱包资产迁移/EVM系/RPC_list.json'
ca_lists_path = '/home/lighthouse/work/工具/钱包资产迁移/EVM系/@CA_list.json'

rpc_info = {}
try:
    with open(rpc_lists_path) as f:
        rpc_data = json.load(f)
        for entry in rpc_data:
            rpc_info[str(entry["chain_id"])] = entry["rpc_url"]
except FileNotFoundError:
    print(f"{Fore.RED}错误: 未找到 RPC 列表文件: {rpc_lists_path}{Style.RESET_ALL}")
    exit()
except json.JSONDecodeError:
    print(f"{Fore.RED}错误: RPC 列表文件格式不正确: {rpc_lists_path}{Style.RESET_ALL}")
    exit()

ca_info = []
chain_ids = []
try:
    with open(ca_lists_path) as f:
        ca_data = json.load(f)
        if ca_data and "data" in ca_data and isinstance(ca_data["data"], list) and len(ca_data["data"]) > 0:
            for entry in ca_data["data"]:
                if "chains" in entry and isinstance(entry["chains"], list):
                    ca_info.extend(entry["chains"])
            if len(ca_info) == 0:
                print(f"{Fore.RED}错误: CA 列表文件格式不正确或为空: {ca_lists_path}{Style.RESET_ALL}")
                exit()
            chain_ids = [str(chain.get("chainIndex")) for chain in ca_info if "chainIndex" in chain]
            print(f"{Fore.GREEN}成功从 @CA_lists.json 加载 {len(chain_ids)} 条链信息{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}错误: CA 列表文件格式不正确或为空: {ca_lists_path}{Style.RESET_ALL}")
            exit()
except FileNotFoundError:
    print(f"{Fore.RED}错误: 未找到 CA 列表文件: {ca_lists_path}{Style.RESET_ALL}")
    exit()
except json.JSONDecodeError:
    print(f"{Fore.RED}错误: CA 列表文件格式不正确: {ca_lists_path}{Style.RESET_ALL}")
    exit()

# 调试输出，确认解析结果
print('DEBUG ca_info:', ca_info)
print('DEBUG chain_ids:', chain_ids)

with open('/home/lighthouse/work/工具/钱包资产迁移/EVM系/ERC20_ABI.json') as f:
    erc20_abi = json.load(f)

# ========== 主逻辑开始 ==========
print(f"\n{Fore.CYAN}{'='*40}")
print(f"🚀 批量资产转移脚本启动！（Dry-run: {DRY_RUN}）")
print(f"📜 加载 {len(chain_ids)} 条链信息")
print(f"💰 当前账户地址: {from_address}")
print(f"{'='*40}{Style.RESET_ALL}\n")

for chain in ca_info:
    try:
        chain_id = chain.get("chainIndex")
        chain_id_str = str(chain_id)
        # 从 rpc_info 获取 RPC URL
        if chain_id_str not in rpc_info:
            print(f"{Fore.RED}❌ 未在 RPC 列表中找到链 ID: {chain_id}{Style.RESET_ALL}")
            continue

        rpc_url = rpc_info[chain_id_str]
        w3 = Web3(Web3.HTTPProvider(rpc_url))

        # 获取当前地址在该链上的 Nonce
        nonce = w3.eth.get_transaction_count(from_address)
        print(f"获取初始 Nonce: {nonce}")

        # 获取 ERC20 token 地址列表（只取 tokenAddress 非空且 balance > 0 的资产）
        erc20_tokens_list = []
        asset_balances = {}  # 新增：记录每个 token 的人类可读 balance
        for asset in chain.get("assets", []):
            token_addr = asset.get("tokenAddress")
            balance_str = asset.get("balance", "0")
            try:
                balance_float = float(balance_str)
            except Exception:
                balance_float = 0
            if token_addr and balance_float > 0:
                erc20_tokens_list.append(token_addr)
                asset_balances[token_addr] = balance_float  # 记录人类可读 balance
        if not erc20_tokens_list:
            print(f"{Fore.YELLOW}⚠️ 未在 CA 列表中找到链 ID {chain_id} 的 ERC20 token 地址，跳过 ERC20 转账。{Style.RESET_ALL}")

        print(f"{Fore.BLUE}{'='*50}")
        print(f"🔵 正在处理链 {chain_id}（{rpc_url}）")
        print(f"{'='*50}{Style.RESET_ALL}")

        # ========== ERC20 转账 ==========
        # 使用从 CA 文件中获取的 token 地址列表
        for token_addr in erc20_tokens_list:
            try: # 添加 try 块处理单个 token 转账失败
                token = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=erc20_abi)
                # 使用 call() 获取链上信息，可能因 RPC 不稳定或合约不存在失败
                try:
                    name = token.functions.name().call()
                    decimals = token.functions.decimals().call()
                    # balance = token.functions.balanceOf(from_address).call()  # 原链上 balance
                    # 新：balance 取自 CA_list.json，需转为链上单位
                    human_amount = asset_balances[token_addr]
                    balance = int(human_amount * (10 ** decimals))
                except Exception as e:
                    print(f"{Fore.YELLOW}跳过 token {token_addr}: 获取链上信息失败 - {e}{Style.RESET_ALL}")
                    if ENABLE_LOG:
                         logging.warning(f"Skip token {token_addr} on chain {chain_id}: Failed to get on-chain info - {str(e)}")
                    continue # 跳过当前 token

                if balance > 0:
                    # human_amount = balance / (10 ** decimals)  # 已在上面获得
                    gas_price = w3.eth.gas_price

                    print(f"{Fore.YELLOW}⚡ 发现 {human_amount} {name} ({token_addr})，准备转出...{Style.RESET_ALL}")

                    try:
                        estimated_gas = token.functions.transfer(to_address, balance).estimate_gas({'from': from_address})
                    except Exception as e:
                        print(f"{Fore.YELLOW}警告: 估算 gas 失败，使用 fallback 值。错误: {e}{Style.RESET_ALL}")
                        estimated_gas = 100000  # fallback

                    tx = token.functions.transfer(to_address, balance).build_transaction({
                        'nonce': nonce, # 使用当前的 nonce
                        'gasPrice': gas_price,
                        'gas': estimated_gas,
                        'chainId': chain_id # 直接使用 int 类型的 chain_id
                    })

                    if DRY_RUN:
                        print(f"📝 模拟转账 {human_amount} {name} ({token_addr})（未发送）{Style.RESET_ALL}")
                        # Dry-run 也应该递增 nonce，以便后续模拟交易 Nonce 正确
                        nonce += 1
                        print(f"Dry-run 模拟转账后 Nonce 递增至: {nonce}")
                    else:
                        signed = w3.eth.account.sign_transaction(tx, private_key)
                        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                        print(f"{Fore.GREEN}✅ 成功转账 {name} ({token_addr})！交易哈希: {w3.to_hex(tx_hash)}{Style.RESET_ALL}")
                        if ENABLE_LOG:
                            logging.info(f"Transferred {human_amount} {name} ({token_addr}) on chain {chain_id}, tx: {w3.to_hex(tx_hash)}")
                        # 成功发送交易后递增 nonce
                        nonce += 1
                        print(f"成功转账后 Nonce 递增至: {nonce}")
            except Exception as e:
                print(f"{Fore.RED}❌ 处理 token {token_addr} 失败: {e}{Style.RESET_ALL}")
                if ENABLE_LOG:
                    logging.error(f"Token {token_addr} on chain {chain_id} processing failed: {str(e)}")

    except Exception as e:
        print(f"{Fore.RED}❌ 处理链 {chain_id_str} 失败: {e}{Style.RESET_ALL}")
        if ENABLE_LOG:
            logging.error(f"链 {chain_id_str} 处理失败: {str(e)}")

print(f"\n{Fore.CYAN}{'='*40}")
print(f"🚀 所有链处理完成")
print(f"{'='*40}{Style.RESET_ALL}")
