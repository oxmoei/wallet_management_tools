import os
import requests
import json
from solders.pubkey import Pubkey as PublicKey
from solders.keypair import Keypair
from solders.message import Message as SoldersMessage
from solders.transaction import Transaction as SoldersTransaction
from solders.hash import Hash
from spl.token.instructions import transfer_checked, get_associated_token_address, TransferCheckedParams
from spl.token.constants import TOKEN_PROGRAM_ID
from dotenv import load_dotenv
from colorama import init, Fore, Style

# ========== 初始化 ==========
init(autoreset=True)

# 获取脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')

# 加载.env配置
load_dotenv(env_path)

# 读取配置
RPC_URL = os.getenv("RPC_URL", "").strip()
TO_ADDRESS = os.getenv("TO_ADDRESS")
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

def print_header():
    """打印优雅的标题"""
    
    # 打印横幅艺术字
    print(f"{Fore.YELLOW}✦ ˚ . ⋆   ˚ ✦  ˚  ✦  . ⋆ ˚   ✦  . ⋆ ˚   ✦ ˚ . ⋆   ˚ ✦  ˚  ✦  . ⋆   ˚ ✦  ˚  ✦  . ⋆ ✦ ˚{Style.RESET_ALL}")
    banner_art = [
        "     ▗▄▄▖▗▄▄▖ ▗▖        ▗▄▄▖ ▗▄▄▖ ▗▄▖ ▗▖  ▗▖▗▄▄▄▖▗▖  ▗▖ ▗▄▄▖▗▄▄▄▖▗▄▄▖ ",
        "    ▐▌   ▐▌ ▐▌▐▌       ▐▌   ▐▌   ▐▌ ▐▌▐▌  ▐▌▐▌   ▐▛▚▖▐▌▐▌   ▐▌   ▐▌ ▐▌",
        "     ▝▀▚▖▐▛▀▘ ▐▌        ▝▀▚▖▐▌   ▐▛▀▜▌▐▌  ▐▌▐▛▀▀▘▐▌ ▝▜▌▐▌▝▜▌▐▛▀▀▘▐▛▀▚▖",
        "    ▗▄▄▞▘▐▌   ▐▙▄▄▖    ▗▄▄▞▘▝▚▄▄▖▐▌ ▐▌ ▝▚▞▘ ▐▙▄▄▖▐▌  ▐▌▝▚▄▞▘▐▙▄▄▖▐▌ ▐▌",
        "",
    ]
    
    # 打印自定义艺术字
    for line in banner_art:
        if line.strip():
            print(f"{Fore.LIGHTBLUE_EX}{line}{Style.RESET_ALL}")
        else:
            print()
    
    # 打印原有标题
    print(f"{Fore.CYAN}{Fore.GREEN}{'💸 一键转移所有 SPL Token '.center(70)}{Fore.CYAN}")
    print(f"{Fore.CYAN}{Fore.YELLOW}{f'Dry-run 模式: {"开启" if DRY_RUN else "关闭"}'.center(70)}{Fore.CYAN}")
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

def print_wallet_header(wallet_address, wallet_idx, total_wallets):
    """打印钱包信息头部"""
    print(f"{Fore.MAGENTA}{'┌' + '─' * 63 + '┐'}")
    print(f"{Fore.MAGENTA}│{Fore.GREEN} 钱包 {wallet_idx}/{total_wallets} - 地址: {Fore.YELLOW}{wallet_address}")
    print(f"{Fore.MAGENTA}{'└' + '─' * 63 + '┘'}{Style.RESET_ALL}")

def print_token_info(token_mint, amount, decimals):
    """打印代币信息"""
    amount_float = amount / (10 ** decimals)
    print(f"{Fore.GREEN}┌─ 代币信息")
    print(f"{Fore.GREEN}├─ Mint: {Fore.CYAN}{token_mint}")
    print(f"{Fore.GREEN}├─ 数量: {Fore.YELLOW}{amount_float}")
    print(f"{Fore.GREEN}└─ 精度: {Fore.CYAN}{decimals}{Style.RESET_ALL}")

def print_summary(total_success, total_fail, total_wallets, dry_run):
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
    
    # 钱包统计
    wallet_color = Fore.CYAN if total_wallets > 0 else Fore.WHITE
    print(f"{Fore.MAGENTA}║{wallet_color} 🏠 处理钱包: {total_wallets:>8} 个钱包{' ' * 39}{Fore.MAGENTA}║")
    
    # 总计
    total = total_success + total_fail
    print(f"{Fore.MAGENTA}{'╠' + '═' * 68 + '╣'}")
    print(f"{Fore.MAGENTA}║{Fore.CYAN} 📊 总计处理: {total:>8} 笔交易{' ' * 39}{Fore.MAGENTA}║")
    
    # 模式信息
    mode_text = "🔒 模拟模式" if dry_run else "🚀 实际执行"
    mode_color = Fore.YELLOW if dry_run else Fore.GREEN
    print(f"{Fore.MAGENTA}║{mode_color} {mode_text.center(62)}{Fore.MAGENTA}║")
    
    print(f"{Fore.MAGENTA}{'╚' + '═' * 68 + '╝'}{Style.RESET_ALL}\n")

