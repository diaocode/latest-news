from ast import main
import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any
import random

class GeminiApiUtils:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = "gemini-2.0-pro-exp-02-05"
        # self.model = "gemini-2.0-flash-exp"
        self.api_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        # self.api_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        # 当前时间
        self.curr_date = datetime.now().strftime("%Y-%m-%d")
        
        styles = [
            "汪曾祺的风格写一篇小说",
            "老舍的风格写一篇小说",
            "鲁迅的风格写一篇小说",
            "王小波 的风格写一篇小说",
            "吴晓波的风格写一篇文章",
            "梁文道的风格写一篇文章",
            "卡夫卡的风格写一篇小说",
            "博尔赫斯 的风格写一篇小说",
            "村上春树 的风格写一篇小说",
            "欧・亨利 的风格写一篇小说",
            "雨果 的风格写一篇小说",
            "80%欧・亨利 + 20%博尔赫斯 的风格写一篇小说",
            "80%卡夫卡 + 20%博尔赫斯 的风格写一篇小说",
            "80%老舍 + 20%鲁迅 的风格写一篇杂文",
            "80%老舍 + 20%鲁迅 的风格写一篇小说",
            "80%吴晓波 + 20%梁文道的风格写一篇小说",
            "80%村上春树 + 20%王小波 的风格写一篇小说",
            "80%王小波 + 20%鲁迅 的风格写一篇小说",
            ]
            
        # 从 styles 中随机选择一个写作风格
        style = random.choice(styles)
        print(f"style: {style}")

        self.system_prompt = """用 """ + style + """：
            请根据你选择的题材，创作一篇500-2000字左右的小说。
            你的文字一气呵成，使用简体中文，
            面向简体中文读者，符合简体中文的表达习惯，阅读门槛低，有社会和人文意义和思想深度，
            在逻辑性、卡夫卡风格和人文深度上提升标题和正文，小说情节逐步展开，引入入胜，能引起人的情感共鸣。

            直接给出小说标题和内容，不要包含任何前言、后言。
            请以markdown格式给出,不要在一篇文章中包含多篇文章内容。
            文章的开头标志为以下格式：
            ---
            title: {小说标题} 
            slug: {slug}
            keywords: [{keywords}]
            description: {description}
            authors: [yangshun]
            date: {date}
            tags: [{tags}]
            ---
            {正文内容}

            8. 返回整篇文章内容不要用 ```markdown 包裹,
            tags: [{tags}]中的tags内容是一个字符串数组，用逗号分隔，比如：[恐怖小说,社会新闻],
            keywords: [{keywords}]中的 keywords 内容是一个字符串数组，用逗号分隔，比如：[恐怖小说,社会新闻],
            {小说标题}不要以书名号包裹：比如：《{小说标题}》,
            {小说标题}不要出现双引号或者单引号：比如："加油"的真相,
            格式如下:
            ---
            title: {小说标题} """
        self.system_prompt = self.system_prompt + f"\nslug: {self.curr_date}-" + "{slug}"
        self.system_prompt = self.system_prompt + """
            keywords: [{keywords}]
            description: {description}
            authors: [yangshun]
            meta: {原始新闻标题}
            """ 
        self.system_prompt = self.system_prompt + f"""date: {self.curr_date} """ 
        self.system_prompt = self.system_prompt + """
            tags: [{tags}]
            ---
            {正文内容}

            """

    def generate_story_from_news(self, news_lists: str) -> str:
        """
        根据新闻列表生成微型小说
        :param news_lists: 新闻列表的列表，每个子列表代表一组新闻
        :return: 生成的故事内容
        """
        # 格式化新闻列表
        formatted_news = str(news_lists)
        print(f"formatted_news:\n{formatted_news}")

        # 构建请求数据
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{self.system_prompt}\n新闻热点列表如下：\n{formatted_news}\n"
                        }
                    ]
                }
            ]
        }

        print(f"request data:\n{data}")

        try:
            # 发送请求
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=data
            )
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析响应
            result = response.json()
            print(f"response:\n{result}")
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"生成故事时出错: {e}")
            return "生成故事失败"

    def generate_keywords(self, content: str) -> str:
        """
        使用Gemini生成关键词
        :param content: 输入内容
        :return: 生成的关键词字符串
        """
        prompt = f"请为以下内容生成5-8个关键词，用逗号分隔：\n{content}"
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        try:
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            keywords = result['candidates'][0]['content']['parts'][0]['text']
            if ',' not in keywords:
                keywords = ', '.join(keywords.split())
            return keywords
        except Exception as e:
            print(f"生成关键词时出错: {e}")
            return "无关键词"

    def translate_text(self, text: str, target_lang: str = "en") -> str:
        """
        使用Gemini翻译文本
        :param text: 要翻译的文本
        :param target_lang: 目标语言（en-英文，zh-中文）
        :return: 翻译后的文本
        """
        lang_name = "英语" if target_lang == "en" else "中文"
        prompt = f"""请将以下文本翻译成{lang_name}，保持原文的开头的格式(不要使用额外的```包裹内容),开头的格式如下：
---
title: Weibo热搜 | 2025-01-04_12
slug: weibo-hot-2025-01-04_12
keywords: [Weibo,热搜]
description: Weibo热搜,2025-01-04_12
authors: [yangshun]
date: 2025-01-04 12:00:00
tags: [Weibo,hotSearch]
---
如果文章中包含超链接 （https://www.bing.com/search?q=韩国又一客机起落架故障），请不要修改超链接保持原样。
    ，保持原文的风格和语气：\n{text}"""
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        try:
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"翻译文本时出错: {e}")
            return text  # 出错时返回原文


def main():
    gemini_utils = GeminiApiUtils()

    news_list_str = """
    1. jellycat平替成上海圣诞节顶流(新) 热度：1145953
    2. 平安夜(新) 热度：878519
    3. 守护非遗之美(新) 热度：683863
    4. 肯德基涨价2%(热) 热度：613993
    5. 白鹿 没吻这么激烈(新) 热度：484818
    """


    news_lists = news_list_str.split('\n')
    news_lists = [news_list.split(' 热度：') for news_list in news_lists if ' 热度：' in news_list]
    news_lists = [[news.strip() for news in news_list] for news_list in news_lists]

    # print(f"news_lists:\n{news_lists}")

    response = gemini_utils.generate_story_from_news(news_lists)
    print(f"生成文章内容: \n{response}")

    # keywords = gemini_utils.generate_keywords(news_lists)
    # print(f"生成关键词\n: {keywords}")

    # translation = gemini_utils.translate_text("这是一条要翻译的文本", "zh")
    # print(f"翻译文本\n: {translation}")


if __name__ == "__main__":
    main()