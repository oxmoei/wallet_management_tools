# Scavenger 钱包管理工具

这个目录包含了两个主要的钱包管理脚本，用于批量转移不同区块链上的资产。

## 📁 文件说明

### `erc20.py` - ERC20 代币批量转移脚本
用于批量转移多个区块链上的 ERC20 代币到指定地址。

### `native.py` - 原生代币批量转移脚本  
用于批量转移多个区块链上的原生代币（如 ETH、BNB 等）到指定地址。

## 🚀 功能特性

### ERC20 脚本特性
- ✅ 支持多链批量 ERC20 代币转移
- ✅ 自动获取代币余额和精度信息
- ✅ 智能 Gas 估算和优化
- ✅ Dry-run 模式支持（模拟执行）
- ✅ 彩色终端输出，操作状态清晰
- ✅ 错误处理和跳过机制
- ✅ 详细的执行统计报告

### Native 脚本特性
- ✅ 支持多链批量原生代币转移
- ✅ 智能 EIP-1559 支持检测
- ✅ 动态 Gas 限制估算
- ✅ 特殊链 Gas 参数优化
- ✅ 余额检查和 Gas 费用预留
- ✅ Dry-run 模式支持
- ✅ 彩色终端输出
- ✅ 完整的错误处理

## 📋 环境要求

### 环境变量
在项目根目录的 `.env` 文件中设置：

```env
# 必填：发送方私钥
FROM_ADDRESS=your_address
PRIVATE_KEY=your_private_key_here

# 必填：接收方地址
TO_ADDRESS=0x1234567890123456789012345678901234567890

# 可选：Dry-run 模式（true/false，默认false）
DRY_RUN=false
```

## 📁 配置文件

### `conf/RPC_list.json`
包含各区块链的 RPC 节点信息：
```json
[
  {
    "chain_id": 1,
    "rpc_url": "https://eth-mainnet.alchemyapi.io/v2/your_key"
  },
  {
    "chain_id": 56,
    "rpc_url": "https://bsc-dataseed.binance.org/"
  }
]
```

### `conf/used_chains.json`
定义要处理的链和代币信息：
```json
[
  {
    "chain_id": 1,
    "tokens": [
      {
        "address": "0xA0b86a33E6441b8c4C8C1C1B9C9C9C9C9C9C9C9C9",
        "amount": 100.5
      }
    ]
  }
]
```

### `conf/ERC20_ABI.json`
ERC20 代币的标准 ABI 接口文件。

## 🎯 使用方法

### 重要：执行顺序
在执行转移脚本之前，**必须先运行 `used_chains.py` 来生成 `used_chains.json` 配置文件**：

```bash
cd /home/star/tools/钱包管理/scavenger/src
python3 used_chains.py
```

### 运行 ERC20 代币转移
```bash
cd /home/star/tools/钱包管理/scavenger/src
python3 erc20.py
```

### 运行原生代币转移
```bash
cd /home/star/tools/钱包管理/scavenger/src
python3 native.py
```

### 完整执行流程
1. **第一步**：运行 `used_chains.py` 生成配置文件
2. **第二步**：根据需要运行 `erc20.py` 或 `native.py`
3. **可选**：启用 Dry-run 模式进行测试

## 🔧 配置说明

### 特殊链 Gas 优化
`native.py` 中内置了特殊链的 Gas 限制优化：

| 链 ID | 链名称 | Gas 限制 |
|-------|--------|----------|
| 42161 | Arbitrum | 70,000 |
| 5000  | Mantle | 100,000 |
| 324   | zkSync | 70,000 |
| 204   | opBNB | 70,000 |
| 534352| Scroll | 70,000 |
| 10    | Optimism | 70,000 |
| 59144 | Linea | 70,000 |
| 8453  | Base | 70,000 |

### Dry-run 模式
设置 `DRY_RUN=true` 可以启用模拟模式：
- 不会实际发送交易
- 显示所有操作步骤
- 用于测试配置是否正确

## 📊 输出示例

### 成功执行示例
```
==================================================
🚀 批量 ERC20 转移脚本启动！🚀（Dry-run: false）

⛓️ 成功加载 5 条链信息
🏠 当前账户地址: 0x1234...5678
==================================================

[1/5] 获取初始 Nonce: 42
==================================================
⏳ 正在处理链 1（https://eth-mainnet.alchemyapi.io/v2/xxx）
==================================================

⚡ 发现 100.5 USDT (0xA0b86a33E6441b8c4C8C1C1B9C9C9C9C9C9C9C9C9)，准备转出...
✅ 成功转账 USDT (0xA0b86a33E6441b8c4C8C1C1B9C9C9C9C9C9C9C9C9)！交易哈希: 0x1234...5678
成功转账后 Nonce 递增至: 43

========================================
🔆 所有链处理完成！（Dry-run: false）
✅ 成功: 3，❌ 失败: 1，⏫ 跳过: 1
========================================
```

## ⚠️ 注意事项

1. **执行顺序**：**必须先运行 `used_chains.py` 生成配置文件，再执行转移脚本**
2. **私钥安全**：确保 `.env` 文件权限正确，不要泄露私钥
3. **Gas 费用**：确保账户有足够的原生代币支付 Gas 费用
4. **网络连接**：RPC_list.json 配置的为**公开 RPC 端点**，可能会失效、限频或不稳定，最好修改为自己的**专属 RPC 端点**（可在 Alchemy、Infura、Ankr、Blast 等提供商上免费注册）。
5. **余额检查**：脚本会自动检查余额是否足够支付 Gas
6. **测试建议**：首次使用建议启用 Dry-run 模式测试

## 🛠️ 故障排除

### 常见错误
- **used_chains.json 文件不存在**：先运行 `used_chains.py` 生成配置文件
- **地址格式错误**：确保 TO_ADDRESS 是有效的以太坊地址
- **RPC 连接失败**：检查网络连接和 RPC 节点状态
- **余额不足**：确保账户有足够的代币和 Gas 费用

### 调试建议
1. **确保已运行 `used_chains.py`** 生成必要的配置文件
2. 启用 Dry-run 模式测试配置
3. 检查 `.env` 文件格式
4. 验证 RPC 节点可用性
5. 确认代币合约地址正确

## 📝 更新日志

- **v1.0**：初始版本，支持基本的批量转移功能
- **v1.1**：添加 Dry-run 模式和彩色输出
- **v1.2**：优化 Gas 估算和错误处理
- **v1.3**：添加特殊链 Gas 优化和 EIP-1559 支持 