# 使用指南

## 开发环境设置

### 安装
```bash
# 安装依赖
npm install
```

### 开发命令

#### 启动开发服务器
```bash
# 启动中文版本
npm run start-zh

# 启动英文版本
npm run start-en
```

#### 构建
```bash
# 构建网站
npm run build
```

### 内容管理

#### 博客文章
博客文章存储在不同的目录中：
- 中文故事：`blog/shortstory/`
- 英文翻译：`i18n/en/docusaurus-plugin-content-blog/shortstory/`
- 中文微博文章：`weibo_daily/`
- 英文微博翻译：`i18n/en/docusaurus-plugin-content-blog-weibo-daily/`

#### 翻译脚本
```bash
# 翻译故事文章
python3 scripts/translate_articles.py

# 强制重新翻译所有文章（覆盖现有翻译）
python3 scripts/translate_articles.py --force

# 生成微博热点话题（每小时）
python3 scripts/weibo_list_to_md_per_hour.py

# 脚本将会：
# 1. 获取最新的微博热搜话题
# 2. 在 weibo_daily/ 生成中文内容
# 3. 在 i18n/en/docusaurus-plugin-content-blog-weibo-daily/ 生成英文翻译
# 4. 基于热点话题自动生成 AI 故事
# 5. 保存中英文版本的故事
```

### 文件结构
```
.
├── blog/                    # 中文博客文章
│   └── shortstory/         # 中文短篇故事
├── i18n/                   # 翻译文件
│   └── en/
│       └── docusaurus-plugin-content-blog/
│           └── shortstory/ # 英文翻译
├── weibo_daily/           # 中文微博文章
└── scripts/              # 工具脚本
    ├── translate_articles.py
    ├── utils_gemini.py
    └── weibo_list_to_md_per_hour.py
```

### 国际化 (i18n)

网站支持两种语言：
- 中文 (zh-cn)：默认语言
- 英文 (en)：翻译版本

翻译文件存储在：
- `i18n/en/code.json`：UI 翻译
- `i18n/en/docusaurus-theme-classic/`：主题翻译
- `i18n/en/docusaurus-plugin-content-blog/`：博客内容翻译