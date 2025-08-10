import os
import threading
import requests
import logging
from web3 import Web3
import yaml
import asyncio
from web3.providers.legacy_websocket import LegacyWebSocketProvider
import json
import websockets
from datetime import datetime
import colorama
from colorama import Fore, Back, Style

# 初始化colorama以支持跨平台彩色输出
colorama.init(autoreset=True)

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 自定义彩色日志格式化器
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
            elif '🔌' in record.getMessage():
                # 连接消息使用蓝色
                formatted_msg = f"{Fore.BLUE}{Style.BRIGHT}🔌 {record.getMessage()}{Style.RESET_ALL}"
            elif '📱' in record.getMessage():
                # Telegram消息使用紫色
                formatted_msg = f"{Fore.MAGENTA}{Style.BRIGHT}📱 {record.getMessage()}{Style.RESET_ALL}"
            elif '🔔' in record.getMessage():
                # 检测消息使用青色
                formatted_msg = f"{Fore.CYAN}{Style.BRIGHT}🔔 {record.getMessage()}{Style.RESET_ALL}"
            elif '🔄' in record.getMessage():
                # 切换消息使用黄色
                formatted_msg = f"{Fore.YELLOW}{Style.BRIGHT}🔄 {record.getMessage()}{Style.RESET_ALL}"
            elif '🎯' in record.getMessage():
                # 订阅消息使用绿色
                formatted_msg = f"{Fore.GREEN}{Style.BRIGHT}🎯 {record.getMessage()}{Style.RESET_ALL}"
            elif '👂' in record.getMessage():
                # 监听消息使用蓝色
                formatted_msg = f"{Fore.BLUE}{Style.BRIGHT}👂 {record.getMessage()}{Style.RESET_ALL}"
            elif '🚀' in record.getMessage():
                # 启动消息使用绿色
                formatted_msg = f"{Fore.GREEN}{Style.BRIGHT}🚀 {record.getMessage()}{Style.RESET_ALL}"
            elif '📋' in record.getMessage() or '⛓️' in record.getMessage():
                # 统计信息使用青色
                formatted_msg = f"{Fore.CYAN}{Style.BRIGHT}{record.getMessage()}{Style.RESET_ALL}"
            elif '🔗' in record.getMessage():
                # 交易哈希相关消息使用蓝色
                formatted_msg = f"{Fore.BLUE}{Style.BRIGHT}{record.getMessage()}{Style.RESET_ALL}"
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

# 加载配置文件
config_path = os.path.join(SCRIPT_DIR, "config.yaml")
try:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    logging.error(f"❌ 配置文件未找到: {config_path}")
    logging.error("请确保 config.yaml 文件存在于脚本同目录下")
    exit(1)
except Exception as e:
    logging.error(f"❌ 配置文件读取失败: {e}")
    exit(1)

# 监听地址
WATCH_ADDRESSES = [addr.lower() for addr in config["watch_addresses"]]

# Telegram 配置
TELEGRAM_BOT_TOKEN = config["telegram"]["bot_token"]
TELEGRAM_CHAT_ID = config["telegram"]["chat_id"]

# ERC20 Transfer 事件的 topic
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def print_banner():
    """打印启动横幅"""
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
███████╗██╗   ██╗███╗   ███╗    ███╗   ███╗ ██████╗ ███╗   ██╗██╗████████╗ ██████╗ ██████╗ 
██╔════╝██║   ██║████╗ ████║    ████╗ ████║██╔═══██╗████╗  ██║██║╚══██╔══╝██╔═══██╗██╔══██╗
█████╗  ██║   ██║██╔████╔██║    ██╔████╔██║██║   ██║██╔██╗ ██║██║   ██║   ██║   ██║██████╔╝
██╔══╝  ╚██╗ ██╔╝██║╚██╔╝██║    ██║╚██╔╝██║██║   ██║██║╚██╗██║██║   ██║   ██║   ██║██╔══██╗
███████╗ ╚████╔╝ ██║ ╚═╝ ██║    ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║   ██║   ╚██████╔╝██║  ██║
╚══════╝  ╚═══╝  ╚═╝     ╚═╝    ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
                                                                                           

           ╔══════════════════════════════════════════════════════════════╗
           ║                   🚀 EVM Token 监听器 🚀                     ║
           ║                                                              ║
           ║  📋 监听地址数量: {len(WATCH_ADDRESSES):<8}                                   ║
           ║  ⛓️  监控链数量: {len(config['chains']):<8}                                    ║
           ║  📱 Telegram通知: {'已启用' if TELEGRAM_BOT_TOKEN else '未配置':<8}                                ║
           ║                                                              ║
           ║  🎯 功能: 监听ERC20 Token到账 → 发送Telegram通知             ║
           ╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)
    logging.info(f"✅ 配置文件加载成功: {config_path}")

