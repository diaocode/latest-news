# Daily Focus - 每日焦点

基于 [Docusaurus](https://docusaurus.io/) 构建的现代化静态网站，提供每日热点新闻和AI生成的短篇故事。

## 开发环境设置

### 安装依赖
```bash
npm install
```

### 开发命令

#### 启动开发服务器
```bash
# 启动中文版本
npm run start-zh

# 启动英文版本
npm run start-en

# 启动默认版本
npm run start
```

#### 构建项目
```bash
# 构建网站
npm run build

# 类型检查
npm run typecheck
```

#### 其他命令
```bash
# 清理缓存
npm run clear

# 部署网站
npm run deploy

# 生成翻译文件
npm run write-translations
npm run write-translations-zh-cn
```

## 内容管理

### 博客文章结构
博客文章存储在不同的目录中：
- **中文故事**: `blog/shortstory/`
- **英文翻译**: `i18n/en/docusaurus-plugin-content-blog/shortstory/`
- **中文微博文章**: `weibo_daily/`
- **英文微博翻译**: `i18n/en/docusaurus-plugin-content-blog-weibo-daily/`
- **GitHub热点**: `github_daily/`

### 自动化脚本

#### 翻译脚本
```bash
# 翻译故事文章
python3 scripts/translate_articles.py

# 强制重新翻译所有文章（覆盖现有翻译）
python3 scripts/translate_articles.py --force
```

#### 内容生成脚本
```bash
# 生成微博热点话题（每小时）
python3 scripts/weibo_list_to_md_per_hour.py

# 生成 GitHub 热点话题
python3 scripts/github_trending.py

# 将 GitHub 列表转换为 Markdown
python3 scripts/github_list_to_md.py

# 拆分长文章
python3 scripts/split-articles.py

# 展开压缩的文章
python3 scripts/unwrap-articles.py
```

脚本功能：
1. 获取最新的微博热搜话题
2. 在 `weibo_daily/` 生成中文内容
3. 在 `i18n/en/docusaurus-plugin-content-blog-weibo-daily/` 生成英文翻译
4. 基于热点话题自动生成 AI 故事
5. 保存中英文版本的故事

## 项目结构

```
.
├── blog/                           # 中文博客文章
│   └── shortstory/                # 中文短篇故事
├── github_daily/                   # GitHub 热点文章
├── weibo_daily/                   # 微博热点文章
├── i18n/                          # 国际化翻译文件
│   ├── en/                        # 英文翻译
│   └── zh-cn/                     # 中文本地化
├── scripts/                       # 自动化脚本
│   ├── translate_articles.py      # 文章翻译脚本
│   ├── utils_gemini.py           # Gemini API 工具
│   ├── utils_openais.py          # OpenAI API 工具
│   ├── weibo_list_to_md_per_hour.py  # 微博热点生成
│   ├── github_trending.py        # GitHub 热点获取
│   └── github_list_to_md.py      # GitHub 内容转换
├── src/                           # 源代码
│   ├── components/               # React 组件
│   ├── pages/                   # 页面文件
│   └── theme/                   # 主题定制
├── static/                       # 静态资源
├── docs/                        # 文档
├── docusaurus.config.ts         # Docusaurus 配置
├── sidebars.ts                  # 侧边栏配置
└── package.json                 # 项目依赖
```

## 国际化支持

网站支持多语言：
- **中文 (zh-cn)**: 默认语言
- **英文 (en)**: 英文翻译版本

### 翻译文件位置
- `i18n/en/code.json`: UI界面翻译
- `i18n/en/docusaurus-theme-classic/`: 主题组件翻译
- `i18n/en/docusaurus-plugin-content-blog/`: 博客内容翻译
- `i18n/en/docusaurus-plugin-content-blog-weibo-daily/`: 微博内容翻译
- `i18n/en/docusaurus-plugin-content-blog-github-daily/`: GitHub内容翻译

## 环境变量配置

在项目根目录创建 `.env` 文件，配置以下环境变量：

```bash
# Gemini API (用于AI内容生成)
GEMINI_API_KEY=your_gemini_api_key

# OpenAI API (备用AI服务)
OPENAI_API_KEY=your_openai_api_key
```

## 部署

### 构建项目
```bash
# 构建网站
npm run build
```

### 部署到静态托管服务
构建完成后，`build/` 目录包含所有静态文件，可部署到以下平台：

- **Vercel**: 连接 GitHub 仓库，自动部署
- **Netlify**: 拖拽 build 文件夹或连接仓库
- **GitHub Pages**: 手动上传或使用 Actions
- **其他 CDN**: 阿里云 OSS、腾讯云 COS 等

### 自动部署（推荐）
使用项目内置的部署命令：
```bash
npm run deploy
```

## 技术栈

- **框架**: [Docusaurus](https://docusaurus.io/) v3.5.2
- **语言**: TypeScript, Python
- **AI服务**: Google Gemini, OpenAI
- **部署**: GitHub Pages, Vercel
- **分析**: Google Analytics, Vercel Analytics

## 贡献指南

1. Fork 本项目
2. 创建特性分支: `git checkout -b feature/your-feature`
3. 提交更改: `git commit -am 'Add some feature'`
4. 推送分支: `git push origin feature/your-feature`
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
