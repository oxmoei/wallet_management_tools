#!/bin/bash

# ERC20授权管理工具安装脚本

set -e

echo "=== ERC20授权管理工具安装脚本 ==="
echo

# 检查是否在正确的目录
if [ ! -f "example.py" ]; then
    echo "错误: 请在erc20_auth_manager目录下运行此脚本"
    exit 1
fi

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi

echo "Python版本检查通过: $python_version"
echo

# 切换到父目录安装依赖
echo "切换到父目录安装依赖..."
cd ..

# 检查Poetry
echo "检查Poetry..."
if ! command -v poetry &> /dev/null; then
    echo "Poetry未安装，正在安装..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "Poetry已安装"
fi

echo

# 安装依赖
echo "安装项目依赖..."
poetry install --no-root

echo

# 切换回erc20_auth_manager目录
cd erc20_auth_manager

# 创建.env文件
echo "创建环境配置文件..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "已创建.env文件，请编辑该文件并填入你的配置信息"
else
    echo ".env文件已存在"
fi

echo

# 设置权限
echo "设置脚本权限..."
chmod +x example.py

echo

echo "=== 安装完成 ==="
echo
echo "下一步操作:"
echo "1. 编辑.env文件，填入你的配置信息"
echo "2. 运行示例: python3 example.py"
echo "3. 使用命令行工具: poetry run erc20-auth --help"
echo
echo "支持的链:"
cd .. && poetry run erc20-auth chains
echo
echo "更多信息请查看README.md文件"
