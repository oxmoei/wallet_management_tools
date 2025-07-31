# 功能：根据【chain_index.json】的 “Chain_ID” 生成初始【RPC_list.json】，“rpc_url”字段留空。

#!/usr/bin/env python3

import json
import requests
import os

def generate_rpc_list_from_index():
    """从chain_index.json生成初始RPC_list.json，rpc_url留空"""
    index_path = 'tools/钱包管理/scavenger/conf/chain_index.json'
    rpc_list_path = 'tools/钱包管理/scavenger/conf/RPC_list.json'
    with open(index_path, 'r', encoding='utf-8') as f:
        chain_index = json.load(f)
    rpc_list = []
    for item in chain_index:
        chain_id = item.get('chain_id')
        if chain_id is not None:
            rpc_list.append({
                'chain_id': chain_id,
                'rpc_url': ''
            })
    with open(rpc_list_path, 'w', encoding='utf-8') as f:
        json.dump(rpc_list, f, indent=2, ensure_ascii=False)
    print(f"已根据chain_index.json生成初始RPC_list.json，共{len(rpc_list)}条")

def load_data():
    """加载数据文件"""
    with open('tools/钱包管理/scavenger/conf/RPC_list.json', 'r', encoding='utf-8') as f:
        rpc_list = json.load(f)
    
    # 在线加载chainlist
    url = 'https://chainlist.org/rpcs.json'
    response = requests.get(url)
    response.raise_for_status()
    chainlist = response.json()
    
    return rpc_list, chainlist

def strategy_keep_first(chainlist):
    """策略1: 使用第一个rpc url"""
    chain_info_map = {}
    for chain in chainlist:
        if 'chainId' in chain and 'rpc' in chain:
            chain_id = chain['chainId']
            name = chain.get('name', 'Unknown')
            
            # 从rpc数组中提取所有url
            rpc_urls = []
            for rpc_item in chain['rpc']:
                if 'url' in rpc_item:
                    rpc_urls.append(rpc_item['url'])
            
            if rpc_urls:  # 如果有可用的rpc url
                # 使用第一个rpc url
                url = rpc_urls[0]
                chain_info_map[chain_id] = {
                    'name': name,
                    'url': url,
                    'all_urls': rpc_urls
                }
    return chain_info_map

def strategy_use_all_rpc(chainlist):
    """策略2: 使用所有rpc url，用分号连接"""
    chain_info_map = {}
    for chain in chainlist:
        if 'chainId' in chain and 'rpc' in chain:
            chain_id = chain['chainId']
            name = chain.get('name', 'Unknown')
            
            # 从rpc数组中提取所有url
            rpc_urls = []
            for rpc_item in chain['rpc']:
                if 'url' in rpc_item:
                    rpc_urls.append(rpc_item['url'])
            
            if rpc_urls:  # 如果有可用的rpc url
                # 将所有url用分号连接
                combined_url = ';'.join(rpc_urls)
                chain_info_map[chain_id] = {
                    'name': name,
                    'url': combined_url,
                    'all_urls': rpc_urls
                }
    return chain_info_map

def strategy_select_best_rpc(chainlist):
    """策略3: 选择最佳的RPC URL (优先选择无跟踪的)"""
    chain_info_map = {}
    for chain in chainlist:
        if 'chainId' in chain and 'rpc' in chain:
            chain_id = chain['chainId']
            name = chain.get('name', 'Unknown')
            
            # 从rpc数组中提取所有url，并分析tracking状态
            rpc_items = []
            for rpc_item in chain['rpc']:
                if 'url' in rpc_item:
                    tracking = rpc_item.get('tracking', 'unknown')
                    rpc_items.append({
                        'url': rpc_item['url'],
                        'tracking': tracking
                    })
            
            if rpc_items:
                # 优先选择无跟踪的RPC
                no_tracking_urls = [item['url'] for item in rpc_items if item['tracking'] == 'none']
                limited_tracking_urls = [item['url'] for item in rpc_items if item['tracking'] == 'limited']
                
                if no_tracking_urls:
                    selected_url = no_tracking_urls[0]  # 选择第一个无跟踪的
                elif limited_tracking_urls:
                    selected_url = limited_tracking_urls[0]  # 选择第一个有限跟踪的
                else:
                    selected_url = rpc_items[0]['url']  # 选择第一个
                
                chain_info_map[chain_id] = {
                    'name': name,
                    'url': selected_url,
                    'all_urls': [item['url'] for item in rpc_items]
                }
    return chain_info_map

