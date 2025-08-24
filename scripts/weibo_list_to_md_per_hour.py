import os
import re
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from datetime import timedelta
import pytz
from utils_gemini import GeminiApiUtils

# 加载 .env 文件
load_dotenv()

# Initialize AI API utils
ai_utils = GeminiApiUtils()

# 配置常量
OUTPUT_DIR = 'weibo_daily'  # 输出目录
FILE_PREFIX = 'Weibo-hot'  # 文件名前缀
FILE_EXT = '.md'  # 文件扩展名

class DataItem:
    def __init__(self, id: str, word: str, num: int, label_name: str, **kwargs):
        self.word = word
        self.num = num
        self.label_name = label_name

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

def fetch_data():
    """
    使用requests库获取微博热搜数据的函数
    """
    url = 'https://weibo.com/ajax/side/hotSearch'
    headers = {
        # 这里需要设置合适的请求头，模拟浏览器访问，以下是示例，你可根据实际情况调整
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果请求出现4xx、5xx错误，抛出异常
        data = response.json()  # 将响应内容解析为JSON格式数据
        
        hot_search_list = []
        for hot_item in data['data']['realtime']:
            word = hot_item['word']  # 热搜词条
            num = hot_item['num']  # 热度数值（具体含义根据微博定义）
            label_name = hot_item.get('label_name', '')  # Use get() with default empty string if key doesn't exist
            hot_search_list.append({
                'id': str(len(hot_search_list)),
                'word': word,
                'num': num,
                'label_name': label_name
            })
        
        # Sort by num and take top 30
        sorted_items = sorted(hot_search_list, key=lambda x: x['num'], reverse=True)[:30]
        return [DataItem(**item) for item in sorted_items]

    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return []


def generate_markdown(result_list,date_str) -> str:
    """生成Markdown内容并保存到指定目录"""
    """
    title 格式如下：
    ---
    title: Weibo热搜 | 2024-12-27_08
    slug: weibo-hot-20241227_08
    keywords: [Weibo,热搜]
    description: Weibo热搜,2024-12-27_08
    authors: [yangshun]
    date: 2024-12-27 08:00:00
    tags: [Weibo,hotSearch]
    ---
    """
    # 截取 date_str 前面的年份和月份和日期
    new_date_str = date_str[:10]
    short_date_str = date_str.replace('-', '')
    short_date_str = short_date_str[9:]
    print(f"short_date_str: {short_date_str}")


    markdown_content = f"---\ntitle: Weibo热搜 | {date_str}\nslug: weibo-hot-{date_str}\nkeywords: [Weibo,热搜]\ndescription: Weibo热搜,{date_str}\nauthors: [yangshun]\ndate: {new_date_str} {short_date_str}:00:00\ntags: [Weibo,hotSearch]\n---\n\n"

    # 把 result_list 内容添加到 markdown_content 中
    for rank,result in enumerate(result_list,1):
        markdown_content += result.to_markdown(rank)

    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 生成文件名
    file_name = os.path.join(OUTPUT_DIR, f"{new_date_str}-{FILE_PREFIX}-{short_date_str}{FILE_EXT}")
    
    # 添加截断标记
    markdown_content = update_content(markdown_content)
    markdown_content = insert_truncate_marker(markdown_content)

    # 如果文件存在，直接覆盖
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(markdown_content)
    print(f"文件 {file_name} 生成成功并已覆盖。")
    return markdown_content

def convert_to_beijing_time(utc_time_str: str) -> str:
    """将UTC时间转换为北京时间"""
    try:
        # First try the original format
        utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        # If that fails, try the new format
        utc_time = datetime.strptime(utc_time_str, '%Y-%m-%d %H:%M:%S')
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_time = utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)
    return beijing_time.strftime('%Y-%m-%d_%H')

