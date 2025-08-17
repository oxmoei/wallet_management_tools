#!/usr/bin/env python3
"""
ERC20授权管理工具使用示例
"""

from module.manager import ERC20AuthManager
from module.config import Config
import getpass

def show_menu():
    """显示主菜单"""
    print("\n=== ERC20授权管理工具 ===")
    print("1. 查询授权")
    print("2. 撤销授权")
    print("3. 查看支持的链")
    print("4. 退出")
    print("=" * 30)

def get_chain_selection():
    """获取用户选择的链"""
    chains = Config.get_supported_chains()
    print("\n支持的链:")
    for i, chain in enumerate(chains, 1):
        chain_info = Config.get_chain_info(chain)
        print(f"{i}. {chain_info['name']} (Chain ID: {chain_info['chain_id']})")
    
    while True:
        try:
            choice = input(f"\n请选择链 (1-{len(chains)}): ").strip()
            chain_index = int(choice) - 1
            if 0 <= chain_index < len(chains):
                return chains[chain_index]
            else:
                print("无效选择，请重新输入")
        except ValueError:
            print("请输入有效的数字")

def query_approvals():
    """查询授权功能"""
    print("\n=== 查询授权 ===")
    
    try:
        # 选择链
        chain = get_chain_selection()
        print(f"\n已选择链: {Config.get_chain_info(chain)['name']}")
        
        # 输入地址
        address = input("请输入要查询的地址 (留空使用默认钱包地址): ").strip()
        if not address:
            # 需要私钥来获取钱包地址
            private_key = getpass.getpass("请输入私钥 (用于获取钱包地址): ").strip()
            if not private_key:
                print("私钥不能为空")
                return
            
            # 临时设置环境变量
            import os
            os.environ['WALLET_PRIVATE_KEY'] = private_key
            
            # 初始化管理器
            manager = ERC20AuthManager(chain)
            address = manager.wallet_address
            print(f"使用钱包地址: {address}")
        else:
            # 验证地址格式
            from web3 import Web3
            try:
                address = Web3.to_checksum_address(address)
            except:
                print("无效的地址格式")
                return
            
            # 初始化管理器（不需要私钥）
            manager = ERC20AuthManager(chain)
        
        # 检查网络连接
        if not manager.check_network_status():
            print("网络连接失败，请检查配置")
            return
        
        # 查询授权
        approvals = manager.query_approvals(address)
        
        if approvals:
            print(f"\n总共发现 {len(approvals)} 个授权")
        else:
            print("\n未发现任何授权")
            
    except Exception as e:
        print(f"查询授权失败: {e}")

def revoke_approval():
    """撤销授权功能"""
    print("\n=== 撤销授权 ===")
    
    try:
        # 输入私钥
        private_key = getpass.getpass("请输入私钥: ").strip()
        if not private_key:
            print("私钥不能为空")
            return
        
        # 临时设置环境变量
        import os
        os.environ['WALLET_PRIVATE_KEY'] = private_key
        
        # 选择链
        chain = get_chain_selection()
        print(f"\n已选择链: {Config.get_chain_info(chain)['name']}")
        
        # 输入合约地址
        contract_address = input("请输入代币合约地址: ").strip()
        if not contract_address:
            print("合约地址不能为空")
            return
        
        # 验证地址格式
        from web3 import Web3
        try:
            contract_address = Web3.to_checksum_address(contract_address)
        except:
            print("无效的合约地址格式")
            return
        
        # 初始化管理器
        manager = ERC20AuthManager(chain)
        
        # 检查网络连接
        if not manager.check_network_status():
            print("网络连接失败，请检查配置")
            return
        
        # 显示钱包信息
        wallet_info = manager.get_wallet_info()
        print(f"\n钱包地址: {wallet_info['address']}")
        print(f"ETH余额: {wallet_info['balance_eth']:.6f}")
        
        # 获取代币信息
        try:
            token_info = manager.get_token_info(contract_address)
            print(f"代币信息: {token_info['name']} ({token_info['symbol']})")
        except Exception as e:
            print(f"获取代币信息失败: {e}")
            return
        
        # 查询当前授权
        print("\n正在查询当前授权...")
        approvals = manager.query_approvals(manager.wallet_address, [contract_address])
        
        if not approvals:
            print("该代币没有发现任何授权")
            return
        
        # 选择要撤销的授权
        print("\n请选择要撤销的授权:")
        for i, approval in enumerate(approvals, 1):
            print(f"{i}. {approval['token_symbol']} -> {approval['spender']}")
            print(f"   金额: {approval['allowance_formatted']}")
        
        while True:
            try:
                choice = input(f"\n请选择要撤销的授权 (1-{len(approvals)}): ").strip()
                approval_index = int(choice) - 1
                if 0 <= approval_index < len(approvals):
                    selected_approval = approvals[approval_index]
                    break
                else:
                    print("无效选择，请重新输入")
            except ValueError:
                print("请输入有效的数字")
        
        # 确认撤销
        confirm = input(f"\n确认撤销 {selected_approval['token_symbol']} 对 {selected_approval['spender']} 的授权? (y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消撤销操作")
            return
        
        # 执行撤销
        print("\n正在撤销授权...")
        tx_hash = manager.revoke_approval(
            selected_approval['token_address'],
            selected_approval['spender'],
            manager.wallet_address
        )
        
        if tx_hash:
            print(f"撤销授权成功！交易哈希: {tx_hash}")
            chain_info = Config.get_chain_info(chain)
            print(f"可在 {chain_info['explorer']}/tx/{tx_hash} 查看交易详情")
        
    except Exception as e:
        print(f"撤销授权失败: {e}")

def show_supported_chains():
    """显示支持的链"""
    print("\n=== 支持的链 ===")
    chains = Config.get_supported_chains()
    for chain in chains:
        chain_info = Config.get_chain_info(chain)
        print(f"- {chain_info['name']} (Chain ID: {chain_info['chain_id']})")
        print(f"  区块浏览器: {chain_info['explorer']}")

def main():
    """主函数"""
    print("欢迎使用 ERC20授权管理工具！")
    
    while True:
        show_menu()
        
        choice = input("请选择操作 (1-4): ").strip()
        
        if choice == '1':
            query_approvals()
        elif choice == '2':
            revoke_approval()
        elif choice == '3':
            show_supported_chains()
        elif choice == '4':
            print("感谢使用，再见！")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()
