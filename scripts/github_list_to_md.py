import os
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timezone
from datetime import timedelta
import pytz
from utils_gemini import GeminiApiUtils
from github_trending import get_trending_repos
from typing import List
import shutil

# 加载 .env 文件
load_dotenv()

# Initialize AI API utils
ai_utils = GeminiApiUtils()

# 配置常量
OUTPUT_DIR = 'github_daily'  # 输出目录
FILE_PREFIX = 'Github-hot'  # 文件名前缀
FILE_EXT = '.md'  # 文件扩展名

class DataItem:
    def __init__(self, id: str, word: str, num: int, label_name: str, description: str, 
                 daily_stars: str = '0', built_by: List[str] = None, **kwargs):
        self.word = word
        self.num = num
        self.label_name = label_name
        self.description = description
        self.daily_stars = daily_stars
        self.built_by = built_by or []

    def convert_to_beijing_time(self, utc_time_str: str) -> str:
        """将UTC时间转换为北京时间"""
        try:
            # First try the original format
            utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            # If that fails, try the new format
            utc_time = datetime.strptime(utc_time_str, '%Y-%m-%d %H:%M:%S')
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_time = utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)
        return beijing_time.strftime('%Y年%m月%d日 %p%I:%M (北京时间)')

    def to_markdown(self, rank: int) -> str:
        """返回数据的Markdown格式"""
        # Only show label_name if it's not empty
        encoded_word = self.word.replace(' ', '%20')
        title = f"#### {rank}. [{self.word}](https://www.bing.com/search?q={encoded_word})"
        if self.label_name:
            title += f" ({self.label_name}) "
        # title += "\n"
        
        return (
            f"{title} **热度**：{self.num}\n"
        )

def fetch_data(current_time):
    """
    Fetch trending repositories using github_trending methods
    
    Args:
        current_time (datetime): Current time (not used in this implementation)
    
    Returns:
        list: A list of trending repositories
    """
    # Use the get_trending_repos method from github_trending
    trending_repos = get_trending_repos({
        'since': 'daily'  # Fetch daily trending repositories
    })
    
    # Transform the data to match the existing DataItem structure
    result_list = []
    for idx, repo in enumerate(trending_repos, 1):
        data_item = DataItem(
            id=str(idx),
            word=repo.get('owner', 'Unknown') + '/' + repo.get('repo', 'Unknown'),
            num=int(repo.get('stars', '0').replace(',', '')),
            label_name=repo.get('language', ''),
            description=repo.get('desc', ''),
            daily_stars=repo.get('daily_stars', '0'),
            built_by=repo.get('built_by', [])
        )
        result_list.append(data_item)
    
    return result_list

