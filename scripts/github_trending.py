#!/usr/bin/env python3
# encoding: utf-8

"""
@author: anly_jun
@file: github_trending
@time: 16/10/17 下午2:23

Note: To use lxml parser, install it with:
pip install lxml
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple, Optional, Union, Any
import re
import warnings

GITHUB = 'https://github.com'
TRENDING_URL = GITHUB + "/trending"
TRENDING_DEV_URL = TRENDING_URL + "/developers"

USER_AGENT_BY_MOBILE = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36'


def get_trending_repos(opts: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Fetch trending repositories from GitHub
    
    Args:
        opts (dict): Options for filtering repositories
    
    Returns:
        list: List of trending repositories
    """
    repos = []

    language = opts.get('language', None)
    since = opts.get('since', None)

    url = TRENDING_URL

    if language:
        url = url + '/' + language

    if since:
        url += f'?since={since}'

    response, code = read_page(url)

    if code == 200:
        repos = parser_repos(response)

    return repos


def get_trending_developers(opts: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Fetch trending developers from GitHub
    
    Args:
        opts (dict): Options for filtering developers
    
    Returns:
        list: List of trending developers
    """
    developers = []

    language = opts.get('language', None)
    since = opts.get('since', None)

    url = TRENDING_DEV_URL

    if language:
        url = url + '/' + language

    if since:
        url += f'?since={since}'

    print(url)
    response, code = read_page(url)

    if code == 200:
        developers = parser_developers(response)

    return developers


def parser_repos(response: requests.Response) -> List[Dict[str, str]]:
    """
    Parse repository details from GitHub trending page
    
    Args:
        response (requests.Response): HTTP response from GitHub
    
    Returns:
        list: List of parsed repository details
    """
    # Print out the full HTML for investigation
    with open('/tmp/github_trending_html.txt', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("Full HTML saved to /tmp/github_trending_html.txt")

    repos = []

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all repository articles
    repo_articles = soup.find_all('article', class_='Box-row')

    for article in repo_articles:
        try:
            # Find repository name
            name_elem = article.find('h2', class_='h3 lh-condensed')
            if not name_elem:
                continue
            
            name_link = name_elem.find('a')
            if not name_link:
                continue
            
            full_name = name_link.get_text(strip=True)
            
            # Find description
            desc_elem = article.find('p', class_='col-9')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Find language
            lang_elem = article.find('span', itemprop='programmingLanguage')
            language = lang_elem.get_text(strip=True) if lang_elem else 'Unknown'
            
            # Find stars
            stars_elem = article.find('a', class_='Link--muted')
            stars = stars_elem.get_text(strip=True) if stars_elem else '0'
            
            # Find daily stars - look for elements with 'stars today' text
            daily_stars = '0'
            for span in article.find_all('span'):
                span_text = span.get_text(strip=True)
                if 'stars today' in span_text:
                    daily_stars_match = re.search(r'([\d,]+)\s*stars today', span_text)
                    if daily_stars_match:
                        daily_stars = daily_stars_match.group(1)
                        break
            
            # Find built by (contributors)
            built_by = []
            
            # Strategy 1: Find all img tags with alt text that look like names
            img_tags = article.find_all('img')
            for img in img_tags:
                alt = img.get('alt', '')
                # Remove @ from username and check length
                clean_alt = alt.lstrip('@')
                if clean_alt and len(clean_alt) > 2:
                    built_by.append(clean_alt)
            
            # Strategy 2: Look for avatar links
            avatar_links = article.find_all('a', class_='d-inline-block')
            for link in avatar_links:
                img = link.find('img')
                if img:
                    alt = img.get('alt', '')
                    # Remove @ from username and check length
                    clean_alt = alt.lstrip('@')
                    if clean_alt and len(clean_alt) > 2 and clean_alt not in built_by:
                        built_by.append(clean_alt)
            
            # Find link
            link = f"https://github.com{name_link['href']}"

            repos.append({
                'owner': full_name.split('/')[0],
                'repo': full_name.split('/')[1],
                'stars': stars,
                'daily_stars': daily_stars,
                'desc': description,
                'link': link,
                'language': language,
                'built_by': built_by
            })
        except Exception as e:
            print(f"Error parsing repository: {e}")
            continue

    return repos


def parser_desc(desc: BeautifulSoup) -> str:
    """
    Parse repository description
    
    Args:
        desc (BeautifulSoup): Description element
    
    Returns:
        str: Cleaned repository description
    """
    repo_desc = ""

    if desc:
        for each in desc.stripped_strings:
            repo_desc += " " + each

    return repo_desc.lstrip(" ")


def parser_developers(response: requests.Response) -> List[Dict[str, str]]:
    """
    Parse developer details from GitHub trending page
    
    Args:
        response (requests.Response): HTTP response from GitHub
    
    Returns:
        list: List of parsed developer details
    """
    developers = []

    soup = BeautifulSoup(response.text, "html.parser")
    for li in soup.find_all('li', {'class': 'd-sm-flex flex-justify-between border-bottom border-gray-light py-3'}):
        avatar_img = li.find('img', {'class': 'rounded-1'})
        avatar = avatar_img['src'] if avatar_img else None

        href = li.find('a', {'class': 'd-inline-block'})['href']
        link = GITHUB + href
        name = href[1:]

        developers.append({
            'avatar': avatar,
            'name': name,
            'full_name': "",
            'link': link
        })

    return developers


def parser_developer_name(name: BeautifulSoup) -> str:
    """
    Parse full name of a developer
    
    Args:
        name (BeautifulSoup): Name element
    
    Returns:
        str: Cleaned full name
    """
    full_name = ""
    if name:
        for each in name.stripped_strings:
            full_name += " " + each

    return full_name.lstrip(" ")


def read_page(url: str, timeout: int = 5) -> Tuple[Optional[requests.Response], int]:
    """
    Read GitHub page with a mobile user agent
    
    Args:
        url (str): URL to fetch
        timeout (int, optional): Request timeout. Defaults to 5.
    
    Returns:
        tuple: Response and status code
    """
    header = {'User-Agent': USER_AGENT_BY_MOBILE}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = requests.get(url=url, timeout=timeout, headers=header)
        return response, response.status_code
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        return None, False


if __name__ == '__main__':
    # Fetch and print trending repositories
    print("=== Trending Repositories ===")
    repos_opts = {}  # You can add language or since parameters here if needed
    trending_repos = get_trending_repos(repos_opts)
    
    for i, repo in enumerate(trending_repos, 1):
        print(f"{i}. {repo['owner']}/{repo['repo']}")
        print(f"   Stars: {repo['stars']}")
        print(f"   Daily Stars: {repo['daily_stars']}")
        print(f"   Description: {repo['desc']}")
        print(f"   Link: {repo['link']}")
        print(f"   Built by: {', '.join(repo['built_by'])}\n")

    # Fetch and print trending developers
    print("\n=== Trending Developers ===")
    dev_opts = {}  # You can add language or since parameters here if needed
    trending_developers = get_trending_developers(dev_opts)
    
    for i, dev in enumerate(trending_developers, 1):
        print(f"{i}. {dev['name']}")
        print(f"   Avatar: {dev['avatar']}")
        print(f"   Link: {dev['link']}\n")
