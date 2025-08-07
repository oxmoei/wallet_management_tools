#!/bin/bash

# 区块链工具集 CLI
# Blockchain Tools CLI

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 表情符号
ROCKET="🚀"
WALLET="💼"
CHAIN="⛓️"
COIN="🪙"
TOOLS="🛠️"
EXIT="👋"
ERROR="❌"
SUCCESS="✅"
INFO="ℹ️"
WARNING="⚠️"
MAGIC="✨"
FIRE="🔥"
STAR="⭐"
PALM="🖐️"

# 加载动画
show_loading() {
    local message="$1"
    local duration="$2"
    local i=0
    local chars=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")
    
    while [ $i -lt $duration ]; do
        echo -ne "\r${CYAN}${BOLD}${chars[$((i % 10))]} ${message}${NC}"
        sleep 0.1
        i=$((i + 1))
    done
    echo -ne "\r"
}

# 显示横幅
show_banner() {
    clear
    echo -e "${CYAN}${BOLD}"
    echo " __    __      _ _      _     _____            _     ___      _ _           _   _              "
    echo "/ / /\\ \\ \\__ _| | | ___| |_  /__   \\___   ___ | |   / __\\___ | | | ___  ___| |_(_) ___  _ __   "
    echo "\\ \\/  \\/ / _\` | | |/ _ \\ __|   / /\\/ _ \\ / _ \\| |  / /  / _ \\| | |/ _ \\/ __| __| |/ _ \\| '_ \\  "
    echo " \\  /\\  / (_| | | |  __/ |_   / / | (_) | (_) | | / /__| (_) | | |  __/ (__| |_| | (_) | | | | "
    echo "  \\/  \\/ \\__,_|_|_|\\___|\\__|  \\/   \\___/ \\___/|_| \\____/\\___/|_|_|\\___|\\___|\\__|_|\\___/|_| |_| "
    echo ""
    echo -e "${NC}"
    echo ""
}

# 显示主菜单
show_main_menu() {
    echo -e "${CYAN}${BOLD}${INFO} 请选择要使用的工具：${NC}"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # 钱包查询工具组
    echo -e "${BLUE}${BOLD}🔍 钱包余额查询工具${NC}"
    echo -e "${GREEN}${BOLD}  1.${NC} ${WALLET} 批量 EVM 钱包查余额"
    echo -e "${GREEN}${BOLD}  2.${NC} ${WALLET} 批量钱包查余额 (支持任何链)"
    echo -e "${GREEN}${BOLD}  3.${NC} ${WALLET} 单一 EVM 钱包查余额"
    echo -e "${GREEN}${BOLD}  4.${NC} ${WALLET} 单一钱包查余额 (支持任何链)"
    echo ""
    
    # 资产转移工具组
    echo -e "${BLUE}${BOLD}💸 资产转移工具${NC}"
    echo -e "${GREEN}${BOLD}  5.${NC} ${COIN} 一键转移各 EVM 链上的所有 ERC20 代币"
    echo -e "${GREEN}${BOLD}  6.${NC} ${COIN} 一键转移各 EVM 链上的所有原生代币"
    echo -e "${GREEN}${BOLD}  7.${NC} ${COIN} 一键转移 Solana 上的所有 SPL Token"
    echo ""
    
    # 开发工具组
    echo -e "${BLUE}${BOLD}🔧 开发工具${NC}"
    echo -e "${GREEN}${BOLD}  8.${NC} ${TOOLS} 获取最新的免费 RPC 端点"
    echo -e "${GREEN}${BOLD}  9.${NC} ${TOOLS} EVM 智能合约交互 (调用 ABI)"
    echo -e "${GREEN}${BOLD} 10.${NC} ${TOOLS} EVM 智能合约交互 (自定义 HEX)"
    echo -e "${GREEN}${BOLD} 11.${NC} ${FIRE} FlashBots 交易捆绑"
    echo ""
    
    # 退出选项
    echo -e "${PURPLE}${BOLD}  0. ${EXIT} 退出程序${NC}"
    echo "" 

    # 分隔线
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # 输入提示
    echo -e "${YELLOW}${BOLD}${INFO} 请输入选项编号: ${NC}"
}