def send_telegram_alert(message):
    """ 发送 Telegram 报警通知 """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info("📱 Telegram 通知发送成功")
        else:
            logger.error(f"📱 Telegram 发送失败: {response.text}")
    except Exception as e:
        logger.error(f"📱 Telegram 发送异常: {e}")

def handle_event(event, web3):
    """ 处理 ERC20 代币到账事件 """
    if event["topics"][0].lower() == TRANSFER_TOPIC.lower():  # 转账事件的匹配
        from_address = "0x" + event["topics"][1][-40:]
        to_address = "0x" + event["topics"][2][-40:]
        token_address = event["address"]
        transaction_hash = event.get("transactionHash", "")
        data = event.get("data", "")
        if not data:
            return
        try:
            amount = int(data, 16)
        except ValueError:
            return
        if to_address.lower() in WATCH_ADDRESSES:
            # 发送到账通知到 Telegram
            message = (
                f"🚨 *ERC20 代币到账警报* 🚨\n"
                f"=============================\n"
                f"⛓️ 链: `{web3.eth.chain_id}`\n"
                f"🆔 交易哈希: `{transaction_hash}`\n"
                f"📤 发送地址: `{from_address}`\n"
                f"📥 接收地址: `{to_address}`\n"
                f"💰 数量: `{amount}`\n"
                f"📜 代币合约: `{token_address}`"
            )
            send_telegram_alert(message)
            logger.info(f"🔔 检测到 ERC20 代币到账 | 链: {web3.eth.chain_id} | 交易哈希: {transaction_hash[:10]}...{transaction_hash[-8:]} | 接收地址: {to_address[:10]}...{to_address[-8:]} | 数量: {amount} | 合约: {token_address[:10]}...{token_address[-8:]}")

def create_web3(ws_url):
    """创建支持心跳的Web3实例"""
    # ping_interval/ping_timeout 需 web3 6.x+ 和 websocket-client 1.2.1+
    # 如不支持可注释掉相关参数
    # 注意：使用 WebSocket 订阅时，这些参数可能更重要
    # 修改：使用导入的 LegacyWebSocketProvider
    # 注意：这里创建的 Web3 实例主要用于调用同步方法 (如 checksum_address)，
    # WebSocket 连接本身将直接通过 websockets 库管理。
    return Web3(LegacyWebSocketProvider(
        ws_url,
        websocket_timeout=60,  # 连接超时
        # ping_interval=20,    # 心跳间隔（秒），如 web3 支持则加上
        # ping_timeout=10      # 心跳超时（秒），如 web3 支持则加上
    ))

