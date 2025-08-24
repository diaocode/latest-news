# -*- coding: utf-8 -*-
import os
import re
from urllib.parse import quote

def update_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_content = []
    i = 0
    
    # Find and process the title line
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('# Weibo热搜'):
            timestamp = line.split('|')[1].strip()
            new_content.append(f'### Weibo热搜 | {timestamp}\n')
            i += 1
            break
        i += 1
    
    # Process the rest of the content
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('## '):
            # Extract number, title and status
            match = re.match(r'^## (\d+)\. (.+?)(?:\((新|热|沸)\))?$', line)
            if match:
                number = match.group(1)
                title = match.group(2).strip()
                status = match.group(3) if match.group(3) else ''
                
                # Get heat value from next line
                heat_value = ''
                if i + 1 < len(lines):
                    heat_match = re.search(r'\*\*热度\*\*：([\d,]+)', lines[i + 1])
                    if heat_match:
                        heat_value = heat_match.group(1)
                
                # Create the new line with encoded URL
                encoded_title = quote(title)
                url = f'https://www.bing.com/search?q={encoded_title}'
                status_str = f'({status})' if status else ''
                
                new_line = f'#### {number}. [{title}]({url}){status_str} **热度**：{heat_value}'
                new_content.append(new_line)
                new_content.append('---\n')
                
                # Skip the heat value line and separator
                i += 3
                continue
        i += 1
    
    # Write the updated content back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_content)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blog_dir = os.path.join(os.path.dirname(script_dir), 'blog')
    
    for filename in os.listdir(blog_dir):
        if filename.startswith('Weibo-daily-hot-') and filename.endswith('.md'):
            file_path = os.path.join(blog_dir, filename)
            update_file_content(file_path)

if __name__ == '__main__':
    main()