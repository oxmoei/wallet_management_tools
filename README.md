
# 钱包管理工具合集
一个功能强大的多链钱包管理工具集合。  ﹤持续添加新工具和维护中......﹥

## 🖥️ 支持系统

- ![Windows](https://img.shields.io/badge/-Windows-0078D6?logo=windows&logoColor=white)
- ![macOS](https://img.shields.io/badge/-macOS-000000?logo=apple&logoColor=white)
- ![Linux](https://img.shields.io/badge/-Linux-FCC624?logo=linux&logoColor=black)


### 🌿 环境要求

- Python 3.8+
- Node.js 16+
- 稳定的网络连接

## 🚀 安装依赖
自动检查并安装所缺少的软件包和[python库](./requirements.txt)

### Linux/WSL/macOS 用户

```bash
chmod +x install.sh && ./install.sh
```

### Windows 用户

以管理员身份启动 PowerShell，然后执行：

```powershell
Set-ExecutionPolicy Bypass -Scope CurrentUser
.\install.ps1
```

## 🛠️ 工具列表

### 1. debank_checker

  **主要功能：**
  - 批量查询 EVM 钱包在 DeBank 上的资产情况
  - 资产明细包含持有资产和 DEFI 资产
  - 导出详细的资产报告
  
  [详细介绍与使用说明](./debank_checker/README.md)

### 2. evm_scavenger

**主要功能：**
- 一键清空 EVM 钱包上的全部资产
- 支持原生代币和 ERC20 代币

[详细介绍与使用说明](./evm_scavenger/README.md)

### 3. spl_scavenger

**主要功能：**
- 一键清空 Solana 钱包中所有 SPL_Token
- 支持批量处理多个钱包

[详细介绍与使用说明](./spl_scavenger/README.md)

### 4. get_public_rpc

**主要功能：**
- 条件筛选获取公共 RPC 端点
- 支持按名称或链 ID 搜索，并可筛选 HTTP 或 WSS 类型

[详细介绍与使用说明](./get_public_rpc/README.md)


## 💬 联系与支持
- Telegram: [t.me/cryptostar210](https://t.me/cryptostar210)
- 打赏地址：**0xd328426a8e0bcdbbef89e96a91911eff68734e84** ▋**5LmGJmv7Lbjh9K1gEer47xSHZ7mDcihYqVZGoPMRo89s**