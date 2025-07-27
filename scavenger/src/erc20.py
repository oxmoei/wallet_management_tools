import os
import json
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
from colorama import Fore, Style, init

# ========== 初始化 ==========
init(autoreset=True)

# 路径统一获取
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
conf_dir = os.path.join(parent_dir, 'conf')
RPC_list_path = os.path.join(conf_dir, 'RPC_list.json')
used_chains_path = os.path.join(conf_dir, 'used_chains.json')
ERC20_ABI_path = os.path.join(conf_dir, 'ERC20_ABI.json')
env_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path=env_path)

# Dry-run 模式开关
dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

def check_env():
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print(f"{Fore.RED}⚠️ 未设置 PRIVATE_KEY 环境变量！{Style.RESET_ALL}")
        exit(1)
    to_address_raw = os.getenv('TO_ADDRESS')
    if not to_address_raw:
        print(f"{Fore.RED}⚠️ 未设置 TO_ADDRESS 环境变量！{Style.RESET_ALL}")
        exit(1)
    try:
        to_address = Web3.to_checksum_address(to_address_raw)
    except Exception:
        print(f"{Fore.RED}❌ TO_ADDRESS 格式不正确: {to_address_raw}{Style.RESET_ALL}")
        exit(1)
    return private_key, to_address

def load_json_file(path, desc):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}❌ 错误: 未找到 {desc} 文件: {path}{Style.RESET_ALL}")
        exit(1)
    except json.JSONDecodeError:
        print(f"{Fore.RED}❌ 错误: {desc} 文件格式不正确: {path}{Style.RESET_ALL}")
        exit(1)

def main():
    private_key, to_address = check_env()
    account = Account.from_key(private_key)
    from_address = account.address

    rpc_data = load_json_file(RPC_list_path, 'RPC 列表')
    rpc_info = {str(entry["chain_id"]): entry["rpc_url"] for entry in rpc_data}

    chains_data = load_json_file(used_chains_path, 'used_chains')
    if not isinstance(chains_data, list):
        print(f"{Fore.RED}❌ used_chains.json 文件格式不正确: {used_chains_path}{Style.RESET_ALL}")
        exit(1)
    chain_ids = [str(chain.get("chain_id") or chain.get("chainIndex")) for chain in chains_data if chain.get("chain_id") or chain.get("chainIndex")]
    print(f"{Fore.GREEN}🔆 成功加载 {len(chain_ids)} 条链信息{Style.RESET_ALL}")

    with open(ERC20_ABI_path) as f:
        erc20_abi = json.load(f)

    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"\033[7m{Fore.GREEN}🚀 批量 ERC20 转移脚本启动！🚀（Dry-run: {dry_run}）{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}⛓️ 成功加载 {Fore.YELLOW}{len(chain_ids)}{Fore.CYAN} 条链信息")
    print(f"{Fore.CYAN}🏠 当前账户地址: {Fore.YELLOW}{from_address}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")

    total_success = 0
    total_fail = 0
    total_skip = 0
    chain_idx = 0
    for chain in chains_data:
        chain_idx += 1
        try:
            chain_id = chain.get("chain_id") or chain.get("chainIndex")
            chain_id_str = str(chain_id)
            if chain_id_str not in rpc_info:
                print(f"{Fore.RED}❌ 未在 RPC 列表中找到链 ID: {chain_id}{Style.RESET_ALL}\n")
                total_skip += 1
                continue
            rpc_url = rpc_info[chain_id_str]
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            nonce = w3.eth.get_transaction_count(from_address)
            print(f"[{chain_idx}/{len(chain_ids)}] 获取初始 Nonce: {nonce}")
            # 获取 ERC20 token 地址列表
            erc20_tokens_list = []
            asset_balances = {}
            for token in chain.get("tokens", []):
                token_addr = token.get("address")
                amount = token.get("amount", 0)
                try:
                    amount_float = float(amount)
                except Exception:
                    amount_float = 0
                if token_addr and amount_float > 0 and str(token_addr).startswith("0x"):
                    erc20_tokens_list.append(token_addr)
                    asset_balances[token_addr] = amount_float
            if not erc20_tokens_list:
                print(f"{Fore.RED}⚠️ 未在 tokens 组中找到链 ID {chain_id} 的 ERC20 token 地址，跳过 ERC20 转账。{Style.RESET_ALL}\n")
                total_skip += 1
                continue
            print(f"{Fore.YELLOW}{'='*50}")
            print(f"{Fore.YELLOW}⏳ 正在处理链 {chain_id}（{rpc_url}）")
            print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}\n")
            token_idx = 0
            for token_addr in erc20_tokens_list:
                token_idx += 1
                try:
                    token = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=erc20_abi)
                    try:
                        name = token.functions.name().call()
                        decimals = token.functions.decimals().call()
                        human_amount = asset_balances[token_addr]
                        balance = int(human_amount * (10 ** decimals))
                    except Exception as e:
                        print(f"{Fore.RED}⚠️ 跳过 token {token_addr}: 获取链上信息失败 - {e}{Style.RESET_ALL}\n")
                        total_skip += 1
                        continue
                    if balance > 0:
                        gas_price = w3.eth.gas_price
                        print(f"{Fore.GREEN}⚡ 发现 {human_amount} {name} ({token_addr})，准备转出...{Style.RESET_ALL}")
                        try:
                            estimated_gas = token.functions.transfer(to_address, balance).estimate_gas({'from': from_address})
                        except Exception as e:
                            print(f"{Fore.YELLOW}⚠️ 提醒: 估算 gas 失败，使用 {Fore.CYAN}fallback值{Fore.YELLOW}。错误: {e}{Style.RESET_ALL}\n")
                            estimated_gas = 100000
                        tx = token.functions.transfer(to_address, balance).build_transaction({
                            'nonce': nonce,
                            'gasPrice': gas_price,
                            'gas': estimated_gas,
                            'chainId': chain_id
                        })
                        if dry_run:
                            print(f"{Fore.GREEN}🔜 模拟转账 {human_amount} {name} ({token_addr})（未发送）{Style.RESET_ALL}")
                            nonce += 1
                            print(f"Dry-run 模拟转账后 Nonce 递增至: {nonce}\n")
                            total_success += 1
                        else:
                            signed = w3.eth.account.sign_transaction(tx, private_key)
                            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                            print(f"{Fore.GREEN}✅ 成功转账 {name} ({token_addr})！交易哈希: {w3.to_hex(tx_hash)}{Style.RESET_ALL}")
                            nonce += 1
                            print(f"成功转账后 Nonce 递增至: {nonce}\n")
                            total_success += 1
                    else:
                        total_skip += 1
                except Exception as e:
                    print(f"{Fore.RED}❌ 处理 token {token_addr} 失败: {e}{Style.RESET_ALL}\n")
                    total_fail += 1
        except Exception as e:
            print(f"{Fore.RED}❌ 处理链 {chain_id_str} 失败: {e}{Style.RESET_ALL}\n")
            total_fail += 1
    print(f"{Fore.MAGENTA}{'='*40}")
    print(f"\033[7m{Fore.GREEN}🔆 所有链处理完成！（Dry-run: {dry_run}）{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ 成功: {total_success}，{Fore.RED}❌ 失败: {total_fail}，{Fore.YELLOW}⏫ 跳过: {total_skip}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
