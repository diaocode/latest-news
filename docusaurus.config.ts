import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Daily Focus',
  tagline: 'Your Daily Source for Trending Topics and Tech Insights',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://www.tinygame.win',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'xmx0632', // Usually your GitHub org/user name.
  projectName: 'latestnews', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'zh-cn',
    locales: ['zh-cn', 'en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          blogSidebarTitle: 'Latest Posts',
          blogSidebarCount: 30,
          postsPerPage: 10,
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-content-blog',
      {
        id: 'weibo-daily',
        routeBasePath: 'weibo-daily',
        path: './weibo_daily',
        blogTitle: 'Weibo Trending Topics',
        blogDescription: 'Track and analyze daily trending topics from Weibo - China\'s largest social media platform',
        showReadingTime: false,
        blogSidebarTitle: 'Historical Trends',
        blogSidebarCount: 30,
        postsPerPage: 30,
      },
    ],
    [
      '@docusaurus/plugin-content-blog',
      {
        id: 'github-daily',
        routeBasePath: 'github-daily',
        path: './github_daily',
        blogTitle: 'GitHub Trending Topics',
        blogDescription: 'Track and analyze daily trending topics from GitHub - The best place to share code',
        showReadingTime: false,
        blogSidebarTitle: 'Historical Trends',
        blogSidebarCount: 30,
        postsPerPage: 30,
      },
    ],
    [
      '@docusaurus/plugin-google-gtag',
      {
        trackingID: 'G-NYW5WT7VHW',
        anonymizeIP: true,
      },
    ],
  ],
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid',
    [
      "@easyops-cn/docusaurus-search-local",
      {
        hashed: true,
        language: ["en", "zh"],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
      },
    ],
  ],
  
  themeConfig: {
    mermaid: {
      // 可选配置： ['base','forest','neutral','dark','default','null'],
      theme: {light: 'forest', dark: 'forest'},

      options: {
        // Mermaid 主题配色优化（超浅蓝+清新绿+橙黄，极致柔和）
        themeVariables: {
          primaryColor: '#E3F1FF',        // 主色调：超浅蓝色，极致柔和明亮
          secondaryColor: '#A3D977',      // 次色调：清新的绿色，活力有层次
          tertiaryColor: '#F7C873',       // 第三色调：温暖的橙黄色，点缀提升整体观感
          edgeLabelBackground: '#F9FAFB'  // 边标签背景：极浅灰白，保证可读性
        }
      }
    },
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      title: 'Daily Focus',
      logo: {
        alt: 'Daily Focus',
        src: 'img/logo.svg',
      },
      items: [
        {to: '/blog', label: 'All Blog Posts', position: 'left'},
        {to: '/weibo-daily', label: 'Weibo Hot Topics', position: 'left', className: 'margin-left--sm'},
        {to: '/github-daily', label: 'GitHub Hot Topics', position: 'left', className: 'margin-left--sm'},
        {
          type: 'localeDropdown',
          position: 'right',
        },
        {
          href: 'https://game.tinygame.win',
          label: 'Play Games',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Games',
          items: [
            {
              label: 'Play Games',
              to: 'https://game.tinygame.win',
            },
          ],
        },
        {
          title: 'Social Trends',
          items: [
            {
              label: 'Historical Trends',
              to: '/weibo-daily',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Twitter',
              href: 'https://twitter.com/xmx0632',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'IT-Tools',
              to: 'http://47.101.188.149:18010/',
            },
            {
              label: 'PDF-Tools',
              to: 'http://47.101.188.149:18011/',
            },
            {
              label: 'Privacy Policy',
              to: '/privacy-policy',
            },
            {
              label: 'Cookie Policy',
              to: '/cookie-policy',
            },
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} Daily Focus. All rights reserved.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
    headTags: [
    ],
    scripts: [
      {
        src: '/_vercel/insights/script.js',
        async: true,
      },
    ],
  } satisfies Preset.ThemeConfig,
};

export default config;