def strategy_select_best_rpc(chainlist):
    """策略3: 选择最佳的RPC URL (优先选择无跟踪的)"""
    chain_info_map = {}
    for chain in chainlist:
        if 'chainId' in chain and 'rpc' in chain:
            chain_id = chain['chainId']
            name = chain.get('name', 'Unknown')
            
            # 从rpc数组中提取所有url，并分析tracking状态
            rpc_items = []
            for rpc_item in chain['rpc']:
                if 'url' in rpc_item:
                    tracking = rpc_item.get('tracking', 'unknown')
                    rpc_items.append({
                        'url': rpc_item['url'],
                        'tracking': tracking
                    })
            
            if rpc_items:
                # 优先选择无跟踪的RPC
                no_tracking_urls = [item['url'] for item in rpc_items if item['tracking'] == 'none']
                limited_tracking_urls = [item['url'] for item in rpc_items if item['tracking'] == 'limited']
                
                if no_tracking_urls:
                    selected_url = no_tracking_urls[0]  # 选择第一个无跟踪的
                elif limited_tracking_urls:
                    selected_url = limited_tracking_urls[0]  # 选择第一个有限跟踪的
                else:
                    selected_url = rpc_items[0]['url']  # 选择第一个
                
                chain_info_map[chain_id] = {
                    'name': name,
                    'url': selected_url,
                    'all_urls': [item['url'] for item in rpc_items]
                }
    return chain_info_map

def analyze_chains(chainlist):
    """分析链信息"""
    chain_count = 0
    total_rpc_urls = 0
    
    for chain in chainlist:
        if 'chainId' in chain and 'rpc' in chain:
            chain_count += 1
            rpc_urls = []
            for rpc_item in chain['rpc']:
                if 'url' in rpc_item:
                    rpc_urls.append(rpc_item['url'])
            total_rpc_urls += len(rpc_urls)
    
    return chain_count, total_rpc_urls

def update_rpc_list(rpc_list, chain_info_map):
    """更新RPC列表"""
    updated_count = 0
    for item in rpc_list:
        chain_id = item.get('chain_id')
        if chain_id in chain_info_map:
            item['rpc_url'] = chain_info_map[chain_id]['url']
            updated_count += 1
            print(f"Updated chain_id {chain_id} ({chain_info_map[chain_id]['name']}) with url: {chain_info_map[chain_id]['url']}")
    
    return updated_count

def main():
    print("=== 链ID匹配工具 ===\n")
    # 先生成初始RPC_list.json
    generate_rpc_list_from_index()
    # 加载数据
    rpc_list, chainlist = load_data()
    
    # 分析链信息
    chain_count, total_rpc_urls = analyze_chains(chainlist)
    print(f"发现 {chain_count} 个链，总共 {total_rpc_urls} 个RPC URL")
    
    print("\n=== 选择处理策略 ===")
    print("1. 使用第一个RPC URL (默认)")
    print("2. 使用所有RPC URL，用分号连接")
    print("3. 选择最佳的RPC URL (优先无跟踪)")
    
    choice = input("\n请选择策略 (1-3，默认1): ").strip()
    if not choice:
        choice = "1"
    
    if choice == "1":
        chain_info_map = strategy_keep_first(chainlist)
        print("\n使用策略: 使用第一个RPC URL")
    elif choice == "2":
        chain_info_map = strategy_use_all_rpc(chainlist)
        print("\n使用策略: 使用所有RPC URL，用分号连接")
    elif choice == "3":
        chain_info_map = strategy_select_best_rpc(chainlist)
        print("\n使用策略: 选择最佳的RPC URL (优先无跟踪)")
    else:
        print("无效选择，使用默认策略")
        chain_info_map = strategy_keep_first(chainlist)
    
    # 更新RPC列表
    print("\n开始更新RPC列表...")
    updated_count = update_rpc_list(rpc_list, chain_info_map)
    
    # 保存文件
    with open('tools/钱包管理/scavenger/conf/RPC_list.json', 'w', encoding='utf-8') as f:
        json.dump(rpc_list, f, indent=2, ensure_ascii=False)
    
    print(f"\n更新完成! 总共更新了 {updated_count} 个链")
    print("文件已保存到: tools/钱包管理/scavenger/conf/RPC_list.json")

if __name__ == "__main__":
    main() 