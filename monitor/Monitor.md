# 🎒 多链代币监控系统

一个功能强大的跨平台多链代币监控系统，支持 EVM 和 Solana 生态，实时监控代币到账并发送 Telegram 通知。

## 🌟 项目特色

- **🔗 多链支持**: 同时监控EVM兼容链和Solana链
- **📱 实时通知**: Telegram机器人即时推送
- **🎨 美观界面**: 彩色日志输出和艺术字横幅
- **🌍 跨平台**: 支持Windows、macOS、Linux
- **⚡ 高性能**: 异步WebSocket连接，低延迟监控
- **🔄 自动重连**: 智能故障转移和重连机制
- **🔒 安全可靠**: 支持多节点备份
- **📊 详细统计**: 实时显示监控状态和统计信息

## 📁 项目结构

```
monitor/
├── README.md              # 项目说明文档
├── evm/                   # EVM链监控模块
│   ├── evm_monitor.py     # EVM监控主程序
│   └── config.yaml        # EVM配置文件
└── solana/                # Solana链监控模块
    ├── spl_monitor.py     # Solana监控主程序
    └── config.yaml        # Solana配置文件
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- 网络连接
- Telegram Bot Token

### 2. 配置监控

#### EVM链配置 (evm/config.yaml)
```yaml
# 支持配置多条 EVM 链
# 支持配置多个备用节点（建议使用自己的专属节点，可在 Alchemy、Infura、Ankr、QuickNode 等提供商上免费注册）
chains:
  ethereum:
    ws_urls:
      - "wss://mainnet.infura.io/ws/v3/YOUR_PROJECT_ID"
      - "wss://eth-mainnet.alchemyapi.io/v2/YOUR_API_KEY"
  bsc:
    ws_urls:
      - "wss://bsc-ws-node.nariox.org:443"
      - "wss://bsc.getblock.io/YOUR_API_KEY/mainnet/"
  base:
    ws_urls:
      - "wss://mainnet.base.org"
      - "wss://base-mainnet.public.blastapi.io"
  arbitrum:
    ws_urls:
      - "wss://arb1.arbitrum.io/ws"
      - "wss://arbitrum-mainnet.public.blastapi.io"

# 监听地址(支持多个)，全部小写
watch_addresses:
  - "0x1234567890abcdef1234567890abcdef12345678"  # 示例1，请修改为你要监听的地址
  - "0xabcdef1234567890abcdef1234567890abcdef12"  # 示例2，请修改为你要监听的地址

# Telegram Bot 配置
telegram:
  bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # 示例，请替换为你的Bot Token
  chat_id: "9876543210"  # 示例，请替换为你的Chat ID
```

#### Solana链配置 (solana/config.yaml)
```yaml
# Solana Token 监听器配置文件
solana:
  # HTTP RPC节点列表 (支持多个节点，程序会自动切换)
  # WebSocket URL会自动从HTTP URL生成，无需手动配置
  # 建议修改为自己的专属节点，可在 Helius、Alchemy、Infura、Ankr、QuickNode 等提供商上免费注册
  http_urls:
    - "https://api.mainnet-beta.solana.com"
    - "https://solana-api.projectserum.com"
    - "https://rpc.ankr.com/solana"
    - "https://solana.public-rpc.com"

# 监听地址列表 (要监听的Solana钱包地址)
watch_addresses:
  - "2wVXwDnWUBoZqmFvFTMiUtMA5NZSvCtWBHgiEuHzBEd3"  # 示例1，请修改为你要监听的地址
  - "zEftHcuc7jDHwGFVzDEBiAe8bhP8VuvRAE64ETwg6kZ"   # 示例2，请修改为你要监听的地址

# Telegram机器人配置
telegram:
  bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # 示例，请替换为你的Bot Token
  chat_id: "9876543210"  # 示例，请替换为你的Chat ID
