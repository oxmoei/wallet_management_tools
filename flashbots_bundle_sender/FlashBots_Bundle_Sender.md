# 🚀 FlashBots Bundle Transaction Sender

> MEV Bundle Transaction Tool for Ethereum Networks | 闪电机器人交易捆绑发送器

## 📋 项目简介

基于 FlashBots 的 MEV 交易捆绑发送工具，支持以太坊网络的交易捆绑发送，避免交易被抢跑。

## ✨ 主要特性

- 🌐 **多网络支持**: Sepolia 测试网和以太坊主网
- ⚡ **FlashBots集成**: 使用 FlashBots 中继器
- 🎯 **交易捆绑**: 多笔交易原子性执行
- 🔄 **自动重试**: 智能重试机制
- 🎨 **美化输出**: 彩色终端界面

## 🛠️ 技术栈
- Node.js 18+
- ethers.js
- @flashbots/ethers-provider-bundle
- dotenv

## 📦 安装

```bash
# 在 flashbots_bundle_sender 目录下执行以下命令
npm install
```

## ⚙️ 配置

### 环境变量 (.env)

```env
# 以太坊RPC节点
ETHEREUM_RPC_URL=https://eth.llamarpc.com

# FlashBots中继器
FLASHBOTS_RELAY_URL=https://relay.flashbots.net

# FlashBots签名密钥
FLASHBOTS_RELAY_SIGNING_KEY=0xYOUR_SIGNING_KEY

# 钱包私钥
SAFE_WALLET_PRIVATE_KEY=0xYOUR_SAFE_KEY
VICTIM_WALLET_PRIVATE_KEY=0xYOUR_VICTIM_KEY

# 合约配置
CONTRACT_ADDRESS=0xYOUR_CONTRACT
HEX_DATA=0xYOUR_CALL_DATA
GAS_LIMIT=
MAX_PRIORITY_FEE=

# 转账金额
SAFE_TO_VICTIM_AMOUNT=
```

## 🚀 使用

```bash
# 在 flashbots_bundle_sender 目录下执行以下命令
node src/main.js
```

## 🔧 故障排除

### 常见问题

1. **连接错误**: 检查 RPC URL 配置
2. **Gas费用错误**: 确保优先费用不大于最大费用
3. **交易未能成功上链**: 提高 Gas 费用或检查网络拥堵

## 💬 联系与支持
- Telegram: [t.me/cryptostar210](https://t.me/cryptostar210)
- 请我喝杯☕：**0xd328426a8e0bcdbbef89e96a91911eff68734e84** ▋**5LmGJmv7Lbjh9K1gEer47xSHZ7mDcihYqVZGoPMRo89s**