# 异步监听函数 (使用底层 WebSocket 订阅)
async def listen_for_events_async(chain_name, ws_urls):
    """ 异步监听 ERC20 代币的 Transfer 事件，支持自动重连，循环切换备用节点，使用底层 WebSocket 订阅 """
    url_index = 0
    consecutive_failures = 0
    BASE_RETRY_DELAY = 5
    MAX_RETRY_DELAY = 60

    # 创建一个 Web3 实例用于同步方法调用
    # 注意：这个实例不用于管理 WebSocket 连接本身
    web3_sync = None
    try:
        # 尝试使用第一个 URL 创建同步 Web3 实例
        web3_sync = create_web3(ws_urls[0])
    except Exception as e:
        logger.warning(f"⚠️  {chain_name} | 初始化同步 Web3 实例失败: {e}. 部分功能可能受限。")

    while True:
        ws_url = ws_urls[url_index]
        websocket = None # 初始化 websocket 连接
        try:
            logger.info(f"🔌 {chain_name} | 正在连接节点: {ws_url}")
            # 使用 websockets 库建立 WebSocket 连接
            # 注意：ping_interval 和 ping_timeout 在这里可以直接设置
            websocket = await websockets.connect(
                ws_url,
                ping_interval=20, # 心跳间隔
                ping_timeout=10   # 心跳超时
            )

            logger.info(f"✅ {chain_name} | WebSocket 连接成功，正在发送订阅请求...")

            # 构建 eth_subscribe JSON-RPC 请求
            subscribe_request = {
                "jsonrpc": "2.0",
                "method": "eth_subscribe",
                "params": [
                    "logs",
                    {
                        "topics": [TRANSFER_TOPIC]
                        # 如果需要按地址过滤，可以在这里加上 "address": contract_address
                    }
                ],
                "id": 1 # 请求 ID，可以自定义
            }

            # 发送订阅请求
            await websocket.send(json.dumps(subscribe_request))

            # 接收订阅响应 (通常会返回一个 subscription ID)
            response = await websocket.recv()
            sub_response = json.loads(response)

            if "result" in sub_response:
                subscription_id = sub_response["result"]
                logger.info(f"🎯 {chain_name} | 订阅成功 | ID: {subscription_id}")
                consecutive_failures = 0 # 连接和订阅成功，重置失败计数
            else:
                # 如果响应不是预期的结果，可能是订阅失败
                raise Exception(f"订阅请求失败: {sub_response}")

            logger.info(f"👂 {chain_name} | 开始监听 ERC20 转账事件...")

            # 异步接收订阅推送的事件
            async for message in websocket:
                event_data = json.loads(message)
                # 检查消息是否为事件推送
                if event_data.get("method") == "eth_subscription":
                    event = event_data.get("params", {}).get("result")
                    if event:
                         handle_event(event, web3_sync)

        except websockets.exceptions.ConnectionClosed as e:
             # WebSocket 连接关闭异常
             logger.error(f"❌ {chain_name} | WebSocket 连接已关闭: {e}，正在尝试重连...")

        except Exception as e:
            consecutive_failures += 1
            retry_delay = min(MAX_RETRY_DELAY, BASE_RETRY_DELAY * (2 ** (consecutive_failures - 1)))

            logger.error(f"❌ {chain_name} | 连接失败: {str(e)} | {retry_delay}秒后重试")

            # 如果 WebSocket 连接已建立，尝试关闭连接
            if websocket is not None:
                try:
                    # 关闭 WebSocket 连接是异步操作
                    await websocket.close()
                    logger.info(f"🔒 {chain_name} | WebSocket 连接已关闭")
                except Exception as close_e:
                    logger.error(f"🔒 {chain_name} | 关闭 WebSocket 连接失败: {close_e}")

            # 切换到下一个 URL
            url_index = (url_index + 1) % len(ws_urls)
            logger.warning(f"🔄 {chain_name} | 切换到备用节点: {ws_urls[url_index]}")
            await asyncio.sleep(retry_delay)  # 异步等待后重试连接

# 每个线程的入口函数，创建并运行 asyncio 事件循环
def run_listener_thread(chain_name, ws_urls):
    """ 在独立的线程中运行 asyncio 事件循环并启动监听 """
    # 使用 asyncio.run() 运行顶层异步函数
    try:
        asyncio.run(listen_for_events_async(chain_name, ws_urls))
    except KeyboardInterrupt:
        logger.info(f"🛑 {chain_name} | 监听线程接收到中断信号，正在退出...")
    except Exception as e:
        logger.error(f"💥 {chain_name} | 监听线程发生未捕获的异常: {e}")

def start_listeners():
    """ 为每条链启动独立的监听线程 """
    # 打印启动横幅
    print_banner()
    
    logger.info("🚀 启动 ERC20 代币监控系统...")
    logger.info(f"📋 监控地址数量: {len(WATCH_ADDRESSES)}")
    logger.info(f"⛓️  监控链数量: {len(config['chains'])}")
    
    threads = []
    for chain_name, info in config["chains"].items():
        ws_urls = info.get("ws_urls")
        if not ws_urls:
            logger.error(f"❌ 配置错误: 链 {chain_name} 未配置 ws_urls")
            continue
        
        logger.info(f"🔄 启动 {chain_name} 监听线程...")
        # 修改：线程的目标函数改为 run_listener_thread
        thread = threading.Thread(target=run_listener_thread, args=(chain_name, ws_urls))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    logger.info("✅ 所有监听线程已启动，开始监控...")
    
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    start_listeners()