def generate_markdown(result_list, current_time, language='zh') -> str:
    """
    Generate Markdown content for GitHub trending repositories
    
    Args:
        result_list (list): List of trending repositories
        current_time (datetime): Current time for generating the markdown
        language (str): Language of the markdown content, either 'zh' or 'en'
    
    Returns:
        str: Markdown formatted content
    """
    # Prepare time-related information
    bj_time_str = current_time.strftime('%Y-%m-%d %H:%M')
    
    # Choose title and description based on language
    if language == 'zh':
        title = f"🚀 GitHub | {bj_time_str}"
        slug = f"github-trending-{bj_time_str}"
        keywords = "GitHub, 趋势, 开源项目"
        description = "🌟 每日精选 GitHub 最热门的开源项目，助你掌握技术脉搏！"
        tags = "GitHub, 开源, 趋势"
        header = "## 🔥 今日 GitHub 热门仓库一览"
        header_description = "以下是今日最受欢迎的开源项目，每一个都值得你关注！💡"
        daily_stars_text = "今日新增"
        language_text = "语言"
        description_text = "描述"
        built_by_text = "Built by"
        no_description = "暂无描述"
        no_contributors = "暂无贡献者信息"
        closing_header = "## 🌈 每日开源之旅"
        closing_description = "开源世界，无限可能！持续关注，发现更多精彩项目。"
        generated_by = "本报告由 GitHub 趋势爬虫自动生成 🤖"
    else:  # English
        title = f"🚀 GitHub | {bj_time_str}"
        slug = f"github-trending-{bj_time_str}"
        keywords = "GitHub, Trending, Open Source Projects"
        description = "🌟 Daily curated GitHub's most popular open-source projects to help you stay on the pulse of technology!"
        tags = "GitHub, Open Source, Trending"
        header = "## 🔥 Today's GitHub Hot Repositories"
        header_description = "Here are today's most popular open-source projects, each worth your attention! 💡"
        daily_stars_text = "Today's Stars"
        language_text = "Language"
        description_text = "Description"
        built_by_text = "Built by"
        no_description = "No description available"
        no_contributors = "No contributor information"
        closing_header = "## 🌈 Daily Open Source Journey"
        closing_description = "Open source world, infinite possibilities! Keep following, discover more amazing projects."
        generated_by = "This report is automatically generated by GitHub Trending Crawler 🤖"
    
    # Start markdown content with a fun header
    markdown_content = f"""---
title: {title}
slug: {slug}
keywords: [{keywords}]
description: {description}
authors: [yangshun]
date: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
tags: [{tags}]
---

{header}

> {header_description}

"""
    
    # Language emojis dictionary
    language_emojis = {
        'Python': '🐍', 
        'JavaScript': '✨', 
        'TypeScript': '🌐', 
        'Rust': '🦀', 
        'Ruby': '💎', 
        'Java': '☕', 
        'Go': '🚦', 
        'C++': '🔧', 
        'Dart': '🎯',
        'Unknown': '❓'
    }
    
    # Add repositories to markdown content
    for rank, result in enumerate(result_list, 1):
        # Choose an emoji based on the language or repository type
        lang_emoji = language_emojis.get(result.label_name, '📦')
        
        # Create a star rating emoji
        star_rating = '⭐' * min(5, max(1, int(len(str(result.num)) / 3)))
        
        # Remove spaces from the repository name for the URL
        url_safe_repo_name = result.word.replace(' ', '')
        github_url = f"https://github.com/{url_safe_repo_name}"
        
        # Generate contributors with GitHub profile links
        if result.built_by:
            contributors_links = [
                f"[{contributor}](https://github.com/{contributor})"
                for contributor in result.built_by
            ]
            contributors_str = ', '.join(contributors_links)
        else:
            contributors_str = no_contributors
        
        markdown_content += f"""### {rank}. {lang_emoji} [{result.word}]({github_url})

{star_rating} **Stars**: `{result.num}`   •   📈 **{daily_stars_text}**: `{result.daily_stars}`   •   **{language_text}**：`{result.label_name or '未知'}`

📝 **{description_text}**：{result.description or no_description}

🤝 **{built_by_text}**：{contributors_str}

---

"""
    
    # Add a closing section
    markdown_content += f"""{closing_header}

> {closing_description}

*{generated_by}*
"""
    
    return markdown_content

def generate_article_content(current_time=None):
    """
    Main function to generate GitHub trending markdown article
    
    Args:
        current_time (datetime, optional): Time to use for the article. Defaults to current time.
    
    Returns:
        str: Generated markdown content
    """
    # Use current time if not provided
    if current_time is None:
        current_time = datetime.now(timezone(timedelta(hours=8)))
    
    # Fetch trending repositories
    result_list = fetch_data(current_time)
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate filename
    filename = f"{OUTPUT_DIR}/{current_time.strftime('%Y-%m-%d')}-{FILE_PREFIX}-{current_time.strftime('%H')}{FILE_EXT}"
    
    # Generate Chinese markdown
    markdown_content_zh = generate_markdown(result_list, current_time, language='zh')
    
    # Write Chinese markdown content to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content_zh)
    
    # Generate English markdown
    markdown_content_en = generate_markdown(result_list, current_time, language='en')
    
    # Copy to i18n/en directory
    i18n_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'i18n', 'en', 'docusaurus-plugin-content-blog-github-daily')
    os.makedirs(i18n_dir, exist_ok=True)
    
    # Generate English filename in i18n directory
    i18n_filename = os.path.join(i18n_dir, os.path.basename(filename))
    
    # Write English markdown content to i18n directory
    with open(i18n_filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content_en)
    
    return markdown_content_zh

