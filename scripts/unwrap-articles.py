# -*- coding: utf-8 -*-
import os
import re
import shutil
import io

def unwrap_markdown_files(base_dirs):
    """检查Markdown文件中是否被markdown标签包裹，如果有则移除
    需要移除的格式如下：
    ```markdown
    文章内容
    ```
    移除后的内容如下：
    文章内容

    """
    for base_dir in base_dirs:
        for root, _, files in os.walk(base_dir):
            for filename in files:
                if filename.endswith('.md'):
                    filepath = os.path.join(root, filename)
                    process_file(filepath)

def process_file(filepath):
    """处理单个Markdown文件"""
    # 如果文件不存在，直接返回
    if not os.path.exists(filepath):
        return
        
    with io.open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip() #+ u'\n'
    
    unwrapped_content = content

    # 检查是否被```markdown包裹
    pattern = r'^```markdown\s*\n([\s\S]*?)\n```\s*$'
    match = re.match(pattern, content)
    
    if match:
        # 如果匹配到了，提取内容部分
        unwrapped_content = match.group(1).strip()

        # 检查文章开头是否以 --- 开头，如果不是，则找到第一个 --- 的位置，删除文章开头到第一个 --- 之前的内容
        if not content.startswith('---'):
            start_pos = content.find('---')
            if start_pos != -1:
                unwrapped_content = content[start_pos:].strip() + u'\n'
    else:
        # 检查文章开头是否以 --- 开头，如果不是，则找到第一个 --- 的位置，删除文章开头到第一个 --- 之前的内容
        if not content.startswith('---'):
            start_pos = content.find('---')
            if start_pos != -1:
                unwrapped_content = content[start_pos:].strip() + u'\n'

    # 检查是否已经包含了<!-- truncate -->标记
    if not '<!-- truncate -->' in unwrapped_content:
        unwrapped_content = insert_truncate_marker(unwrapped_content)

    # 备份原文件
    # backup_path = str(filepath) + '.bak'
    # shutil.copy2(filepath, backup_path)
    # 写入新内容
    with io.open(filepath, 'w', encoding='utf-8') as f:
        f.write(unwrapped_content)


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


if __name__ == "__main__":
    # 配置需要处理的目录（根据项目结构调整）
    TARGET_DIRS = [
        # 'err_articles/blog/shortstory',
        'blog/shortstory',
        'i18n/en/docusaurus-plugin-content-blog/shortstory'
    ]
    
    # 检查并创建目录结构
    for d in TARGET_DIRS:
        if not os.path.exists(d):
            os.makedirs(d)
    
    # 检查并移除被markdown标签包裹的内容
    unwrap_markdown_files(TARGET_DIRS)
