import yaml
import logging
import requests
import json
import asyncio
import websockets
from datetime import datetime
from pathlib import Path
import colorama
from colorama import Fore, Back, Style

# 初始化colorama以支持跨平台彩色输出
colorama.init(autoreset=True)

# 配置日志 - 只输出到控制台，美化格式
class ColoredFormatter(logging.Formatter):
    """自定义彩色日志格式化器"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }
    
    def format(self, record):
        # 添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 根据日志级别选择颜色
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        
        # 格式化消息
        if record.levelname == 'INFO':
            # 特殊处理INFO级别的消息，添加更多样式
            if '🚨' in record.getMessage():
                # 警报消息使用特殊样式
                formatted_msg = f"{Fore.RED}{Style.BRIGHT}🚨 {record.getMessage()}{Style.RESET_ALL}"
            elif '✅' in record.getMessage():
                # 成功消息使用绿色
                formatted_msg = f"{Fore.GREEN}{Style.BRIGHT}✅ {record.getMessage()}{Style.RESET_ALL}"
            elif '📡' in record.getMessage():
                # 连接消息使用蓝色
                formatted_msg = f"{Fore.BLUE}{Style.BRIGHT}📡 {record.getMessage()}{Style.RESET_ALL}"
            else:
                formatted_msg = f"{color}{record.getMessage()}{Style.RESET_ALL}"
        else:
            formatted_msg = f"{color}{record.getMessage()}{Style.RESET_ALL}"
        
        return f"{Fore.WHITE}[{timestamp}]{Style.RESET_ALL} {formatted_msg}"

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 移除所有现有的处理器
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(ColoredFormatter())
logger.addHandler(console_handler)

# 获取当前脚本所在目录
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "solana.yaml"

# 读取配置文件
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    logging.info(f"✅ 配置文件加载成功: {CONFIG_FILE}")
except FileNotFoundError:
    logging.error(f"❌ 配置文件未找到: {CONFIG_FILE}")
    logging.error("请确保 solana.yaml 文件存在于脚本同目录下")
    exit(1)
except Exception as e:
    logging.error(f"❌ 配置文件读取失败: {e}")
    exit(1)

SOLANA_RPC_URL = config["solana"]["http_urls"]
WATCH_ADDRESSES = [addr for addr in config["watch_addresses"]]
TELEGRAM_BOT_TOKEN = config["telegram"]["bot_token"]
TELEGRAM_CHAT_ID = config["telegram"]["chat_id"]

# 自动生成WebSocket URL
def generate_ws_urls(http_urls):
    """将HTTP URL转换为WebSocket URL"""
    ws_urls = []
    for http_url in http_urls:
        if http_url.startswith("https://"):
            ws_url = http_url.replace("https://", "wss://")
        elif http_url.startswith("http://"):
            ws_url = http_url.replace("http://", "ws://")
        else:
            # 如果不是标准HTTP URL，尝试添加wss://前缀
            ws_url = f"wss://{http_url}"
        ws_urls.append(ws_url)
    return ws_urls

# 生成WebSocket URL列表
SOLANA_WS_URLS = generate_ws_urls(SOLANA_RPC_URL)

# 显示自动生成的WebSocket URL
logging.info(f"🔗 配置了 {len(SOLANA_RPC_URL)} 个HTTP RPC节点")
logging.info(f"📡 自动生成了 {len(SOLANA_WS_URLS)} 个WebSocket节点")
for i, (http_url, ws_url) in enumerate(zip(SOLANA_RPC_URL, SOLANA_WS_URLS), 1):
    logging.info(f"  节点{i}: {http_url} → {ws_url}")

def print_banner():
    """打印启动横幅"""
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
  ___ ___ _      __  __          _ _           
 / __| _ \ |    |  \/  |___ _ _ (_) |_ ___ _ _ 
 \__ \  _/ |__  | |\/| / _ \ ' \| |  _/ _ \ '_|
 |___/_| |____| |_|  |_\___/_||_|_|\__\___/_|

╔══════════════════════════════════════════════════════════════╗
║                    🚀 Solana Token 监听器 🚀                    ║
║                                                              ║
║  📡 监听地址数量: {len(WATCH_ADDRESSES):<8}                                    ║
║  🔗 RPC节点数量: {len(SOLANA_RPC_URL):<8}                                    ║
║  📱 Telegram通知: {'已启用' if TELEGRAM_BOT_TOKEN else '未配置':<8}                    ║
║                                                              ║
║  🎯 功能: 监听SPL Token到账 → 发送Telegram通知                    ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)

def send_telegram_alert(message):
    """发送Telegram通知"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logging.info(f"📱 Telegram通知发送成功")
        else:
            logging.error(f"📱 Telegram通知发送失败: {response.status_code}")
    except Exception as e:
        logging.error(f"📱 Telegram通知失败: {e}")

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
    for url in SOLANA_RPC_URL: # Loop through the list of URLs
        try:
            logging.info(f"🔍 正在查询地址 {owner_address[:8]}...{owner_address[-8:]} 的Token账户")
            resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
            resp.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            result = resp.json()
            if "result" in result and "value" in result["result"]:
                accounts = []
                for acc in result["result"]["value"]:
                    if "account" in acc and "data" in acc["account"] and "parsed" in acc["account"]["data"] and "info" in acc["account"]["data"]["parsed"] and "tokenAmount" in acc["account"]["data"]["parsed"]["info"]:
                         ata = acc["pubkey"]
                         mint = acc["account"]["data"]["parsed"]["info"]["mint"]
                         amount = int(acc["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])
                         accounts.append({"ata": ata, "mint": mint, "amount": amount})
                logging.info(f"✅ 发现 {len(accounts)} 个Token账户")
                return accounts # Return on success
            else:
                 logging.error(f"❌ RPC {url} 返回结果结构异常")
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ RPC {url} 请求失败: {e}")
        except Exception as e:
            logging.error(f"❌ 处理RPC {url} 响应失败: {e}")
    # If all URLs fail
    logging.error(f"❌ 所有RPC端点均无法获取 {owner_address} 的账户信息")
    send_telegram_alert(f"❌ 所有RPC端点均无法获取 {owner_address} 的账户信息")
    return [] # Return empty list if all fail

def get_recent_transactions(ata, limit=5):
    """获取ATA最近的交易哈希"""
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [ata, {"limit": limit}]
    }
    
    for url in SOLANA_RPC_URL:
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
            resp.raise_for_status()
            result = resp.json()
            
            if "result" in result and result["result"]:
                # 返回最新的交易哈希
                return result["result"][0]["signature"]
            else:
                logging.warning(f"⚠️ 未找到ATA {ata[:8]}...{ata[-8:]} 的最近交易")
                return None
                
        except Exception as e:
            logging.error(f"❌ 获取交易哈希失败: {e}")
            continue
    
    return None



async def listen_ata(ata, mint, owner_address):
    """监听特定ATA的余额变化"""
    decimals = get_token_decimals(mint)
    ws_urls = SOLANA_WS_URLS
    ws_index = 0
    fail_count = 0
    
    logging.info(f"🎧 开始监听 ATA: {ata[:8]}...{ata[-8:]} (代币: {mint[:8]}...{mint[-8:]})")
    
    while True:
        ws_url = ws_urls[ws_index]
        try:
            logging.info(f"📡 正在连接WebSocket: {ws_url}")
            async with websockets.connect(
                ws_url,
                ping_interval=20,   # 每20秒发送一次心跳
                ping_timeout=20     # 20秒内无响应则认为超时
            ) as ws:
                sub_msg = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "accountSubscribe",
                    "params": [ata, {"encoding": "jsonParsed"}]
                }
                await ws.send(json.dumps(sub_msg))
                last_amount = None
                fail_count = 0  # 连接成功后重置失败计数
                logging.info(f"✅ WebSocket连接成功，开始监听余额变化")
                
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if "result" in data:  # 订阅确认
                        continue
                    try:
                        # 兼容不同节点推送结构
                        try:
                            parsed_info = data["params"]["result"]["value"]["data"]["parsed"]["info"]
                            amount = int(parsed_info["tokenAmount"]["amount"])
                        except Exception:
                            parsed_info = data["params"]["result"]["value"]["parsed"]["info"]
                            amount = int(parsed_info["tokenAmount"]["amount"])
                    except Exception as e:
                        logging.error(f"❌ 解析余额失败: {e}")
                        continue
                    
                    amount_display = amount / (10 ** decimals)
                    
                    if last_amount is None:
                        last_amount = amount
                        if amount > 0:
                            delta = amount
                            delta_display = delta / (10 ** decimals)
                            logging.info(f"💰 检测到初始余额: {amount_display} (代币: {mint[:8]}...{mint[-8:]})")
                            
                            # 获取交易哈希
                            tx_hash = get_recent_transactions(ata)
                            tx_info = ""
                            if tx_hash:
                                tx_info = f"\n🔗 **交易哈希**: `{tx_hash}`\n🔍 **查看链接**: [Solscan](https://solscan.io/tx/{tx_hash})"
                            
                            msg = (
                                "🚨 **SPL Token 到账警报** 🚨\n"
                                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                f"⛓️ **链**: Solana\n"
                                f"📥 **接收地址**: `{owner_address}`\n"
                                f"💰 **增加数量**: `{delta_display}`\n"
                                f"💰 **当前余额**: `{amount_display}`\n"
                                f"📜 **代币合约**: `{mint}`\n"
                                f"🕐 **时间**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
                                f"{tx_info}"
                            )
                            send_telegram_alert(msg)
                        continue
                    
                    if amount > last_amount:
                        delta = amount - last_amount
                        delta_display = delta / (10 ** decimals)
                        logging.info(f"🎉 检测到新Token到账! 增加: {delta_display}, 当前余额: {amount_display}")
                        
                        # 获取交易哈希
                        tx_hash = get_recent_transactions(ata)
                        tx_info = ""
                        if tx_hash:
                            tx_info = f"\n🔗 **交易哈希**: `{tx_hash}`\n🔍 **查看链接**: [Solscan](https://solscan.io/tx/{tx_hash})"
                        
                        msg = (
                            "🚨 **SPL Token 到账警报** 🚨\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"⛓️ **链**: Solana\n"
                            f"📥 **接收地址**: `{owner_address}`\n"
                            f"💰 **增加数量**: `{delta_display}`\n"
                            f"💰 **当前余额**: `{amount_display}`\n"
                            f"📜 **代币合约**: `{mint}`\n"
                            f"🕐 **时间**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
                            f"{tx_info}"
                        )
                        send_telegram_alert(msg)
                    
                    last_amount = amount
                    
        except (websockets.exceptions.ConnectionClosed, Exception) as e:
            logging.error(f"❌ WebSocket连接异常: {e}")
            fail_count += 1
            if fail_count >= 3:
                logging.warning(f"⚠️ {ws_url} 连续失败3次，等待5秒后重试...")
                fail_count = 0
                await asyncio.sleep(5)
            ws_index = (ws_index + 1) % len(ws_urls)

