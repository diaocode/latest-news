import os
import re
import yaml
from pathlib import Path
import shutil

def split_markdown_files(base_dirs):
    """自动拆分包含多篇文章的Markdown文件"""
    for base_dir in base_dirs:
        for root, _, files in os.walk(base_dir):
            for filename in files:
                if filename.endswith('.md'):
                    filepath = Path(root) / filename
                    process_file(filepath)

def process_file(filepath):
    """处理单个Markdown文件"""
    # 如果文件不存在，直接返回
    if not os.path.exists(filepath):
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip() + '\n'  # 确保末尾换行

    # 预处理检查：统计有效front matter数量
    front_matters = re.findall(r'^---\n(.+?)\n---', content, re.DOTALL | re.MULTILINE)
    
    # 如果只有1个或0个front matter则跳过
    if len(front_matters) < 2:
        return

    # 发现多个front matter，开始处理
    print(f"\n正在分析文件：{filepath}")
    print(f"检测到front matter数量：{len(front_matters)}")

    # 增强分割逻辑：严格匹配完整的文章结构
    # 使用更精确的分割方式，确保每个部分都是完整的文章
    articles = []
    current_pos = 0
    while True:
        # 查找下一个front matter的开始
        match = re.search(r'^---\n', content[current_pos:], re.MULTILINE)
        if not match:
            break
            
        start = current_pos + match.start()
        # 查找这个front matter的结束
        front_matter_end = re.search(r'\n---\n', content[start:], re.MULTILINE)
        if not front_matter_end:
            break
            
        # 查找下一个front matter的开始或文件结束
        next_start = re.search(r'\n---\n', content[start + front_matter_end.end():], re.MULTILINE)
        if next_start:
            end = start + front_matter_end.end() + next_start.start()
        else:
            end = len(content)
            
        article = content[start:end].strip() + '\n'
        if article:
            articles.append((start, end, article))
            
        current_pos = start + front_matter_end.end()
    
    print(f"检测到潜在文章数量：{len(articles)}")
    
    # 有效性检查：必须包含完整front matter且内容不重复
    valid_articles = []
    seen_slugs = set()
    seen_contents = set()
    duplicate_ranges = []  # 存储需要删除的重复内容的范围
    
    for start, end, article in articles:
        # 确保文章以front matter开头
        if not article.startswith('---\n'):
            print("警告：检测到不以front matter开头的内容，跳过")
            continue
            
        front_matter = re.match(r'^---\n(.+?)\n---', article, re.DOTALL)
        if front_matter:
            try:
                meta = yaml.safe_load(front_matter.group(1))
                slug = meta.get('slug')
                
                # 提取文章正文内容（去除front matter）
                content_only = article[front_matter.end():].strip()
                
                # 检查内容是否重复
                if content_only in seen_contents:
                    print(f"警告：发现重复的文章内容，slug: {slug}，跳过")
                    duplicate_ranges.append((start, end))
                    continue
                    
                if slug and slug not in seen_slugs:
                    seen_slugs.add(slug)
                    seen_contents.add(content_only)
                    valid_articles.append((slug, article))
                    print(f"找到有效文章，slug: {slug}")
                elif slug in seen_slugs:
                    print(f"警告：发现重复的slug: {slug}，跳过")
                    duplicate_ranges.append((start, end))
                else:
                    print("警告：未找到slug字段，跳过")
            except Exception as e:
                print(f"YAML解析错误：{str(e)}")
                continue
    
    # 如果发现重复内容，删除它们
    if duplicate_ranges:
        print("发现重复内容，准备删除...")
        # 创建备份
        backup_path = backup_to_err_articles(filepath)
        print(f"已备份原文件到：{backup_path}")
        
        # 删除重复内容
        new_content = content
        for start, end in sorted(duplicate_ranges, reverse=True):
            new_content = new_content[:start].rstrip() + new_content[end:]
        
        # 写入更新后的内容
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content.strip() + '\n')
        print("已删除重复内容")
        
    elif len(valid_articles) > 1:
        print(f"发现有效多篇文章：{len(valid_articles)}篇（基于唯一slug判断）")
        # 备份到err_articles目录
        err_backup_path = backup_to_err_articles(filepath)
        print(f"已备份到错误文件目录：{err_backup_path}")
        create_individual_articles(filepath.parent, valid_articles)
        
        # 删除原文件前先检查文件是否存在
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"已删除原始文件：{filepath}")
            except OSError as e:
                print(f"警告：删除原始文件失败：{e}")
    else:
        print("→ 未发现多篇有效文章，无需处理")

def backup_to_err_articles(filepath):
    """备份文件到项目根目录下的err_articles目录，保持原始的相对目录结构"""
    # 获取项目根目录（脚本所在目录的上一级）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 获取相对于项目根目录的路径
    rel_path = os.path.relpath(filepath, project_root)
    # 构建err_articles下的目标路径
    err_path = os.path.join(project_root, 'err_articles', rel_path)
    # 确保目标目录存在
    os.makedirs(os.path.dirname(err_path), exist_ok=True)
    # 复制文件
    shutil.copy2(filepath, err_path)
    return err_path

def create_individual_articles(directory, articles):
    """创建独立文章文件"""
    for slug, article in articles:
        try:
            # 创建新文件
            new_filename = f"{slug}.md"
            new_path = directory / new_filename
            
            # 写入内容，保持原始格式
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(article)
            print(f"已创建新文件：{new_path}")

        except Exception as e:
            print(f"创建文件时出错：{str(e)}")
            continue

if __name__ == "__main__":
    # 配置需要处理的目录（根据项目结构调整）
    TARGET_DIRS = [
        # 'err_articles/blog/shortstory',
        'blog/shortstory',
        'i18n/en/docusaurus-plugin-content-blog/shortstory'
    ]
    
    # 检查并创建目录结构
    for d in TARGET_DIRS:
        Path(d).mkdir(parents=True, exist_ok=True)
    
    split_markdown_files(TARGET_DIRS)
