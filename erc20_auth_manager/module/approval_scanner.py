"""
授权扫描器模块
用于扫描和查询代币授权情况
"""

import requests
from typing import Dict, List, Optional, Tuple
from web3 import Web3
from .config import Config
from .erc20_contract import ERC20Contract

class ApprovalScanner:
    """授权扫描器类"""
    
    def __init__(self, web3: Web3, chain: str):
        """
        初始化扫描器
        
        Args:
            web3: Web3实例
            chain: 链名称
        """
        self.web3 = web3
        self.chain = chain
        self.chain_info = Config.get_chain_info(chain)
        self.explorer_api_key = Config.get_explorer_api_key(chain)
    
    def get_approval_events(self, address: str, from_block: int = None, to_block: int = None) -> List[Dict]:
        """
        获取授权事件
        
        Args:
            address: 钱包地址
            from_block: 起始区块
            to_block: 结束区块
            
        Returns:
            授权事件列表
        """
        if from_block is None:
            # 默认从最近10000个区块开始扫描
            current_block = self.web3.eth.block_number
            from_block = max(0, current_block - 10000)
        
        if to_block is None:
            to_block = self.web3.eth.block_number
        
        # 获取Approval事件
        approval_events = []
        
        # 这里简化处理，实际项目中可能需要使用区块浏览器的API
        # 或者使用事件日志查询
        try:
            # 尝试使用区块浏览器API
            events = self._get_approval_events_from_explorer(address, from_block, to_block)
            if events:
                approval_events.extend(events)
        except Exception as e:
            print(f"从区块浏览器获取事件失败: {e}")
        
        return approval_events
    
    def _get_approval_events_from_explorer(self, address: str, from_block: int, to_block: int) -> List[Dict]:
        """从区块浏览器获取授权事件"""
        if not self.explorer_api_key:
            return []
        
        # 构建API请求
        if self.chain == 'ethereum':
            api_url = "https://api.etherscan.io/api"
            module = "account"
            action = "txlist"
        elif self.chain == 'bsc':
            api_url = "https://api.bscscan.com/api"
            module = "account"
            action = "txlist"
        elif self.chain == 'polygon':
            api_url = "https://api.polygonscan.com/api"
            module = "account"
            action = "txlist"
        elif self.chain == 'arbitrum':
            api_url = "https://api.arbiscan.io/api"
            module = "account"
            action = "txlist"
        elif self.chain == 'optimism':
            api_url = "https://api-optimistic.etherscan.io/api"
            module = "account"
            action = "txlist"
        else:
            return []
        
        params = {
            'module': module,
            'action': action,
            'address': address,
            'startblock': from_block,
            'endblock': to_block,
            'apikey': self.explorer_api_key,
            'sort': 'desc'
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=30)
            data = response.json()
            
            if data.get('status') == '1':
                transactions = data.get('result', [])
                approval_events = []
                
                for tx in transactions:
                    # 检查是否是approve交易
                    if self._is_approve_transaction(tx):
                        approval_events.append({
                            'hash': tx['hash'],
                            'token_address': tx['to'],
                            'spender': self._extract_spender_from_input(tx['input']),
                            'amount': self._extract_amount_from_input(tx['input']),
                            'block_number': int(tx['blockNumber']),
                            'timestamp': int(tx['timeStamp'])
                        })
                
                return approval_events
            else:
                print(f"API请求失败: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"请求区块浏览器API失败: {e}")
            return []
    
    def _is_approve_transaction(self, tx: Dict) -> bool:
        """检查是否是approve交易"""
        # approve方法的函数签名: 0x095ea7b3
        return tx.get('input', '').startswith('0x095ea7b3')
    
    def _extract_spender_from_input(self, input_data: str) -> str:
        """从交易输入中提取spender地址"""
        if len(input_data) < 74:  # 0x + 4字节函数签名 + 32字节spender地址
            return ""
        
        # 提取spender地址（第2-3个32字节）
        spender_hex = input_data[34:74]  # 跳过0x和函数签名
        return "0x" + spender_hex[-40:]  # 取最后20字节作为地址
    
    def _extract_amount_from_input(self, input_data: str) -> int:
        """从交易输入中提取授权金额"""
        if len(input_data) < 138:  # 0x + 4字节函数签名 + 32字节spender + 32字节amount
            return 0
        
        # 提取amount（第3-4个32字节）
        amount_hex = input_data[74:138]
        return int(amount_hex, 16)
    
    def get_current_approvals(self, address: str, token_addresses: List[str] = None) -> List[Dict]:
        """
        获取当前有效的授权
        
        Args:
            address: 钱包地址
            token_addresses: 代币地址列表，如果为None则使用常见代币
            
        Returns:
            当前授权列表
        """
        if token_addresses is None:
            token_addresses = self._get_common_tokens()
        
        approvals = []
        
        for token_address in token_addresses:
            try:
                contract = ERC20Contract(self.web3, token_address)
                token_info = contract.get_token_info()
                
                # 检查是否有授权（这里简化处理，实际需要扫描所有可能的spender）
                # 在实际应用中，你可能需要维护一个已知的spender列表
                
                # 示例：检查一些常见的DEX和协议
                common_spenders = self._get_common_spenders()
                
                for spender in common_spenders:
                    allowance = contract.get_allowance(address, spender)
                    if allowance > 0:
                        approvals.append({
                            'token_address': token_address,
                            'token_name': token_info['name'],
                            'token_symbol': token_info['symbol'],
                            'spender': spender,
                            'allowance': allowance,
                            'allowance_formatted': contract.format_amount(allowance)
                        })
                        
            except Exception as e:
                print(f"检查代币 {token_address} 授权失败: {e}")
                continue
        
        return approvals
    
    def _get_common_tokens(self) -> List[str]:
        """获取常见代币地址列表"""
        common_tokens = {
            'ethereum': [
                '0xA0b86a33E6441b8C4C8C8C8C8C8C8C8C8C8C8C8',  # USDT
                '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # USDT
                '0xA0b86a33E6441b8C4C8C8C8C8C8C8C8C8C8C8C8',  # USDC
                '0xA0b86a33E6441b8C4C8C8C8C8C8C8C8C8C8C8C8',  # DAI
                '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # WETH
            ],
            'bsc': [
                '0x55d398326f99059fF775485246999027B3197955',  # USDT
                '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',  # USDC
                '0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3',  # DAI
                '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',  # WETH
            ],
            'polygon': [
                '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',  # USDT
                '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',  # USDC
                '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',  # DAI
                '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',  # WETH
            ]
        }
        
        return common_tokens.get(self.chain, [])
    
    def _get_common_spenders(self) -> List[str]:
        """获取常见的spender地址列表"""
        common_spenders = {
            'ethereum': [
                '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',  # Uniswap V2 Router
                '0xE592427A0AEce92De3Edee1F18E0157C05861564',  # Uniswap V3 Router
                '0x1111111254EEB25477B68fb85Ed929f73A960582',  # 1inch Router
            ],
            'bsc': [
                '0x10ED43C718714eb63d5aA57B78B54704E256024E',  # PancakeSwap Router
                '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',  # SushiSwap Router
            ],
            'polygon': [
                '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',  # QuickSwap Router
                '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',  # SushiSwap Router
            ]
        }
        
        return common_spenders.get(self.chain, [])
