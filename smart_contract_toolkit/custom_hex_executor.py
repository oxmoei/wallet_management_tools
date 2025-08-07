from web3 import Web3
from eth_account import Account
import os
import time
from dotenv import load_dotenv
from colorama import init, Fore, Style

# 初始化 colorama（确保 Windows 终端正确显示颜色）
init(autoreset=True)

# 确保输出立即显示
import sys
sys.stdout.flush()

# 颜色定义
RED = Fore.RED + Style.BRIGHT     # 错误/警告
GREEN = Fore.GREEN + Style.BRIGHT  # 成功
YELLOW = Fore.YELLOW + Style.BRIGHT  # 提示
BLUE = Fore.BLUE + Style.BRIGHT    # 信息
CYAN = Fore.CYAN + Style.BRIGHT    # 状态
MAGENTA = Fore.MAGENTA + Style.BRIGHT  # 重要信息
WHITE = Fore.WHITE + Style.BRIGHT  # 标题
RESET = Style.RESET_ALL  # 重置颜色

def print_banner():
    """打印程序横幅"""
    # 使用紫色背景，白色文字
    purple_bg = '\033[45m'  # 紫色背景
    white_text = '\033[37m'  # 白色文字
    bold = '\033[1m'  # 粗体
    reset = '\033[0m'  # 重置
    
    banner = f"""
{purple_bg}{white_text}{bold}════════════════════════════════════════════════════════════════════════════════{reset}
{purple_bg}{white_text}{bold}  ╔══════════════════════════════════════════════════════════════════════════╗  {reset}
{purple_bg}{white_text}{bold}  ║                                                                          ║  {reset}
{purple_bg}{white_text}{bold}  ║                        🎯 智能合约交互工具 🎯                            ║  {reset}
{purple_bg}{white_text}{bold}  ║                                                                          ║  {reset}
{purple_bg}{white_text}{bold}  ║                   Custom HEX Transaction Executor                        ║  {reset}
{purple_bg}{white_text}{bold}  ║                           自定义HEX交易执行器                             ║  {reset}
{purple_bg}{white_text}{bold}  ║                                                                          ║  {reset}
{purple_bg}{white_text}{bold}  ║             Version: 2.0.0             Supported_Chains: EVM             ║  {reset}
{purple_bg}{white_text}{bold}  ║                                                                          ║  {reset}
{purple_bg}{white_text}{bold}  ╚══════════════════════════════════════════════════════════════════════════╝  {reset}
{purple_bg}{white_text}{bold}════════════════════════════════════════════════════════════════════════════════{reset}
"""
    print(banner)
    sys.stdout.flush()  # 确保横幅立即显示

# 立即显示横幅
print_banner()

