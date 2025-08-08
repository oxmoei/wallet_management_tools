from web3 import Web3
from eth_account import Account
import os
import json
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
RESET = Style.RESET_ALL  # 重置颜色

def print_banner():
    """打印程序横幅"""
    # 使用紫色背景，白色文字
    purple_bg = '\033[45m'  # 紫色背景
    white_text = '\033[37m'  # 白色文字
    bold = '\033[1m'  # 粗体
    reset = '\033[0m'  # 重置
    
    banner = f"""
{purple_bg}{white_text}{bold}  ╔══════════════════════════════════════════════════════════════════════════╗  {reset}
{purple_bg}{white_text}{bold}  ║                                                                          ║  {reset}
{purple_bg}{white_text}{bold}  ║                      🎯 智能合约交互工具 🎯                              ║  {reset}
{purple_bg}{white_text}{bold}  ║                                                                          ║  {reset}
{purple_bg}{white_text}{bold}  ║             Multi-Function Token & NFT Management Tool                   ║  {reset}
{purple_bg}{white_text}{bold}  ║                      ERC20代币 & NFT 管理工具                            ║  {reset}
{purple_bg}{white_text}{bold}  ║                                                                          ║  {reset}
{purple_bg}{white_text}{bold}  ║             Version: 2.0.0         Supported_Chains: EVM                 ║  {reset}
{purple_bg}{white_text}{bold}  ║                                                                          ║  {reset}
{purple_bg}{white_text}{bold}  ╚══════════════════════════════════════════════════════════════════════════╝  {reset}
"""
    print(banner)
    sys.stdout.flush()  # 确保横幅立即显示

# 立即显示横幅
print_banner()

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
    print(f"{YELLOW}⚠️ .env 文件不存在，将使用交互式输入{RESET}")
    print(f"{BLUE}📝 建议创建 .env 文件以避免重复输入{RESET}")
    
    # 交互式输入配置
    RPC_URL = input(f"{YELLOW}✍️ 请输入 RPC URL: {RESET}").strip()
    PRIVATE_RPC = input(f"{YELLOW}✍️ 请输入私有 RPC URL (可选，留空跳过): {RESET}").strip() or None
    TAR_WALLET = input(f"{YELLOW}✍️ 请输入目标钱包私钥: {RESET}").strip()
    AID_WALLET_PRIVATE_KEY = input(f"{YELLOW}✍️ 请输入辅助钱包私钥: {RESET}").strip()
    
    # 验证输入
    if not RPC_URL or not TAR_WALLET or not AID_WALLET_PRIVATE_KEY:
        raise ValueError(f"{RED}❌ 必要配置缺失，请重新运行程序{RESET}")
else:
    # 参数检查
    if not RPC_URL or not TAR_WALLET or not AID_WALLET_PRIVATE_KEY:
        raise ValueError(f"{RED}❌ .env 配置缺失，请检查 RPC_URL, TAR_WALLET_PRIVATE_KEY, AID_WALLET_PRIVATE_KEY{RESET}")

# 全局变量
w3 = None
private_w3 = None
CHAIN_ID = None
aid_wallet = None
tar_wallet = None
TOKEN_CONTRACT = None
token_contract = None

def get_token_contract():
    """获取代币合约地址"""
    print_section_header("合约配置", "📄")
    while True:
        try:
            contract_address = input(f"{YELLOW}✍️ 请输入代币合约地址: {RESET}").strip()
            if not contract_address:
                print_warning_box("输入错误", "⚠️ 合约地址不能为空，请重新输入")
                continue
            
            # 验证地址格式
            if not Web3.is_address(contract_address):
                print_warning_box("地址格式错误", "⚠️请输入有效的以太坊地址")
                continue
            
            # 转换为 Checksum 格式
            contract_address = Web3.to_checksum_address(contract_address)
            
            # 验证合约是否存在
            try:
                code = w3.eth.get_code(contract_address)
                if code == b'':
                    print_warning_box("合约验证", "⚠️ 该地址没有合约代码，可能不是合约地址")
                else:
                    print_success_box("合约验证", f"📜 合约代码存在，大小: {len(code)} 字节")
            except Exception as e:
                print_warning_box("合约检查", f"⚠️ 无法检查合约状态: {e}")
            
            return contract_address
            
        except Exception as e:
            print_error_box("地址错误", f"❌ 地址验证失败: {e}")
            continue

def initialize_token_contract():
    """初始化代币合约"""
    global TOKEN_CONTRACT, token_contract
    
    # 读取 ABI
    abi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ABI.json')
    try:
        with open(abi_path, "r") as abi_file:
            token_abi = json.load(abi_file)
        print_success_box("加载ABI文件", f"🧾 成功加载 ABI 文件: {os.path.basename(abi_path)}")
    except FileNotFoundError:
        print_error_box("文件错误", f"❌ 找不到 ABI 文件: {abi_path}")
        return False
    except json.JSONDecodeError:
        print_error_box("格式错误", "❌ ABI 文件格式错误")
        return False
    
    # 获取合约地址
    TOKEN_CONTRACT = get_token_contract()
    
    # 创建合约实例
    token_contract = w3.eth.contract(address=TOKEN_CONTRACT, abi=token_abi)
    
    # 快速验证合约是否有效
    try:
        # 尝试调用 name() 函数来验证合约
        token_name = token_contract.functions.name().call()
        print_success_box("合约检测", f"🎉 检测成功！代币名称: {token_name}")
    except Exception as e:
        print_warning_box("检测警告", f"⚠️ 合约检测失败，但继续执行: {e}")
    
    return True

