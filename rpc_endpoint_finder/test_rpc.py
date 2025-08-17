from web3 import Web3
import json
import time
from datetime import datetime

# ANSI 颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """ 打印美化的标题 """
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    🌐 RPC 连接测试工具                       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

def print_section(title):
    """ 打印分节标题 """
    print(f"\n{Colors.CYAN}{Colors.BOLD}━━━ {title} ━━━{Colors.ENDC}")

def print_success(msg):
    """ 打印成功信息 """
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg):
    """ 打印错误信息 """
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")

def print_info(msg):
    """ 打印信息 """
    print(f"{Colors.BLUE}ℹ {msg}{Colors.ENDC}")

def print_warning(msg):
    """ 打印警告信息 """
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.ENDC}")

def print_progress(current, total, prefix="测试进度"):
    """ 打印进度条 """
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    percentage = current / total * 100
    print(f"\r{Colors.CYAN}{prefix}: [{bar}] {percentage:.1f}% ({current}/{total}){Colors.ENDC}", end='', flush=True)
    if current == total:
        print()

print_header()

def get_rpc_from_console():
    """ 从控制台获取 RPC 地址 """
    rpc_list = []
    
    print_section("输入 RPC 地址")
    print_info("请输入要测试的 RPC 地址（输入空行结束输入）：")
    
    while True:
        rpc_url = input().strip()
        
        if not rpc_url:
            break
            
        rpc_list.append(rpc_url)
    
    return rpc_list

def test_rpc(chain_name, rpc_url, index, total):
    """ 测试 RPC 连接是否可用 """
    print_progress(index, total, f"测试 {chain_name}")
    
    print(f"\n{Colors.BOLD}🔍 测试 {chain_name}{Colors.ENDC}")
    print(f"{Colors.CYAN}🌐 RPC: {rpc_url}{Colors.ENDC}")

    try:
        # 根据协议类型选择 provider
        if rpc_url.startswith("wss://") or rpc_url.startswith("ws://"):
            web3 = Web3(Web3.WebsocketProvider(rpc_url))
        elif rpc_url.startswith("https://") or rpc_url.startswith("http://"):
            web3 = Web3(Web3.HTTPProvider(rpc_url))
        else:
            print_error(f"无法识别的 RPC 协议: {rpc_url}")
            return False

        if not web3.is_connected():
            print_error(f"连接失败：无法连接到 {rpc_url}")
            return False

        # 获取链信息
        block_number = web3.eth.block_number
        gas_price = web3.eth.gas_price
        chain_id = web3.eth.chain_id

        # 美化输出链信息
        print()
        print(f"{Colors.GREEN}┌─ 连接状态: 成功{Colors.ENDC}")
        print(f"{Colors.BLUE}├─ 区块高度: {block_number:,}{Colors.ENDC}")
        print(f"{Colors.BLUE}├─ Gas 价格: {web3.from_wei(gas_price, 'gwei'):.2f} Gwei{Colors.ENDC}")
        print(f"{Colors.BLUE}└─ 链 ID: {chain_id}{Colors.ENDC}")

        return True

    except Exception as e:
        print_error(f"初始化 Web3 或获取链信息失败：{e}")
        print_warning(f"请确认 RPC 地址是否正确：{rpc_url}")
        return False

def print_summary(results):
    """ 打印测试结果摘要 """
    print_section("测试结果摘要")
    
    total = len(results)
    successful = sum(1 for result in results if result)
    failed = total - successful
    
    print(f"{Colors.BOLD}📊 统计信息:{Colors.ENDC}")
    print(f"  {Colors.GREEN}✓ 成功: {successful}{Colors.ENDC}")
    print(f"  {Colors.RED}✗ 失败: {failed}{Colors.ENDC}")
    

def print_footer():
    """ 打印页脚 """
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print(f"║                    测试完成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}            ║")
    print("║                    感谢使用 RPC 测试工具                     ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
if __name__ == "__main__":
    # 从控制台获取 RPC 列表
    rpc_list = get_rpc_from_console()
    
    if not rpc_list:
        print_error("未输入任何 RPC 地址，程序退出")
        exit(1)
    
    print_section("开始测试")
    print_info(f"准备测试 {len(rpc_list)} 个 RPC 端点...")
    
    # 测试每个 RPC 端点
    results = []
    for i, rpc_url in enumerate(rpc_list, 1):
        result = test_rpc(f"RPC #{i}", rpc_url, i, len(rpc_list))
        results.append(result)
        time.sleep(0.5)  # 添加小延迟，让输出更优雅
    
    # 打印摘要
    print_summary(results)
    
    # 打印页脚
    print_footer()
