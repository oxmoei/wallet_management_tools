# EVM 智能合约交互 CLI - PowerShell版本

# 颜色定义
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"
$BLUE = "Blue"
$PURPLE = "Magenta"
$CYAN = "Cyan"
$WHITE = "White"

# 表情符号
$ROCKET = "🚀"
$WALLET = "💼"
$CHAIN = "⛓️"
$COIN = "🪙"
$TOOLS = "🛠️"
$EXIT = "👋"
$ERROR = "❌"
$SUCCESS = "✅"
$INFO = "ℹ️"
$WARNING = "⚠️"
$MAGIC = "✨"
$FIRE = "🔥"
$STAR = "⭐"
$PALM = "🖐️"

# 加载动画
function Show-Loading {
    param(
        [string]$Message,
        [int]$Duration
    )
    
    $chars = @("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    
    for ($i = 0; $i -lt $Duration; $i++) {
        $char = $chars[$i % 10]
        Write-Host "`r$char $Message" -ForegroundColor $CYAN -NoNewline
        Start-Sleep -Milliseconds 100
    }
    Write-Host "`r" -NoNewline
}

# 显示横幅
function Show-Banner {
    Clear-Host
    Write-Host " __    __      _ _      _     _____            _     ___      _ _           _   _              " -ForegroundColor $CYAN
    Write-Host "/ / /\ \ \__ _| | | ___| |_  /__   \___   ___ | |   / __\___ | | | ___  ___| |_(_) ___  _ __   " -ForegroundColor $CYAN
    Write-Host "\ \/  \/ / _\` | | |/ _ \ __|   / /\/ _ \ / _ \| |  / /  / _ \| | |/ _ \\/ __| __| |/ _ \| '_ \  " -ForegroundColor $CYAN
    Write-Host " \  /\  / (_| | | |  __/ |_   / / | (_) | (_) | | / /__| (_) | | |  __/ (__| |_| | (_) | | | | " -ForegroundColor $CYAN
    Write-Host "  \/  \/ \__,_|_|_|\___|\__|  \/   \___/ \___/|_| \____/\___/|_|_|\___|\___|\__|_|\___/|_| |_| " -ForegroundColor $CYAN
    Write-Host ""
    
    # 重要提醒
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $YELLOW
    Write-Host "      ⚠️  重要提醒 ⚠️" -ForegroundColor $YELLOW
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $YELLOW
    Write-Host ""
    Write-Host "ℹ️ 请确保您已经安装必要的依赖和环境配置，否则无法正常使用!" -ForegroundColor $CYAN
    Write-Host "ℹ️ 如果您还没有安装依赖，请先退出程序并以管理员身份执行以下命令:" -ForegroundColor $CYAN
    Write-Host ""
    Write-Host "     🔜 ./install.ps1" -ForegroundColor $GREEN
    Write-Host ""
    Write-Host "ℹ️ 如果已经安装完成，请按任意键继续..." -ForegroundColor $CYAN
    Write-Host "⌨️ 按任意键继续..." -ForegroundColor $YELLOW -NoNewline
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host ""
    Write-Host ""
}

# 显示主菜单
function Show-MainMenu {
    Write-Host "$INFO 请选择要使用的工具：" -ForegroundColor $CYAN
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $CYAN
    
    # 钱包查询工具组
    Write-Host "🔍 钱包余额查询工具" -ForegroundColor $BLUE
    Write-Host "  1. $WALLET 批量 EVM 钱包查余额" -ForegroundColor $GREEN
    Write-Host "  2. $WALLET 批量钱包查余额 (支持任何链)" -ForegroundColor $GREEN
    Write-Host "  3. $WALLET 单一 EVM 钱包查余额" -ForegroundColor $GREEN
    Write-Host "  4. $WALLET 单一钱包查余额 (支持任何链)" -ForegroundColor $GREEN
    Write-Host ""
    
    # 资产转移工具组
    Write-Host "💸 资产转移工具" -ForegroundColor $BLUE
    Write-Host "  5. $COIN 一键转移各 EVM 链上的所有 ERC20 代币" -ForegroundColor $GREEN
    Write-Host "  6. $COIN 一键转移各 EVM 链上的所有原生代币" -ForegroundColor $GREEN
    Write-Host "  7. $COIN 一键转移 Solana 上的所有 SPL Token" -ForegroundColor $GREEN
    Write-Host ""
    
    # 开发工具组
    Write-Host "🔧 开发工具" -ForegroundColor $BLUE
    Write-Host "  8. $TOOLS 获取最新的免费 RPC 端点" -ForegroundColor $GREEN
    Write-Host "  9. $TOOLS EVM 智能合约交互 (调用 ABI)" -ForegroundColor $GREEN
    Write-Host " 10. $TOOLS EVM 智能合约交互 (自定义 HEX)" -ForegroundColor $GREEN
    Write-Host " 11. $FIRE FlashBots 交易捆绑" -ForegroundColor $GREEN
    Write-Host ""
    
    # 监控工具组
    Write-Host "📊 监控工具" -ForegroundColor $BLUE
    Write-Host " 12. $TOOLS 监控多条 EVM 链的 ERC20 代币余额变动" -ForegroundColor $GREEN
    Write-Host " 13. $TOOLS 监控 Solana 的 SPL 余额变动" -ForegroundColor $GREEN
    Write-Host ""
    
    # 退出选项
    Write-Host "  0. $EXIT 退出程序" -ForegroundColor $PURPLE
    Write-Host "" 

    # 分隔线
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $CYAN

    # 输入提示
    Write-Host "$INFO 请输入选项编号: " -ForegroundColor $YELLOW -NoNewline
}

# 检查工具是否存在
function Test-ToolExists {
    param([string]$ToolPath)
    
    Show-Loading "正在检查工具文件..." 10
    if (-not (Test-Path $ToolPath)) {
        Write-Host "$ERROR 错误: 工具文件不存在" -ForegroundColor $RED
        Write-Host "路径: $ToolPath" -ForegroundColor $YELLOW
        return $false
    }
    Write-Host "$SUCCESS 工具文件检查通过" -ForegroundColor $GREEN
    return $true
}

# 检查目录是否存在
function Test-DirectoryExists {
    param([string]$DirPath)
    
    Show-Loading "正在检查目录..." 10
    if (-not (Test-Path $DirPath -PathType Container)) {
        Write-Host "$ERROR 错误: 目录不存在" -ForegroundColor $RED
        Write-Host "路径: $DirPath" -ForegroundColor $YELLOW
        return $false
    }
    Write-Host "$SUCCESS 目录检查通过" -ForegroundColor $GREEN
    return $true
}

# 执行工具
function Execute-Tool {
    param(
        [string]$ToolName,
        [string]$Command
    )
    
    Write-Host ""
    Write-Host "$ROCKET 正在执行: $ToolName" -ForegroundColor $CYAN
    Write-Host "$INFO 命令: $Command" -ForegroundColor $YELLOW
    Write-Host ""
    
    # 检查是否包含notepad命令
    if ($Command -like "*notepad*") {
        Write-Host "🔊 提示：准备使用记事本来编辑 .env 文件" -ForegroundColor $PURPLE
        Write-Host "     ┌─────────────────────────────────────────┐" -ForegroundColor $PURPLE
        Write-Host "     │  • 编辑完成后按 Ctrl + S 保存           │" -ForegroundColor $PURPLE
        Write-Host "     │  • 按 Ctrl + X 或关闭窗口退出           │" -ForegroundColor $PURPLE
        Write-Host "     │  • 文件将自动保存                      │" -ForegroundColor $PURPLE
        Write-Host "     └─────────────────────────────────────────┘" -ForegroundColor $PURPLE
        Write-Host ""
    }
    
    # 询问是否继续执行
    Write-Host "$WARNING 是否继续执行? (y/n): " -ForegroundColor $YELLOW -NoNewline
    $continueExec = Read-Host
    if ($continueExec -match "^[Yy]$") {
        Write-Host ""
        Write-Host "$SUCCESS 开始执行..." -ForegroundColor $GREEN
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $CYAN
        Write-Host ""
        
        # 显示加载动画
        Show-Loading "正在准备执行工具..." 20
        
        # 显示执行进度
        Write-Host "$ROCKET 正在执行命令..." -ForegroundColor $BLUE
        
        try {
            # 执行命令
            Invoke-Expression $Command
        }
        catch {
            Write-Host "$ERROR 执行命令时出错: $($_.Exception.Message)" -ForegroundColor $RED
        }
        
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $CYAN
        Write-Host "$SUCCESS 执行完成!" -ForegroundColor $GREEN
        Write-Host "$STAR 工具已成功运行完毕" -ForegroundColor $GREEN
    }
    else {
        Write-Host "$WARNING 已取消执行" -ForegroundColor $YELLOW
        Write-Host "$INFO 您可以稍后重新选择此选项" -ForegroundColor $YELLOW
    }
    
    Write-Host ""
    Write-Host "$INFO 按任意键返回主菜单..." -ForegroundColor $YELLOW
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# 显示退出信息
function Show-ExitMessage {
    Write-Host ""
    Write-Host "╔═════════════════════════════════════════════╗" -ForegroundColor $CYAN
    Write-Host "║  $EXIT 感谢使用 WEB3 钱包管理工具集 CLI! $EXIT    ║" -ForegroundColor $CYAN
    Write-Host "║  $STAR 祝您使用愉快! $STAR                        ║" -ForegroundColor $CYAN
    Write-Host "╚═════════════════════════════════════════════╝" -ForegroundColor $CYAN
    Write-Host ""
}

# 主程序
function Main {
    # 显示启动加载动画
    Show-Loading "正在启动 WEB3 钱包管理百宝箱..." 15
    Write-Host ""
    
    while ($true) {
        Show-Banner
        Show-MainMenu
        $choice = Read-Host
        
        switch ($choice) {
            "1" {
                # 批量 EVM 钱包查余额
                if (Test-ToolExists "debank_checker/main.py") {
                    Execute-Tool "批量 EVM 钱包查余额" "poetry run python debank_checker/main.py"
                }
            }
            "2" {
                # 批量钱包查余额--支持任何链
                if (Test-ToolExists "okxOS_checker/src/batch.js") {
                    Execute-Tool "批量钱包查余额 (支持任何链)" "node okxOS_checker/src/batch.js"
                }
            }
            "3" {
                # 单一 EVM 钱包查余额
                if (Test-ToolExists "debank_checker/gen_used_chains.py") {
                    Execute-Tool "单一 EVM 钱包查余额" "poetry run python debank_checker/used_chains_checker.py"
                }
            }
            "4" {
                # 单一钱包查余额--支持任何链
                if (Test-ToolExists "okxOS_checker/src/single.js") {
                    Execute-Tool "单一钱包查余额 (支持任何链)" "node okxOS_checker/src/single.js"
                }
            }
            "5" {
                # 一键转移 EVM 上的全部 ERC20
                if (Test-DirectoryExists "evm_scavenger") {
                    $command = "notepad evm_scavenger/.env; poetry run python evm_scavenger/src/gen_used_chains.py; poetry run python evm_scavenger/src/erc20.py"
                    Execute-Tool "一键转移 EVM 上的全部 ERC20" $command
                }
            }
            "6" {
                # 一键转移 EVM 上的全部原生币
                if (Test-DirectoryExists "evm_scavenger") {
                    $command = "notepad evm_scavenger/.env; poetry run python evm_scavenger/src/gen_used_chains.py; poetry run python evm_scavenger/src/native.py"
                    Execute-Tool "一键转移 EVM 上的全部原生币" $command
                }
            }
            "7" {
                # 一键转移 Solana 上的所有 SPL_Token
                if (Test-DirectoryExists "spl_scavenger") {
                    $command = "notepad spl_scavenger/.env; poetry run python spl_scavenger/spl_scavenger.py"
                    Execute-Tool "一键转移 Solana 上的所有 SPL Token" $command
                }
            }
            "8" {
                # 获取最新的免费 RPC 端点
                if (Test-ToolExists "rpc_endpoint_finder/main.py") {
                    Execute-Tool "获取最新的免费 RPC 端点" "poetry run python rpc_endpoint_finder/main.py"
                }
            }
            "9" {
                # EVM 智能合约交互--调用 ABI
                if (Test-ToolExists "smart_contract_toolkit/erc20_nft_manager.py") {
                    $command = "notepad smart_contract_toolkit/.env; poetry run python smart_contract_toolkit/erc20_nft_manager.py"
                    Execute-Tool "EVM 智能合约交互 (调用 ABI)" $command
                }
            }
            "10" {
                # EVM 智能合约交互--自定义 HEX
                if (Test-ToolExists "smart_contract_toolkit/custom_hex_executor.py") {
                    $command = "notepad smart_contract_toolkit/.env; poetry run python smart_contract_toolkit/custom_hex_executor.py"
                    Execute-Tool "EVM 智能合约交互 (自定义 HEX)" $command
                }
            }
            "11" {
                # flashBots 交易捆绑
                if (Test-DirectoryExists "flashbots_bundle_sender") {
                    $command = "notepad flashbots_bundle_sender/.env; node flashbots_bundle_sender/src/main.js"
                    Execute-Tool "FlashBots 交易捆绑" $command
                }
            }
            "12" {
                # 监控多条 EVM 链的 ERC20 代币余额变动
                if (Test-ToolExists "monitor/evm/evm_monitor.py") {
                    $command = "notepad monitor/evm/config.yaml; poetry run python monitor/evm/evm_monitor.py"
                    Execute-Tool "监控多条 EVM 链的 ERC20 代币余额变动" $command
                }
            }
            "13" {
                # 监控 Solana 的 SPL 余额变动
                if (Test-ToolExists "monitor/solana/spl_monitor.py") {
                    $command = "notepad monitor/solana/config.yaml; poetry run python monitor/solana/spl_monitor.py"
                    Execute-Tool "监控 Solana 的 SPL 余额变动" $command
                }
            }
            "0" {
                Show-ExitMessage
                exit 0
            }
            default {
                Write-Host "$ERROR 无效选项，请重新选择" -ForegroundColor $RED
                Write-Host "$INFO 请输入 0-13 之间的数字" -ForegroundColor $YELLOW
                Start-Sleep -Seconds 2
            }
        }
    }
}

# 检查是否以正确的方式运行
if ($MyInvocation.InvocationName -eq $MyInvocation.MyCommand.Name) {
    # 设置控制台编码以正确显示中文
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    
    # 运行主程序
    Main
}
else {
    Write-Host "$ERROR 请直接运行此脚本: .\cli_for_wins.ps1" -ForegroundColor $RED
} 