def get_user_choice():
    """获取用户选择的操作类型"""
    print_section_header("操作选择", "🖐️")
                         
    print(f"{BLUE}                  🪙 ERC20 代币操作 {RESET}")
    print()
    print(f"{MAGENTA}┌─ 1. 💸 转账全部余额 ─────────────────────────────────────┐{RESET}")
    print(f"{MAGENTA}│   📤 将目标钱包中的所有代币余额转账到指定钱包地址        │{RESET}")
    print(f"{MAGENTA}└──────────────────────────────────────────────────────────┘{RESET}")
    
    print(f"{MAGENTA}┌─ 2. 💰 批量转账 ─────────────────────────────────────────┐{RESET}")
    print(f"{MAGENTA}│   📤 向多个地址批量转账代币                              │{RESET}")
    print(f"{MAGENTA}└──────────────────────────────────────────────────────────┘{RESET}")
    
    print(f"{MAGENTA}┌─ 3. 🔐 授权代币 ─────────────────────────────────────────┐{RESET}")
    print(f"{MAGENTA}│   🔑 授权指定地址使用特定数量的代币                      │{RESET}")
    print(f"{MAGENTA}└──────────────────────────────────────────────────────────┘{RESET}")
    
    print(f"{MAGENTA}┌─ 4. 📈 增加授权额度 ─────────────────────────────────────┐{RESET}")
    print(f"{MAGENTA}│   ➕ 在现有授权基础上增加代币使用额度                    │{RESET}")
    print(f"{MAGENTA}└──────────────────────────────────────────────────────────┘{RESET}")
    
    print(f"{MAGENTA}┌─ 5. ❌ 撤销授权 ─────────────────────────────────────────┐{RESET}")
    print(f"{MAGENTA}│   🚫 撤销指定地址的代币授权                              │{RESET}")
    print(f"{MAGENTA}└──────────────────────────────────────────────────────────┘{RESET}")
    
    # NFT 操作区域
    print(f"{BLUE}                      🎨 NFT 操作 {RESET}")
    print()
    print(f"{MAGENTA}┌─ 6. 🎨 设置全部 NFT 授权 ────────────────────────────────┐{RESET}")
    print(f"{MAGENTA}│   🔑 设置指定地址对所有 NFT 的授权状态                   │{RESET}")
    print(f"{MAGENTA}└──────────────────────────────────────────────────────────┘{RESET}")
    
    print(f"{MAGENTA}┌─ 7. 🎭 转移全部 NFT ─────────────────────────────────────┐{RESET}")
    print(f"{MAGENTA}│   📤 将目标钱包中的所有 NFT 转移到指定地址               │{RESET}")
    print(f"{MAGENTA}└──────────────────────────────────────────────────────────┘{RESET}")
    
    while True:
        try:
            choice = input(f"\n{YELLOW}👉 请输入选择 (1-7): {RESET}").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return choice
            else:
                print_error_box("输入错误", "❌ 无效选择，请输入 1-7")
        except KeyboardInterrupt:
            print_error_box("操作取消", "❌ 用户取消了操作")
            exit(0)

