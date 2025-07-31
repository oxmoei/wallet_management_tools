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

# 初始化colorama
init(autoreset=True)

print(f"""
{Fore.MAGENTA}{Style.BRIGHT}
============================================
  🧹 Solana SPL Token 清道夫 (Scavenger)
  💸 一键清空钱包 SPL Token 到指定地址
============================================{Style.RESET_ALL}
""")

# 获取脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')

# 加载.env配置
load_dotenv(env_path)

# 读取配置
RPC_URL = os.getenv("RPC_URL", "").strip()
TO_ADDRESS = os.getenv("TO_ADDRESS")
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# 验证配置
if not RPC_URL:
    print(f"{Fore.RED}❌ 错误: RPC_URL 配置为空或无效{Style.RESET_ALL}")
    print(f"请在 .env 文件中正确配置 RPC_URL，例如:")
    print(f"RPC_URL=https://api.mainnet-beta.solana.com")
    exit(1)

if not TO_ADDRESS:
    print(f"{Fore.RED}❌ 错误: TO_ADDRESS 配置为空{Style.RESET_ALL}")
    print(f"请在 .env 文件中配置 TO_ADDRESS")
    exit(1)

print(f"{Fore.CYAN}ℹ️ 已加载配置:{Style.RESET_ALL}")
print(f"    {Fore.WHITE}🌐 RPC URL: {Fore.YELLOW}{RPC_URL}{Style.RESET_ALL}")
print(f"    {Fore.WHITE}🏦 目标地址: {Fore.YELLOW}{TO_ADDRESS}{Style.RESET_ALL}")
print(f"    {Fore.WHITE}⚙️ Dry Run: {Fore.YELLOW}{DRY_RUN}{Style.RESET_ALL}")

# 自动收集所有私钥，并推导钱包地址
PRIVATE_KEYS = {}
for k, v in os.environ.items():
    if k.startswith("PRIVATE_KEY_") and v.strip():
        try:
            keypair = Keypair.from_base58_string(v.strip())
            pubkey = str(keypair.pubkey())
            PRIVATE_KEYS[pubkey] = v.strip()
            print(f"  {Fore.GREEN}✅ 已加载私钥: {k} -> {Fore.YELLOW}🏠  {pubkey}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ [警告] 无法解析私钥 {k}: {e}{Style.RESET_ALL}")

