from termcolor import colored

from .config import *

def get_action():
    print(colored("🖐️ 请选择选项:", 'light_yellow'))
    print(colored("1. 💲 -获取钱包中所有EVM链的代币余额", 'light_blue'))
    print(colored("2. 🪙 -仅获取特定代币的余额", 'light_blue'))
    print(colored("3. 📖 -帮助", 'light_blue'))
    print(colored("4. 📤 -退出", 'light_blue'))
    
    while True:
        choice = input(colored("请输入选项 (1-4): ", 'yellow')).strip()
        if choice == "1":
            return "💲 -获取钱包中所有EVM链的代币余额"
        elif choice == "2":
            return "🪙 -仅获取特定代币的余额"
        elif choice == "3":
            return "📖 -帮助"
        elif choice == "4":
            return "📤 -退出"
        else:
            print(colored("❌ 无效选项，请重新输入", 'red'))

def select_chains(chains):
    print(colored("💁‍♀️  选择您想要获取余额的网络:", 'light_yellow'))
    print(colored("0. 所有 EVM 网络", 'light_blue'))
    for i, chain in enumerate(chains, 1):
        print(colored(f"{i}. {chain}", 'light_blue'))
    
    while True:
        try:
            choice = input(colored("请输入选项 (0 表示所有网络，多个选项用逗号分隔): ", 'yellow')).strip()
            if choice == "0":
                return chains
            
            selected_indices = [int(x.strip()) for x in choice.split(',')]
            selected_chains = []
            for idx in selected_indices:
                if 1 <= idx <= len(chains):
                    selected_chains.append(chains[idx-1])
            
            if selected_chains:
                return selected_chains
            else:
                print(colored("❌ 无效选项，请重新输入", 'red'))
        except ValueError:
            print(colored("❌ 输入格式错误，请重新输入", 'red'))

def get_ticker():
    ticker = input(colored("✍️  输入代币名称（Symbol）: ", 'yellow')).strip()
    return ticker.upper() if ticker else ""

def get_minimal_amount_in_usd():
    while True:
        min_amount = input(colored("✍️  请输入最小金额（默认值：0.01美元）: ", 'yellow')).strip()
        if not min_amount:
            min_amount = "0.01"
        
        try:
            min_amount = float(min_amount)
            break
        except:
            logger.error('❌  错误！输入无效')
    
    if min_amount == 0:
        min_amount = -1
    return min_amount

def get_num_of_threads():
    while True:
        num_of_threads = input(colored("✍️  工作线程数量（如果你有超过100个地址，请只设置1个线程）: ", 'yellow')).strip()
        if not num_of_threads:
            num_of_threads = "1"
        
        try:
            num_of_threads = int(num_of_threads)
            break
        except:
            logger.error('❌  错误！输入无效')
    
    if num_of_threads == 0:
        num_of_threads = 3
    return num_of_threads
