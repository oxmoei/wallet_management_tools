import json
import sys
import os
import requests

# 定义颜色码
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_RED = '\033[91m'
COLOR_BLUE = '\033[94m'
COLOR_END = '\033[0m'
COLOR_PURPLE = '\033[95m'
COLOR_CYAN = '\033[96m'
COLOR_GRAY = '\033[90m' 

def find_rpc_entry(keyword, search_type="name"):
    """
    从 https://chainlist.org/rpcs.json 加载数据并查找符合条件的 RPC 条目。
    
    Args:
        keyword: 搜索关键词
        search_type: 搜索类型，"name" 或 "chainId"
    """
    try:
        # 从 URL 加载数据
        response = requests.get('https://chainlist.org/rpcs.json', timeout=30)
        response.raise_for_status()  # 检查 HTTP 错误
        rpc_data = response.json()
    except requests.RequestException as e:
        print(f"{COLOR_RED}错误：无法从 URL 加载数据 - {e}{COLOR_END}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"{COLOR_RED}错误：无法解析从 URL 获取的 JSON 数据{COLOR_END}")
        sys.exit(1)

    found_entries = []
    keyword_lower = keyword.lower()
    
    for item in rpc_data:
        if search_type == "name":
            # 根据关键词匹配 name 字段
            chain_name = item.get("name", "")
            if keyword_lower in chain_name.lower():
                found_entries.append(item)
        elif search_type == "chainId":
            # 根据关键词精准匹配 chainId 字段
            chain_id = str(item.get("chainId", ""))
            if keyword_input == chain_id:
                found_entries.append(item)

    return found_entries

def print_banner():
    """打印优雅的程序横幅"""
    banner = f"""

{COLOR_BLUE}██████╗ ██████╗  ██████╗    ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗{COLOR_END}
{COLOR_BLUE}██╔══██╗██╔══██╗██╔════╝    ██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗{COLOR_END}
{COLOR_BLUE}██████╔╝██████╔╝██║         █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝{COLOR_END}
{COLOR_BLUE}██╔══██╗██╔═══╝ ██║         ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗{COLOR_END}
{COLOR_BLUE}██║  ██║██║     ╚██████╗    ██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║{COLOR_END}
{COLOR_BLUE}╚═╝  ╚═╝╚═╝      ╚═════╝    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝{COLOR_END}
{COLOR_BLUE}╔═══════════════════════════════════════════════════════════════════════╗{COLOR_END}
{COLOR_BLUE}║{COLOR_END}                 {COLOR_GREEN}🔍 RPC 端点查找器 - 区块链连接专家 🔍{COLOR_END}                 {COLOR_BLUE}║{COLOR_END}
{COLOR_BLUE}║{COLOR_END}                  {COLOR_YELLOW}✨ 快速查找和筛选区块链RPC端点 ✨{COLOR_END}                    {COLOR_BLUE}║{COLOR_END}
{COLOR_BLUE}╚═══════════════════════════════════════════════════════════════════════╝{COLOR_END}
"""
    print(banner)

if __name__ == "__main__":
    print_banner()
    
    # 提示用户选择搜索类型
    print(f"\n{COLOR_GREEN}╭───────────────── 搜索配置 ─────────────────╮{COLOR_END}")
    print(f"{COLOR_GREEN}│{COLOR_END} {COLOR_YELLOW}请选择搜索类型：{COLOR_END}                           {COLOR_GREEN}│{COLOR_END}")
    print(f"{COLOR_GREEN}│{COLOR_END} {COLOR_YELLOW}1. 按名称 (name) 搜索{COLOR_END}                      {COLOR_GREEN}│{COLOR_END}")
    print(f"{COLOR_GREEN}│{COLOR_END} {COLOR_YELLOW}2. 按链ID (chainId) 搜索{COLOR_END}                   {COLOR_GREEN}│{COLOR_END}")
    print(f"{COLOR_GREEN}╰────────────────────────────────────────────╯{COLOR_END}")
    
    while True:
        choice = input(f"\n{COLOR_GREEN}🎯 请输入选择 (1 或 2): {COLOR_END}").strip()
        if choice in ["1", "2"]:
            break
        else:
            print(f"{COLOR_RED}❌ 无效选择，请输入 1 或 2{COLOR_END}")
    
    # 根据选择确定搜索类型
    search_type = "name" if choice == "1" else "chainId"
    search_field = "名称" if choice == "1" else "链ID"
    
    # 提示输入关键词
    print(f"\n{COLOR_BLUE}╭───────────────── 搜索参数 ─────────────────╮{COLOR_END}")
    if search_type == "chainId":
        keyword_input = input(f"{COLOR_GREEN}🔢 请输入链ID (精准匹配): {COLOR_END}")
    else:
        keyword_input = input(f"{COLOR_GREEN}🔍 请输入 {search_field} 关键词: {COLOR_END}")
    print(f"{COLOR_BLUE}╰────────────────────────────────────────────╯{COLOR_END}")

    # 选择 URL 类型
    print(f"\n{COLOR_PURPLE}╭───────────────── URL 类型 ─────────────────╮{COLOR_END}")
    print(f"{COLOR_PURPLE}│{COLOR_END} {COLOR_YELLOW}请选择要筛选的 URL 类型：{COLOR_END}                  {COLOR_PURPLE}│{COLOR_END}")
    print(f"{COLOR_PURPLE}│{COLOR_END} {COLOR_YELLOW}1. 🌐 http(s) URL{COLOR_END}                          {COLOR_PURPLE}│{COLOR_END}")
    print(f"{COLOR_PURPLE}│{COLOR_END} {COLOR_YELLOW}2. ⚡ wss URL{COLOR_END}                              {COLOR_PURPLE}│{COLOR_END}")
    print(f"{COLOR_PURPLE}╰────────────────────────────────────────────╯{COLOR_END}")
    
    while True:
        url_choice = input(f"\n{COLOR_GREEN}🌐 请输入选择 (1 或 2): {COLOR_END}").strip()
        if url_choice in ["1", "2"]:
            break
        else:
            print(f"{COLOR_RED}❌ 无效选择，请输入 1 或 2{COLOR_END}")
    url_type = "http" if url_choice == "1" else "wss"

    # 调用函数时传递关键词和搜索类型
    results = find_rpc_entry(keyword_input, search_type)

    # 新增：根据 url_type 进一步筛选
    filtered_results = []
    for entry in results:
        filtered_rpcs = []
        for rpc_item in entry.get("rpc", []):
            # 处理 rpc 可能是字典或字符串的情况
            if isinstance(rpc_item, dict):
                url = rpc_item.get("url", "")
            else:
                url = str(rpc_item)
            
            if url_type == "http" and url.startswith("http"):
                filtered_rpcs.append(rpc_item)
            elif url_type == "wss" and url.startswith("wss"):
                filtered_rpcs.append(rpc_item)
        if filtered_rpcs:
            new_entry = entry.copy()
            new_entry["rpc"] = filtered_rpcs
            filtered_results.append(new_entry)

    # 显示搜索进度
    print(f"\n{COLOR_BLUE}🔄 正在搜索区块链数据...{COLOR_END}")
    
    if filtered_results:
        # 将结果保存到文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file_path = os.path.join(script_dir, 'result.json')
        try:
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                json.dump(filtered_results, outfile, indent=2)
            
            print(f"\n{COLOR_GREEN}╭───────────────── 搜索结果 ─────────────────╮{COLOR_END}")
            print(f"{COLOR_GREEN}│{COLOR_END} {COLOR_YELLOW}🎉 搜索完成！{COLOR_END}                              {COLOR_GREEN}│{COLOR_END}")
            print(f"{COLOR_GREEN}│{COLOR_END} {COLOR_BLUE}📊 找到 {len(filtered_results)} 个匹配的条目{COLOR_END}                     {COLOR_GREEN}│{COLOR_END}")
            print(f"{COLOR_GREEN}│{COLOR_END} {COLOR_PURPLE}💾 结果已保存到: {output_file_path}{COLOR_END}")
            print(f"{COLOR_GREEN}╰────────────────────────────────────────────╯{COLOR_END}")
            
            # 显示RPC端点结果
            print(f"\n{COLOR_YELLOW}📋 RPC端点列表：{COLOR_END}")
            for i, entry in enumerate(filtered_results, 1):
                print(f"\n{COLOR_BLUE}🔗 {i}. {entry.get('name', 'Unknown')}{COLOR_END}")
                
                # 只显示RPC端点
                rpc_list = entry.get('rpc', [])
                if rpc_list:
                    for j, rpc in enumerate(rpc_list, 1):
                        if isinstance(rpc, dict):
                            url = rpc.get('url', '')
                            if url:
                                print(f"   {j}. {url}")
                        else:
                            print(f"   {j}. {rpc}")
                else:
                    print(f"   {COLOR_RED}无RPC端点{COLOR_END}")
                
                print(f"   {COLOR_GRAY}{'─' * 40}{COLOR_END}")
            
            if len(filtered_results) > 5:
                print(f"\n{COLOR_PURPLE}💡 提示：完整结果已保存到 {output_file_path}，共 {len(filtered_results)} 个条目{COLOR_END}")
                
        except IOError as e:
            print(f"\n{COLOR_RED}╭───────────────── 错误信息 ─────────────────╮{COLOR_END}")
            print(f"{COLOR_RED}│{COLOR_END} ❌ 无法写入文件 {output_file_path} - {e} {COLOR_RED}│{COLOR_END}")
            print(f"{COLOR_RED}╰────────────────────────────────────────────╯{COLOR_END}")
    else:
        print(f"\n{COLOR_YELLOW}╭───────────────── 搜索结果 ─────────────────╮{COLOR_END}")
        print(f"{COLOR_YELLOW}│{COLOR_END} ❌ 没有找到匹配的条目。{COLOR_END}                    {COLOR_YELLOW}│{COLOR_END}")
        print(f"{COLOR_YELLOW}│{COLOR_END} 💡 请尝试使用不同的关键词或搜索类型{COLOR_END}        {COLOR_YELLOW}│{COLOR_END}")
        print(f"{COLOR_YELLOW}╰────────────────────────────────────────────╯{COLOR_END}")
    
    # 程序结束信息
    print(f"\n{COLOR_PURPLE}╭───────────────── 程序结束 ─────────────────╮{COLOR_END}")
    print(f"{COLOR_PURPLE}│{COLOR_END} {COLOR_GREEN}🎯 感谢使用 RPC 端点查找器！{COLOR_END}               {COLOR_PURPLE}│{COLOR_END}")
    print(f"{COLOR_PURPLE}│{COLOR_END} {COLOR_BLUE}🌟 祝您区块链开发顺利！{COLOR_END}                    {COLOR_PURPLE}│{COLOR_END}")
    print(f"{COLOR_PURPLE}╰────────────────────────────────────────────╯{COLOR_END}") 