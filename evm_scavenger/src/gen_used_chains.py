import os
from dotenv import load_dotenv
import sys

# 保证可以import到gen_used_chains.py
sys.path.append(os.path.join(os.path.dirname(__file__), '../../debank_checker'))
from used_chains_checker import run_with_wallets

# 加载.env
load_dotenv()
address = os.getenv('FROM_ADDRESS')
if not address:
    print('未在.env中找到 FROM_ADDRESS 变量！')
    exit(1)

print("""
\033[94m╔═╗╔═╗╔╗╔╔═╗╦═╗╔═╗╔╦╗╔═╗  ╦ ╦╔═╗╔═╗╔╦╗  ╔═╗╦ ╦╔═╗╦╔╗╔╔═╗
║ ╦║╣ ║║║║╣ ╠╦╝╠═╣ ║ ║╣   ║ ║╚═╗║╣  ║║  ║  ╠═╣╠═╣║║║║╚═╗
╚═╝╚═╝╝╚╝╚═╝╩╚═╩ ╩ ╩ ╚═╝  ╚═╝╚═╝╚═╝═╩╝  ╚═╝╩ ╩╩ ╩╩╝╚╝╚═╝\033[0m
""")

run_with_wallets([address.strip().lower()]) 