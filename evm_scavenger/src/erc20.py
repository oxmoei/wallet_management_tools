import os
import json
import time
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

def print_header():
    """打印优雅的标题"""
    # 打印装饰性分隔线
    print(f"{Fore.YELLOW}✦ ˚ . ⋆   ˚ ✦  ˚  ✦  . ⋆ ˚   ✦  . ⋆ ˚   ✦ ˚ . ⋆   ˚ ✦  ˚  ✦  . ⋆   ˚ ✦  ˚  ✦  . ⋆ ✦ ˚{Style.RESET_ALL}")

    # 打印横幅艺术
    banner_art = [
        "   ▗▄▄▄▖▗▄▄▖  ▗▄▄▖▄▄▄▄ ▄▀▀▚▖     ▗▄▄▖ ▗▄▄▖ ▗▄▖ ▗▖  ▗▖▗▄▄▄▖▗▖  ▗▖ ▗▄▄▖▗▄▄▄▖▗▄▄▖ ",
        "   ▐▌   ▐▌ ▐▌▐▌      █ █  ▐▌    ▐▌   ▐▌   ▐▌ ▐▌▐▌  ▐▌▐▌   ▐▛▚▖▐▌▐▌   ▐▌   ▐▌ ▐▌",
        "   ▐▛▀▀▘▐▛▀▚▖▐▌   █▀▀▀ █  ▐▌     ▝▀▚▖▐▌   ▐▛▀▜▌▐▌  ▐▌▐▛▀▀▘▐▌ ▝▜▌▐▌▝▜▌▐▛▀▀▘▐▛▀▚▖",
        "   ▐▙▄▄▖▐▌ ▐▌▝▚▄▄▖█▄▄▄ ▀▄▄▞▘    ▗▄▄▞▘▝▚▄▄▖▐▌ ▐▌ ▝▚▞▘ ▐▙▄▄▖▐▌  ▐▌▝▚▄▞▘▐▙▄▄▖▐▌ ▐▌",
        "",
    ]
    
    # 打印自定义艺术字
    for line in banner_art:
        if line.strip():
            print(f"{Fore.LIGHTBLUE_EX}{line}{Style.RESET_ALL}")
        else:
            print()
    
    # 打印原有标题
    print(f"{Fore.CYAN}{Fore.GREEN}{'🚀 一键转移各链所有 ERC20 代币'.center(67)}{Fore.CYAN}")
    print(f"{Fore.CYAN}{Fore.YELLOW}{f'Dry-run 模式: {"开启" if dry_run else "关闭"}'.center(71)}{Fore.CYAN}")
    print(f"{Fore.YELLOW}✦ ˚ . ⋆   ˚ ✦  ˚  ✦  . ⋆ ˚   ✦  . ⋆ ˚   ✦ ˚ . ⋆   ˚ ✦  ˚  ✦  . ⋆   ˚ ✦  ˚  ✦  . ⋆ ✦ ˚{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}✨{Fore.LIGHTBLUE_EX}{'─' * 75}{Fore.YELLOW}✨{Style.RESET_ALL}\n")

def print_section_header(title, color=Fore.CYAN):
    """打印章节标题"""
    print(f"\n{color}{'─' * 20} {title} {'─' * 20}{Style.RESET_ALL}")

def print_progress_bar(current, total, prefix="进度", width=40):
    """打印进度条"""
    filled = int(width * current // total)
    bar = '█' * filled + '░' * (width - filled)
    percentage = current / total * 100
    print(f"\r{Fore.CYAN}{prefix}: [{bar}] {percentage:.1f}% ({current}/{total})", end='', flush=True)
    if current == total:
        print()

def print_status(message, status_type="info"):
    """打印状态消息"""
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "loading": "⏳"
    }
    colors = {
        "info": Fore.CYAN,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "loading": Fore.BLUE
    }
    icon = icons.get(status_type, "ℹ️")
    color = colors.get(status_type, Fore.WHITE)
    print(f"{color}{icon} {message}{Style.RESET_ALL}")

def print_token_info(token_name, token_addr, amount, decimals):
    """打印代币信息"""
    print(f"{Fore.GREEN}┌─ 代币信息")
    print(f"{Fore.GREEN}├─ 名称: {Fore.YELLOW}{token_name}")
    print(f"{Fore.GREEN}├─ CA: {Fore.CYAN}{token_addr}")
    print(f"{Fore.GREEN}├─ 数量: {Fore.YELLOW}{amount}")
    print(f"{Fore.GREEN}└─ 精度: {Fore.CYAN}{decimals}{Style.RESET_ALL}")

