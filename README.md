
# 📦 钱包管理百宝箱

```
 __    __      _ _      _     _____            _     ___      _ _           _   _              
/ / /\ \ \__ _| | | ___| |_  /__   \___   ___ | |   / __\___ | | | ___  ___| |_(_) ___  _ __   
\ \/  \/ / _` | | |/ _ \ __|   / /\/ _ \ / _ \| |  / /  / _ \| | |/ _ \/ __| __| |/ _ \| '_ \  
 \  /\  / (_| | | |  __/ |_   / / | (_) | (_) | | / /__| (_) | | |  __/ (__| |_| | (_) | | | | 
  \/  \/ \__,_|_|_|\___|\__|  \/   \___/ \___/|_| \____/\___/|_|_|\___|\___|\__|_|\___/|_| |_|
```

一个功能强大的 web3 钱包管理工具集合。  ﹤持续添加新工具和维护中......﹥

## 🖥️ 支持系统

- ![Windows](https://img.shields.io/badge/-Windows-0078D6?logo=windows&logoColor=white)
- ![macOS](https://img.shields.io/badge/-macOS-000000?logo=apple&logoColor=white)
- ![Linux](https://img.shields.io/badge/-Linux-FCC624?logo=linux&logoColor=black)

## ♻️ 克隆仓库并进入项目目录
```bash
git clone https://github.com/oxmoei/wallet_management_tools.git && cd wallet_management_tools

```
## 🌿 安装依赖
自动检查并安装所缺少的 [软件包](./dependencies.txt) 和 [python库](./requirements.txt)

- **Linux/WSL/macOS 用户：**
在项目根目录下执行以下命令
```bash
chmod +x install.sh && ./install.sh
```

- **Windows 用户：**
以管理员身份启动 PowerShell，在项目根目录下执行以下命令
```powershell
Set-ExecutionPolicy Bypass -Scope CurrentUser
.\install.ps1
```

## 🚀 快速开始

### 启动 CLI 界面来管理所有工具

- **linux/wsl/macOs 用户：**
在项目根目录下执行以下命令
```bash
chmod +x cli.sh && ./cli.sh
```
- **windows 用户：**
以管理员身份启动 PowerShell，在项目根目录下执行以下命令
```powershell
.\cli_for_wins.ps1
```

## 🧾 工具合集

### 1️⃣ debank_checker

  **主要功能：**               ➡️[详细介绍与使用说明](./debank_checker/DeBank_Checker.md)
  - 批量查询 EVM 钱包的资产情况（基于 DeBank ）
  - 资产明细包含持有资产和 DEFI 资产（仅支持 EVM 链，如：Arbiturm、BSC、BeraChain、Merlin、Plume等）
  - 导出详细的资产报告
  
### 2️⃣ okxOS_checker

  **主要功能：**               ➡️[详细介绍与使用说明](./okxOS_checker/OKXOS_Checker.md)
  - 批量查询多链资产的余额（基于 OKXOS API ）
  - 支持 62+ 个区块链网络（不只限于 EVM 链，如：BTC、Litecoin、Dogecoin、Solana、Sui等）
  - 导出详细的资产报告
  
### 3️⃣ evm_scavenger

**主要功能：**                 ➡️[详细介绍与使用说明](./evm_scavenger/EVM_Scavenger.md)
- 一键转移 EVM 钱包上的全部资产
- 包括：一键清空原生代币（如：ETH、BNB、BERA等）和一键清空 ERC20 代币

### 4️⃣ spl_scavenger

**主要功能：**                 ➡️[详细介绍与使用说明](./spl_scavenger/SPL_Scavenger.md)
- 一键转移 Solana 钱包中所有 SPL_Token
- 支持批量处理多个钱包

### 5️⃣ rpc_endpoint_finder

**主要功能：**                 ➡️[详细介绍与使用说明](./rpc_endpoint_finder/RPC_Endpoint_Finder.md)
- 获取最新的免费 RPC 端点
- 支持按名称或链 ID 搜索，并可筛选 HTTP 或 WSS 类型

### 6️⃣ flashbots_bundle_sender

**主要功能：**                 ➡️[详细介绍与使用说明](./flashbots_bundle_sender/FlashBots_Bundle_Sender.md)
- 基于 FlashBots 的 MEV 交易捆绑发送工具
- 仅支持以太坊及其测试网

### 7️⃣ smart_contract_toolkit

**主要功能：**                 ➡️[详细介绍与使用说明](./smart_contract_toolkit/SmartContract_Toolkit.md)
- EVM 智能合约交互工具集
- 包括：调用 ABI 执行和自定义 HEX 执行

### 8️⃣ monitor

**主要功能：**                 ➡️[详细介绍与使用说明](./monitor/Monitor.md)
- 代币监控系统，实时监控代币到账并发送 Telegram 通知
- 支持 EVM 和 Solana 生态

## 💬 联系与支持
- Telegram: [t.me/cryptostar210](https://t.me/cryptostar210)
- 请我喝杯☕：**0xd328426a8e0bcdbbef89e96a91911eff68734e84** ▋**5LmGJmv7Lbjh9K1gEer47xSHZ7mDcihYqVZGoPMRo89s**