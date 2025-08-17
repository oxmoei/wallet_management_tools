# RPC 端点管理工具集

本工具集包含两个主要功能：
1. **RPC 条目查询脚本** - 用于查询和筛选区块链 RPC 端点
2. **RPC 连接测试脚本** - 用于测试 RPC 端点的连接性和获取链信息

## 📋 工具概览

### 🔍 RPC 条目查询脚本 (`main.py`)
支持按名称或链 ID 搜索，并可筛选 HTTP 或 WSS 类型的 RPC 端点。

### 🧪 RPC 连接测试脚本 (`test_rpc.py`)
优雅美观的 RPC 连接测试工具，支持批量测试多个 RPC 端点的连接性和获取链信息。

## 🌟 功能特点

### RPC 条目查询脚本
- 🔍 **智能搜索**: 支持按区块链名称或链 ID 进行模糊搜索
- 🌐 **URL 类型筛选**: 可选择 HTTP(s) 或 WSS 类型的 RPC 端点
- 📊 **数据源**: 从 [chainlist.org](https://chainlist.org) 获取最新的 RPC 数据
- 💾 **结果保存**: 自动将查询结果保存为 JSON 文件

### RPC 连接测试脚本
- 🎨 **优雅界面**: 使用 ANSI 颜色和 Unicode 字符的美观输出
- 📊 **实时进度**: 显示测试进度条和百分比
- 🔗 **多协议支持**: 自动识别 HTTP/HTTPS 和 WebSocket 协议
- 📈 **链信息获取**: 获取区块高度、Gas 价格、链 ID 等关键信息
- 📋 **统计摘要**: 提供详细的测试结果统计
- ⚡ **批量测试**: 支持一次性测试多个 RPC 端点

## 📖 使用方法

### 🔴 RPC 条目查询脚本

#### 1. 运行程序
在 rpc_endpoint_finder 目录下执行以下命令：
```
poetry run python main.py
```

### 2. 按提示操作

脚本运行后会引导你完成以下步骤：

1. **选择搜索类型**：
   - `1` - 按名称 (name) 搜索
   - `2` - 按链ID (chainId) 搜索

2. **输入搜索关键词**：
   - 如果选择按名称搜索，输入区块链名称关键词（如：ethereum、polygon、bsc）
   - 如果选择按链ID搜索，请输入链ID (精准匹配)（如：1、56、137）

3. **选择 URL 类型**：
   - `1` - HTTP(s) URL
   - `2` - WSS URL

### 3. 查看结果

- 如果找到匹配的条目，结果会保存到 `result.json` 文件中
- 脚本会显示找到的条目数量和文件保存路径
- 如果没有找到匹配的条目，会显示相应提示

### 🔴 RPC 连接测试脚本

#### 1. 运行程序
在 rpc_endpoint_finder 目录下执行以下命令：
```
poetry run python test_rpc.py
```

#### 2. 输入 RPC 地址
- 按提示输入要测试的 RPC 地址
- 支持 HTTP/HTTPS 和 WebSocket 协议
- 输入空行结束输入

#### 3. 查看测试结果
- 实时显示测试进度和连接状态
- 获取每个 RPC 的区块高度、Gas 价格、链 ID 等信息
- 最后显示测试统计摘要

## 📊 使用示例

### 🔍 RPC 条目查询脚本示例

#### 示例 1：搜索以太坊相关 RPC

```
✨ RPC 条目查询脚本 ✨
请选择搜索类型：
1. 按名称 (name) 搜索
2. 按链ID (chainId) 搜索
请输入选择 (1 或 2): 1
请输入 名称 关键词: ethereum
请选择要筛选的 URL 类型：
1. http(s) URL
2. wss URL
请输入选择 (1 或 2): 1
✅ 找到 5 个匹配的条目，结果已保存到 /path/to/script/result.json
```

### 示例 2：搜索 `链ID` 为1的 RPC

```
✨ RPC 条目查询脚本 ✨
请选择搜索类型：
1. 按名称 (name) 搜索
2. 按链ID (chainId) 搜索

请输入选择 (1 或 2): 2
请输入链ID (精准匹配): 1

请选择要筛选的 URL 类型：
1. http(s) URL
2. wss URL

请输入选择 (1 或 2): 2
✅ 找到 3 个匹配的条目，结果已保存到 /path/to/script/result.json
```

### 🧪 RPC 连接测试脚本示例

#### 示例：测试多个 RPC 端点

```
╔══════════════════════════════════════════════════════════════╗
║                    🌐 RPC 连接测试工具                       ║
╚══════════════════════════════════════════════════════════════╝

━━━ 输入 RPC 地址 ━━━
ℹ 请输入要测试的 RPC 地址（输入空行结束输入）：
https://mainnet.infura.io/v3/YOUR_PROJECT_ID
https://bsc-dataseed.binance.org/
wss://eth-mainnet.ws.alchemyapi.io/v2/YOUR_API_KEY

━━━ 开始测试 ━━━
ℹ 准备测试 3 个 RPC 端点...

🔍 测试 RPC #1
🌐 RPC: https://mainnet.infura.io/v3/YOUR_PROJECT_ID

┌─ 连接状态: 成功
├─ 区块高度: 18,456,789
├─ Gas 价格: 25.67 Gwei
└─ 链 ID: 1

━━━ 测试结果摘要 ━━━
📊 统计信息:
  ✓ 成功: 2
  ✗ 失败: 1

╔══════════════════════════════════════════════════════════════╗
║                    测试完成于 2024-01-15 14:30:25            ║
║                    感谢使用 RPC 测试工具                     ║
╚══════════════════════════════════════════════════════════════╝
```

## 📋 输出文件格式

结果文件 `result.json` 包含以下格式的数据：

```json
[
  {
    "name": "Ethereum Mainnet",
    "chainId": 1,
    "rpc": [
      "https://eth-mainnet.alchemyapi.io/v2/your-api-key",
      "https://mainnet.infura.io/v3/your-project-id"
    ],
    "nativeCurrency": {
      "name": "Ether",
      "symbol": "ETH",
      "decimals": 18
    },
    "blockExplorers": [
      {
        "name": "Etherscan",
        "url": "https://etherscan.io"
      }
    ]
  }
]
```

## ⚙️ 技术特点

### RPC 条目查询脚本
- **数据源**: 使用 [chainlist.org](https://chainlist.org) 的公开 API
- **超时处理**: 网络请求设置 30 秒超时
- **编码处理**: 使用 UTF-8 编码保存文件
- **路径处理**: 使用 `os.path` 确保跨平台兼容性

### RPC 连接测试脚本
- **Web3 集成**: 使用 web3.py 库进行区块链交互
- **多协议支持**: 自动识别 HTTP/HTTPS/WebSocket 协议
- **ANSI 颜色**: 使用 ANSI 转义序列实现彩色输出
- **Unicode 字符**: 使用 Unicode 字符绘制美观的界面元素
- **进度显示**: 实时进度条和百分比显示
- **错误处理**: 完善的异常处理和用户友好的错误提示

## ❓ 常见问题

### RPC 条目查询脚本

#### Q: 搜索结果为空怎么办？
A: 尝试使用更宽泛的关键词，或者检查网络连接是否正常

#### Q: 结果文件保存在哪里？
A: 结果文件会保存在脚本所在的目录中，文件名为 `result.json`

#### Q: 如何获取 WSS 类型的 RPC？
A: 在 URL 类型选择时选择选项 2 (WSS URL)

### RPC 连接测试脚本

#### Q: 支持哪些 RPC 协议？
A: 支持 HTTP、HTTPS、WebSocket (ws://) 和 WebSocket Secure (wss://) 协议

#### Q: 如何结束 RPC 地址输入？
A: 直接按回车键（输入空行）即可结束输入

#### Q: 测试失败怎么办？
A: 检查 RPC 地址是否正确，网络连接是否正常，以及 RPC 服务是否可用

#### Q: 为什么有些 RPC 连接很慢？
A: 这取决于 RPC 服务提供商的响应速度和您的网络连接质量

---
## 💬 联系与支持
- Telegram: [t.me/cryptostar210](https://t.me/cryptostar210)
- 请我喝杯☕：**0xd328426a8e0bcdbbef89e96a91911eff68734e84** ▋**5LmGJmv7Lbjh9K1gEer47xSHZ7mDcihYqVZGoPMRo89s**