import yaml
import logging
import requests
import json
import asyncio
import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI, InvalidHandshake, WebSocketException
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
            elif '📱' in record.getMessage():
                # Telegram消息使用紫色
                formatted_msg = f"{Fore.MAGENTA}{Style.BRIGHT}📱 {record.getMessage()}{Style.RESET_ALL}"
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
CONFIG_FILE = SCRIPT_DIR / "config.yaml"

# 读取配置文件
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    logging.error(f"❌ 配置文件未找到: {CONFIG_FILE}")
    logging.error("请确保 config.yaml 文件存在于脚本同目录下")
    exit(1)
except Exception as e:
    logging.error(f"❌ 配置文件读取失败: {e}")
    exit(1)

SOLANA_RPC_URL = config["solana"]["http_urls"]
WATCH_ADDRESSES = [addr.strip() for addr in config["watch_addresses"] if addr and addr.strip()]
TELEGRAM_BOT_TOKEN = config["telegram"]["bot_token"]
TELEGRAM_CHAT_ID = config["telegram"]["chat_id"]

# 验证配置
if not WATCH_ADDRESSES:
    logging.error("❌ 配置文件中没有有效的监听地址")
    exit(1)

# 静默验证地址格式，不输出日志
for i, addr in enumerate(WATCH_ADDRESSES, 1):
    if len(addr) < 43 or len(addr) > 44:
        logging.warning(f"⚠️ 地址 {i} 长度异常: {addr} (长度: {len(addr)}, 期望: 43-44)")

# 自动生成WebSocket URL
def generate_ws_urls(http_urls):
    """将HTTP URL转换为WebSocket URL"""
    ws_urls = []
    for http_url in http_urls:
        # 检查是否是已知不支持WebSocket的节点
        if "zan.top" in http_url or "ankr.com" in http_url:
            # 这些节点可能不支持WebSocket，跳过
            continue
            
        if http_url.startswith("https://"):
            ws_url = http_url.replace("https://", "wss://")
        elif http_url.startswith("http://"):
            ws_url = http_url.replace("http://", "ws://")
        else:
            # 如果不是标准HTTP URL，尝试添加wss://前缀
            ws_url = f"wss://{http_url}"
        ws_urls.append(ws_url)
    
    # 如果没有可用的WebSocket URL，添加一些已知支持WebSocket的备用节点
    if not ws_urls:
        logging.warning("⚠️ 没有可用的WebSocket节点，使用备用节点")
        ws_urls = [
            "wss://api.mainnet-beta.solana.com",
            "wss://solana-api.projectserum.com"
        ]
    
    return ws_urls

# 生成WebSocket URL列表
SOLANA_WS_URLS = generate_ws_urls(SOLANA_RPC_URL)

# 静默生成WebSocket节点，不输出日志

