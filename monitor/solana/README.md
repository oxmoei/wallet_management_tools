# Solana Token 监听器

一个用于监听Solana钱包SPL Token到账并发送Telegram通知的工具。

## 🚀 功能特点

- ✅ 实时监听多个Solana钱包地址
- ✅ 自动检测SPL Token到账
- ✅ 发送Telegram通知（包含交易哈希）
- ✅ 支持多个RPC节点自动切换
- ✅ 美观的控制台输出
- ✅ 无需生成日志文件

## 📋 系统要求

- Python 3.7+
- 网络连接（访问Solana RPC节点和Telegram API）

## 🔧 安装依赖

```bash
pip install yaml requests solders solana websockets colorama
```

## ⚙️ 配置步骤

### 1. 创建Telegram机器人

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称和用户名
4. 保存获得的Bot Token

### 2. 获取Chat ID

1. 在Telegram中搜索 `@userinfobot`
2. 发送任意消息
3. 保存获得的Chat ID

### 3. 配置YAML文件

复制 `config_example.yaml` 为 `solana.yaml` 并修改：

```yaml
solana:
  http_urls:
    - "https://api.mainnet-beta.solana.com"
    - "https://solana-api.projectserum.com"
  
  ws_urls:
    - "wss://api.mainnet-beta.solana.com"
    - "wss://solana-api.projectserum.com"

watch_addresses:
  - "你的Solana钱包地址1"
  - "你的Solana钱包地址2"

safe_address: "你的安全地址"

telegram:
  bot_token: "你的Bot Token"
  chat_id: "你的Chat ID"
```

## 🎯 使用方法

### 1. 准备配置文件

```bash
# 复制配置文件示例
cp config_example.yaml solana.yaml

# 编辑配置文件
nano solana.yaml  # 或使用其他编辑器
```

### 2. 运行监听器

```bash
python solana.py
```

### 程序输出示例

```
╔══════════════════════════════════════════════════════════════╗
║                    🚀 Solana Token 监听器 🚀                    ║
║                                                              ║
║  📡 监听地址数量: 2                                          ║
║  🔗 RPC节点数量: 2                                          ║
║  📱 Telegram通知: 已启用                                    ║
║                                                              ║
║  🎯 功能: 监听SPL Token到账 → 发送Telegram通知                    ║
╚══════════════════════════════════════════════════════════════╝

[2024-01-01 12:00:00] 🚀 Solana Token监听器启动完成，正在监听 5 个Token账户
[2024-01-01 12:00:01] 🎧 开始监听 ATA: 9WzDXwB...AWWM (代币: EPjFW...Ue2)
[2024-01-01 12:00:02] 📡 正在连接WebSocket: wss://api.mainnet-beta.solana.com
[2024-01-01 12:00:03] ✅ WebSocket连接成功，开始监听余额变化
```

## 📱 Telegram通知格式

当检测到Token到账时，会发送如下格式的通知：

```
🚨 **SPL Token 到账警报** 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⛓️ **链**: Solana
📥 **接收地址**: `9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM`
💰 **增加数量**: `100.5`
💰 **当前余额**: `100.5`
📜 **代币合约**: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
🕐 **时间**: `2024-01-01 12:00:00`
🔗 **交易哈希**: `5J7X...abc123`
🔍 **查看链接**: [Solscan](https://solscan.io/tx/5J7X...abc123)
```

## 🔧 配置说明

### RPC节点配置

- `http_urls`: HTTP RPC节点列表，用于查询账户信息和交易详情
- WebSocket URL会自动从HTTP URL生成，无需手动配置
- 建议配置多个节点以提高稳定性

### 监听地址

- `watch_addresses`: 要监听的Solana钱包地址列表
- 程序会自动发现这些地址下的所有SPL Token账户
- 支持监听多个地址

### Telegram配置

- `bot_token`: 从@BotFather获得的机器人Token
- `chat_id`: 接收通知的聊天ID（个人、群组或频道）

## 🛠️ 故障排除

### 常见问题

1. **连接失败**
   - 检查网络连接
   - 确认RPC节点地址正确
   - 尝试使用不同的RPC节点

2. **Telegram通知失败**
   - 确认Bot Token正确
   - 确认Chat ID正确
   - 检查机器人是否已启动

3. **监听不到Token**
   - 确认钱包地址正确
   - 检查地址是否有Token账户
   - 确认RPC节点响应正常

### 日志级别

程序使用彩色日志输出：
- 🟢 绿色：成功信息
- 🔵 蓝色：连接信息
- 🟡 黄色：警告信息
- 🔴 红色：错误信息

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## ⚠️ 免责声明

此工具仅供学习和研究使用，请确保遵守相关法律法规。使用本工具产生的任何后果由用户自行承担。 