def print_section_header(title, emoji="📋"):
    """打印章节标题"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{CYAN}{emoji} {title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_info_box(title, content, emoji="ℹ️"):
    """打印信息框"""
    print(f"\n{YELLOW}┌─ {emoji} {title} {'─' * (48 - len(title))}┐{RESET}")
    print(f"{YELLOW}│{RESET} {content}")
    print(f"{YELLOW}└{'─' * 58}┘{RESET}")

def print_success_box(title, content, emoji="✅"):
    """打印成功信息框"""
    print(f"\n{GREEN}┌─ {emoji} {title} {'─' * (48 - len(title))}┐{RESET}")
    print(f"{GREEN}│{RESET} {content}")
    print(f"{GREEN}└{'─' * 58}┘{RESET}")

def print_warning_box(title, content, emoji="⚠️"):
    """打印警告信息框"""
    print(f"\n{YELLOW}┌─ {emoji} {title} {'─' * (48 - len(title))}┐{RESET}")
    print(f"{YELLOW}│{RESET} {content}")
    print(f"{YELLOW}└{'─' * 58}┘{RESET}")

def print_error_box(title, content, emoji="❌"):
    """打印错误信息框"""
    print(f"\n{RED}┌─ {emoji} {title} {'─' * (48 - len(title))}┐{RESET}")
    print(f"{RED}│{RESET} {content}")
    print(f"{RED}└{'─' * 58}┘{RESET}")

def print_progress_bar(current, total, description="进度"):
    """打印进度条"""
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    percentage = current / total * 100
    print(f"\r{CYAN}{description}: [{bar}] {percentage:.1f}%{RESET}", end='', flush=True)
    if current == total:
        print()  # 换行

def format_wei_to_eth(wei_amount):
    """将 Wei 转换为更易读的格式"""
    if wei_amount >= 10**18:
        
        eth_amount = wei_amount / 10**18
        return f"{eth_amount:.6f} ETH"
    elif wei_amount >= 10**15:
        gwei_amount = wei_amount / 10**15
        return f"{gwei_amount:.3f} Gwei"
    else:
        return f"{wei_amount:,} Wei"

def format_address(address):
    """格式化地址显示"""
    return f"{address[:6]}...{address[-4:]}"

def parse_hex_data(hex_data):
    """解析十六进制数据"""
    try:
        if not hex_data.startswith('0x'):
            hex_data = '0x' + hex_data
        
        # 检查长度
        if len(hex_data) < 10:
            return {"error": "数据长度不足"}
        
        # 提取方法ID
        method_id = hex_data[:10]
        
        # 常见ERC20和NFT方法ID
        method_signatures = {
            # ERC20方法
            "0x23b872dd": "transferFrom(address,address,uint256)",
            "0xa9059cbb": "transfer(address,uint256)",
            "0x095ea7b3": "approve(address,uint256)",
            "0x39509351": "increaseAllowance(address,uint256)",
            "0x40c10f19": "mint(address,uint256)",
            "0x42966c68": "burn(uint256)",
            "0xdd62ed3e": "allowance(address,address)",
            "0x70a08231": "balanceOf(address)",
            "0x18160ddd": "totalSupply()",
            "0x95d89b41": "symbol()",
            "0x06fdde03": "name()",
            "0x313ce567": "decimals()",
            # NFT方法
            "0xa22cb465": "setApprovalForAll(address,bool)",
            "0x42842e0e": "safeTransferFrom(address,address,uint256)",
            "0xb88d4fde": "safeTransferFrom(address,address,uint256,bytes)",
            "0x6352211e": "ownerOf(uint256)",
            "0x8da5cb5b": "owner()",
            "0x2f745c59": "tokenOfOwnerByIndex(address,uint256)",
            "0x4f6ccce7": "tokenByIndex(uint256)",
            "0x162094c4": "setTokenURI(uint256,string)",
            "0x01ffc9a7": "supportsInterface(bytes4)",
            "0x80ac58cd": "isApprovedForAll(address,address)",
            "0x5a3d5493": "tokenURI(uint256)",
            "0x40c10f19": "mint(address,uint256)",
            "0x42966c68": "burn(uint256)"
        }
        
        result = {
            "method_id": method_id,
            "method_name": method_signatures.get(method_id, "未知方法"),
            "parameters": []
        }
        
        # 解析参数
        if method_id in ["0x23b872dd", "0xa9059cbb", "0x095ea7b3", "0x39509351", "0x40c10f19", "0x42842e0e", "0xb88d4fde"]:
            # 这些方法有address参数
            if len(hex_data) >= 74:
                address1 = "0x" + hex_data[34:74]
                result["parameters"].append({
                    "type": "address",
                    "value": address1,
                    "formatted": address1
                })
            
            if method_id in ["0x23b872dd", "0xdd62ed3e", "0x42842e0e", "0xb88d4fde", "0x80ac58cd"]:
                # 这些方法有第二个address参数
                if len(hex_data) >= 138:
                    address2 = "0x" + hex_data[98:138]
                    result["parameters"].append({
                        "type": "address", 
                        "value": address2,
                        "formatted": address2
                    })
            
            # 解析数值参数
            if method_id in ["0x23b872dd", "0xa9059cbb", "0x095ea7b3", "0x39509351", "0x40c10f19", "0x42842e0e", "0xb88d4fde"]:
                # 计算数值参数的起始位置
                if method_id in ["0x23b872dd", "0xdd62ed3e", "0x42842e0e", "0xb88d4fde", "0x80ac58cd"]:
                    # transferFrom和allowance有两个address参数，数值从第138位开始
                    amount_start = 138
                else:
                    # approve, transfer, mint只有一个address参数，数值从第74位开始
                    amount_start = 74
                
                if len(hex_data) >= amount_start + 64:  # 64位十六进制 = 32字节
                    amount_hex = hex_data[amount_start:amount_start + 64]
                    try:
                        amount = int(amount_hex, 16)
                        result["parameters"].append({
                            "type": "uint256",
                            "value": amount,
                            "formatted": f"{amount:,} (token_id)"
                        })
                    except:
                        result["parameters"].append({
                            "type": "uint256",
                            "value": amount_hex,
                            "formatted": f"0x{amount_hex}"
                        })
                elif len(hex_data) > amount_start:
                    # 如果数据长度不够64位，但还有剩余数据
                    amount_hex = hex_data[amount_start:]
                    try:
                        amount = int(amount_hex, 16)
                        result["parameters"].append({
                            "type": "uint256",
                            "value": amount,
                            "formatted": f"{amount:,} (token_id)"
                        })
                    except:
                        result["parameters"].append({
                            "type": "uint256",
                            "value": amount_hex,
                            "formatted": f"0x{amount_hex}"
                        })
        
        elif method_id in ["0x42966c68"]:
            # burn方法只有一个uint256参数
            if len(hex_data) >= 74:
                amount_hex = hex_data[10:74]
                try:
                    amount = int(amount_hex, 16)
                    result["parameters"].append({
                        "type": "uint256",
                        "value": amount,
                        "formatted": f"{amount:,} (wei)"
                    })
                except:
                    result["parameters"].append({
                        "type": "uint256",
                        "value": amount_hex,
                        "formatted": f"0x{amount_hex}"
                    })
        
        elif method_id in ["0x70a08231", "0x06fdde03", "0x95d89b41", "0x313ce567"]:
            # 这些方法有address参数或没有参数
            if len(hex_data) >= 74:
                address = "0x" + hex_data[34:74]
                result["parameters"].append({
                    "type": "address",
                    "value": address,
                    "formatted": format_address(address)
                })
        
        elif method_id in ["0xa22cb465"]:
            # setApprovalForAll(address,bool) 方法
            if len(hex_data) >= 74:
                address = "0x" + hex_data[34:74]
                result["parameters"].append({
                    "type": "address",
                    "value": address,
                    "formatted": address
                })
            
            # 解析布尔参数
            if len(hex_data) >= 138:
                bool_hex = hex_data[98:138]
                try:
                    bool_value = int(bool_hex, 16)
                    result["parameters"].append({
                        "type": "bool",
                        "value": bool_value,
                        "formatted": "true" if bool_value else "false"
                    })
                except:
                    result["parameters"].append({
                        "type": "bool",
                        "value": bool_hex,
                        "formatted": f"0x{bool_hex}"
                    })
        
        elif method_id in ["0x6352211e", "0x5a3d5493", "0x162094c4", "0x2f745c59", "0x4f6ccce7"]:
            # 这些方法只有一个uint256参数（token_id）
            if len(hex_data) >= 74:
                token_id_hex = hex_data[10:74]
                try:
                    token_id = int(token_id_hex, 16)
                    result["parameters"].append({
                        "type": "uint256",
                        "value": token_id,
                        "formatted": f"{token_id:,} (token_id)"
                    })
                except:
                    result["parameters"].append({
                        "type": "uint256",
                        "value": token_id_hex,
                        "formatted": f"0x{token_id_hex}"
                    })
        
        return result
        
    except Exception as e:
        return {"error": f"解析失败: {str(e)}"}

# 加载环境变量
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path)

# 读取 RPC URL
RPC_URL = os.getenv("RPC_URL")
PRIVATE_RPC = os.getenv("PRIVATE_RPC")

# 目标钱包和辅助钱包的私钥
TAR_WALLET = os.getenv("TAR_WALLET_PRIVATE_KEY")
AID_WALLET_PRIVATE_KEY = os.getenv("AID_WALLET_PRIVATE_KEY")

# 检查 .env 文件是否存在
env_file_exists = os.path.exists(dotenv_path)

if not env_file_exists:
    print_warning_box("配置文件", ".env 文件不存在，将使用交互式输入")
    print_info_box("建议操作", "创建 .env 文件以避免重复输入")
    
    # 交互式输入配置
    RPC_URL = input(f"{YELLOW}✍️ 请输入 RPC URL: {RESET}").strip()
    PRIVATE_RPC = input(f"{YELLOW}✍️ 请输入私有 RPC URL (可选，留空跳过): {RESET}").strip() or None
    TAR_WALLET = input(f"{YELLOW}✍️ 请输入目标钱包私钥: {RESET}").strip()
    AID_WALLET_PRIVATE_KEY = input(f"{YELLOW}✍️ 请输入辅助钱包私钥: {RESET}").strip()
    
    # 验证输入
    if not RPC_URL or not TAR_WALLET or not AID_WALLET_PRIVATE_KEY:
        print_error_box("配置错误", "⚠️ 必要配置缺失，请重新运行程序")
        raise ValueError("必要配置缺失")
else:
    # 参数检查
    if not RPC_URL or not TAR_WALLET or not AID_WALLET_PRIVATE_KEY:
        print_error_box("配置错误", "⚠️ .env 配置缺失，请检查 RPC_URL, TAR_WALLET_PRIVATE_KEY, AID_WALLET_PRIVATE_KEY")
        raise ValueError(".env 配置缺失")

# 全局变量
w3 = None
private_w3 = None
CHAIN_ID = None
aid_wallet = None
tar_wallet = None
CONTRACT = None
CUSTOM_HEX = None

def get_contract_address():
    """获取合约地址"""
    print_section_header("合约配置", "📄")
    while True:
        try:
            contract_address = input(f"{YELLOW}✍️ 请输入合约地址: {RESET}").strip()
            if not contract_address:
                print_warning_box("输入错误", "⚠️ 合约地址不能为空，请重新输入")
                continue
            
            # 验证地址格式
            if not Web3.is_address(contract_address):
                print_warning_box("地址格式错误", "⚠️请输入有效的以太坊地址")
                continue
            
            # 转换为 Checksum 格式
            contract_address = Web3.to_checksum_address(contract_address)
            
            # 验证合约是否存在并获取代币信息
            try:
                code = w3.eth.get_code(contract_address)
                if code == b'':
                    print_warning_box("合约验证", "⚠️ 该地址没有合约代码，可能不是合约地址")
                else:
                    print_success_box("合约验证", f"📜 合约代码存在，大小: {len(code)} 字节")
                    
                    # 尝试获取代币名称（同时用于ERC20检测）
                    try:
                        name_call = w3.eth.call({
                            "to": contract_address,
                            "data": "0x06fdde03"  # name()方法ID
                        }, "latest")
                        
                        if name_call and name_call != b'':
                            # 解码返回的数据
                            name_hex = name_call.hex()[2:]  # 去掉0x
                            # 去除前导零和空字节
                            name_bytes = bytes.fromhex(name_hex)
                            token_name = name_bytes.decode('utf-8').rstrip('\x00')
                            
                            # 同时用于ERC20检测
                            print_success_box("合约检测", f"🎉 检测成功！代币名称: {token_name}")
                        else:
                            print_info_box("合约检测", "⚠️ 无法获取代币名称")
                    except Exception as e:
                        print_info_box("合约检测", "⚠️ 无法获取代币名称")
                        
            except Exception as e:
                print_warning_box("合约检查", f"⚠️ 无法检查合约状态: {e}")
            
            return contract_address
            
        except Exception as e:
            print_error_box("地址错误", f"❌ 地址验证失败: {e}")
            continue

def get_custom_hex():
    """获取自定义HEX数据"""
    print_section_header("HEX数据配置", "🔧")
    while True:
        try:
            custom_hex = input(f"{YELLOW}✍️ 请输入自定义HEX数据: {RESET}").strip()
            if not custom_hex:
                print_warning_box("输入错误", "⚠️ HEX数据不能为空，请重新输入")
                continue
            
            # 验证HEX格式
            if not custom_hex.startswith('0x'):
                custom_hex = '0x' + custom_hex
            
            # 验证是否为有效的十六进制
            try:
                int(custom_hex, 16)
            except ValueError:
                print_warning_box("HEX格式错误", "⚠️ 请输入有效的十六进制数据")
                continue

            print_info_box("解析HEX数据", f"🤖 正在解析十六进制数据...")

            # 解析HEX数据
            parsed_data = parse_hex_data(custom_hex)
            if "error" not in parsed_data:
                print(f"    {CYAN}🆔 函数识别: {RESET}{parsed_data['method_name']}")
                
                # 显示参数
                if parsed_data['parameters']:
                    for i, param in enumerate(parsed_data['parameters'], 1):
                        if param['type'] == 'address':
                            print(f"    {CYAN}📍 参数{i} ({param['type']}): {RESET}{param['formatted']}")
                        elif param['type'] == 'uint256':
                            print(f"    {CYAN}💰 参数{i} ({param['type']}): {RESET}{param['formatted']}")
                        else:
                            print(f"    {CYAN}📄 参数{i} ({param['type']}): {RESET}{param['value']}")
            else:
                print(f"    {YELLOW}⚠️ HEX解析错误: {RESET}{parsed_data['error']}")
            
            print_success_box("验证HEX数据", f"🔆 验证成功: {custom_hex}")
            return custom_hex
            
        except Exception as e:
            print_error_box("HEX数据错误", f"❌ HEX数据验证失败: {e}")
            continue

def initialize_network():
    """初始化网络连接"""
    global w3, private_w3, CHAIN_ID, aid_wallet, tar_wallet
    
    print_section_header("网络初始化", "🌐")
    
    # 连接 Web3
    print_info_box("网络连接", "🛜 正在连接网络...")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print_error_box("连接失败", "❌ 无法连接到 RPC，请检查 RPC_URL 是否正确")
        return False
    
    # 检查私有 RPC
    if PRIVATE_RPC:
        private_w3 = Web3(Web3.HTTPProvider(PRIVATE_RPC))
        if not private_w3.is_connected():
            print_warning_box("私有RPC失败", "❌ 私有 RPC 连接失败，回退到公共 RPC")
            private_w3 = w3
    else:
        private_w3 = w3
    
    # 创建钱包账户
    aid_wallet = Account.from_key(AID_WALLET_PRIVATE_KEY)
    tar_wallet = Account.from_key(TAR_WALLET)
    
    # 获取链 ID
    CHAIN_ID = w3.eth.chain_id
    
    # 显示链ID信息
    print_success_box("网络信息", f"🌐 当前链 ID: {CHAIN_ID}")
    
    # 显示系统配置
    print_section_header("系统配置", "⚙️")
    print(f"    {CYAN}🎯 目标钱包: {RESET}{tar_wallet.address}")
    print(f"    {CYAN}🆕 辅助钱包: {RESET}{aid_wallet.address}")
    print(f"    {CYAN}🌐 网络ID: {RESET}{CHAIN_ID}")
    
    return True

def execute_custom_hex_transaction():
    """执行自定义HEX交易"""
    global CONTRACT, CUSTOM_HEX
    
    # 获取合约地址和HEX数据
    CONTRACT = get_contract_address()
    CUSTOM_HEX = get_custom_hex()
    
    print_section_header("交易执行", "🚀")
    
    # 获取交易参数
    nonce_tar = w3.eth.get_transaction_count(tar_wallet.address)
    base_gas_price = w3.eth.gas_price
    gas_price = int(base_gas_price * 1.2)
    tar_balance = w3.eth.get_balance(tar_wallet.address)

    # 预估 gas 限制
    try:
        estimated_gas = w3.eth.estimate_gas({
            "from": tar_wallet.address,
            "to": CONTRACT,
            "data": CUSTOM_HEX
        })
        print_info_box("预估Gas限制", f"⚡ 预估Gas限制: {estimated_gas} 单位")
    except Exception as e:
        print_warning_box("Gas 预估失败", f"❌ 预估 Gas 限制失败: {e}")
        
        # 分析错误原因
        error_str = str(e)
        if "execution reverted" in error_str.lower():
            print_error_box("合约错误", "❌ 合约执行被回滚，可能原因：")
            print(f"{YELLOW}   • 代币余额不足{RESET}")
            print(f"{YELLOW}   • 授权额度不足{RESET}")
            print(f"{YELLOW}   • 合约地址错误{RESET}")
            print(f"{YELLOW}   • 参数格式错误{RESET}")
        elif "invalid opcode" in error_str.lower():
            print_error_box("合约错误", "❌ 无效操作码，合约地址可能错误")
        elif "out of gas" in error_str.lower():
            print_error_box("Gas不足", "❌ Gas不足，请检查交易复杂度")
        else:
            print_error_box("未知错误", f"❌ 未知错误类型: {error_str}")
        
        # 使用更保守的 Gas 限制
        estimated_gas = 300000  # 增加默认 Gas 限制
        print_info_box("使用默认", f"⚡ 使用默认 Gas 限制: {estimated_gas} 单位")

    gas_limit = int(estimated_gas * 1.2)  # 增加 20% 的缓冲  
    gas_fee = gas_price * gas_limit
    
    print_info_box("预计Gas费用", f"💰 {format_wei_to_eth(gas_fee)}")
    print_info_box("钱包余额", f"🪙 {format_wei_to_eth(tar_balance)}")

    if tar_balance < gas_fee:
        deficit = gas_fee - tar_balance
        print_warning_box("余额不足", f"⚠️ 目标钱包余额不足 {format_wei_to_eth(gas_fee)}，缺少 {format_wei_to_eth(deficit)}，正在转账...")

        # 计算转账金额
        additional_funds = int(gas_fee * 0.03)
        transfer_amount = deficit + additional_funds
        
        fund_tx = {
            "to": tar_wallet.address,
            "value": transfer_amount,
            "gas": 21000,
            "gasPrice": gas_price,
            "nonce": w3.eth.get_transaction_count(aid_wallet.address),
            "chainId": CHAIN_ID,
        }

        signed_fund_tx = w3.eth.account.sign_transaction(fund_tx, aid_wallet.key)
        fund_tx_hash = w3.eth.send_raw_transaction(signed_fund_tx.raw_transaction)
        
        try:
            receipt = w3.eth.wait_for_transaction_receipt(fund_tx_hash, timeout=180)
            if receipt.status == 1:
                print_success_box("转账成功", "🎉 资金已到账")
            else:
                print_error_box("转账失败", "❌ 资金转账失败")
                return
        except Exception as e:
            print_error_box("转账超时", f"❌ 转账等待超时: {e}")
            return

    # 创建并发送交易
    custom_tx = {
        "to": CONTRACT,
        "data": CUSTOM_HEX,
        "gas": gas_limit,
        "gasPrice": gas_price,
        "nonce": nonce_tar,
        "chainId": CHAIN_ID,
    }
    
    signed_custom_tx = w3.eth.account.sign_transaction(custom_tx, tar_wallet.key)

    try:
        tx_hash = private_w3.eth.send_raw_transaction(signed_custom_tx.raw_transaction)
        print_info_box("交易提交", f"🎉 交易已提交，Tx Hash: 0x{tx_hash.hex()}")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        if receipt.status == 1:           
            gas_used = receipt.gasUsed
            gas_limit = receipt.gasLimit
            print_info_box("交易详情", f"📊 Gas 使用: {gas_used:,} / {gas_limit:,}")
            print_success_box("交易成功", "🎉 自定义 Hex 交易执行成功！")
        else:
            print_error_box("交易失败", "❌ 交易执行失败")
    except Exception as e:
        print_error_box("交易失败", f"❌ {e}")

def main():
    """主函数"""
    try:
        # 初始化网络
        if not initialize_network():
            print_error_box("初始化失败", "❌ 网络初始化失败，退出程序")
            return
        
        while True:
            # 执行交易
            execute_custom_hex_transaction()
            
            # 询问是否继续执行其他HEX交易
            print_section_header("本次交易完成", "✅")
            continue_choice = input(f"{YELLOW}❓ 是否要执行其它 HEX 交易？(y/n): {RESET}").strip().lower()
            
            if continue_choice != 'y':
                print_success_box("脚本完成", "🎉 自定义 Hex 交易脚本执行完毕")
                break
            else:
                print_info_box("继续执行", "🔄 准备执行下一个 HEX 交易...")
                print(f"{MAGENTA}{'☆'*60}{RESET}")
        
    except Exception as e:
        print_section_header("执行失败", "❌")
        print_error_box("脚本错误", f"❌ 自定义 Hex 交易脚本执行失败: {e}\n")
        exit(1)

if __name__ == "__main__":
    main()