"""
ERC20授权管理器
主要功能类，整合所有功能
"""

from typing import Dict, List, Optional
from web3 import Web3
from .config import Config
from .erc20_contract import ERC20Contract
from .approval_scanner import ApprovalScanner

class ERC20AuthManager:
    """ERC20授权管理器"""
    
    def __init__(self, chain: str = None):
        """
        初始化授权管理器
        
        Args:
            chain: 链名称，如果为None则使用默认链
        """
        if chain is None:
            chain = Config.get_default_chain()
        
        self.chain = chain
        self.rpc_url = Config.get_rpc_url(chain)
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.private_key = Config.get_wallet_private_key()
        self.wallet_address = self.web3.eth.account.from_key(self.private_key).address
        
        # 初始化扫描器
        self.scanner = ApprovalScanner(self.web3, chain)
        
        print(f"初始化完成 - 链: {chain}, 钱包地址: {self.wallet_address}")
    
    def query_approvals(self, address: str = None, token_addresses: List[str] = None) -> List[Dict]:
        """
        查询授权情况
        
        Args:
            address: 要查询的地址，如果为None则使用当前钱包地址
            token_addresses: 要查询的代币地址列表
            
        Returns:
            授权列表
        """
        if address is None:
            address = self.wallet_address
        
        print(f"正在查询地址 {address} 的授权情况...")
        
        # 获取当前授权
        current_approvals = self.scanner.get_current_approvals(address, token_addresses)
        
        if not current_approvals:
            print("未发现任何授权")
            return []
        
        print(f"发现 {len(current_approvals)} 个授权:")
        for approval in current_approvals:
            print(f"  - {approval['token_symbol']} ({approval['token_address']})")
            print(f"    授权给: {approval['spender']}")
            print(f"    金额: {approval['allowance_formatted']}")
            print()
        
        return current_approvals
    
    def revoke_approval(self, token_address: str, spender: str, address: str = None) -> str:
        """
        撤销指定代币的授权
        
        Args:
            token_address: 代币地址
            spender: 被授权地址
            address: 授权者地址，如果为None则使用当前钱包地址
            
        Returns:
            交易哈希
        """
        if address is None:
            address = self.wallet_address
        
        print(f"正在撤销 {token_address} 对 {spender} 的授权...")
        
        # 创建合约实例
        contract = ERC20Contract(self.web3, token_address)
        
        # 检查当前授权
        current_allowance = contract.get_allowance(address, spender)
        if current_allowance == 0:
            print("该地址没有授权，无需撤销")
            return ""
        
        # 撤销授权
        try:
            tx_hash = contract.revoke_approval(spender, address, self.private_key)
            print(f"撤销授权成功，交易哈希: {tx_hash}")
            return tx_hash
        except Exception as e:
            print(f"撤销授权失败: {e}")
            raise
    
    def revoke_all_approvals(self, address: str = None, token_addresses: List[str] = None) -> List[str]:
        """
        撤销所有代币的授权
        
        Args:
            address: 授权者地址，如果为None则使用当前钱包地址
            token_addresses: 要撤销的代币地址列表
            
        Returns:
            交易哈希列表
        """
        if address is None:
            address = self.wallet_address
        
        print(f"正在撤销地址 {address} 的所有授权...")
        
        # 获取当前所有授权
        approvals = self.query_approvals(address, token_addresses)
        
        if not approvals:
            print("没有发现需要撤销的授权")
            return []
        
        tx_hashes = []
        
        for approval in approvals:
            try:
                tx_hash = self.revoke_approval(
                    approval['token_address'],
                    approval['spender'],
                    address
                )
                if tx_hash:
                    tx_hashes.append(tx_hash)
            except Exception as e:
                print(f"撤销 {approval['token_symbol']} 授权失败: {e}")
                continue
        
        print(f"成功撤销 {len(tx_hashes)} 个授权")
        return tx_hashes
    
    def get_token_info(self, token_address: str) -> Dict:
        """
        获取代币信息
        
        Args:
            token_address: 代币地址
            
        Returns:
            代币信息
        """
        contract = ERC20Contract(self.web3, token_address)
        return contract.get_token_info()
    
    def get_token_balance(self, token_address: str, address: str = None) -> str:
        """
        获取代币余额
        
        Args:
            token_address: 代币地址
            address: 地址，如果为None则使用当前钱包地址
            
        Returns:
            格式化的余额字符串
        """
        if address is None:
            address = self.wallet_address
        
        contract = ERC20Contract(self.web3, token_address)
        balance = contract.get_balance(address)
        return contract.format_amount(balance)
    
    def approve_token(self, token_address: str, spender: str, amount: str, address: str = None) -> str:
        """
        授权代币
        
        Args:
            token_address: 代币地址
            spender: 被授权地址
            amount: 授权金额（字符串格式）
            address: 授权者地址，如果为None则使用当前钱包地址
            
        Returns:
            交易哈希
        """
        if address is None:
            address = self.wallet_address
        
        print(f"正在授权 {token_address} 给 {spender}，金额: {amount}")
        
        contract = ERC20Contract(self.web3, token_address)
        amount_int = contract.parse_amount(amount)
        
        try:
            tx_hash = contract.approve(spender, amount_int, address, self.private_key)
            print(f"授权成功，交易哈希: {tx_hash}")
            return tx_hash
        except Exception as e:
            print(f"授权失败: {e}")
            raise
    
    def check_network_status(self) -> bool:
        """检查网络连接状态"""
        try:
            # 检查网络连接
            latest_block = self.web3.eth.block_number
            print(f"网络连接正常，最新区块: {latest_block}")
            return True
        except Exception as e:
            print(f"网络连接失败: {e}")
            return False
    
    def get_wallet_info(self) -> Dict:
        """获取钱包信息"""
        balance_wei = self.web3.eth.get_balance(self.wallet_address)
        balance_eth = self.web3.from_wei(balance_wei, 'ether')
        
        return {
            'address': self.wallet_address,
            'balance_wei': balance_wei,
            'balance_eth': float(balance_eth),
            'chain': self.chain,
            'rpc_url': self.rpc_url
        }
