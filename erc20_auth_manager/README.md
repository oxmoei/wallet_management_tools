# ERC20代币授权管理工具

一个用于管理ERC20代币授权的Python工具，支持查询、撤销授权等操作。

## 功能特性

- 🔍 查询钱包代币授权情况
- ❌ 撤销指定代币的授权
- 🗑️ 撤销所有代币的授权
- ⛓️ 支持多链（Ethereum、BSC、Polygon、Arbitrum、Optimism等）
- 🔐 敏感信息从.env文件加载
- 🎨 美观的命令行界面

## 安装

1. 进入项目目录：
```bash
cd tools/钱包管理百宝箱/erc20_auth_manager
```

2. 运行安装脚本：
```bash
chmod +x install.sh
./install.sh
```

或者手动安装：

1. 切换到父目录安装依赖：
```bash
cd tools/钱包管理百宝箱
poetry install --no-root
```

2. 配置环境变量：
```bash
cd erc20_auth_manager
cp env.example .env
# 编辑.env文件，填入你的配置信息
```

3. 测试配置：
```bash
python3 test_setup.py
```

4. 快速启动：
```bash
chmod +x quick_start.sh
./quick_start.sh
```

## 使用方法

### 查询授权情况
```bash
# 查询指定地址的授权情况
cd tools/钱包管理百宝箱 && poetry run erc20-auth query --address 0x1234... --chain ethereum

# 查询当前钱包的授权情况
cd tools/钱包管理百宝箱 && poetry run erc20-auth query --chain ethereum
```

### 撤销授权
```bash
# 撤销指定代币的授权
cd tools/钱包管理百宝箱 && poetry run erc20-auth revoke --token 0x1234... --spender 0x5678... --chain ethereum

# 撤销所有代币的授权
cd tools/钱包管理百宝箱 && poetry run erc20-auth revoke-all --chain ethereum
```

### 支持的链
- ethereum (以太坊主网)
- bsc (币安智能链)
- polygon (Polygon)
- arbitrum (Arbitrum)
- optimism (Optimism)

## 配置说明

在`.env`文件中配置以下参数：

- `WALLET_PRIVATE_KEY`: 钱包私钥
- `ETHEREUM_RPC_URL`: 以太坊RPC节点
- `BSC_RPC_URL`: BSC RPC节点
- `POLYGON_RPC_URL`: Polygon RPC节点
- `ARBITRUM_RPC_URL`: Arbitrum RPC节点
- `OPTIMISM_RPC_URL`: Optimism RPC节点
- `DEFAULT_CHAIN`: 默认链（可选）

## 安全提醒

⚠️ **重要安全提醒**：
- 请妥善保管私钥，不要泄露给他人
- 建议使用测试网络进行测试
- 在生产环境中使用前，请充分测试

## 许可证

MIT License