# 验证配置
if not RPC_URL:
    print_status("RPC_URL 配置为空或无效", "error")
    print(f"请在 .env 文件中正确配置 RPC_URL，例如:")
    print(f"RPC_URL=https://api.mainnet-beta.solana.com")
    exit(1)

if not TO_ADDRESS:
    print_status("TO_ADDRESS 配置为空", "error")
    print(f"请在 .env 文件中配置 TO_ADDRESS")
    exit(1)

# 自动收集所有私钥，并推导钱包地址
PRIVATE_KEYS = {}
for k, v in os.environ.items():
    if k.startswith("PRIVATE_KEY_") and v.strip():
        try:
            keypair = Keypair.from_base58_string(v.strip())
            pubkey = str(keypair.pubkey())
            PRIVATE_KEYS[pubkey] = v.strip()
        except Exception as e:
            print_status(f"无法解析私钥 {k}: {e}", "warning")

if not PRIVATE_KEYS:
    print_status("未找到有效的私钥配置", "error")
    print(f"请在 .env 文件中配置 PRIVATE_KEY_1, PRIVATE_KEY_2 等")
    exit(1)

from solana.rpc.api import Client
client = Client(RPC_URL)

def get_all_token_accounts(owner_address):
    """返回owner_address下所有SPL Token账户的ATA和mint"""
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            owner_address,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
    }
    try:
        resp = requests.post(RPC_URL, headers=headers, data=json.dumps(data), timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if "result" in result and "value" in result["result"]:
            accounts = []
            for acc in result["result"]["value"]:
                if "account" in acc and "data" in acc["account"] and "parsed" in acc["account"]["data"] and "info" in acc["account"]["data"]["parsed"] and "tokenAmount" in acc["account"]["data"]["parsed"]["info"]:
                     ata = acc["pubkey"]
                     mint = acc["account"]["data"]["parsed"]["info"]["mint"]
                     amount = int(acc["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])
                     accounts.append({"ata": ata, "mint": mint, "amount": amount})
            print_status(f"获取到 {len(accounts)} 个Token账户\n", "success")
            return accounts
        else:
             print_status(f"获取账户信息成功，但返回结果结构异常", "warning")
    except requests.exceptions.Timeout:
        print_status(f"获取账户信息超时（RPC: {RPC_URL}）", "warning")
    except requests.exceptions.RequestException as e:
        print_status(f"获取账户信息失败（RPC: {RPC_URL}）: {e}", "error")
    except Exception as e:
        print_status(f"处理账户信息响应失败（RPC: {RPC_URL}）: {e}", "error")
    print_status(f"无法获取 {owner_address} 的账户信息", "error")
    return []

def get_token_decimals(token_mint):
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenSupply",
        "params": [token_mint]
    }
    try:
        resp = requests.post(RPC_URL, headers=headers, data=json.dumps(data), timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if "result" in result and "value" in result["result"] and "decimals" in result["result"]["value"]:
            decimals = result["result"]["value"]["decimals"]
            return decimals
        else:
             print_status(f"获取代币精度成功，但返回结果结构异常", "warning")
    except requests.exceptions.Timeout:
        print_status(f"获取代币精度超时（RPC: {RPC_URL}）", "warning")
    except requests.exceptions.RequestException as e:
        print_status(f"获取代币精度失败（RPC: {RPC_URL}）: {e}", "error")
    except Exception as e:
        print_status(f"处理代币精度响应失败（RPC: {RPC_URL}）: {e}", "error")
    print_status(f"无法获取代币 {token_mint} 的精度", "error")
    raise Exception(f"无法获取代币 {token_mint} 的精度")

def send_token(from_address, private_key, to_address, amount, token_mint, decimals):
    """
    amount: 支持小数（如1.23），内部自动转换为整数
    decimals: 代币精度，外部传入
    返回True表示成功，False表示失败
    """
    amount_float = float(amount)
    amount_int = int(round(amount_float * (10 ** decimals)))
    from_keypair = Keypair.from_base58_string(private_key)
    from_pubkey = PublicKey.from_string(from_address)
    to_pubkey = PublicKey.from_string(to_address)
    mint_pubkey = PublicKey.from_string(token_mint)
    from_ata = get_associated_token_address(from_pubkey, mint_pubkey)
    to_ata = get_associated_token_address(to_pubkey, mint_pubkey)

    ix = transfer_checked(
        TransferCheckedParams(
            program_id=TOKEN_PROGRAM_ID,
            source=from_ata,
            mint=mint_pubkey,
            dest=to_ata,
            owner=from_pubkey,
            amount=amount_int,
            decimals=decimals,
            signers=[]
        )
    )

    recent_blockhash = None
    try:
        client = Client(RPC_URL)
        blockhash_resp = client.get_latest_blockhash()
        if hasattr(blockhash_resp, 'value') and hasattr(blockhash_resp.value, 'blockhash'):
            recent_blockhash = blockhash_resp.value.blockhash
        elif isinstance(blockhash_resp, dict):
            recent_blockhash = blockhash_resp["result"]["value"]["blockhash"]
        else:
            print_status(f"获取区块哈希成功，但返回结果结构异常", "warning")
        if isinstance(recent_blockhash, str):
            recent_blockhash = Hash.from_string(recent_blockhash)
    except Exception as e:
        print_status(f"获取最新区块哈希失败（RPC: {RPC_URL}）: {e}", "error")
        return False

    if recent_blockhash is None:
        print_status(f"无法获取最新区块哈希", "error")
        return False

    tx = SoldersTransaction([from_keypair], SoldersMessage([ix], from_pubkey), recent_blockhash)

    tx_sig = None
    try:
        client = Client(RPC_URL)
        raw_tx = bytes(tx)
        if DRY_RUN:
            print_status(f"\n模拟转账 {amount_float} 个 {token_mint} (未发送)", "success")
            return True
        resp = client.send_raw_transaction(raw_tx)
        if hasattr(resp, 'value'):
            tx_sig = resp.value
        elif isinstance(resp, dict):
            tx_sig = resp.get("result")
        else:
            tx_sig = str(resp)
        print_status(f"\nSPL Token转账成功: {tx_sig}", "success")
        return True
    except Exception as e:
        print_status(f"\n发送SPL Token转账失败（RPC: {RPC_URL}）: {e}", "error")
    print_status(f"\n无法发送SPL Token转账", "error")
    return False

if __name__ == "__main__":
    # 打印启动信息
    print_header()
    
    # 环境检查
    print_section_header("环境变量检查", Fore.BLUE)
    print_status(f"RPC URL: {RPC_URL}", "success")
    print_status(f"目标地址: {Fore.YELLOW}{TO_ADDRESS}{Style.RESET_ALL}", "success")
    print_status(f"已加载 {Fore.YELLOW}{len(PRIVATE_KEYS)}{Fore.GREEN} 个私钥", "success")
    
    # 开始处理
    print_section_header("♻️ 开始批量处理♻️", Fore.GREEN)
    
    total_success = 0
    total_fail = 0
    
    for wallet_idx, (owner_address, privkey) in enumerate(PRIVATE_KEYS.items(), 1):
        # 打印钱包信息头部
        print_wallet_header(owner_address, wallet_idx, len(PRIVATE_KEYS))
        
        accounts = get_all_token_accounts(owner_address)
        if not accounts:
            print_status(f"钱包 {owner_address} 没有SPL Token账户", "warning")
            print()
            continue
            
        # 过滤有余额的代币
        valid_accounts = [acc for acc in accounts if acc["amount"] > 0]
        if not valid_accounts:
            print_status(f"钱包 {owner_address} 没有有余额的SPL Token", "warning")
            print()
            continue
            
        print_status(f"发现 {len(valid_accounts)} 个有余额的代币需要处理", "info")
        
        # 处理代币
        for token_idx, acc in enumerate(valid_accounts, 1):
            try:
                # 显示进度
                print_progress_bar(token_idx, len(valid_accounts), f"处理代币 {token_idx}/{len(valid_accounts)}")
                
                # 获取代币精度
                decimals = get_token_decimals(acc["mint"])
                amount_float = acc["amount"] / (10 ** decimals)
                
                # 显示代币信息（只显示一次，使用正确的精度）
                print(f"\n{Fore.GREEN}🎯 处理代币 {token_idx}/{len(valid_accounts)}")
                print_token_info(acc["mint"], acc["amount"], decimals)
                
                result = send_token(
                    from_address=owner_address,
                    private_key=privkey,
                    to_address=TO_ADDRESS,
                    amount=amount_float,
                    token_mint=acc["mint"],
                    decimals=decimals
                )
                
                if result:
                    total_success += 1
                else:
                    total_fail += 1
                    
            except Exception as e:
                print_status(f"处理代币 {acc['mint']} 失败: {e}", "error")
                total_fail += 1
                
        print()  # 空行分隔
        
    # 打印总结
    print_summary(total_success, total_fail, len(PRIVATE_KEYS), DRY_RUN)