def print_chain_header(chain_id, rpc_url, chain_idx, total_chains):
    """打印链信息头部"""
    print(f"{Fore.MAGENTA}{'┌' + '─' * 60 + '┐'}")
    print(f"{Fore.MAGENTA}│{Fore.GREEN} 链 {chain_idx}/{total_chains} - ID: {Fore.YELLOW}{chain_id}")
    print(f"{Fore.MAGENTA}│{Fore.CYAN} RPC: {Fore.WHITE}{rpc_url[:50]}{'...' if len(rpc_url) > 50 else ''}{' ' * (54 - min(len(rpc_url), 50))}{Fore.MAGENTA}│")
    print(f"{Fore.MAGENTA}{'└' + '─' * 60 + '┘'}{Style.RESET_ALL}")

def print_summary(total_success, total_fail, total_skip, dry_run):
    """打印总结信息"""
    print(f"\n{Fore.MAGENTA}{'╔' + '═' * 68 + '╗'}")
    print(f"{Fore.MAGENTA}║{Fore.GREEN}{'🎯 执行完成总结'.center(61)}{Fore.MAGENTA}║")
    print(f"{Fore.MAGENTA}{'╠' + '═' * 68 + '╣'}")
    
    # 成功统计
    success_color = Fore.GREEN if total_success > 0 else Fore.WHITE
    print(f"{Fore.MAGENTA}║{success_color} ✅ 成功处理: {total_success:>8} 笔交易{' ' * 39}{Fore.MAGENTA}║")
    
    # 失败统计
    fail_color = Fore.RED if total_fail > 0 else Fore.WHITE
    print(f"{Fore.MAGENTA}║{fail_color} ❌ 处理失败: {total_fail:>8} 笔交易{' ' * 39}{Fore.MAGENTA}║")
    
    # 跳过统计
    skip_color = Fore.YELLOW if total_skip > 0 else Fore.WHITE
    print(f"{Fore.MAGENTA}║{skip_color} ⏫ 跳过处理: {total_skip:>8} 笔交易{' ' * 39}{Fore.MAGENTA}║")
    
    # 总计
    total = total_success + total_fail + total_skip
    print(f"{Fore.MAGENTA}{'╠' + '═' * 68 + '╣'}")
    print(f"{Fore.MAGENTA}║{Fore.CYAN} 📊 总计处理: {total:>8} 笔交易{' ' * 39}{Fore.MAGENTA}║")
    
    # 模式信息
    mode_text = "🔒 模拟模式" if dry_run else "🚀 实际执行"
    mode_color = Fore.YELLOW if dry_run else Fore.GREEN
    print(f"{Fore.MAGENTA}║{mode_color} {mode_text.center(62)}{Fore.MAGENTA}║")
    
    print(f"{Fore.MAGENTA}{'╚' + '═' * 68 + '╝'}{Style.RESET_ALL}\n")

def check_env():
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print_status("未设置 PRIVATE_KEY 环境变量！", "error")
        exit(1)
    to_address_raw = os.getenv('TO_ADDRESS')
    if not to_address_raw:
        print_status("未设置 TO_ADDRESS 环境变量！", "error")
        exit(1)
    try:
        to_address = Web3.to_checksum_address(to_address_raw)
    except Exception:
        print_status(f"TO_ADDRESS 格式不正确: {to_address_raw}", "error")
        exit(1)
    return private_key, to_address

def load_json_file(path, desc):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print_status(f"未找到 {desc} 文件: {path}", "error")
        exit(1)
    except json.JSONDecodeError:
        print_status(f"{desc} 文件格式不正确: {path}", "error")
        exit(1)