async def main_async():
    """主异步函数"""
    tasks = []
    ata_set = set()
    addr2atas = {addr: set() for addr in WATCH_ADDRESSES}
    
    async def refresh_atas():
        """刷新ATA列表"""
        for addr in WATCH_ADDRESSES:
            accounts = get_all_token_accounts(addr)
            for acc in accounts:
                key = (acc["ata"], acc["mint"], addr)
                if key not in ata_set:
                    ata_set.add(key)
                    addr2atas[addr].add(acc["ata"])
                    tasks.append(asyncio.create_task(listen_ata(acc["ata"], acc["mint"], addr)))
    
    await refresh_atas()
    logging.info(f"🚀 Solana Token监听器启动完成，正在监听 {len(tasks)} 个Token账户")
    
    # 定时刷新ATA，支持新Token自动监听
    while True:
        await asyncio.sleep(60)
        await refresh_atas()

def get_token_decimals(token_mint):
    """获取代币精度"""
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenSupply",
        "params": [token_mint]
    }
    for url in SOLANA_RPC_URL: # Loop through the list of URLs
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
            resp.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            result = resp.json()
            if "result" in result and "value" in result["result"] and "decimals" in result["result"]["value"]:
                return result["result"]["value"]["decimals"] # Return on success
            else:
                 logging.error(f"❌ RPC {url} 返回代币精度结构异常")
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ RPC {url} 获取代币精度失败: {e}")
        except Exception as e:
            logging.error(f"❌ 处理RPC {url} 代币精度响应失败: {e}")
    # If all URLs fail
    logging.error(f"❌ 所有RPC端点均无法获取代币 {token_mint} 的精度")
    send_telegram_alert(f"❌ 所有RPC端点均无法获取代币 {token_mint} 的精度")
    raise Exception(f"无法获取代币 {token_mint} 的精度") # Raise exception if all fail

if __name__ == "__main__":
    print_banner()
    asyncio.run(main_async())