```

### 3. 获取Telegram配置

#### 创建Telegram机器人
1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称和用户名
4. 获得bot_token (格式: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)

#### 获取Chat ID
1. 在Telegram中搜索 `@userinfobot`
2. 发送任意消息
3. 获得您的chat_id

### 4. 运行监控

#### 🔴 启动EVM监控
在 monitor/evm 目录下执行以下命令：
```
poetry run python evm_monitor.py
# 或者，后台运行（即使终端关闭也能继续运行），使用以下命令：
nohup poetry run python evm_monitor.py > monitor.log 2>&1 &
```

#### 🔴 启动Solana监控
在 monitor/solana 目录下执行以下命令：
```
poetry run python spl_monitor.py
# 或者，后台运行（即使终端关闭也能继续运行），使用以下命令：
nohup poetry run python spl_monitor.py > monitor.log 2>&1 &
```

## 📱 通知格式

### EVM链通知示例
```
🚨 **EVM Token 到账警报** 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⛓️ **链**: Ethereum
📥 **接收地址**: `0x1234567890abcdef1234567890abcdef12345678`
💰 **增加数量**: `100.5`
💰 **当前余额**: `100.5`
📜 **代币合约**: `0xa0b86a33e6441b8c4c8c8c8c8c8c8c8c8c8c8c8c8`
🕐 **时间**: `2024-01-01 12:00:00`
🔗 **交易哈希**: `0xabc123def456...`
🔍 **查看链接**: [Etherscan](https://etherscan.io/tx/0xabc123def456...)
```

### Solana链通知示例
```
🚨 **SPL Token 到账警报** 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⛓️ **链**: Solana
📥 **接收地址**: `2wVXwDnWUBoZqmFvFTMiUtMA5NZSvCtWBHgiEuHzBEd3`
💰 **增加数量**: `100.5`
💰 **当前余额**: `100.5`
📜 **代币合约**: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
🕐 **时间**: `2024-01-01 12:00:00`
🔗 **交易哈希**: `5J7X...abc123`
🔍 **查看链接**: [Solscan](https://solscan.io/tx/5J7X...abc123)
```

## 🔧 高级配置

### 支持的EVM链
- **Ethereum**: 以太坊主网
- **BSC**: 币安智能链
- **Base**: Coinbase Layer2
- **Arbitrum**: Arbitrum One
- **Polygon**: Polygon网络
- **Avalanche**: Avalanche C-Chain
- **Optimism**: Optimism网络

### RPC节点推荐
- **Alchemy**: 提供免费API，稳定性好
- **Infura**: 知名提供商，支持多链
- **Ankr**: 免费公共节点
- **QuickNode**: 专业节点服务
- **GetBlock**: 多链支持

### 性能优化建议
1. **使用专用节点**: 避免使用公共节点，提高稳定性
2. **配置多个备用节点**: 确保故障转移
3. **合理设置监听地址数量**: 避免过多地址影响性能
4. **定期更新依赖**: 保持最新版本

## 🛠️ 故障排除

### 常见问题

#### 1. 连接失败
**症状**: 程序无法连接到RPC节点
**解决方案**:
- 检查网络连接
- 确认RPC节点地址正确
- 尝试使用不同的RPC节点
- 检查防火墙设置

#### 2. Telegram通知失败
**症状**: 程序运行正常但收不到通知
**解决方案**:
- 确认Bot Token正确
- 确认Chat ID正确
- 检查机器人是否已启动
- 测试机器人权限

#### 3. 监听不到Token
**症状**: 向监听地址转账但未收到通知
**解决方案**:
- 确认钱包地址正确
- 检查地址是否有Token账户
- 确认RPC节点响应正常
- 检查代币合约是否支持

#### 4. 程序崩溃
**症状**: 程序运行一段时间后自动退出
**解决方案**:
- 检查Python版本兼容性
- 更新依赖包到最新版本
- 检查配置文件格式
- 查看错误日志

## 📊 监控统计

程序运行时会显示实时统计信息：
- 监听地址数量
- RPC节点数量
- 连接状态
- 交易检测数量
- 通知发送状态

## 🔒 安全建议

1. **保护配置文件**: 不要将包含真实Token的配置文件提交到公共仓库
2. **使用专用节点**: 避免使用公共RPC节点，提高安全性
3. **定期更新**: 保持程序和依赖包的最新版本
4. **监控日志**: 定期检查程序运行日志，发现异常及时处理
5. **备份配置**: 定期备份重要配置文件

## 💬 联系与支持
- Telegram: [t.me/cryptostar210](https://t.me/cryptostar210)
- 请我喝杯☕：**0xd328426a8e0bcdbbef89e96a91911eff68734e84** ▋**5LmGJmv7Lbjh9K1gEer47xSHZ7mDcihYqVZGoPMRo89s**