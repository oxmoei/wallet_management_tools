# OKX OS 钱包资产查询工具

基于 OKX OS 钱包 API 的多链（不限于 EVM ）资产余额查询工具，支持查询 62+ 个区块链网络的资产余额。

## 🌟 功能特性

- **多链支持**: 支持 62+ 个区块链网络，包括主流公链（BTC、ETH、Solana、Sui等）和 Layer2 网络
- **批量查询**: 支持单个地址查询和批量地址查询
- **实时数据**: 通过 OKX API 获取实时资产余额数据
- **美观输出**: 使用彩色控制台输出，结果展示清晰
- **错误处理**: 完善的错误处理和重试机制
- **配置灵活**: 支持环境变量配置 API 密钥

## 📋 支持的区块链网络
- 官网文档：https://web3.okx.com/zh-hans/build/docs/waas/walletapi-resources-supported-networks

- 完整网络列表请查看 [chains.json](./chains.json) 文件。

## 🚀 快速开始

### 环境要求

- Node.js 16.0 或更高版本
- npm 或 yarn 包管理器

### 安装依赖

```bash
cd okxOS_checker
npm install
```

### 配置 API 密钥

- 获取 OKX API 密钥
1. 登录 [OKX 官网](https://web3.okx.com/zh-hans/build/dev-portal)
2. 进入 API 管理页面
3. 创建新的 API 密钥
4. 确保 API 密钥具有读取权限
5. 记录 API Key、Secret Key、Passphrase 和 Project 信息

- 在 `.env` 文件中添加您的 OKX API 配置：
```env
OKX_API_KEY=your_api_key_here
OKX_SECRET_KEY=your_secret_key_here
OKX_PASSPHRASE=your_passphrase_here
OKX_PROJECT=your_project_here
```

## 📖 使用方法

### 单个地址查询

查询单个钱包地址在所有支持网络上的资产余额：

```bash
npm run single
```

程序会提示您输入钱包地址（支持任何类型地址），然后显示该地址在所有支持网络上的资产余额。

```
┌───────────────────────┬──────────┐
│ 链名称                │ 资产估值 │
├───────────────────────┼──────────┤
│ Ethereum              │ 3.86     │
├───────────────────────┼──────────┤
│ Sui                   │ 5.48     │
├───────────────────────┼──────────┤
│ Bitcoin               │ 2.26     │
├───────────────────────┼──────────┤
│ BNB Smart Chain       │ 6.78     │
├───────────────────────┼──────────┤
│ Solana                │ 6.55     │
├───────────────────────┼──────────┤
│ Polygon               │ 2.95     │
└───────────────────────┴──────────┘
```

### 批量地址查询

批量查询多个钱包地址的资产余额：

```bash
npm run batch
```

程序会提示您输入多个钱包地址（每行一个，支持任何类型地址），然后显示各个地址的资产余额。

```
┌─────────┬──────────────────────────────────────────────┬──────────┐
│ (index) │ 钱包地址                                     │ 资产估值 │
├─────────┼──────────────────────────────────────────────┼──────────┤
│ 0       │ '0x1234567890123456789012345678901234567890' │ '2.52'   │
│ 1       │ 'bc1q6tzmdnsnkzljc6nplg46qahykal0e2myq6zusz' │ '11.93'  │
└─────────┴──────────────────────────────────────────────┴──────────┘
```

## ⚙️ 配置选项

### 环境变量

| 变量名 | 描述 | 必需 |
|--------|------|------|
| `OKX_API_KEY` | OKX API 密钥 | ✅ |
| `OKX_SECRET_KEY` | OKX API 密钥 | ✅ |
| `OKX_PASSPHRASE` | OKX API 密码短语 | ✅ |
| `OKX_PROJECT` | OKX 项目标识 | ✅ |`

## 📦 依赖包

主要依赖包包括：
- `axios` - HTTP 请求库
- `chalk` - 控制台颜色输出
- `cli-table3` - 表格输出

## 🛠️ 故障排除

### 常见问题
1. **网络连接** （检查： `ping -c 3 www.okx.com`）
   ```
   ❌ 无法连接到 OKX 的 API 服务器
   ```
   解决方案：尝试使用代理或在其它环境（ 如：VPS ）上运行。

2. **API 配置错误**
   ```
   ❌ 缺少必要的API配置: api_key, secret_key
   ```
   解决方案：检查 `.env` 文件中的 API 配置是否正确。

3. **区块链网络不支持**
   ```
   ❌ API错误: totalValueByAddress.chains: Chain not support
   ```
   解决方案：持续关注官方公示所支持的链列表 https://web3.okx.com/zh-hans/build/docs/waas/walletapi-resources-supported-networks ，手动更新`chains.json`。（有个别链虽然已公示支持，但实际并未支持。）

3. **查询结果不准确**
   ```
   ❌ 查询 EVM 钱包余额不够准确
   ```
   解决方案：OKX OS API 并未支持所有 EVM，如需查询更全面的结果，可移步`debank_checker`


## 💬 联系与支持
- Telegram: [t.me/cryptostar210](https://t.me/cryptostar210)
- 请我喝杯☕：**0xd328426a8e0bcdbbef89e96a91911eff68734e84** ▋**5LmGJmv7Lbjh9K1gEer47xSHZ7mDcihYqVZGoPMRo89s**