def get_approval_amount():
    """获取授权金额"""
    print_info_box("授权配置", "💳 请输入授权金额信息")
    while True:
        try:
            amount = input(f"{YELLOW}💰 授权金额 (输入 'max' 表示最大授权): {RESET}").strip()
            if amount.lower() == 'max':
                print_success_box("授权设置", "使用最大授权额度")
                return 'max'
            else:
                amount_float = float(amount)
                if amount_float > 0:
                    print_success_box("授权设置", f"授权金额: {amount_float}")
                    return amount_float
                else:
                    print_error_box("输入错误", "❌ 金额必须大于 0")
        except ValueError:
            print_error_box("格式错误", "❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print_error_box("操作取消", "❌ 用户取消了操作")
            exit(0)

def get_spender_address():
    """获取被授权地址"""
    print_info_box("地址配置", "🎯 请输入被授权的钱包地址信息")
    while True:
        try:
            spender = input(f"{YELLOW}✍️ 被授权地址 (留空则使用辅助钱包地址): {RESET}").strip()
            if not spender:
                print_success_box("地址设置", f"地址: {aid_wallet.address}")
                return aid_wallet.address
            else:
                # 验证地址格式
                checksum_address = Web3.to_checksum_address(spender)
                print_success_box("地址设置", f"🎯 被授权地址: {checksum_address}")
                return checksum_address
        except ValueError:
            print_error_box("格式错误", "❌ 无效的以太坊地址格式")
        except KeyboardInterrupt:
            print_error_box("操作取消", "❌ 用户取消了操作")
            exit(0)

def send_transaction(tx_data, description):
    """通用交易发送函数"""
    print_section_header(f"{description}操作", "🚀")
    
    nonce_tar = w3.eth.get_transaction_count(tar_wallet.address)
    nonce_aid_wallet = w3.eth.get_transaction_count(aid_wallet.address)

    # 获取动态 gas 价格并提高 1.2 倍
    gas_price = int(w3.eth.gas_price * 1.2)
    
    # 预估 gas 限制
    try:
        estimated_gas = w3.eth.estimate_gas({
            "from": tar_wallet.address,
            "to": TOKEN_CONTRACT,
            "data": tx_data,
        })
        print_info_box("预估Gas限制", f"⚡ {estimated_gas} 单位")
    except Exception as e:
        print_warning_box("Gas 预估失败", f"❌ 预估 gas 失败: {e}")
        # 使用更保守的 Gas 限制
        estimated_gas = 200000  # 增加默认 Gas 限制
        print_info_box("使用默认", f"⚡ 使用默认 Gas 限制: {estimated_gas} 单位")

    gas_limit = int(estimated_gas * 1.2)  # 增加 20% 的缓冲  
    gas_fee = gas_price * gas_limit
    print_info_box("费用预估", f"💰 预计 Gas 费用: {gas_fee} Wei")

    # 检查目标钱包的原生代币余额是否足够支付 gas 费
    tar_balance = w3.eth.get_balance(tar_wallet.address)
    print_info_box("余额检查", f"🪙 目标钱包的原生代币余额: {tar_balance} Wei")
    
    if tar_balance < gas_fee:
        deficit = gas_fee - tar_balance
        print_warning_box("余额不足", f"⚠️ 目标钱包的余额不足 {gas_fee} Wei，辅助钱包正在给目标钱包转入原始代币...")

        # 动态计算增加的资金，按 gas 费用的 3% 增加
        additional_funds = int(gas_fee * 0.03)
        fund_tx = {
            "to": tar_wallet.address,
            "value": deficit + additional_funds,
            "gas": 21000,
            "gasPrice": gas_price,
            "nonce": nonce_aid_wallet,
            "chainId": CHAIN_ID,
        }

        signed_fund_tx = w3.eth.account.sign_transaction(fund_tx, aid_wallet.key)
        fund_tx_hash = w3.eth.send_raw_transaction(signed_fund_tx.raw_transaction)

        print_info_box("资金转账", f"⏳ 等待原生代币转账确认... Tx Hash: {fund_tx_hash.hex()}")
        try:
            receipt = w3.eth.wait_for_transaction_receipt(fund_tx_hash, timeout=180)
            print_success_box("资金到账", "🎉 资金到账，继续执行操作...")
        except Exception as e:
            print_error_box("转账失败", f"❌ 资金转账失败: {e}")
            return False

    # 智能等待，检查余额是否已更新
    if tar_balance < gas_fee:
        print_info_box("等待确认", "⏳ 等待余额更新...")
        max_wait_time = 30  # 最大等待30秒
        wait_interval = 2   # 每2秒检查一次
        waited_time = 0
        
        while waited_time < max_wait_time:
            time.sleep(wait_interval)
            waited_time += wait_interval
            
            # 重新检查余额
            current_balance = w3.eth.get_balance(tar_wallet.address)
            if current_balance >= gas_fee:
                print_success_box("余额更新", f"♻️ 原生代币余额已更新: {current_balance} Wei")
                break
            else:
                print(f"{CYAN}⏳ 等待中... ({waited_time}/{max_wait_time}秒) 当前原生代币余额: {current_balance} Wei{RESET}")
        else:
            print_warning_box("等待超时", "⚠️ 等待原生代币余额更新超时，继续执行...")

    # 创建交易
    tx = {
        "to": TOKEN_CONTRACT,
        "data": tx_data,
        "gas": gas_limit,
        "gasPrice": gas_price,
        "nonce": nonce_tar,
        "chainId": CHAIN_ID,
    }
    
    signed_tx = w3.eth.account.sign_transaction(tx, tar_wallet.key)

    # 发送交易
    try:
        print_info_box("交易发送", f"🚀 {description}...")
        tx_hash = private_w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print_success_box("交易提交", f"🎉 交易已提交，Tx Hash: 0x{tx_hash.hex()}，等待确认...")

        # 等待交易确认
        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            if receipt.status == 1:
                print_info_box("交易详情", f"📊 Gas 使用: {receipt.gasUsed} / {gas_limit}")
                print_success_box("操作成功", f"🎉 {description}成功！")           
                return True
            else:
                print_error_box("交易失败", f"❌ {description}交易执行失败")
                print_info_box("失败原因", f"🔍 交易状态: {receipt.status} (0=失败, 1=成功)")
                return False
        except Exception as e:
            print_error_box("等待超时", f"❌ 交易等待超时: {e}")
            return False

    except Exception as e:
        print_error_box("发送失败", f"❌ 交易发送失败: {e}")
        # 尝试获取更详细的错误信息
        if "insufficient funds" in str(e).lower():
            print_info_box("错误分析", "💰 余额不足，请检查钱包余额")
        elif "nonce" in str(e).lower():
            print_info_box("错误分析", "🔄 Nonce 错误，请稍后重试")
        elif "gas" in str(e).lower():
            print_info_box("错误分析", "⚡ Gas 相关错误，请检查网络状态")
        else:
            print_info_box("错误分析", f"🔍 其他错误: {type(e).__name__}")
        return False

def transfer_tokens():
    """转账代币操作"""
    print_section_header("代币转账操作", "💸")
    print(f"{BLUE}⚠️ 请确认 {TOKEN_CONTRACT} 为 ERC20 合约，否则会转账失败{RESET}")
    
    # 查询目标钱包的代币余额
    token_balance = token_contract.functions.balanceOf(tar_wallet.address).call()
    decimals = token_contract.functions.decimals().call()
    formatted_balance = token_balance / (10 ** decimals)
    print_success_box("余额查询", f"🎉 目标钱包代币余额: {formatted_balance}")

    if token_balance == 0:
        print_error_box("余额不足", "❌ 目标钱包没有代币，退出...")
        return False

    # 获取转出地址
    print_info_box("转账配置", "🎯 请输入要转出的钱包地址")
    while True:
        try:
            transfer_address = input(f"{YELLOW}✍️ 转账到 (留空则使用辅助钱包地址): {RESET}").strip()
            if not transfer_address:
                transfer_address = aid_wallet.address
                break
            else:
                # 验证地址格式
                checksum_address = Web3.to_checksum_address(transfer_address)
                print_success_box("地址设置", f"🎯 转出地址: {checksum_address}")
                transfer_address = checksum_address
                break
        except ValueError:
            print_error_box("格式错误", "❌ 无效的以太坊地址格式")
        except KeyboardInterrupt:
            print_error_box("操作取消", "❌ 用户取消了操作")
            exit(0)

    print_info_box("转账信息", f"📤 将转账 {formatted_balance} 代币到 {transfer_address}")

    # 构建转账交易数据
    transfer_data = token_contract.functions.transfer(transfer_address, token_balance).build_transaction({
        "from": tar_wallet.address,
    })['data']
    
    return send_transaction(transfer_data, "代币转账")

def approve_tokens():
    """授权代币操作"""
    print_section_header("代币授权操作", "🔐")
    print(f"{BLUE}⚠️ 请确认 {TOKEN_CONTRACT} 为 ERC20 合约，否则会授权失败{RESET}")
    spender = get_spender_address()
    amount = get_approval_amount()
    
    if amount == 'max':
        # 使用最大 uint256 值
        amount = 2**256 - 1
        print(f"{BLUE}📝 使用最大授权额度: {amount}{RESET}")
    else:
        # 获取代币精度并转换为原始单位
        decimals = token_contract.functions.decimals().call()
        amount_raw = int(amount * (10 ** decimals))
        print(f"{BLUE}📝 授权金额: {amount}{RESET}")
        amount = amount_raw
    
    
    # 构建授权交易数据
    approve_data = token_contract.functions.approve(spender, amount).build_transaction({
        "from": tar_wallet.address,
    })['data']
    
    return send_transaction(approve_data, "代币授权")

def set_approval_for_all():
    """设置全部授权操作"""
    print_section_header("NFT 全部授权设置", "🎨")
    print(f"{BLUE}⚠️ 请确认 {TOKEN_CONTRACT} 为 NFT 合约，否则会授权失败{RESET}")
    
    try:
        # 检测NFT标准类型
        nft_type = detect_nft_standard()
        print_success_box("NFT标准检测", f"🎯 检测到合约标准: {nft_type}")
        
        if nft_type not in ["ERC721", "ERC1155"]:
            print_error_box("NFT标准不支持", f"❌ 不支持的NFT标准: {nft_type}")
            return False
        
        spender = get_spender_address()
        
        # 询问是否启用全部授权
        print_info_box("授权状态", "🔐 请选择授权状态")
        while True:
            try:
                approval_status = input(f"{YELLOW}🎯 是否启用全部授权？(y/n): {RESET}").strip().lower()
                if approval_status in ['y', 'yes', '是']:
                    approved = True
                    print_success_box("授权状态", "✅ 启用全部授权")
                    break
                elif approval_status in ['n', 'no', '否']:
                    approved = False
                    print_success_box("授权状态", "❌ 禁用全部授权")
                    break
                else:
                    print_error_box("输入错误", "请输入 y 或 n")
            except KeyboardInterrupt:
                print_error_box("操作取消", "❌ 用户取消了操作")
                exit(0)
        
        # 检查当前授权状态
        try:
            current_approval = token_contract.functions.isApprovedForAll(tar_wallet.address, spender).call()
            if current_approval == approved:
                if approved:
                    print_warning_box("授权状态", f"⚠️ 地址 {spender} 已经被授权，无需重复操作")
                else:
                    print_warning_box("授权状态", f"⚠️ 地址 {spender} 已经被撤销授权，无需重复操作")
                return True
            else:
                status_text = "已授权" if current_approval else "未授权"
                print_info_box("当前状态", f"📊 地址 {spender} 当前状态: {status_text}")
        except Exception as e:
            print_warning_box("状态检查", f"⚠️ 无法检查当前授权状态: {e}")
        
        # 构建 setApprovalForAll 交易数据
        approval_data = token_contract.functions.setApprovalForAll(spender, approved).build_transaction({
            "from": tar_wallet.address,
        })['data']
        
        operation_text = f"设置{nft_type}全部授权"
        return send_transaction(approval_data, operation_text)
        
    except Exception as e:
        print_error_box("授权失败", f"❌ 设置全部授权失败: {e}")
        return False

def transfer_all_nfts():
    """转移全部NFT操作"""
    print_section_header("转移全部NFT", "🎭")
    print(f"{BLUE}⚠️ 请确认 {TOKEN_CONTRACT} 为 NFT 合约，否则会转移失败{RESET}")
    
    # 获取转移目标地址
    print_info_box("转移配置", "🎯 请输入转移目标地址")
    while True:
        try:
            transfer_address = input(f"{YELLOW}✍️ 转移到 (留空则使用辅助钱包地址): {RESET}").strip()
            if not transfer_address:
                print_success_box("地址设置", f"🎯 转移目标地址: {aid_wallet.address}")
                transfer_address = aid_wallet.address
                break
            else:
                # 验证地址格式
                checksum_address = Web3.to_checksum_address(transfer_address)
                print_success_box("地址设置", f"🎯 转移目标地址: {checksum_address}")
                transfer_address = checksum_address
                break
        except ValueError:
            print_error_box("格式错误", "❌ 无效的以太坊地址格式")
        except KeyboardInterrupt:
            print_error_box("操作取消", "❌ 用户取消了操作")
            exit(0)
    
    try:
        # 检测NFT标准类型
        nft_type = detect_nft_standard()
        
        if nft_type == "ERC721":
            return transfer_erc721_nfts(transfer_address)
        elif nft_type == "ERC1155":
            return transfer_erc1155_nfts(transfer_address)
        else:
            print_error_box("NFT标准不支持", f"❌ 不支持的NFT标准: {nft_type}")
            return False
        
    except Exception as e:
        print_error_box("转移失败", f"❌ 转移全部NFT失败: {e}")
        return False

def detect_nft_standard():
    """检测NFT合约标准"""
    try:
        # 检查合约是否支持ERC721特有的方法
        has_erc721_methods = False
        has_erc1155_methods = False
        
        # 检查ERC721方法：tokenOfOwnerByIndex
        try:
            token_contract.functions.tokenOfOwnerByIndex(tar_wallet.address, 0).call()
            has_erc721_methods = True
        except Exception:
            pass
        
        # 检查ERC1155方法：balanceOf(address, id)
        try:
            token_contract.functions.balanceOf(tar_wallet.address, 0).call()
            has_erc1155_methods = True
        except Exception:
            pass
        
        # 根据检测结果判断标准
        if has_erc721_methods and not has_erc1155_methods:
            return "ERC721"
        elif has_erc1155_methods and not has_erc721_methods:
            return "ERC1155"
        elif has_erc721_methods and has_erc1155_methods:
            # 如果同时支持两种方法，优先使用ERC721
            print_warning_box("标准检测", "⚠️ 合约同时支持ERC721和ERC1155方法，优先使用ERC721")
            return "ERC721"
        else:
            # 如果都不支持，尝试ERC721的balanceOf(address)
            try:
                token_contract.functions.balanceOf(tar_wallet.address).call()
                return "ERC721"
            except Exception:
                print_warning_box("标准检测", "⚠️ 无法确定NFT标准，默认使用ERC721")
                return "ERC721"
            
    except Exception as e:
        print_warning_box("标准检测", f"⚠️ 检测过程中发生错误，默认使用ERC721: {e}")
        return "ERC721"

def transfer_erc721_nfts(transfer_address):
    """转移ERC721 NFT"""
    try:
        # 查询目标钱包拥有的NFT数量
        nft_balance = token_contract.functions.balanceOf(tar_wallet.address).call()
        print_success_box("ERC721余额查询", f"🎭 目标钱包拥有的ERC721 NFT数量: {nft_balance}")
        
        if nft_balance == 0:
            print_error_box("余额不足", "❌ 目标钱包没有ERC721 NFT，无法进行转移")
            return False
        
        # 获取所有NFT的Token ID
        nft_list = []
        
        # 首先尝试使用tokenOfOwnerByIndex方法
        print_info_box("Token ID自动获取", "🔍 正在自动获取NFT Token IDs...")
        
        for i in range(nft_balance):
            try:
                token_id = token_contract.functions.tokenOfOwnerByIndex(tar_wallet.address, i).call()
                nft_list.append(token_id)
                print_success_box("Token ID自动获取", f"🆔 获取到Token ID: {token_id}")
            except Exception as e:
                print_warning_box("Token ID自动获取失败", f"⚠️ 无法获取第 {i+1} 个NFT的Token ID: {e}")
                continue
        
        # 如果tokenOfOwnerByIndex方法失败，尝试其他方法
        if not nft_list:
            print_warning_box("备用方案", "⚠️ tokenOfOwnerByIndex方法失败，尝试其他获取方式...")
            
            # 尝试使用tokensOfOwner方法（如果存在）
            try:
                tokens = token_contract.functions.tokensOfOwner(tar_wallet.address).call()
                if tokens:
                    nft_list = tokens
                    print_success_box("备用方案", f"🆔 通过tokensOfOwner获取到 {len(tokens)} 个Token ID")
            except Exception:
                pass
            
            # 如果还是失败，尝试手动扫描Token ID
            if not nft_list:
                print_warning_box("手动扫描", "⚠️ 尝试手动扫描Token ID...")
                max_scan = 10000  # 最大扫描范围
                
                for token_id in range(max_scan):
                    try:
                        # 检查是否拥有这个Token ID
                        owner = token_contract.functions.ownerOf(token_id).call()
                        if owner.lower() == tar_wallet.address.lower():
                            nft_list.append(token_id)
                            print_success_box("手动扫描", f"🆔 扫描到Token ID: {token_id}")
                    except Exception:
                        continue
                    
                    # 如果找到了足够的Token ID，停止扫描
                    if len(nft_list) >= nft_balance:
                        break
        
        if not nft_list:
            print_error_box("NFT获取失败", "❌ 无法获取任何ERC721 NFT的Token ID")
            print_info_box("可能原因", "💡 请检查：1. 合约是否为标准ERC721 2. 钱包是否真的拥有这些NFT 3. 合约是否实现了必要的接口")
            return False
        
        print_success_box("NFT列表", f"📋 找到 {len(nft_list)} 个ERC721 NFT，Token IDs: {nft_list}")
        
        # 确认转移
        print_info_box("转移确认", "🔍 请确认以下转移信息:")
        print(f"    {CYAN}转移目标地址: {RESET}{transfer_address}")
        print(f"    {CYAN}NFT数量: {RESET}{len(nft_list)}")
        print(f"    {CYAN}Token IDs: {RESET}{nft_list}")
        
        confirm = input(f"\n{YELLOW}✍️ 确认执行转移全部ERC721 NFT？(y/n): {RESET}").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            print_warning_box("操作取消", "❌ 用户取消了ERC721 NFT转移")
            return False
        
        # 执行批量转移
        success_count = 0
        total_count = len(nft_list)
        
        for i, token_id in enumerate(nft_list, 1):
            print_progress_bar(i, total_count, f"⏳ 转移ERC721 NFT进度 ({i}/{total_count})")
            
            try:
                # 构建转移ERC721 NFT交易数据
                transfer_data = token_contract.functions.transferFrom(tar_wallet.address, transfer_address, token_id).build_transaction({
                    "from": tar_wallet.address,
                })['data']
                
                if send_transaction(transfer_data, f"🎭 转移ERC721 NFT Token ID: {token_id}"):
                    success_count += 1
                else:
                    print_warning_box("转移失败", f"⚠️ 转移ERC721 NFT Token ID: {token_id} 失败")
                    
            except Exception as e:
                print_error_box("转移异常", f"❌ 转移ERC721 NFT Token ID: {token_id} 时发生异常: {e}")
        
        print_success_box("转移完成", f"🎉 ERC721 NFT转移完成！成功: {success_count}/{total_count}")
        return success_count == total_count
        
    except Exception as e:
        print_error_box("转移失败", f"❌ 转移ERC721 NFT失败: {e}")
        return False

def transfer_erc1155_nfts(transfer_address):
    """转移ERC1155 NFT"""
    try:
        # 获取用户拥有的所有Token ID
        print_info_box("ERC1155代币检测", "🔍 正在检测ERC1155 Token IDs...")
        
        # 询问用户扫描范围
        print_info_box("扫描配置", "⚙️ 请选择扫描范围")
        try:
            scan_range = input(f"{YELLOW}🔍 扫描Token ID范围 (默认1000，输入数字或回车使用默认): {RESET}").strip()
            if scan_range:
                max_check = int(scan_range)
                if max_check <= 0 or max_check > 10000:
                    print_warning_box("范围调整", "⚠️ 范围无效，使用默认值1000")
                    max_check = 1000
            else:
                max_check = 1000
        except ValueError:
            print_warning_box("范围调整", "⚠️ 输入无效，使用默认值1000")
            max_check = 1000
        except KeyboardInterrupt:
            print_error_box("操作取消", "❌ 用户取消了操作")
            return False
        
        # 尝试获取常见的Token ID范围
        token_ids = []
        consecutive_failures = 0  # 连续失败计数
        max_consecutive_failures = 50  # 最大连续失败次数
        
        print(f"{CYAN}⏳ 正在扫描Token ID范围 0-{max_check-1}...{RESET}")
        
        for token_id in range(max_check):
            # 每100个Token ID显示一次进度
            if token_id % 100 == 0:
                print(f"{CYAN}⏳ 扫描进度: {token_id}/{max_check} ({token_id/max_check*100:.1f}%){RESET}")
            
            try:
                balance = token_contract.functions.balanceOf(tar_wallet.address, token_id).call()
                if balance > 0:
                    token_ids.append((token_id, balance))
                    print_success_box("Token数量检测", f"🎯 发现Token ID: {token_id}, 数量: {balance}")
                    consecutive_failures = 0  # 重置连续失败计数
                else:
                    consecutive_failures += 1
            except KeyboardInterrupt:
                print(f"\n{YELLOW}⚠️ 用户中断扫描{RESET}")
                break
            except Exception:
                # 如果某个Token ID不存在，继续检查下一个
                consecutive_failures += 1
                continue
            
            # 如果连续失败次数过多，提前退出
            if consecutive_failures >= max_consecutive_failures:
                print(f"{YELLOW}⚠️ 连续 {max_consecutive_failures} 次未发现Token，提前结束扫描{RESET}")
                break
        
        print(f"{GREEN}✅ 扫描完成！{RESET}")
        
        if not token_ids:
            print_error_box("余额不足", "❌ 目标钱包没有ERC1155 Token，无法进行转移")
            return False
        
        print_success_box("Token种类列表", f"📋 找到 {len(token_ids)} 种ERC1155 Token")
        
        # 确认转移
        print_info_box("转移确认", "🔍 请确认以下转移信息:")
        print(f"    {CYAN}转移目标地址: {RESET}{transfer_address}")
        print(f"    {CYAN}Token种类: {RESET}{len(token_ids)}")
        for token_id, balance in token_ids:
            print(f"    {CYAN}Token ID {token_id}: {RESET}{balance} 个")
        
        confirm = input(f"\n{YELLOW}✍️ 确认执行转移全部ERC1155 Token？(y/n): {RESET}").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            print_warning_box("操作取消", "❌ 用户取消了ERC1155 Token转移")
            return False
        
        # 执行批量转移
        success_count = 0
        total_count = len(token_ids)
        
        for i, (token_id, balance) in enumerate(token_ids, 1):
            print_progress_bar(i, total_count, f"⏳ 转移ERC1155 Token进度 ({i}/{total_count})")
            
            try:
                # 构建转移ERC1155 Token交易数据
                transfer_data = token_contract.functions.safeTransferFrom(
                    tar_wallet.address, 
                    transfer_address, 
                    token_id, 
                    balance, 
                    b''  # 空数据
                ).build_transaction({
                    "from": tar_wallet.address,
                })['data']
                
                if send_transaction(transfer_data, f"🎭 转移ERC1155 Token ID: {token_id}, 数量: {balance}"):
                    success_count += 1
                else:
                    print_warning_box("转移失败", f"⚠️ 转移ERC1155 Token ID: {token_id} 失败")
                    
            except Exception as e:
                print_error_box("转移异常", f"❌ 转移ERC1155 Token ID: {token_id} 时发生异常: {e}")
        
        print_success_box("转移完成", f"🎉 ERC1155 Token转移完成！成功: {success_count}/{total_count}")
        return success_count == total_count
        
    except Exception as e:
        print_error_box("转移失败", f"❌ 转移ERC1155 Token失败: {e}")
        return False

def increase_allowance():
    print_section_header("增加授权额度", "📈")
    print(f"{BLUE}⚠️ 请确认 {TOKEN_CONTRACT} 为 ERC20 合约，否则会授权失败{RESET}")
    """增加授权额度操作"""
    spender = get_spender_address()
    amount = get_approval_amount()
    
    if amount == 'max':
        print(f"{RED}❌ increaseAllowance 不支持 'max' 参数，请输入具体金额{RESET}")
        return False
    
    # 获取代币精度并转换为原始单位
    decimals = token_contract.functions.decimals().call()
    amount_raw = int(amount * (10 ** decimals))
    print(f"{BLUE}✍️ 增加授权金额: {amount}{RESET}")
    print(f"{BLUE}✍️ 被授权地址: {spender}{RESET}")
    
    # 构建增加授权额度交易数据
    increase_data = token_contract.functions.increaseAllowance(spender, amount_raw).build_transaction({
        "from": tar_wallet.address,
    })['data']
    
    return send_transaction(increase_data, "增加授权额度")

def revoke_allowance():
    """撤销授权"""
    print_section_header("撤销授权", "❌")
    print(f"{BLUE}⚠️ 请确认 {TOKEN_CONTRACT} 为 ERC20 合约，否则会撤销失败{RESET}")
    
    spender = get_spender_address()
    
    try:
        # 先查询当前授权状态
        current_allowance = token_contract.functions.allowance(tar_wallet.address, spender).call()
        
        if current_allowance == 0:
            print_warning_box("无需撤销", f"⚠️ 地址 {spender} 当前没有被授权，无需撤销")
            return True
        
        decimals = token_contract.functions.decimals().call()
        formatted_allowance = current_allowance / (10 ** decimals)
        print_info_box("当前状态", f"💰 当前授权额度: {formatted_allowance}")
        print_info_box("撤销操作", f"❌ 将撤销地址 {spender} 的所有授权")
        
        # 构建撤销授权交易数据（设置为0）
        revoke_data = token_contract.functions.approve(spender, 0).build_transaction({
            "from": tar_wallet.address,
        })['data']
        
        return send_transaction(revoke_data, "撤销授权")
        
    except Exception as e:
        print_error_box("撤销失败", f"❌ 撤销授权失败: {e}")
        return False

def batch_transfer():
    """批量转账功能"""
    print_section_header("批量转账", "💰")
    print(f"{BLUE}⚠️ 请确认 {TOKEN_CONTRACT} 为 ERC20 合约，否则会转账失败{RESET}")
    
    # 查询目标钱包余额
    tar_balance = token_contract.functions.balanceOf(tar_wallet.address).call()
    decimals = token_contract.functions.decimals().call()
    formatted_balance = tar_balance / (10 ** decimals)
    print_success_box("余额查询", f"🎯 目标钱包的代币余额: {formatted_balance}")
    
    if tar_balance == 0:
        print_error_box("余额不足", "❌ 目标钱包没有代币，无法进行批量转账")
        return False
    
    # 获取转账列表
    transfer_list = get_batch_transfer_list()
    if not transfer_list:
        print_warning_box("操作取消", "⚠️ 批量转账已取消")
        return False
    
    # 计算总转账金额
    total_amount = sum(amount for _, amount in transfer_list)
    print_info_box("转账统计", f"📊 总转账金额: {total_amount}")
    
    if total_amount > tar_balance:
        print_error_box("余额不足", f"❌ 总转账金额 {total_amount} 超过钱包余额 {tar_balance}")
        return False
    
    # 确认转账
    print_info_box("转账确认", "🔍 请确认以下转账信息:")
    for i, (address, amount) in enumerate(transfer_list, 1):
        formatted_amount = amount / (10 ** decimals)
        print(f"{CYAN}{i}. 地址: {RESET}{address}")
        print(f"{CYAN}   金额: {RESET}{formatted_amount}")
    
    confirm = input(f"\n{YELLOW}✍️ 确认执行批量转账？(y/n): {RESET}").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print_warning_box("操作取消", "❌ 用户取消了批量转账")
        return False
    
    # 执行批量转账
    success_count = 0
    total_count = len(transfer_list)
    
    for i, (address, amount) in enumerate(transfer_list, 1):
        print_progress_bar(i, total_count, f"⏳ 批量转账进度 ({i}/{total_count})")
        
        try:
            # 构建转账交易数据
            transfer_data = token_contract.functions.transfer(address, amount).build_transaction({
                "from": tar_wallet.address,
            })['data']
            
            if send_transaction(transfer_data, f"批量转账"):
                success_count += 1
            else:
                print_warning_box("转账失败", f"⚠️ 转账到 {address} 失败")
                
        except Exception as e:
            print_error_box("转账异常", f"❌ 转账到 {address} 时发生异常: {e}")
    
    print_success_box("转账完成", f"🎉 批量转账完成！成功: {success_count}/{total_count}")
    return success_count == total_count

def get_batch_transfer_list():
    """获取批量转账列表"""
    transfer_list = []
    
    print(f"{MAGENTA}   - 请输入转账地址和金额，格式为 '地址:金额'{RESET}")
    print(f"{MAGENTA}   - 每行一个转账，输入空行结束{RESET}")
    print(f"{MAGENTA}   - 示例: 0x1234567890abcdef1234567890abcdef12345678:1000{RESET}")
    
    while True:
        try:
            line = input(f"{YELLOW}✍️ 请输入转账信息 (地址:金额): {RESET}").strip()
            
            if not line:  # 空行结束输入
                break
            
            if ':' not in line:
                print_error_box("格式错误", "❌ 格式错误，请使用 '地址:金额' 格式")
                continue
            
            address, amount_str = line.split(':', 1)
            address = address.strip()
            amount_str = amount_str.strip()
            
            # 验证地址格式
            try:
                checksum_address = Web3.to_checksum_address(address)
            except ValueError:
                print_error_box("地址错误", f"❌ 无效的以太坊地址: {address}")
                continue
            
            # 验证金额
            try:
                amount = float(amount_str)
                if amount <= 0:
                    print_error_box("金额错误", f"❌ 金额必须大于0: {amount_str}")
                    continue
            except ValueError:
                print_error_box("金额错误", f"❌ 无效的金额: {amount_str}")
                continue
            
            # 获取代币精度并转换为原始单位
            decimals = token_contract.functions.decimals().call()
            amount_raw = int(amount * (10 ** decimals))
            
            transfer_list.append((checksum_address, amount_raw))
            print_success_box("添加成功", f"🎉 已添加转账: {checksum_address} -> {amount}")
            
        except KeyboardInterrupt:
            print_error_box("操作取消", "❌ 用户取消了输入")
            return None
    
    if not transfer_list:
        print_warning_box("列表为空", "⚠️ 没有输入任何转账信息")
        return None
    
    return transfer_list

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

def main():
    """主函数"""
    global w3, private_w3, CHAIN_ID, aid_wallet, tar_wallet
    
    print_section_header("网络初始化", "🌐")
    
    # 连接 Web3
    print_info_box("网络连接", "🛜 正在连接网络...")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print_error_box("连接失败", "❌ 无法连接到 RPC，请检查 RPC_URL 是否正确")
        return
    
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
    
    # 显示配置信息
    print_section_header("系统配置", "⚙️")
    print(f"    {CYAN}🎯 目标钱包: {RESET}{tar_wallet.address}")
    print(f"    {CYAN}🆕 辅助钱包: {RESET}{aid_wallet.address}")
    print(f"    {CYAN}🌐 网络ID: {RESET}{CHAIN_ID}")
    
    # 直接初始化代币合约
    if not initialize_token_contract():
        print_error_box("初始化失败", "❌ 代币合约初始化失败，退出程序")
        return
    
    # 主操作循环
    while True:
        choice = get_user_choice()
        
        if choice == '1':
            transfer_tokens()
        elif choice == '2':
            batch_transfer()
        elif choice == '3':
            approve_tokens()
        elif choice == '4':
            increase_allowance()
        elif choice == '5':
            revoke_allowance()
        elif choice == '6':
            set_approval_for_all()
        elif choice == '7':
            transfer_all_nfts()
        else:
            print(f"{RED}❌ 无效选择{RESET}")
        
        # 询问是否继续执行其他操作
        print_section_header("操作完成", "✅")
        while True:
            try:
                continue_choice = input(f"{YELLOW}🔄 是否需要执行其他操作？(y/n): {RESET}").strip().lower()
                if continue_choice in ['y', 'yes', '是']:
                    print_success_box("继续操作", "🔄 准备执行下一个操作...")
                    print(f"{MAGENTA}{'☆'*60}{RESET}")
                    break
                elif continue_choice in ['n', 'no', '否']:
                    print_success_box("程序结束", "👋 感谢使用，程序即将退出...")
                    return
                else:
                    print_error_box("输入错误", "❌ 请输入 y 或 n")
            except KeyboardInterrupt:
                print_error_box("操作取消", "❌ 用户取消了操作")
                return

if __name__ == "__main__":
    main()
