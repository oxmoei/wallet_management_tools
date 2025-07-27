

# 主要功能
批量转移多个 EVM 链上的原生币和 ERC20 代币

# 注意事项
运行转移资产脚本前先执行'python3 used_chains.py'，生成**used_chains.json**
RPC_list.json 配置的为**公开 RPC 端点**，可能会失效、限频或不稳定，最好修改为自己的**专属 RPC 端点**（可在 Alchemy、Infura、Ankr、Blast 等提供商上免费注册）。

python3 /home/star/tools/钱包管理/scavenger/src/used_chains.py