import os
from dotenv import load_dotenv
from openai import OpenAI

class AiApiUtils:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4"  # 默认使用 GPT-4 模型

    def generate_keywords(self, content: str, max_tokens: int = 50) -> str:
        """
        根据内容生成关键词
        :param content: 输入内容
        :param max_tokens: 最大token数
        :return: 生成的关键词字符串
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个关键词生成助手，请根据提供的内容生成相关的关键词，用逗号分隔。"},
                    {"role": "user", "content": content},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            keywords = response.choices[0].message.content.strip()
            if ',' not in keywords:
                keywords = ', '.join(keywords.split())
            return keywords
        except Exception as e:
            print(f"生成关键词时出错: {e}")
            return "无关键词"

    def generate_story(self, prompt: str, max_tokens: int = 500) -> str:
        """
        根据提示生成故事内容
        :param prompt: 故事提示
        :param max_tokens: 最大token数
        :return: 生成的故事内容
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个故事创作助手，请根据提供的提示生成一个引人入胜的微型故事。"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.8,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"生成故事时出错: {e}")
            return "生成故事失败"

    def translate_text(self, text: str, target_lang: str = "en") -> str:
        """
        翻译文本
        :param text: 要翻译的文本
        :param target_lang: 目标语言（en-英文，zh-中文）
        :return: 翻译后的文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是一个翻译助手，请将文本翻译成{target_lang}语言，保持原文的风格和语气。"},
                    {"role": "user", "content": text},
                ],
                max_tokens=len(text) * 2,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"翻译文本时出错: {e}")
            return text  # 出错时返回原文