"""
命令行界面模块
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import List, Optional

from .manager import ERC20AuthManager
from .config import Config

console = Console()

@click.group()
@click.option('--chain', '-c', default=None, help='指定链名称')
@click.pass_context
def main(ctx, chain):
    """ERC20代币授权管理工具"""
    ctx.ensure_object(dict)
    ctx.obj['chain'] = chain

@main.command()
@click.option('--address', '-a', help='要查询的地址')
@click.option('--tokens', '-t', multiple=True, help='要查询的代币地址列表')
@click.pass_context
def query(ctx, address, tokens):
    """查询代币授权情况"""
    try:
        chain = ctx.obj.get('chain')
        manager = ERC20AuthManager(chain)
        
        # 检查网络连接
        if not manager.check_network_status():
            console.print("[red]网络连接失败，请检查RPC配置[/red]")
            return
        
        # 显示钱包信息
        wallet_info = manager.get_wallet_info()
        console.print(Panel(
            f"钱包地址: {wallet_info['address']}\n"
            f"链: {wallet_info['chain']}\n"
            f"ETH余额: {wallet_info['balance_eth']:.6f}",
            title="钱包信息"
        ))
        
        # 查询授权
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("正在查询授权...", total=None)
            approvals = manager.query_approvals(address, list(tokens) if tokens else None)
            progress.update(task, completed=True)
        
        if approvals:
            # 创建表格显示结果
            table = Table(title="授权列表")
            table.add_column("代币", style="cyan")
            table.add_column("代币地址", style="blue")
            table.add_column("被授权地址", style="green")
            table.add_column("授权金额", style="yellow")
            
            for approval in approvals:
                table.add_row(
                    approval['token_symbol'],
                    approval['token_address'],
                    approval['spender'],
                    approval['allowance_formatted']
                )
            
            console.print(table)
        else:
            console.print("[yellow]未发现任何授权[/yellow]")
            
    except Exception as e:
        console.print(f"[red]查询失败: {e}[/red]")

@main.command()
@click.option('--token', '-t', required=True, help='代币地址')
@click.option('--spender', '-s', required=True, help='被授权地址')
@click.option('--address', '-a', help='授权者地址')
@click.pass_context
def revoke(ctx, token, spender, address):
    """撤销指定代币的授权"""
    try:
        chain = ctx.obj.get('chain')
        manager = ERC20AuthManager(chain)
        
        # 检查网络连接
        if not manager.check_network_status():
            console.print("[red]网络连接失败，请检查RPC配置[/red]")
            return
        
        # 获取代币信息
        token_info = manager.get_token_info(token)
        console.print(f"代币: {token_info['name']} ({token_info['symbol']})")
        
        # 确认操作
        if not click.confirm(f"确定要撤销 {token_info['symbol']} 对 {spender} 的授权吗？"):
            console.print("[yellow]操作已取消[/yellow]")
            return
        
        # 撤销授权
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("正在撤销授权...", total=None)
            tx_hash = manager.revoke_approval(token, spender, address)
            progress.update(task, completed=True)
        
        if tx_hash:
            console.print(f"[green]撤销成功！交易哈希: {tx_hash}[/green]")
        else:
            console.print("[yellow]无需撤销，该地址没有授权[/yellow]")
            
    except Exception as e:
        console.print(f"[red]撤销失败: {e}[/red]")

@main.command()
@click.option('--address', '-a', help='授权者地址')
@click.option('--tokens', '-t', multiple=True, help='要撤销的代币地址列表')
@click.pass_context
def revoke_all(ctx, address, tokens):
    """撤销所有代币的授权"""
    try:
        chain = ctx.obj.get('chain')
        manager = ERC20AuthManager(chain)
        
        # 检查网络连接
        if not manager.check_network_status():
            console.print("[red]网络连接失败，请检查RPC配置[/red]")
            return
        
        # 先查询当前授权
        approvals = manager.query_approvals(address, list(tokens) if tokens else None)
        
        if not approvals:
            console.print("[yellow]没有发现需要撤销的授权[/yellow]")
            return
        
        # 确认操作
        console.print(f"发现 {len(approvals)} 个授权:")
        for approval in approvals:
            console.print(f"  - {approval['token_symbol']} -> {approval['spender']}")
        
        if not click.confirm("确定要撤销所有授权吗？"):
            console.print("[yellow]操作已取消[/yellow]")
            return
        
        # 撤销所有授权
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("正在撤销所有授权...", total=len(approvals))
            tx_hashes = manager.revoke_all_approvals(address, list(tokens) if tokens else None)
            progress.update(task, completed=len(approvals))
        
        if tx_hashes:
            console.print(f"[green]成功撤销 {len(tx_hashes)} 个授权[/green]")
            for tx_hash in tx_hashes:
                console.print(f"  交易哈希: {tx_hash}")
        else:
            console.print("[yellow]没有成功撤销任何授权[/yellow]")
            
    except Exception as e:
        console.print(f"[red]撤销失败: {e}[/red]")

@main.command()
@click.option('--token', '-t', required=True, help='代币地址')
@click.option('--spender', '-s', required=True, help='被授权地址')
@click.option('--amount', '-a', required=True, help='授权金额')
@click.option('--address', '-addr', help='授权者地址')
@click.pass_context
def approve(ctx, token, spender, amount, address):
    """授权代币"""
    try:
        chain = ctx.obj.get('chain')
        manager = ERC20AuthManager(chain)
        
        # 检查网络连接
        if not manager.check_network_status():
            console.print("[red]网络连接失败，请检查RPC配置[/red]")
            return
        
        # 获取代币信息
        token_info = manager.get_token_info(token)
        console.print(f"代币: {token_info['name']} ({token_info['symbol']})")
        
        # 确认操作
        if not click.confirm(f"确定要授权 {amount} {token_info['symbol']} 给 {spender} 吗？"):
            console.print("[yellow]操作已取消[/yellow]")
            return
        
        # 执行授权
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("正在授权...", total=None)
            tx_hash = manager.approve_token(token, spender, amount, address)
            progress.update(task, completed=True)
        
        console.print(f"[green]授权成功！交易哈希: {tx_hash}[/green]")
        
    except Exception as e:
        console.print(f"[red]授权失败: {e}[/red]")

@main.command()
@click.option('--token', '-t', required=True, help='代币地址')
@click.option('--address', '-a', help='地址')
@click.pass_context
def balance(ctx, token, address):
    """查询代币余额"""
    try:
        chain = ctx.obj.get('chain')
        manager = ERC20AuthManager(chain)
        
        # 检查网络连接
        if not manager.check_network_status():
            console.print("[red]网络连接失败，请检查RPC配置[/red]")
            return
        
        # 获取代币信息
        token_info = manager.get_token_info(token)
        balance = manager.get_token_balance(token, address)
        
        console.print(Panel(
            f"代币: {token_info['name']} ({token_info['symbol']})\n"
            f"地址: {address or manager.wallet_address}\n"
            f"余额: {balance}",
            title="代币余额"
        ))
        
    except Exception as e:
        console.print(f"[red]查询失败: {e}[/red]")

@main.command()
def chains():
    """显示支持的链"""
    chains = Config.get_supported_chains()
    
    table = Table(title="支持的链")
    table.add_column("链名称", style="cyan")
    table.add_column("显示名称", style="blue")
    table.add_column("链ID", style="green")
    
    for chain in chains:
        chain_info = Config.get_chain_info(chain)
        table.add_row(chain, chain_info['name'], str(chain_info['chain_id']))
    
    console.print(table)

@main.command()
def info():
    """显示钱包信息"""
    try:
        chain = Config.get_default_chain()
        manager = ERC20AuthManager(chain)
        
        # 检查网络连接
        if not manager.check_network_status():
            console.print("[red]网络连接失败，请检查RPC配置[/red]")
            return
        
        wallet_info = manager.get_wallet_info()
        
        console.print(Panel(
            f"钱包地址: {wallet_info['address']}\n"
            f"链: {wallet_info['chain']}\n"
            f"RPC: {wallet_info['rpc_url']}\n"
            f"ETH余额: {wallet_info['balance_eth']:.6f}",
            title="钱包信息"
        ))
        
    except Exception as e:
        console.print(f"[red]获取信息失败: {e}[/red]")

if __name__ == '__main__':
    main()