def main():
    # 打印启动信息
    print_header()
    
    # 环境检查
    print_section_header("环境变量检查", Fore.BLUE)
    private_key, to_address = check_env()
    account = Account.from_key(private_key)
    from_address = account.address
    
    print_status(f"发送方地址: {Fore.YELLOW}{from_address}{Style.RESET_ALL}", "success")
    print_status(f"接收方地址: {Fore.YELLOW}{to_address}{Style.RESET_ALL}", "success")
    
    # 加载配置文件
    print_section_header("配置文件加载", Fore.BLUE)
    rpc_data = load_json_file(RPC_list_path, 'RPC 列表')
    rpc_info = {str(entry["chain_id"]): entry["rpc_url"] for entry in rpc_data}
    print_status(f"RPC 列表加载成功: {Fore.YELLOW}{len(rpc_data)}{Style.RESET_ALL} 个节点", "success")
    
    chains_data = load_json_file(used_chains_path, 'used_chains')
    if not isinstance(chains_data, list):
        print_status(f"used_chains.json 文件格式不正确: {used_chains_path}", "error")
        exit(1)
    chain_ids = [str(chain.get("chain_id") or chain.get("chainIndex")) for chain in chains_data if chain.get("chain_id") or chain.get("chainIndex")]
    print_status(f"链信息加载成功: {Fore.YELLOW}{len(chain_ids)}{Style.RESET_ALL} 条链", "success")
    
    with open(ERC20_ABI_path) as f:
        erc20_abi = json.load(f)
    print_status("ERC20 ABI 加载成功", "success")
    
    # 开始处理
    print_section_header("♻️ 开始批量处理♻️", Fore.GREEN)
    
    total_success = 0
    total_fail = 0
    total_skip = 0
    
    for chain_idx, chain in enumerate(chains_data, 1):
        try:
            chain_id = chain.get("chain_id") or chain.get("chainIndex")
            chain_id_str = str(chain_id)
            
            if chain_id_str not in rpc_info:
                print_status(f"未在 RPC 列表中找到链 ID: {chain_id}", "warning")
                total_skip += 1
                continue
                
            rpc_url = rpc_info[chain_id_str]
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            nonce = w3.eth.get_transaction_count(from_address)
            
            # 打印链信息头部
            print_chain_header(chain_id, rpc_url, chain_idx, len(chains_data))
            print_status(f"初始 Nonce: {nonce}", "info")
            
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
                print_status(f"链 {chain_id} 未找到有效的 ERC20 token，跳过\n", "warning")
                total_skip += 1
                continue
                
            print_status(f"发现 {len(erc20_tokens_list)} 个代币需要处理", "info")
            
            # 处理代币
            for token_idx, token_addr in enumerate(erc20_tokens_list, 1):
                try:
                    # 显示进度
                    print_progress_bar(token_idx, len(erc20_tokens_list), f"处理代币 {token_idx}/{len(erc20_tokens_list)}")
                    
                    token = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=erc20_abi)
                    
                    try:
                        name = token.functions.name().call()
                        decimals = token.functions.decimals().call()
                        human_amount = asset_balances[token_addr]
                        balance = int(human_amount * (10 ** decimals))
                    except Exception as e:
                        print_status(f"获取代币 {token_addr} 信息失败: {e}", "warning")
                        total_skip += 1
                        continue
                        
                    if balance > 0:
                        gas_price = w3.eth.gas_price
                        
                        # 打印代币信息
                        print(f"\n{Fore.GREEN}🎯 处理代币 {token_idx}/{len(erc20_tokens_list)}")
                        print_token_info(name, token_addr, human_amount, decimals)
                        
                        try:
                            estimated_gas = token.functions.transfer(to_address, balance).estimate_gas({'from': from_address})
                        except Exception as e:
                            print_status(f"估算 gas 失败，使用默认值 100,000。错误: {e}", "warning")
                            estimated_gas = 100000
                            
                        tx = token.functions.transfer(to_address, balance).build_transaction({
                            'nonce': nonce,
                            'gasPrice': gas_price,
                            'gas': estimated_gas,
                            'chainId': chain_id
                        })
                        
                        if dry_run:
                            print_status(f"模拟转账 {human_amount} {name} (未发送)", "success")
                            nonce += 1
                            print_status(f"Nonce 递增至: {nonce}\n", "info")
                            total_success += 1
                        else:
                            signed = w3.eth.account.sign_transaction(tx, private_key)
                            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                            print_status(f"成功转账 {name}！交易哈希: {w3.to_hex(tx_hash)}", "success")
                            nonce += 1
                            print_status(f"Nonce 递增至: {nonce}\n", "info")
                            total_success += 1
                    else:
                        total_skip += 1
                        
                except Exception as e:
                    print_status(f"处理代币 {token_addr} 失败: {e}\n", "error")
                    total_fail += 1
                    
            print()  # 空行分隔
            time.sleep(0.5)  # 短暂延迟，让输出更清晰
            
        except Exception as e:
            print_status(f"处理链 {chain_id_str} 失败: {e}", "error")
            total_fail += 1
    
    # 打印总结
    print_summary(total_success, total_fail, total_skip, dry_run)

if __name__ == "__main__":
    main()