def print_banner():
    """打印启动横幅"""
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
███████╗██████╗ ██╗         ███╗   ███╗ ██████╗ ███╗   ██╗██╗████████╗ ██████╗ ██████╗ 
██╔════╝██╔══██╗██║         ████╗ ████║██╔═══██╗████╗  ██║██║╚══██╔══╝██╔═══██╗██╔══██╗
███████╗██████╔╝██║         ██╔████╔██║██║   ██║██╔██╗ ██║██║   ██║   ██║   ██║██████╔╝
╚════██║██╔═══╝ ██║         ██║╚██╔╝██║██║   ██║██║╚██╗██║██║   ██║   ██║   ██║██╔══██╗
███████║██║     ███████╗    ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║   ██║   ╚██████╔╝██║  ██║
╚══════╝╚═╝     ╚══════╝    ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
                                                                                       

           ╔══════════════════════════════════════════════════════════════╗
           ║                   🚀 Solana Token 监听器 🚀                  ║
           ║                                                              ║
           ║  📡 监听地址数量: {len(WATCH_ADDRESSES):<8}                                   ║
           ║  🌐 RPC节点数量: {len(SOLANA_RPC_URL):<8}                                    ║
           ║  📱 Telegram通知: {'已启用' if TELEGRAM_BOT_TOKEN else '未配置':<8}                                ║
           ║                                                              ║
           ║  🎯 功能: 监听SPL Token到账 → 发送Telegram通知               ║
           ╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)
    logging.info(f"✅ 配置文件加载成功: {CONFIG_FILE}")

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
    # 验证地址格式
    if not owner_address or not isinstance(owner_address, str):
        logging.error(f"❌ 无效的地址格式: {owner_address}")
        return []
    
    # 检查地址长度（Solana地址通常是43-44个字符）
    if len(owner_address) < 43 or len(owner_address) > 44:
        logging.error(f"❌ 地址长度不正确: {owner_address} (长度: {len(owner_address)}, 期望: 43-44)")
        return []
    
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
    
    # 确保地址完整显示
    display_address = owner_address if len(owner_address) <= 20 else f"{owner_address[:10]}...{owner_address[-10:]}"
    
    for url in SOLANA_RPC_URL: # Loop through the list of URLs
        try:
            logging.info(f"🔍 正在查询地址 {display_address} 的Token账户")
            resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
            resp.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            result = resp.json()
            
            # 检查是否有错误响应
            if "error" in result:
                logging.error(f"❌ RPC {url} 返回错误: {result['error']}")
                continue
                
            if "result" in result and "value" in result["result"]:
                accounts = []
                for acc in result["result"]["value"]:
                    try:
                        if ("account" in acc and "data" in acc["account"] and 
                            "parsed" in acc["account"]["data"] and 
                            "info" in acc["account"]["data"]["parsed"] and 
                            "tokenAmount" in acc["account"]["data"]["parsed"]["info"]):
                            
                            ata = acc["pubkey"]
                            mint = acc["account"]["data"]["parsed"]["info"]["mint"]
                            amount = int(acc["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])
                            accounts.append({"ata": ata, "mint": mint, "amount": amount})
                    except (KeyError, ValueError, TypeError) as e:
                        logging.warning(f"⚠️ 跳过无效账户数据: {e}")
                        continue
                        
                logging.info(f"✅ 发现 {len(accounts)} 个Token账户")
                return accounts # Return on success
            else:
                logging.error(f"❌ RPC {url} 返回结果结构异常: {result}")
        except requests.exceptions.Timeout as e:
            logging.error(f"❌ RPC {url} 请求超时: {e}")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"❌ RPC {url} 连接失败: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ RPC {url} 请求失败: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"❌ RPC {url} 响应JSON解析失败: {e}")
        except Exception as e:
            logging.error(f"❌ 处理RPC {url} 响应失败: {type(e).__name__}: {e}")
    
    # If all URLs fail
    logging.error(f"❌ 所有RPC端点均无法获取 {display_address} 的账户信息")
    send_telegram_alert(f"❌ 所有RPC端点均无法获取 {display_address} 的账户信息")
    return [] # Return empty list if all fail

def get_recent_transactions(ata, limit=5):
    """获取ATA最近的交易哈希"""
    # 验证ATA地址格式
    if not ata or not isinstance(ata, str):
        logging.warning(f"⚠️ 无效的ATA地址格式: {ata}")
        return None
    
    # 检查ATA地址长度
    if len(ata) < 43 or len(ata) > 44:
        logging.warning(f"⚠️ ATA地址长度不正确: {ata} (长度: {len(ata)}, 期望: 43-44)")
        return None
    
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [ata, {"limit": limit}]
    }
    
    # 确保ATA地址完整显示
    display_ata = ata if len(ata) <= 20 else f"{ata[:10]}...{ata[-10:]}"
    
    for url in SOLANA_RPC_URL:
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
            resp.raise_for_status()
            result = resp.json()
            
            # 检查是否有错误响应
            if "error" in result:
                logging.warning(f"⚠️ RPC {url} 获取交易哈希返回错误: {result['error']}")
                continue
            
            if "result" in result and result["result"]:
                # 返回最新的交易哈希
                return result["result"][0]["signature"]
            else:
                logging.warning(f"⚠️ 未找到ATA {display_ata} 的最近交易")
                return None
                
        except requests.exceptions.Timeout as e:
            logging.warning(f"⚠️ 获取交易哈希超时: {e}")
        except requests.exceptions.ConnectionError as e:
            logging.warning(f"⚠️ 获取交易哈希连接失败: {e}")
        except Exception as e:
            logging.warning(f"⚠️ 获取交易哈希失败: {type(e).__name__}: {e}")
            continue
    
    return None



async def listen_ata(ata, mint, owner_address):
    """监听特定ATA的余额变化"""
    decimals = get_token_decimals(mint)
    ws_urls = SOLANA_WS_URLS
    ws_index = 0
    fail_count = 0
    total_fail_count = 0
    
    logging.info(f"🎧 开始监听 ATA: {ata[:8]}...{ata[-8:]} (代币: {mint[:8]}...{mint[-8:]})")
    logging.info(f"🌐 可用WebSocket节点: {len(ws_urls)} 个")
    
    while True:
        ws_url = ws_urls[ws_index]
        try:
            logging.info(f"📡 正在连接WebSocket: {ws_url}")
            async with websockets.connect(
                ws_url,
                ping_interval=20,   # 每20秒发送一次心跳
                ping_timeout=20,    # 20秒内无响应则认为超时
                close_timeout=10,   # 关闭连接超时
                max_size=2**20      # 最大消息大小1MB
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
                    
        except ConnectionClosed as e:
            logging.error(f"❌ WebSocket连接已关闭: {ws_url} - {e}")
            fail_count += 1
            total_fail_count += 1
            if fail_count >= 3:
                logging.warning(f"⚠️ {ws_url} 连续失败3次，切换到下一个节点...")
                fail_count = 0
                await asyncio.sleep(2)
            ws_index = (ws_index + 1) % len(ws_urls)
        except InvalidURI as e:
            logging.error(f"❌ WebSocket URL格式无效: {ws_url} - {e}")
            total_fail_count += 1
            ws_index = (ws_index + 1) % len(ws_urls)
        except InvalidHandshake as e:
            logging.error(f"❌ WebSocket握手失败: {ws_url} - {e}")
            fail_count += 1
            total_fail_count += 1
            if fail_count >= 3:
                logging.warning(f"⚠️ {ws_url} 连续失败3次，切换到下一个节点...")
                fail_count = 0
                await asyncio.sleep(2)
            ws_index = (ws_index + 1) % len(ws_urls)
        except WebSocketException as e:
            logging.error(f"❌ WebSocket异常: {ws_url} - {type(e).__name__}: {e}")
            fail_count += 1
            total_fail_count += 1
            if fail_count >= 3:
                logging.warning(f"⚠️ {ws_url} 连续失败3次，切换到下一个节点...")
                fail_count = 0
                await asyncio.sleep(2)
            ws_index = (ws_index + 1) % len(ws_urls)
        except TimeoutError as e:
            logging.error(f"❌ WebSocket连接超时: {ws_url} - {e}")
            fail_count += 1
            total_fail_count += 1
            if fail_count >= 3:
                logging.warning(f"⚠️ {ws_url} 连续超时3次，切换到下一个节点...")
                fail_count = 0
                await asyncio.sleep(2)
            ws_index = (ws_index + 1) % len(ws_urls)
        except Exception as e:
            logging.error(f"❌ 未知连接异常: {ws_url} - {type(e).__name__}: {e}")
            fail_count += 1
            total_fail_count += 1
            if fail_count >= 3:
                logging.warning(f"⚠️ {ws_url} 连续失败3次，切换到下一个节点...")
                fail_count = 0
                await asyncio.sleep(2)
            ws_index = (ws_index + 1) % len(ws_urls)
        
        # 如果所有节点都失败了，等待更长时间后重试
        if total_fail_count >= len(ws_urls) * 3:
            logging.warning(f"⚠️ 所有WebSocket节点都失败了，等待30秒后重试...")
            total_fail_count = 0
            await asyncio.sleep(30)

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
    # 验证代币地址格式
    if not token_mint or not isinstance(token_mint, str):
        logging.error(f"❌ 无效的代币地址格式: {token_mint}")
        raise Exception(f"无效的代币地址格式: {token_mint}")
    
    # 检查代币地址长度
    if len(token_mint) < 43 or len(token_mint) > 44:
        logging.error(f"❌ 代币地址长度不正确: {token_mint} (长度: {len(token_mint)}, 期望: 43-44)")
        raise Exception(f"代币地址长度不正确: {token_mint}")
    
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenSupply",
        "params": [token_mint]
    }
    
    # 确保代币地址完整显示
    display_mint = token_mint if len(token_mint) <= 20 else f"{token_mint[:10]}...{token_mint[-10:]}"
    
    for url in SOLANA_RPC_URL: # Loop through the list of URLs
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
            resp.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            result = resp.json()
            
            # 检查是否有错误响应
            if "error" in result:
                logging.error(f"❌ RPC {url} 返回代币精度错误: {result['error']}")
                continue
                
            if "result" in result and "value" in result["result"] and "decimals" in result["result"]["value"]:
                return result["result"]["value"]["decimals"] # Return on success
            else:
                logging.error(f"❌ RPC {url} 返回代币精度结构异常: {result}")
        except requests.exceptions.Timeout as e:
            logging.error(f"❌ RPC {url} 获取代币精度超时: {e}")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"❌ RPC {url} 获取代币精度连接失败: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ RPC {url} 获取代币精度失败: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"❌ RPC {url} 代币精度响应JSON解析失败: {e}")
        except Exception as e:
            logging.error(f"❌ 处理RPC {url} 代币精度响应失败: {type(e).__name__}: {e}")
    
    # If all URLs fail
    logging.error(f"❌ 所有RPC端点均无法获取代币 {display_mint} 的精度")
    send_telegram_alert(f"❌ 所有RPC端点均无法获取代币 {display_mint} 的精度")
    raise Exception(f"无法获取代币 {display_mint} 的精度") # Raise exception if all fail

if __name__ == "__main__":
    print_banner()
    asyncio.run(main_async())