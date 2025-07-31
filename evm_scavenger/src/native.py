import os
import json
from web3 import Web3
# from web3.middleware.geth_poa import geth_poa_middleware
from eth_account import Account
from dotenv import load_dotenv
from colorama import Fore, Style, init

# ========== 常量与初始化 ==========
init(autoreset=True)

# 特殊链 gasLimit 覆盖
SPECIAL_GAS = {
    42161: 70000,   # Arbitrum
    5000: 100000,   # Mantle
    324: 70000,     # zkSync
    204: 70000,     # opBNB
    534352: 70000,  # Scroll
    10: 70000,      # Optimism
    59144: 70000,   # Linea
    8453: 70000,    # Base
}

# ========== 工具函数 ==========
def load_json(path, desc):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}❌ 错误: 未找到{desc}文件: {path}{Style.RESET_ALL}")
        exit()
    except json.JSONDecodeError:
        print(f"{Fore.RED}❌ 错误: {desc}文件格式不正确: {path}{Style.RESET_ALL}")
        exit()

def check_env(var, desc):
    val = os.getenv(var)
    if not val:
        print(f"{Fore.RED}❌ 错误: 缺少环境变量 {var}（{desc}）{Style.RESET_ALL}")
        exit()
    return val

# ========== 主链处理逻辑 ==========
def process_chain(chain_id_str, rpc_info, from_address, to_address, private_key, dry_run, enable_log):
    try:
        chain_id = int(chain_id_str)
        if chain_id_str not in rpc_info:
            print(f"\n{Fore.RED}❌ 未在 RPC 列表中找到链 ID: {chain_id}{Style.RESET_ALL}")
            return
        rpc_url = rpc_info[chain_id_str]
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        # w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        nonce = w3.eth.get_transaction_count(from_address)
        balance = w3.eth.get_balance(from_address)
        # ====== 动态估算 gasLimit ======
        tx_for_gas = {'from': from_address, 'to': to_address, 'value': 1}
        try:
            estimated_gas = w3.eth.estimate_gas(tx_for_gas)
            gas_limit = int(estimated_gas * 1.1)
        except Exception:
            gas_limit = 21000
        gas_limit = SPECIAL_GAS.get(chain_id, gas_limit)
        # ====== 动态适配 EIP-1559 参数 ======
        supports_eip1559 = False
        try:
            latest_block = w3.eth.get_block('latest')
            if 'baseFeePerGas' in latest_block:
                supports_eip1559 = True
        except:
            pass
        tx = {'nonce': nonce, 'to': to_address, 'chainId': chain_id}
        if supports_eip1559:
            max_priority_fee = w3.to_wei(1.5, 'gwei')
            base_fee = w3.eth.gas_price
            max_fee = base_fee + max_priority_fee
            tx.update({'gas': gas_limit, 'maxFeePerGas': max_fee, 'maxPriorityFeePerGas': max_priority_fee})
            eth_gas_cost = int(gas_limit * max_fee * 1.05)
        else:
            gas_price = w3.eth.gas_price
            tx.update({'gas': gas_limit, 'gasPrice': gas_price})
            eth_gas_cost = int(gas_limit * gas_price * 1.05)
        if balance > eth_gas_cost:
            value = balance - eth_gas_cost
            tx['value'] = value
            if dry_run:
                print(f"\n{Fore.GREEN}🔜 模拟转账 {w3.from_wei(value, 'ether')}（未发送）{Style.RESET_ALL}")
                print(f"Dry-run 模拟转账后 Nonce 递增至: {nonce+1}\n")
            else:
                signed = w3.eth.account.sign_transaction(tx, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                print(f"\n{Fore.GREEN}✅ 成功转出！交易哈希: {w3.to_hex(tx_hash)}{Style.RESET_ALL}")
                print(f"成功转出后 Nonce 递增至: {nonce+1}\n")
        else:
            print(f"\n{Fore.RED}⚠️ 余额 ({w3.from_wei(balance, 'ether')}) 不足支付 gas ({w3.from_wei(eth_gas_cost, 'ether')})，跳过转账{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"\n{Fore.RED}❌ 处理链 {chain_id_str} 失败: {e}{Style.RESET_ALL}\n")

# ========== 主程序入口 ==========
def main():
    # 获取脚本文件所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    load_dotenv(dotenv_path=os.path.join(parent_dir, '.env'))
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    private_key = check_env('PRIVATE_KEY', '私钥')
    to_address = Web3.to_checksum_address(check_env('TO_ADDRESS', '目标地址'))
    account = Account.from_key(private_key)
    from_address = account.address
    rpc_lists_path = os.path.join(parent_dir, 'conf', 'RPC_list.json')
    used_chains_path = os.path.join(parent_dir, 'conf', 'used_chains.json')
    rpc_data = load_json(rpc_lists_path, 'RPC 列表')
    rpc_info = {str(entry["chain_id"]): entry["rpc_url"] for entry in rpc_data}
    used_chains_data = load_json(used_chains_path, 'used_chains')
    if not (isinstance(used_chains_data, list) and len(used_chains_data) > 0 and "chain_id" in used_chains_data[0]):
        print(f"\n{Fore.RED}❌ 错误: used_chains.json 文件格式不正确或为空: {used_chains_path}{Style.RESET_ALL}\n")
        exit()
    chain_ids = [str(chain['chain_id']) for chain in used_chains_data]
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"\033[7m{Fore.GREEN}🚀 原生币转移脚本启动！🚀（Dry-run: {dry_run}）{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}⛓️ 成功加载 {Fore.YELLOW}{len(chain_ids)}{Fore.CYAN} 条链信息")
    print(f"{Fore.CYAN}🏠 当前账户地址: {Fore.YELLOW}{from_address}")
    print(f"{Fore.CYAN}🏦 目标账户地址: {Fore.YELLOW}{to_address}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
    success_count = 0
    fail_count = 0
    for idx, chain_id_str in enumerate(chain_ids, 1):
        nonce = None
        try:
            chain_id = int(chain_id_str)
            if chain_id_str not in rpc_info:
                print(f"\n{Fore.RED}❌ 未在 RPC 列表中找到链 ID: {chain_id}{Style.RESET_ALL}\n")
                fail_count += 1
                continue
            rpc_url = rpc_info[chain_id_str]
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            nonce = w3.eth.get_transaction_count(from_address)
            print(f"{Fore.RED}[{idx}/{len(chain_ids)}] {Fore.YELLOW}获取初始 Nonce: {nonce}")
            print(f"{Fore.YELLOW}{'='*50}")
            print(f"{Fore.YELLOW}⏳ 正在处理链 {chain_id}（{rpc_url}）")
            print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ 获取链 {chain_id_str} Nonce 或 RPC 失败: {e}{Style.RESET_ALL}\n")
            fail_count += 1
            continue
        try:
            process_chain(chain_id_str, rpc_info, from_address, to_address, private_key, dry_run, False)
            success_count += 1
        except Exception:
            fail_count += 1
    print(f"{Fore.MAGENTA}{'='*40}")
    print(f"\033[7m{Fore.GREEN}🔆 所有链处理完成！（Dry-run: {dry_run}）{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ 成功: {success_count}，{Fore.RED}❌ 失败: {fail_count}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