def generate_article_content(news_list_str) -> str:
    """生成文章的内容"""

    # news_list_str = """
    # 1. jellycat平替成上海圣诞节顶流(新) 热度：1145953
    # 2. 平安夜(新) 热度：878519
    # 3. 守护非遗之美(新) 热度：683863
    # 4. 肯德基涨价2%(热) 热度：613993
    # 5. 白鹿 没吻这么激烈(新) 热度：484818
    # """

    """
    过滤掉 news_list_str 开头的 --- 部分内容：

    ---
    title: Weibo热搜 | 2024-12-30_10
    slug: weibo-hot-2024-12-30_10
    keywords: [Weibo,热搜]
    description: Weibo热搜,2024-12-30_10
    authors: [yangshun]
    date: 2024-12-30 10:00:00
    tags: [Weibo,hotSearch]
    ---

    #### 1. [韩国又一客机起落架故障](https://www.bing.com/search?q=韩国又一客机起落架故障) (热)  **热度**：2019316
    #### 2. [雷军千万年薪挖角95后AI天才少女](https://www.bing.com/search?q=雷军千万年薪挖角95后AI天才少女) (新)  **热度**：1208120
    #### 3. [2024他们让五星红旗飘扬国际赛场](https://www.bing.com/search?q=2024他们让五星红旗飘扬国际赛场) **热度**：1086094

    """

    # 过滤掉 news_list_str  第二个 --- 之前的内容
    news_list_str = news_list_str.split('---')[2]

    print(f"news_list_str: \n{news_list_str}")

    news_lists = news_list_str

    print(f"news_lists:\n{news_lists}")

    response = ai_utils.generate_story_from_news(news_lists)
    print(f"生成文章内容: \n{response}")
    return response


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
        content = update_content(content)
        
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
    en_output_dir = os.path.join('i18n', 'en', 'docusaurus-plugin-content-blog-weibo-daily')
    os.makedirs(en_output_dir, exist_ok=True)
    
    # Generate the file name
    file_name = os.path.join(en_output_dir, f"{date_str}-{FILE_PREFIX}-{hour_str}{FILE_EXT}")
    
    # 添加截断标记
    content = update_content(content)
    
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
        content = update_content(content)

        # Write content to file
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"English article file {file_name} generated successfully.")
    except Exception as e:
        print(f"Error saving English article file: {e}")

def replace_punctuation(text: str) -> str:
    """
    Replace specific punctuation marks in the text:
    - English half-width double quotes -> Chinese double quotes "..."
    - English single quotes -> Chinese single quotes '...'
    - English colons -> Chinese colons ':'
    
    Does not modify text if it already contains Chinese quotes or single quotes.
    
    Args:
        text (str): Input text to process
    
    Returns:
        str: Text with punctuation replaced
    """
    # 替换英文双引号为中文双引号
    text = text.replace('"', '\u201c').replace('"', '\u201d')
    
    # 替换英文单引号为中文单引号
    text = text.replace("'", '\u2018').replace("'", '\u2019')
    
    # 替换英文冒号为中文冒号
    text = text.replace(':', '：')
    
    return text

def update_title(content: str) -> str:
    """解析出文章中第二行的标题，标题格式为：title: {文章标题}
    如果标题中包含英文半角双引号，则替换为中文的双引号"{标题内容}"
    如果标题中包含英文单引号，则替换为中文单引号'{标题内容}'
    如果标题中包含中文双引号，则不做修改
    如果标题中包含中文单引号，则不做修改
    """
    # 按行分割内容
    lines = content.split('\n')
    
    # 找到标题行（第二行）
    if len(lines) > 1 and lines[1].startswith('title:'):
        # 提取标题部分
        title = lines[1].split('title:')[1].strip()
        # 调用函数处理标题中的标点符号
        title = replace_punctuation(title)

        # 重新构建标题行
        lines[1] = f'title: {title}'
        
        # 重新组合内容
        return '\n'.join(lines)
    
    return content

def update_meta(content: str) -> str:
    """解析出文章中第7行的meta信息，meta信息格式为：meta: {meta内容}
    如果meta中包含英文半角双引号，则替换为中文的双引号"{meta内容}"
    如果meta中包含英文单引号，则替换为中文单引号'{meta内容}'
    如果meta中包含英文冒号，则替换为中文冒号'：'
    如果meta中包含中文双引号，则不做修改
    如果meta中包含中文单引号，则不做修改
    """
    lines = content.split('\n')
    
    # 检查是否有meta行
    if len(lines) < 7 or not lines[6].startswith('meta:'):
        return content
    
    # 提取meta行
    meta = lines[6].split('meta: ', 1)[1]
    
    # 使用 replace_punctuation 函数处理 meta 中的标点符号
    meta = replace_punctuation(meta)
    
    lines[6] = f'meta: {meta}'

    # 重新组合内容
    return '\n'.join(lines)