# 检查工具是否存在
check_tool_exists() {
    local tool_path="$1"
    show_loading "正在检查工具文件..." 10
    if [ ! -f "$tool_path" ]; then
        echo -e "${RED}${ERROR} 错误: 工具文件不存在${NC}"
        echo -e "${YELLOW}${BOLD}路径: ${NC}$tool_path"
        return 1
    fi
    echo -e "${GREEN}${BOLD}${SUCCESS} 工具文件检查通过${NC}"
    return 0
}

# 检查目录是否存在
check_dir_exists() {
    local dir_path="$1"
    show_loading "正在检查目录..." 10
    if [ ! -d "$dir_path" ]; then
        echo -e "${RED}${ERROR} 错误: 目录不存在${NC}"
        echo -e "${YELLOW}${BOLD}路径: ${NC}$dir_path"
        return 1
    fi
    echo -e "${GREEN}${BOLD}${SUCCESS} 目录检查通过${NC}"
    return 0
}

# 执行工具
execute_tool() {
    local tool_name="$1"
    local command="$2"
    
    echo ""
    echo -e "${CYAN}${BOLD}${ROCKET} 正在执行: ${NC}${WHITE}${BOLD}$tool_name${NC}"
    echo -e "${YELLOW}${BOLD}${INFO} 命令: ${NC}$command"
    echo ""
    
    # 检查是否包含nano命令
    if [[ $command == *"nano"* ]]; then
        echo -e "${PURPLE}${BOLD}${PALM} 提示：准备使用nano编辑器来编辑 .env 文件${NC}"
        echo -e "     ${PURPLE}┌─────────────────────────────────────────┐${NC}"
        echo -e "     ${PURPLE}│  • 编辑完成后按 ${YELLOW}${BOLD}Ctrl + X${NC}${PURPLE} 退出           │${NC}"
        echo -e "     ${PURPLE}│  • 按 ${YELLOW}${BOLD}Y${NC}${PURPLE} 确认保存                        │${NC}"
        echo -e "     ${PURPLE}│  • 按 ${YELLOW}${BOLD}Enter${NC}${PURPLE} 确认文件名                  │${NC}"
        echo -e "     ${PURPLE}└─────────────────────────────────────────┘${NC}"
        echo ""
    fi
    
    # 询问是否继续执行
    echo -e "${YELLOW}${BOLD}${WARNING} 是否继续执行? (y/n): ${NC}"
    read -r continue_exec
    if [[ $continue_exec =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${GREEN}${BOLD}${SUCCESS} 开始执行...${NC}"
        echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        
        # 显示加载动画
        show_loading "正在准备执行工具..." 20
        
        # 显示执行进度
        echo -e "${BLUE}${BOLD}${ROCKET} 正在执行命令...${NC}"
        eval "$command"
        
        echo ""
        echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}${BOLD}${SUCCESS} 执行完成!${NC}"
        echo -e "${GREEN}${BOLD}${STAR} 工具已成功运行完毕${NC}"
    else
        echo -e "${YELLOW}${BOLD}${WARNING} 已取消执行${NC}"
        echo -e "${YELLOW}${BOLD}${INFO} 您可以稍后重新选择此选项${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}${BOLD}${INFO} 按任意键返回主菜单...${NC}"
    read -n 1
}

# 显示退出信息
show_exit_message() {
    echo ""
    echo -e "${CYAN}${BOLD}"
    echo "╔═════════════════════════════════════════════╗"
    echo "║  ${EXIT} 感谢使用 WEB3 钱包管理工具集 CLI! ${EXIT}    ║"
    echo "║  ${STAR} 祝您使用愉快! ${STAR}                        ║"
    echo "╚═════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# 主程序
main() {
    # 显示启动加载动画
    show_loading "正在启动 WEB3 钱包管理百宝箱..." 15
    echo ""
    
    while true; do
        show_banner
        show_main_menu
        read -r choice
        
        case $choice in
            1)
                # 批量 EVM 钱包查余额
                if check_tool_exists "debank_checker/main.py"; then
                    execute_tool "批量 EVM 钱包查余额" "python3 debank_checker/main.py"
                fi
                ;;
            2)
                # 批量钱包查余额--支持任何链
                if check_tool_exists "okxOS_checker/src/batch.js"; then
                    execute_tool "批量钱包查余额 (支持任何链)" "node okxOS_checker/src/batch.js"
                fi
                ;;
            3)
                # 单一 EVM 钱包查余额
                if check_tool_exists "debank_checker/gen_used_chains.py"; then
                    execute_tool "单一 EVM 钱包查余额" "python3 debank_checker/gen_used_chains.py"
                fi
                ;;
            4)
                # 单一钱包查余额--支持任何链
                if check_tool_exists "okxOS_checker/src/single.js"; then
                    execute_tool "单一钱包查余额 (支持任何链)" "node okxOS_checker/src/single.js"
                fi
                ;;
            5)
                # 一键转移 EVM 上的全部 ERC20
                if check_dir_exists "evm_scavenger"; then
                    local command="nano evm_scavenger/.env && python3 evm_scavenger/src/used_chains.py && python3 evm_scavenger/src/erc20.py"
                    execute_tool "一键转移 EVM 上的全部 ERC20" "$command"
                fi
                ;;
            6)
                # 一键转移 EVM 上的全部原生币
                if check_dir_exists "evm_scavenger"; then
                    local command="nano evm_scavenger/.env && python3 evm_scavenger/src/used_chains.py && python3 evm_scavenger/src/native.py"
                    execute_tool "一键转移 EVM 上的全部原生币" "$command"
                fi
                ;;
            7)
                # 一键转移 Solana 上的所有 SPL_Token
                if check_dir_exists "spl_scavenger"; then
                    local command="nano spl_scavenger/.env && python3 spl_scavenger/spl_scavenger.py"
                    execute_tool "一键转移 Solana 上的所有 SPL Token" "$command"
                fi
                ;;
            8)
                # 获取最新的免费 RPC 端点
                if check_tool_exists "rpc_endpoint_finder/main.py"; then
                    execute_tool "获取最新的免费 RPC 端点" "python3 rpc_endpoint_finder/main.py"
                fi
                ;;
            9)
                # EVM 智能合约交互--调用 ABI
                if check_tool_exists "smart_contract_toolkit/erc20_nft_manager.py"; then
                    local command="nano smart_contract_toolkit/.env && python3 smart_contract_toolkit/erc20_nft_manager.py"
                    execute_tool "EVM 智能合约交互 (调用 ABI)" "$command"
                fi
                ;;
            10)
                # EVM 智能合约交互--自定义 HEX
                if check_tool_exists "smart_contract_toolkit/custom_hex_executor.py"; then
                    local command="nano smart_contract_toolkit/.env && python3 smart_contract_toolkit/custom_hex_executor.py"
                    execute_tool "EVM 智能合约交互 (自定义 HEX)" "$command"
                fi
                ;;
            11)
                # flashBots 交易捆绑
                if check_dir_exists "flashbots_bundle_sender"; then
                    local command="nano flashbots_bundle_sender/.env && node flashbots_bundle_sender/src/main.js"
                    execute_tool "FlashBots 交易捆绑" "$command"
                fi
                ;;
            0)
                show_exit_message
                exit 0
                ;;
            *)
                echo -e "${RED}${ERROR} 无效选项，请重新选择${NC}"
                echo -e "${YELLOW}${BOLD}${INFO} 请输入 0-11 之间的数字${NC}"
                sleep 2
                ;;
        esac
    done
}

# 检查是否以正确的方式运行
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    # 给脚本执行权限
    chmod +x "$0"
    main
else
    echo -e "${RED}${ERROR} 请直接运行此脚本: ./blockchain_cli.sh${NC}"
fi 