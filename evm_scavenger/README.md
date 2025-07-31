# Scavenger 钱包管理工具

用于转移钱包内 EVM 链上的全部资产。

## 📁 文件说明

### `erc20.py` - ERC20 代币自动转移脚本
自动转移 EVM 钱包持有的全部 ERC20 代币到指定地址。

### `native.py` - 原生代币自动转移脚本  
自动转移 EVM 钱包持有的全部原生代币（如 ETH、BNB 等）到指定地址。

## 🚀 功能特性

### ERC20.py 脚本特性
- ✅ 自动获取代币余额和精度信息
- ✅ 智能 Gas 估算和优化
- ✅ Dry-run 模式支持（模拟执行）
- ✅ 彩色终端输出，操作状态清晰
- ✅ 错误处理和跳过机制
- ✅ 详细的执行统计报告

### Native.py 脚本特性
- ✅ 智能 EIP-1559 支持检测
- ✅ 动态 Gas 限制估算
- ✅ 特殊链 Gas 参数优化
- ✅ 余额检查和 Gas 费用预留
- ✅ Dry-run 模式支持
- ✅ 彩色终端输出
- ✅ 完整的错误处理

## 🔧 依赖库

脚本依赖以下Python库：

```
web3 - 用于与以太坊区块链交互
eth-account - 用于以太坊账户管理和交易签名
python-dotenv - 用于加载环境变量
colorama - 用于终端彩色输出
python-dotenv - 用于配置环境变量
```
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
包含各 EVM 链的 RPC 端点信息（已配置了**公开 RPC 端点**，可能会失效、限频或不稳定，最好修改为自己的**专属 RPC 端点**）：
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
定义要处理的链和代币信息（运行 `used_chains.py` 自动生成）：
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
### 激活 python 虚拟环境
- **适用 linux/wsl/macOs 系统**
```bash
# 在项目根目录下执行以下命令
source venv/bin/activate
```
- **适用 windows 系统**
```powershell
# 在项目根目录下执行以下命令
.\venv\Scripts\Activate
```

### 重要：执行顺序
在执行转移脚本之前，**必须先运行 `used_chains.py` 来更新 `used_chains.json` 配置文件**：
- **适用 linux/wsl/macOs 系统**
```bash
# 进入 evm_scavenger/src 目录，执行以下命令
python3 used_chains.py
```
- **适用 windows 系统**
```powershell
# 进入 evm_scavenger\src 目录，执行以下命令
python used_chains.py
```

### 运行 ERC20 代币转移脚本
运行前确保你的钱包在各链有足够的原生代币支付 Gas 费用
- **适用 linux/wsl/macOs 系统**
```bash
# 进入 evm_scavenger/src 目录，执行以下命令
python3 erc20.py
```
- **适用 windows 系统**
```powershell
# 进入 evm_scavenger\src 目录，执行以下命令
python erc20.py
```

### 运行原生代币转移脚本
- **适用 linux/wsl/macOs 系统**
```bash
# 进入 evm_scavenger/src 目录，执行以下命令
python3 native.py
```
- **适用 windows 系统**
```powershell
# 进入 evm_scavenger\src 目录，执行以下命令
python native.py
```

### 完整执行流程
1. **第一步**：运行 `used_chains.py` 更新配置文件
2. **第二步**：根据需要运行 `erc20.py` 或 `native.py`
3. **可选**：启用 Dry-run 模式进行测试

## 🔧 配置说明
### Dry-run 模式
设置 `DRY_RUN=true` 可以启用模拟模式：
- 不会实际发送交易
- 显示所有操作步骤
- 用于测试配置是否正确

## ⚠️ 注意事项

1. **执行顺序**：**必须先运行 `used_chains.py` 更新配置文件，再执行资产转移脚本**
2. **Gas 费用**：确保账户有足够的原生代币支付 Gas 费用
3. **网络连接**：`RPC_list.json` 配置的为**公开 RPC 端点**，个别可能会失效、限频或不稳定，建议手动修改为自己的**专属 RPC 端点**（可在 Alchemy、Infura、Ankr、QuickNode 等提供商上免费注册）
4. **支持的 EVM 链**：`chain_index.json` 配置的为支持的 EVM 链列表，但不一定齐全，可手动进行添加。格式：`{ "chain_id": 1, "name": "eth" },`,确保`name`字段名称与 DeBank 的命名相同。
5. **测试建议**：首次使用建议启用 Dry-run 模式测试

## 🛠️ 故障排除
- **ModuleNotFoundError: No module named...**: 确保你已激活虚拟环境，并已成功安装了所需的 python 库。（可手动运行 `pip install -r requirements.txt `进行再次安装）
- **输出大量 PRC 错误日志**：确保运行 `资产转移脚本`前先运行 `used_chains.py` 来更新配置文件 `used_chains.json`
- **RPC 连接失败**：RPC 端点失效、限频或不稳定，请检查 RPC 端点状态
- **余额不足**：确保你的钱包在各链有足够的原生代币支付 Gas 费用

## 💬 联系与支持
- Telegram: [t.me/cryptostar210](https://t.me/cryptostar210)
- 打赏地址：**0xd328426a8e0bcdbbef89e96a91911eff68734e84** ▋**5LmGJmv7Lbjh9K1gEer47xSHZ7mDcihYqVZGoPMRo89s**