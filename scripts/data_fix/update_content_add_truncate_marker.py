# -*- coding: utf-8 -*-
import os
import re
from urllib.parse import quote

def insert_truncate_marker(content: str) -> str:
    """在文章内容的第13行位置单独写入一行标记：<!-- truncate -->
    Args:
        content: 原始文章内容
    Returns:
        str: 插入标记后的文章内容
    """
    lines = content.split('\n')
    if len(lines) >= 13:
        lines.insert(13, '<!-- truncate -->')
    return '\n'.join(lines)

def process_markdown_files(directory):
    """处理指定目录下的所有markdown文件
    Args:
        directory: 目录路径
    """
    # 遍历目录下的所有文件
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 插入截断标记
                updated_content = insert_truncate_marker(content)
                
                # 写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"Updated file: {file_path}")

def main():
    # 需要处理的目录列表
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    directories = [
        os.path.join(base_dir, 'blog/shortstory'),
        os.path.join(base_dir, 'weibo_daily'),
        os.path.join(base_dir, 'i18n/en/docusaurus-plugin-content-blog/shortstory'),
        os.path.join(base_dir, 'i18n/en/docusaurus-plugin-content-blog-weibo-daily')
    ]
    
    # 处理每个目录
    for directory in directories:
        if os.path.exists(directory):
            print(f"\nProcessing directory: {directory}")
            process_markdown_files(directory)
        else:
            print(f"Directory not found: {directory}")

if __name__ == '__main__':
    main()