def write_to_md_file(content: str) -> str:
    """
    将生成的文章内容写入markdown文件
    :param content: markdown格式的文章内容
    """
    try:
        # 从内容中提取标题
        title_match = re.search(r'slug: (.*?)\n', content)
        if not title_match:
            print("无法从内容中提取标题")
            return
            
        # 获取标题并转换为英文文件名格式
        title = title_match.group(1)
        file_name = f"{title.lower().replace(' ', '-')}.md"
        
        # 确保目录存在
        output_dir = 'blog/shortstory'
        os.makedirs(output_dir, exist_ok=True)
        
        # 添加截断标记
        content = insert_truncate_marker(content)
        
        # 写入文件
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"文章已保存到: {file_path}")
        return file_name
    except Exception as e:
        print(f"保存文件时出错: {e}")


def write_to_en_md_file(content: str):
    """
    Write the generated English Weibo hot search content to markdown file in the i18n/en directory
    :param content: markdown formatted English content for Weibo hot search
    """
    # Extract the date and hour from the content
    match = re.search(r'date: (\d{4}-\d{2}-\d{2}) (\d{2}):00:00', content)
    if not match:
        print("Could not find date in content")
        return
    
    date_str = match.group(1)
    hour_str = match.group(2)
    
    # Ensure the output directory exists
    en_output_dir = os.path.join('i18n', 'en', 'docusaurus-plugin-content-blog-github-daily')
    os.makedirs(en_output_dir, exist_ok=True)
    
    # Generate the file name
    file_name = os.path.join(en_output_dir, f"{date_str}-{FILE_PREFIX}-{hour_str}{FILE_EXT}")
    
    # 添加截断标记
    content = insert_truncate_marker(content)
    
    # Write content to file
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"English Weibo hot search file {file_name} generated successfully.")

def write_to_en_article_file(content: str, article_file_name: str):
    """
    Write the generated English article content to markdown file in the i18n/en directory
    :param content: markdown formatted English article content
    :param article_file_name: original Chinese article file name to maintain consistency
    """
    try:
        # Get the base filename without the directory path
        base_filename = os.path.basename(article_file_name)
        
        # Ensure the output directory exists
        en_output_dir = os.path.join('i18n', 'en', 'docusaurus-plugin-content-blog', 'shortstory')
        os.makedirs(en_output_dir, exist_ok=True)
        
        # Generate the file name using the same base filename
        file_name = os.path.join(en_output_dir, base_filename)
        
        # 添加截断标记
        content = insert_truncate_marker(content)

        # Write content to file
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"English article file {file_name} generated successfully.")
    except Exception as e:
        print(f"Error saving English article file: {e}")

def insert_truncate_marker(content: str) -> str:
    """在文章内容的第12行位置单独写入一行标记：<!-- truncate -->
    Args:
        content: 原始文章内容
    Returns:
        str: 插入标记后的文章内容
    """
    lines = content.split('\n')
    if len(lines) >= 12:
        lines.insert(12, '<!-- truncate -->')
    return '\n'.join(lines)

def main():
    """
    Main function to run the GitHub trending scraper and generate markdown
    """
    # 获取当前时间（北京时间）
    current_time = datetime.now(timezone(timedelta(hours=8)))
    bj_time_str = current_time.strftime('%Y-%m-%d_%H')
    print(f"bj_time_str={bj_time_str}")

    # 生成Markdown文件
    markdown_content = generate_article_content(current_time)
    print(f"markdown_content=\n{markdown_content}")

if __name__ == "__main__":
    main()
