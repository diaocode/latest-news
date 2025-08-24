import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta, timezone
from openai import OpenAI
from bs4 import BeautifulSoup
import pytz

# 加载 .env 文件
load_dotenv()

# 创建 OpenAI 客户端实例
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

producthunt_client_id = os.getenv('PRODUCTHUNT_CLIENT_ID')
producthunt_client_secret = os.getenv('PRODUCTHUNT_CLIENT_SECRET')


print ("producthunt_client_id=",producthunt_client_id)
print ("producthunt_client_secret=",producthunt_client_secret)

# 配置常量
OUTPUT_DIR = 'blog'  # 输出目录
FILE_PREFIX = 'Weibo-daily-hot'  # 文件名前缀
FILE_EXT = '.md'  # 文件扩展名

class DataItem:
    def __init__(self, id: str, word: str, num: int, label_name: str, **kwargs):
        self.word = word
        self.num = num
        self.label_name = label_name
        
    def fetch_og_image_url(self) -> str:
        """获取产品的Open Graph图片URL"""
        response = requests.get(self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            og_image = soup.find("meta", property="og:image")
            if og_image:
                return og_image["content"]
        return ""

    def generate_keywords(self) -> str:
        """生成产品的关键词，显示在一行，用逗号分隔"""
        prompt = f"根据以下内容生成适合的中文关键词，用英文逗号分隔开：\n\n产品名称：{self.name}\n\n标语：{self.tagline}\n\n描述：{self.description}"
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Generate suitable Chinese keywords based on the product information provided. The keywords should be separated by commas."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=50,
                temperature=0.7,
            )
            keywords = response.choices[0].message.content.strip()
            if ',' not in keywords:
                keywords = ', '.join(keywords.split())
            return keywords
        except Exception as e:
            print(f"Error occurred during keyword generation: {e}")
            return "无关键词"

    def translate_text(self, text: str) -> str:
        """使用OpenAI翻译文本内容"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是世界上最专业的翻译工具，擅长英文和中文互译。你是一位精通英文和中文的专业翻译，尤其擅长将IT公司黑话和专业词汇翻译成简洁易懂的地道表达。你的任务是将以下内容翻译成地道的中文，风格与科普杂志或日常对话相似。"},
                    {"role": "user", "content": text},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            translated_text = response.choices[0].message.content.strip()
            return translated_text
        except Exception as e:
            print(f"Error occurred during translation: {e}")
            return text

    def convert_to_beijing_time(self, utc_time_str: str) -> str:
        """将UTC时间转换为北京时间"""
        utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ')
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_time = utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)
        return beijing_time.strftime('%Y年%m月%d日 %p%I:%M (北京时间)')

    def to_markdown(self, rank: int) -> str:
        """返回数据的Markdown格式"""
        # Only show label_name if it's not empty
        title = f"## {rank}. {self.word}"
        if self.label_name:
            title += f"({self.label_name})"
        title += "\n"
        
        return (
            f"{title}"
            f"**热度**：{self.num}\n"
            f"---\n\n"
        )

def get_access_token():
    """通过 client_id 和 client_secret 获取 数据源访问令牌 的 access_token"""
    url = "https://api.producthunt.com/v2/oauth/token"
    payload = {
        "client_id": producthunt_client_id,
        "client_secret": producthunt_client_secret,
        "grant_type": "client_credentials",
    }

    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to obtain access token: {response.status_code}, {response.text}")

    token = response.json().get("access_token")
    return token


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


def generate_markdown(result_list,date_str):
    """生成Markdown内容并保存到指定目录"""
    
    markdown_content = f"# Weibo热搜 | {date_str}\n\n"

    # 把 result_list 内容添加到 markdown_content 中
    for rank,result in enumerate(result_list,1):
        # print(result)
        # markdown_content += f"{rank}. {result.word}\n"
        markdown_content += result.to_markdown(rank)

    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 生成文件名
    file_name = os.path.join(OUTPUT_DIR, f"{FILE_PREFIX}-{date_str}{FILE_EXT}")
    
    # 如果文件存在，直接覆盖
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(markdown_content)
    print(f"文件 {file_name} 生成成功并已覆盖。")


def main():
    # 获取昨天的日期并格式化
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    yesterday_date_str = yesterday.strftime('%Y-%m-%d')
    print(f"yesterday_date_str={yesterday_date_str}")

    # 获取Weibo数据
    results = fetch_data()
    # for result in results:
    #     print(result)

    # 获取今天的日期并格式化
    date_today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    # 生成Markdown文件
    generate_markdown(results,date_today_str)

if __name__ == "__main__":
    main()
