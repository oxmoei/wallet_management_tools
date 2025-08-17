#!/bin/bash

# ERC20授权管理工具快速启动脚本

echo "=== ERC20授权管理工具快速启动 ==="
echo

# 检查是否在正确的目录
if [ ! -f "example.py" ]; then
    echo "错误: 请在erc20_auth_manager目录下运行此脚本"
    exit 1
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️ .env文件不存在，正在创建..."
    cp env.example .env
    echo "已创建.env文件，请编辑该文件并填入你的配置信息"
    echo "然后重新运行此脚本"
    exit 1
fi

# 测试配置
echo "测试项目配置..."
python3 test_setup.py

if [ $? -eq 0 ]; then
    echo
    echo "✅ 配置测试通过！"
    echo
    echo "可用的命令:"
    echo "1. 运行示例: python3 example.py"
    echo "2. 查询授权: cd .. && poetry run erc20-auth query"
    echo "3. 撤销所有授权: cd .. && poetry run erc20-auth revoke-all"
    echo "4. 查看帮助: cd .. && poetry run erc20-auth --help"
    echo
    echo "选择操作:"
    echo "1) 运行示例"
    echo "2) 查询授权"
    echo "3) 查看帮助"
    echo "4) 退出"
    echo
    read -p "请选择 (1-4): " choice
    
    case $choice in
        1)
            echo "运行示例..."
            python3 example.py
            ;;
        2)
            echo "查询授权..."
            cd .. && poetry run erc20-auth query
            ;;
        3)
            echo "查看帮助..."
            cd .. && poetry run erc20-auth --help
            ;;
        4)
            echo "退出"
            ;;
        *)
            echo "无效选择"
            ;;
    esac
else
    echo
    echo "❌ 配置测试失败，请检查配置"
fi
