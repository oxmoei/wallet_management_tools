# DeBank Checker

用于批量查询 EVM 钱包的持有资产和 defi 资产。

---
## 🗂️ 依赖库

```
alive_progress==3.1.4 - 进度条显示
loguru==0.6.0 - 日志记录
requests==2.28.2 - HTTP请求
termcolor==2.3.0 - 终端颜色输出
tls_client==0.2.1 - TLS客户端
tabulate - 表格美化（脚本中有检测，如果没有安装会降级到普通输出）
setuptools==65.0.0 - 包管理
```

## 1️⃣ main.py

### 功能简介
- 批量查询多个 EVM 钱包在各条链（及池子）上的资产余额。
- 支持详细模式（各链/池子余额明细）和简洁模式（仅总余额）。
- 支持多线程加速查询。
- 查询结果自动保存为 JSON 文件，并以表格形式美观展示。
- 支持筛选特定代币余额。

### 使用方法
在 debank_checker 目录下执行以下命令：
```
poetry run python main.py
```

- 按提示输入钱包地址（每行一个，两次回车结束）。
- 选择输出模式：详细/简洁。
- 按菜单选择操作：
  - 查询所有 EVM 链余额
  - 查询特定代币余额
  - 查看帮助
  - 退出

### 典型输出
- 钱包总数、总余额、余额大于0的钱包数
- 每个钱包的余额明细（可选）
- 结果文件：`balances.json`

---

## 2️⃣ used_chains_checker.py

### 功能简介
- 针对单个 EVM 钱包，分析其在各链上的代币分布。
- 自动生成 `used_chains.json`，包含每条链的名称、Chain_ID、代币明细和币种数量。
- 支持链ID映射、进度条、彩色输出。

### 使用方法
在 debank_checker 目录下执行以下命令：
```
poetry run python used_chains_checker.py
```

- 按提示输入一个钱包地址（仅支持单个地址）。
- 自动分析该地址在各链的代币分布。
- 结果文件：`used_chains.json`

### 典型输出
- 每条链的名称、ID、币种数量、代币明细
- 汇总表格和美观的终端输出

### 故障排除
- **ModuleNotFoundError: No module named...**: 未安装了所需的 python 库。| 解决方法：运行 `install.sh`或`install.ps1`进行安装。
- **获取 DeBank 数据很慢或失败**：请求被 Cloudflare 限制。| 解决方法：稍候重试、减少查询地址数、减少线程数。

## 💬 联系与支持
- Telegram: [t.me/cryptostar210](https://t.me/cryptostar210)
- 请我喝杯☕：**0xd328426a8e0bcdbbef89e96a91911eff68734e84** ▋**5LmGJmv7Lbjh9K1gEer47xSHZ7mDcihYqVZGoPMRo89s**