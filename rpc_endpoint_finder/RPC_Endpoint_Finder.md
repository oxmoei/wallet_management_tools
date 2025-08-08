# RPC 条目查询脚本

一个用于查询和筛选区块链 RPC 端点的 Python 脚本，支持按名称或链 ID 搜索，并可筛选 HTTP 或 WSS 类型的 RPC 端点。

## 功能特点

- 🔍 **智能搜索**: 支持按区块链名称或链 ID 进行模糊搜索
- 🌐 **URL 类型筛选**: 可选择 HTTP(s) 或 WSS 类型的 RPC 端点
- 📊 **数据源**: 从 [chainlist.org](https://chainlist.org) 获取最新的 RPC 数据
- 💾 **结果保存**: 自动将查询结果保存为 JSON 文件

## 使用方法

### 1. 运行程序
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

## 使用示例

### 示例 1：搜索以太坊相关 RPC

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

## 输出文件格式

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

## 错误处理

脚本包含完善的错误处理机制：

- **网络连接错误**: 当无法访问数据源时显示错误信息
- **JSON 解析错误**: 当数据格式不正确时显示错误信息
- **文件写入错误**: 当无法保存结果文件时显示错误信息
- **用户输入验证**: 确保用户输入的选择有效

## 技术特点

- **数据源**: 使用 [chainlist.org](https://chainlist.org) 的公开 API
- **超时处理**: 网络请求设置 30 秒超时
- **编码处理**: 使用 UTF-8 编码保存文件
- **路径处理**: 使用 `os.path` 确保跨平台兼容性

## 常见问题

### Q: 搜索结果为空怎么办？
A: 尝试使用更宽泛的关键词，或者检查网络连接是否正常

### Q: 结果文件保存在哪里？
A: 结果文件会保存在脚本所在的目录中，文件名为 `result.json`

### Q: 如何获取 WSS 类型的 RPC？
A: 在 URL 类型选择时选择选项 2 (WSS URL)

---
## 💬 联系与支持
- Telegram: [t.me/cryptostar210](https://t.me/cryptostar210)
- 请我喝杯☕：**0xd328426a8e0bcdbbef89e96a91911eff68734e84** ▋**5LmGJmv7Lbjh9K1gEer47xSHZ7mDcihYqVZGoPMRo89s**