def update_description(content: str) -> str: 
    """解析出文章中第二行的描述，描述格式为：description: {文章描述}
    如果描述中包含英文半角双引号，则替换为中文的双引号"{描述内容}"
    如果描述中包含英文单引号，则替换为中文单引号'{描述内容}'
    如果描述中包含英文冒号，则替换为中文冒号'：'
    如果描述中包含中文双引号，则不做修改
    如果描述中包含中文单引号，则不做修改
    """
    lines = content.split('\n')
    
    # 检查是否有描述行
    if len(lines) < 2 or not lines[1].startswith('description:'):
        return content
    
    # 提取描述
    description = lines[1].split('description: ', 1)[1]
    
    # 使用 replace_punctuation 函数处理描述中的标点符号
    description = replace_punctuation(description)
    
    # 重新构建描述行
    lines[1] = f'description: {description}'
    
    # 重新组合内容
    return '\n'.join(lines)

def update_ending(content: str) -> str:
    """
    检查文章最后去掉空格或者空行是否有 '---' 标记，如果有则删除，如果没有则不做修改直接返回
    :param content: 原始文章内容
    :return: 删除截断标记后的文章内容
    """
    # 按行分割内容并去除末尾的空行
    lines = content.rstrip().split('\n')
    
    # 如果最后一行是 '---'，则删除
    if lines and lines[-1].strip() == '---':
        lines = lines[:-1]
    
    # 重新组合内容
    return '\n'.join(lines)

def update_content(content: str) -> str:
    new_content = update_title(content)
    # print(new_content)

    new_content = update_description(new_content)
    # print(new_content)

    new_content = update_meta(new_content)
    # print(new_content)

    new_content = update_ending(new_content)
    # print(new_content)

    return new_content


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

def main():
    # 获取Weibo数据
    results = fetch_data()
    # for result in results:
    #     print(result)

    # 获取今天的日期并格式化
    date_today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    # print(f"date_today_str={date_today_str}")
    bj_time_str = convert_to_beijing_time(date_today_str)
    print(f"bj_time_str={bj_time_str}")

    # 生成Markdown文件
    markdown_content = generate_markdown(results,bj_time_str)
    print(f"markdown_content=\n{markdown_content}")

    # 把生成的 markdown_content 文章翻译成英文版本
    en_markdown_content = ai_utils.translate_text(markdown_content)
    print(f"en_markdown_content=\n{en_markdown_content}")

    # 写入 i18n/en/docusaurus-plugin-content-blog/weibo 下，文件名与 generate_markdown 中的文件名一致
    write_to_en_md_file(en_markdown_content)



    # 使用文章关键词生成文章内容
    article_content = generate_article_content(markdown_content)
    print(f"article_content=\n{article_content}")

    # 用当前日期yyyy-mm-dd-{英文文章标题}作为文件名,把 article_content 写入到 blog/shortstory/ 目录下的 .md文件中
    article_file_name = write_to_md_file(article_content)

   # 把生成的 article_content 文章翻译成英文版本
    en_article_content = ai_utils.translate_text(article_content)
    print(f"en_article_content=\n{en_article_content}")

    # 写入 i18n/en/docusaurus-plugin-content-blog/shortstory 下，文件名与 generate_article_content 中的文件名一致
    write_to_en_article_file(en_article_content,article_file_name)

if __name__ == "__main__":
    main()

#     content = """---
# title: "Medicine" Can't Stop
# slug: 2025-01-14-yaobunengting
# keywords: [Medical, System, Irony, Absurdity]
# description: The ab: "medicine" withdrawal of imported drugs from public hospitals has triggered an absurd farce about life.
# authors: [yangshun]
# meta: Canada:Thousands Brave -20 Degrees to Scramble for One Family Doctor
# date: 2025-01-14
# tags: [Society, Satire, Micro-fiction]
# ---

# Old Wang was once again sitting on an empty waiting chair in the hospital, he was used to it. Ever since the notice "Imported drugs withdrawn from public hospitals" was posted, the place had become eerily quiet. In the past, it was crowded with anxious patients and their families, the air thick with the smell of disinfectant and unease, but now, only the cold wind whistling in the corners and Old Wang's heavy breathing could be heard.
# abc
# ---


# """
#     new_content = update_content(content)
#     print(new_content)

    # new_content = update_title(content)
    # print(new_content)

    # new_content = update_description(new_content)
    # print(new_content)

    # new_content = update_meta(new_content)
    # print(f'===update_meta new_content: {new_content}')

    # new_content = update_ending(new_content)
    # print(new_content)
