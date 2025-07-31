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

if __name__ == "__main__":
    print(f"{COLOR_BLUE}✨ RPC 条目查询脚本 ✨{COLOR_END}")
    
    # 提示用户选择搜索类型
    print(f"\n{COLOR_GREEN}请选择搜索类型：{COLOR_END}")
    print(f"{COLOR_YELLOW}1. 按名称 (name) 搜索{COLOR_END}")
    print(f"{COLOR_YELLOW}2. 按链ID (chainId) 搜索{COLOR_END}")
    
    while True:
        choice = input(f"\n{COLOR_GREEN}请输入选择 (1 或 2): {COLOR_END}").strip()
        if choice in ["1", "2"]:
            break
        else:
            print(f"{COLOR_RED}无效选择，请输入 1 或 2{COLOR_END}")
    
    # 根据选择确定搜索类型
    search_type = "name" if choice == "1" else "chainId"
    search_field = "名称" if choice == "1" else "链ID"
    
    # 提示输入关键词
    if search_type == "chainId":
        keyword_input = input(f"\n{COLOR_GREEN}请输入链ID (精准匹配): {COLOR_END}")
    else:
        keyword_input = input(f"\n{COLOR_GREEN}请输入 {search_field} 关键词: {COLOR_END}")

    # 选择 URL 类型
    print(f"{COLOR_GREEN}请选择要筛选的 URL 类型：{COLOR_END}")
    print(f"{COLOR_YELLOW}1. http(s) URL{COLOR_END}")
    print(f"{COLOR_YELLOW}2. wss URL{COLOR_END}")
    while True:
        url_choice = input(f"\n{COLOR_GREEN}请输入选择 (1 或 2): {COLOR_END}").strip()
        if url_choice in ["1", "2"]:
            break
        else:
            print(f"{COLOR_RED}无效选择，请输入 1 或 2{COLOR_END}")
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

    if filtered_results:
        # 将结果保存到文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file_path = os.path.join(script_dir, 'result.json')
        try:
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                json.dump(filtered_results, outfile, indent=2)
            print(f"{COLOR_BLUE}✅ 找到 {len(filtered_results)} 个匹配的条目，结果已保存到 {output_file_path}{COLOR_END}")
        except IOError as e:
            print(f"{COLOR_RED}错误：无法写入文件 {output_file_path} - {e}{COLOR_END}")
    else:
        print(f"\n{COLOR_YELLOW}❌ 没有找到匹配的条目。{COLOR_END}") 