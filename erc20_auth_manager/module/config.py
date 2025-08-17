"""
配置管理模块
"""

import os
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# 使用 pathlib 定义路径
MODULE_DIR = Path(__file__).parent
PROJECT_ROOT = MODULE_DIR.parent
ENV_FILE = PROJECT_ROOT / 'env'

# 加载环境变量
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
    print(f"已从 {ENV_FILE} 加载环境变量")
else:
    print(f"警告: 环境文件 {ENV_FILE} 不存在")
    # 尝试从默认位置加载
    load_dotenv()

class Config:
    """配置管理类"""
    
    # 支持的链配置
    CHAINS = {
        'ethereum': {
            'name': 'Ethereum',
            'rpc_url': 'ETHEREUM_RPC_URL',
            'explorer': 'https://etherscan.io',
            'chain_id': 1
        },
        'bsc': {
            'name': 'BSC',
            'rpc_url': 'BSC_RPC_URL',
            'explorer': 'https://bscscan.com',
            'chain_id': 56
        },
        'base': {
            'name': 'Base',
            'rpc_url': 'BASE_RPC_URL',
            'explorer': 'https://basescan.org',
            'chain_id': 8453
        },
        'arbitrum': {
            'name': 'Arbitrum',
            'rpc_url': 'ARBITRUM_RPC_URL',
            'explorer': 'https://arbiscan.io',
            'chain_id': 42161
        },
        'optimism': {
            'name': 'Optimism',
            'rpc_url': 'OPTIMISM_RPC_URL',
            'explorer': 'https://optimistic.etherscan.io',
            'chain_id': 10
        }
    }
    
    @classmethod
    def get_rpc_url(cls, chain: str) -> str:
        """获取指定链的RPC URL"""
        if chain not in cls.CHAINS:
            raise ValueError(f"不支持的链: {chain}")
        
        env_key = cls.CHAINS[chain]['rpc_url']
        rpc_url = os.getenv(env_key)
        
        if not rpc_url:
            raise ValueError(f"未配置{chain}的RPC URL，请在.env文件中设置{env_key}")
        
        return rpc_url
    
    @classmethod
    def get_wallet_private_key(cls) -> str:
        """获取钱包私钥"""
        private_key = os.getenv('WALLET_PRIVATE_KEY')
        if not private_key:
            raise ValueError("未配置钱包私钥，请在.env文件中设置WALLET_PRIVATE_KEY")
        return private_key
    
    @classmethod
    def get_default_chain(cls) -> str:
        """获取默认链"""
        return os.getenv('DEFAULT_CHAIN', 'ethereum')
    
    @classmethod
    def get_chain_info(cls, chain: str) -> Dict:
        """获取链信息"""
        if chain not in cls.CHAINS:
            raise ValueError(f"不支持的链: {chain}")
        return cls.CHAINS[chain]
    
    @classmethod
    def get_supported_chains(cls) -> list:
        """获取支持的链列表"""
        return list(cls.CHAINS.keys())
    
    @classmethod
    def get_explorer_api_key(cls, chain: str) -> Optional[str]:
        """获取区块浏览器API密钥"""
        api_keys = {
            'ethereum': 'ETHERSCAN_API_KEY',
            'bsc': 'BSCSCAN_API_KEY',
            'polygon': 'POLYGONSCAN_API_KEY',
            'arbitrum': 'ARBISCAN_API_KEY',
            'optimism': 'OPTIMISTIC_ETHERSCAN_API_KEY'
        }
        
        if chain in api_keys:
            return os.getenv(api_keys[chain])
        return None
