# Daily Focus

A modern static website built with [Docusaurus](https://docusaurus.io/), providing daily trending news and AI-generated short stories.

## Development Setup

### Installation
```bash
npm install
```

### Development Commands

#### Start Development Server
```bash
# Start Chinese version
npm run start-zh

# Start English version
npm run start-en

# Start default version
npm run start
```

#### Build Project
```bash
# Build website
npm run build

# Type checking
npm run typecheck
```

#### Other Commands
```bash
# Clear cache
npm run clear

# Deploy website
npm run deploy

# Generate translation files
npm run write-translations
npm run write-translations-zh-cn
```

## Content Management

### Blog Post Structure
Blog posts are stored in different directories:
- **Chinese Stories**: `blog/shortstory/`
- **English Translations**: `i18n/en/docusaurus-plugin-content-blog/shortstory/`
- **Chinese Weibo Posts**: `weibo_daily/`
- **English Weibo Translations**: `i18n/en/docusaurus-plugin-content-blog-weibo-daily/`
- **GitHub Trending**: `github_daily/`

### Automation Scripts

#### Translation Scripts
```bash
# Translate story articles
python3 scripts/translate_articles.py

# Force retranslate all articles (overwrite existing translations)
python3 scripts/translate_articles.py --force
```

#### Content Generation Scripts
```bash
# Generate Weibo trending topics (hourly)
python3 scripts/weibo_list_to_md_per_hour.py

# Generate GitHub trending topics
python3 scripts/github_trending.py

# Convert GitHub lists to Markdown
python3 scripts/github_list_to_md.py

# Split long articles
python3 scripts/split-articles.py

# Unwrap compressed articles
python3 scripts/unwrap-articles.py
```

Script Features:
1. Fetch latest Weibo trending topics
2. Generate Chinese content in `weibo_daily/`
3. Generate English translations in `i18n/en/docusaurus-plugin-content-blog-weibo-daily/`
4. Automatically generate AI stories based on trending topics
5. Save both Chinese and English versions of stories

## Project Structure

```
.
├── blog/                           # Chinese blog posts
│   └── shortstory/                # Chinese short stories
├── github_daily/                   # GitHub trending articles
├── weibo_daily/                   # Weibo trending articles
├── i18n/                          # Internationalization files
│   ├── en/                        # English translations
│   └── zh-cn/                     # Chinese localization
├── scripts/                       # Automation scripts
│   ├── translate_articles.py      # Article translation script
│   ├── utils_gemini.py           # Gemini API utilities
│   ├── utils_openais.py          # OpenAI API utilities
│   ├── weibo_list_to_md_per_hour.py  # Weibo trending generator
│   ├── github_trending.py        # GitHub trending fetcher
│   └── github_list_to_md.py      # GitHub content converter
├── src/                           # Source code
│   ├── components/               # React components
│   ├── pages/                   # Page files
│   └── theme/                   # Theme customization
├── static/                       # Static assets
├── docs/                        # Documentation
├── docusaurus.config.ts         # Docusaurus configuration
├── sidebars.ts                  # Sidebar configuration
└── package.json                 # Project dependencies
```

## Internationalization Support

The website supports multiple languages:
- **Chinese (zh-cn)**: Default language
- **English (en)**: English translation version

### Translation File Locations
- `i18n/en/code.json`: UI interface translations
- `i18n/en/docusaurus-theme-classic/`: Theme component translations
- `i18n/en/docusaurus-plugin-content-blog/`: Blog content translations
- `i18n/en/docusaurus-plugin-content-blog-weibo-daily/`: Weibo content translations
- `i18n/en/docusaurus-plugin-content-blog-github-daily/`: GitHub content translations

## Environment Variables Configuration

Create a `.env` file in the project root and configure the following environment variables:

```bash
# Gemini API (for AI content generation)
GEMINI_API_KEY=your_gemini_api_key

# OpenAI API (backup AI service)
OPENAI_API_KEY=your_openai_api_key
```

## Deployment

### Build Project
```bash
# Build website
npm run build
```

### Deploy to Static Hosting Services

After building, the `build/` directory contains all static files that can be deployed to various platforms:

- **Vercel**: Connect GitHub repository for automatic deployment
- **Netlify**: Drag and drop build folder or connect repository
- **GitHub Pages**: Manual upload or use GitHub Actions
- **Other CDNs**: Alibaba Cloud OSS, Tencent Cloud COS, etc.

### Automatic Deployment (Recommended)
Use the built-in deployment command:
```bash
npm run deploy
```

## Tech Stack

- **Framework**: [Docusaurus](https://docusaurus.io/) v3.5.2
- **Languages**: TypeScript, Python
- **AI Services**: Google Gemini, OpenAI
- **Deployment**: GitHub Pages, Vercel
- **Analytics**: Google Analytics, Vercel Analytics

## Contributing

1. Fork this project
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push the branch: `git push origin feature/your-feature`
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.