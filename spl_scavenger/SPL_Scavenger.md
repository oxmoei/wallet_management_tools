# 🧹 Solana SPL Token 清道夫 (Scavenger)

一个用于一键清空 Solana 钱包中所有 SPL_Token 的 Python 脚本。支持批量处理多个钱包，自动检测 Token 余额并转账到指定地址。

## ✨ 功能特性

- 🔍 **自动检测**: 自动扫描钱包中的所有 SPL_Token 账户
- 💸 **批量转账**: 支持同时处理多个钱包的 Token 转账
- 🎯 **精确转账**: 使用`transfer_checked`确保转账精度正确
- 🧪 **Dry Run模式**: 支持模拟运行，不实际执行转账
- ⚙️ **灵活配置**: 通过`.env`文件配置所有参数
- 📊 **统计报告**: 显示成功和失败的转账数量

## 📋 系统要求

- Python 3.8+
- Solana网络连接
- 目标地址需要已初始化（有SOL余额）

## 🔧 依赖库

脚本依赖以下Python库：

```
solana==0.36.6
solders==0.23.0
python-dotenv==1.0.0
colorama==0.4.6
requests==2.28.2
httpx==0.28.1
```

## 📖 使用方法

### 激活 python 虚拟环境
- **适用 linux/wsl/macOS 系统**
```bash
# 在项目根目录下执行以下命令
source venv/bin/activate
```
- **适用 windows 系统**
```powershell
# 在项目根目录下执行以下命令
.\venv\Scripts\Activate
```
### 基本使用
- **适用 linux/wsl/macOS 系统**
```bash
# 在 spl_scavenger 目录下执行以下命令
python3 spl_scavenger.py
```
- **适用 windows 系统**
```powershell
# 在 spl_scavenger 目录下执行以下命令
python spl_scavenger.py
```

### 配置说明

#### RPC_URL
Solana网络的RPC节点地址，支持：
- 主网: `https://api.mainnet-beta.solana.com`
- 测试网: `https://api.testnet.solana.com`
- 开发网: `https://api.devnet.solana.com`
- 自定义RPC: `https://your-rpc-endpoint.com`

#### TO_ADDRESS
接收所有Token的目标钱包地址。**重要**: 目标地址必须已经初始化（有SOL余额）。

#### DRY_RUN
- `true`: 模拟运行，显示将要执行的转账但不实际发送
- `false`: 实际执行转账

#### PRIVATE_KEY_X
源钱包的私钥，支持Base58格式。脚本会自动推导出对应的公钥地址。

## 📊 输出示例

```
============================================
  🧹 Solana SPL Token 清道夫 (Scavenger)
  💸 一键清空钱包 SPL Token 到指定地址
============================================

ℹ️ 已加载配置:
    🌐 RPC URL: https://api.mainnet-beta.solana.com
    🏦 目标地址: 6uqskVFXM3QYd7HfTRJYbthm8gQyWLQzZD1WawAWvWkN
    ⚙️ Dry Run: false
  ✅ 已加载私钥: PRIVATE_KEY_1 -> 🏠 2wVXwDnWUBoZqmFvFTMiUtMA5NZSvCtWBHgiEuHzBEd3

================================================================================
⏳ 开始处理钱包: 2wVXwDnWUBoZqmFvFTMiUtMA5NZSvCtWBHgiEuHzBEd3
✅ 获取到 3 个Token账户

🔍 发现Token: 71Vn8BVNsF3t6xE1bhH59coAxeCLwniKZQh3v3sFAMT9, 余额: 39000000000
✅ 获取代币精度: 9
✅ 获取最新区块哈希: 8L9UQRtaQELXzkKnrNiYwqFLR5mJXGh36HnnVVyMLJBn
✅ SPL Token转账成功: 3FnxzVfrtNEhSTH7n9rLQroPAcq5qF5yurH7Wgnn9x4jkShV1pzpKcNhvKoUhYeDcotg2Jo9i6migALv54VT8HSY
-----

⚠️ 发现空余额Token: 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU, 余额: 0
-----

========================================
🔆 所有链处理完成！（Dry-run: false）
✅ 成功: 1，❌ 失败: 0
========================================
```

## ⚠️ 注意事项

1. **目标地址初始化**: 确保目标地址已经初始化（有SOL余额），否则转账会失败
2. **私钥安全**: 私钥是敏感信息，请妥善保管，不要泄露给他人
3. **网络费用**: 每次转账都需要支付SOL作为网络费用
4. **Dry Run测试**: 建议先使用`DRY_RUN=true`测试配置是否正确
5. **RPC限制**: 某些RPC节点可能有请求频率限制

## ❓ 常见问题

### Q: 转账失败提示"invalid account data for instruction"
A: 确保目标地址已经初始化（有SOL余额）。

### Q: 获取账户信息失败
A: 检查RPC_URL是否正确，网络连接是否正常。

### Q: 私钥解析失败
A: 确保私钥格式正确，使用Base58编码格式。


## 🔒 安全建议

- 在测试网络上先验证脚本功能
- 使用专门的测试钱包进行测试
- 定期备份重要数据
- 不要在公共环境中暴露私钥

## 💬 联系与支持
- Telegram: [t.me/cryptostar210](https://t.me/cryptostar210)
- 打赏地址：**0xd328426a8e0bcdbbef89e96a91911eff68734e84** ▋**5LmGJmv7Lbjh9K1gEer47xSHZ7mDcihYqVZGoPMRo89s**
