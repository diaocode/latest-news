# -*- coding: utf-8 -*-
import os
import re
from urllib.parse import quote

def update_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title and timestamp
    title_match = re.search(r'# Weibo热搜 \| ([\d-]+ [\d:]+)', content)
    if not title_match:
        return
    
    timestamp = title_match.group(1)
    
    # Split content into lines
    lines = content.split('\n')
    
    # Initialize new content
    new_content = [f'### Weibo热搜 | {timestamp}\n']
    
    # Process items
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for numbered items
        item_match = re.search(r'## (\d+)\. (.*?)(?:\((新|热|沸)\))?$', line)
        if item_match:
            number = item_match.group(1)
            title = item_match.group(2).strip()
            status = item_match.group(3) if item_match.group(3) else ''
            
            # Get heat value from next line
            heat_value = ''
            if i + 1 < len(lines):
                heat_match = re.search(r'\*\*热度\*\*：([\d,]+)', lines[i + 1])
                if heat_match:
                    heat_value = heat_match.group(1)
                    i += 2  # Skip the heat line and separator
            
            # Create search URL
            encoded_title = quote(title)
            search_url = f'https://www.bing.com/search?q={encoded_title}'
            
            # Format the new line
            status_str = f'({status})' if status else ''
            new_line = f'#### {number}. [{title}]({search_url}){status_str} **热度**：{heat_value}'
            new_content.append(new_line)
            new_content.append('---\n')
        
        i += 1
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_content))

def main():
    blog_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'blog')
    for filename in os.listdir(blog_dir):
        if filename.startswith('Weibo-') and filename.endswith('.md'):
            file_path = os.path.join(blog_dir, filename)
            update_file_content(file_path)

if __name__ == '__main__':
    main()