if not PRIVATE_KEYS:
    print(f"{Fore.RED}❌ 错误: 未找到有效的私钥配置{Style.RESET_ALL}")
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
        resp.raise_for_status() # 对错误响应引发 HTTPError（4xx 或 5xx）
        result = resp.json()
        if "result" in result and "value" in result["result"]:
            accounts = []
            for acc in result["result"]["value"]:
                if "account" in acc and "data" in acc["account"] and "parsed" in acc["account"]["data"] and "info" in acc["account"]["data"]["parsed"] and "tokenAmount" in acc["account"]["data"]["parsed"]["info"]:
                     ata = acc["pubkey"]
                     mint = acc["account"]["data"]["parsed"]["info"]["mint"]
                     amount = int(acc["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])
                     accounts.append({"ata": ata, "mint": mint, "amount": amount})
            print(f"{Fore.CYAN}✅ 获取到{Fore.YELLOW} {len(accounts)} {Fore.CYAN}个Token账户{Style.RESET_ALL}\n")
            return accounts
        else:
             print(f"{Fore.YELLOW}⚠️ 获取账户信息成功，但返回结果结构异常: {result}{Style.RESET_ALL}\n")
    except requests.exceptions.Timeout:
        print(f"{Fore.YELLOW}⚠️ 获取账户信息超时（RPC: {RPC_URL}）{Style.RESET_ALL}\n")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}❌ 获取账户信息失败（RPC: {RPC_URL}）: {e}{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"{Fore.RED}❌ 处理账户信息响应失败（RPC: {RPC_URL}）: {e}{Style.RESET_ALL}\n")
    print(f"{Fore.RED}❌ 无法获取 {owner_address} 的账户信息{Style.RESET_ALL}\n")
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
        resp.raise_for_status() # 对错误响应引发 HTTPError（4xx 或 5xx）
        result = resp.json()
        if "result" in result and "value" in result["result"] and "decimals" in result["result"]["value"]:
            decimals = result["result"]["value"]["decimals"]
            print(f"{Fore.GREEN}✅ 获取代币精度: {decimals}{Style.RESET_ALL}")
            return decimals
        else:
             print(f"{Fore.YELLOW}⚠️ 获取代币精度成功，但返回结果结构异常: {result}{Style.RESET_ALL}")
    except requests.exceptions.Timeout:
        print(f"{Fore.YELLOW}⚠️ 获取代币精度超时（RPC: {RPC_URL}）{Style.RESET_ALL}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}❌ 获取代币精度失败（RPC: {RPC_URL}）: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ 处理代币精度响应失败（RPC: {RPC_URL}）: {e}{Style.RESET_ALL}")
    print(f"{Fore.RED}❌ 无法获取代币 {token_mint} 的精度{Style.RESET_ALL}")
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
            print(f"{Fore.YELLOW}⚠️ 获取区块哈希成功，但返回结果结构异常: {blockhash_resp}{Style.RESET_ALL}")
        if isinstance(recent_blockhash, str):
            recent_blockhash = Hash.from_string(recent_blockhash)
        print(f"{Fore.GREEN}✅ 获取最新区块哈希: {recent_blockhash}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ 获取最新区块哈希失败（RPC: {RPC_URL}）: {e}{Style.RESET_ALL}")
        return False

    if recent_blockhash is None:
        print(f"{Fore.RED}❌ 无法获取最新区块哈希{Style.RESET_ALL}")
        return False

    tx = SoldersTransaction([from_keypair], SoldersMessage([ix], from_pubkey), recent_blockhash)

    tx_sig = None
    try:
        client = Client(RPC_URL)
        raw_tx = bytes(tx)
        if DRY_RUN:
            print(f"{Fore.CYAN}🟦 [DRY-RUN] 将从 {from_address} 转出{Fore.MAGENTA} {amount_float} {Fore.CYAN}个 {Fore.MAGENTA}{token_mint} {Fore.CYAN}到 {to_address}{Style.RESET_ALL}\n")
            return True
        resp = client.send_raw_transaction(raw_tx)
        if hasattr(resp, 'value'):
            tx_sig = resp.value
        elif isinstance(resp, dict):
            tx_sig = resp.get("result")
        else:
            tx_sig = str(resp)
        print(f"{Fore.GREEN}✅ SPL Token转账成功: {tx_sig}{Style.RESET_ALL}")
        print(f"{'-'*5}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ 发送SPL Token转账失败（RPC: {RPC_URL}）: {e}{Style.RESET_ALL}\n")
    print(f"{Fore.RED}❌ 无法发送SPL Token转账{Style.RESET_ALL}\n")
    return False

if __name__ == "__main__":
    total_success = 0
    total_fail = 0
    for owner_address, privkey in PRIVATE_KEYS.items():
        print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⏳ 开始处理钱包:{Fore.YELLOW} {owner_address}{Style.RESET_ALL}")
        accounts = get_all_token_accounts(owner_address)
        if not accounts:
            print(f"{Fore.RED}⚠️ 钱包 {owner_address} 没有SPL Token账户{Style.RESET_ALL}\n")
            continue
        for acc in accounts:
            if acc["amount"] > 0:
                print(f"{Fore.GREEN}🔍 发现Token:{Fore.MAGENTA} {acc['mint']}{Fore.GREEN}, 余额:{Fore.MAGENTA} {acc['amount']}{Style.RESET_ALL}")
                decimals = get_token_decimals(acc["mint"])
                amount_float = acc["amount"] / (10 ** decimals)
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
            else:
                print(f"{Fore.YELLOW}⚠️ 发现空余额Token:{Fore.MAGENTA} {acc['mint']}{Fore.YELLOW}, 余额:{Fore.MAGENTA} 0{Style.RESET_ALL}")
                print(f"{'-'*5}")
    print(f"\n{Fore.MAGENTA}{'='*40}")
    print(f"{Fore.WHITE}🔆 所有链处理完成！（Dry-run:{Fore.YELLOW} {DRY_RUN}）{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ 成功: {total_success}{Style.RESET_ALL}，{Fore.RED}❌ 失败: {total_fail}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}\n")