"""
ERC20合约交互模块
"""

from typing import Dict, List, Optional, Tuple
from web3 import Web3
from web3.contract import Contract
from eth_abi import decode
import json

# ERC20 ABI (简化版，只包含必要的方法)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]

class ERC20Contract:
    """ERC20合约交互类"""
    
    def __init__(self, web3: Web3, contract_address: str):
        """
        初始化ERC20合约
        
        Args:
            web3: Web3实例
            contract_address: 合约地址
        """
        self.web3 = web3
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract = web3.eth.contract(
            address=self.contract_address,
            abi=ERC20_ABI
        )
        
        # 缓存代币信息
        self._token_info = None
    
    def get_token_info(self) -> Dict:
        """获取代币信息"""
        if self._token_info is None:
            try:
                name = self.contract.functions.name().call()
            except:
                name = "Unknown"
            
            try:
                symbol = self.contract.functions.symbol().call()
            except:
                symbol = "Unknown"
            
            try:
                decimals = self.contract.functions.decimals().call()
            except:
                decimals = 18
            
            self._token_info = {
                'name': name,
                'symbol': symbol,
                'decimals': decimals,
                'address': self.contract_address
            }
        
        return self._token_info
    
    def get_balance(self, address: str) -> int:
        """获取地址的代币余额"""
        address = Web3.to_checksum_address(address)
        return self.contract.functions.balanceOf(address).call()
    
    def get_allowance(self, owner: str, spender: str) -> int:
        """获取授权额度"""
        owner = Web3.to_checksum_address(owner)
        spender = Web3.to_checksum_address(spender)
        return self.contract.functions.allowance(owner, spender).call()
    
    def approve(self, spender: str, amount: int, from_address: str, private_key: str) -> str:
        """
        授权操作
        
        Args:
            spender: 被授权地址
            amount: 授权金额
            from_address: 授权者地址
            private_key: 私钥
            
        Returns:
            交易哈希
        """
        spender = Web3.to_checksum_address(spender)
        from_address = Web3.to_checksum_address(from_address)
        
        # 构建交易
        transaction = self.contract.functions.approve(spender, amount).build_transaction({
            'from': from_address,
            'nonce': self.web3.eth.get_transaction_count(from_address),
            'gas': 100000,
            'gasPrice': self.web3.eth.gas_price
        })
        
        # 签名并发送交易
        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return tx_hash.hex()
    
    def revoke_approval(self, spender: str, from_address: str, private_key: str) -> str:
        """
        撤销授权（将授权金额设为0）
        
        Args:
            spender: 被授权地址
            from_address: 授权者地址
            private_key: 私钥
            
        Returns:
            交易哈希
        """
        return self.approve(spender, 0, from_address, private_key)
    
    def format_amount(self, amount: int, decimals: int = None) -> str:
        """格式化代币金额"""
        if decimals is None:
            decimals = self.get_token_info()['decimals']
        
        return str(amount / (10 ** decimals))
    
    def parse_amount(self, amount_str: str, decimals: int = None) -> int:
        """解析代币金额字符串为整数"""
        if decimals is None:
            decimals = self.get_token_info()['decimals']
        
        return int(float(amount_str) * (10 ** decimals))
