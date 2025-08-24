import os
import glob
import argparse
from utils_gemini import GeminiApiUtils
import re
# 导入 update_content 函数
from weibo_list_to_md_per_hour import update_content

def clean_title(content):
    """
    Clean the title by removing quotes and extra spaces
    """
    # Find the title line in the markdown frontmatter
    title_match = re.search(r'title: (.*)', content)
    if title_match:
        title_line = title_match.group(0)
        # Remove quotes and clean up spaces
        title = title_match.group(1).replace('"', '').strip()
        # Remove multiple spaces
        title = ' '.join(title.split())
        cleaned_title = f'title: {title}'
        # Replace the original title line with the cleaned one
        content = content.replace(title_line, cleaned_title)
    return content

def translate_markdown_file(input_file, output_file, ai_utils):
    """
    Translate a markdown file from Chinese to English while preserving the format
    """
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Translate the content
    translated_content = ai_utils.translate_text(content)
    
    # Clean quotes from title
    translated_content = clean_title(translated_content)

    # 使用 update_content 函数处理翻译后的内容
    translated_content = update_content(translated_content)

    # Write the translated content to the output file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(translated_content)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Translate markdown files from Chinese to English')
    parser.add_argument('--force', '-f', action='store_true', help='Force override existing translations')
    args = parser.parse_args()

    # Initialize the AI utils
    ai_utils = GeminiApiUtils()

    # Define the input and output directories
    input_dir = 'blog/shortstory'
    output_dir = 'i18n/en/docusaurus-plugin-content-blog/shortstory'

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all markdown files in the input directory
    md_files = glob.glob(os.path.join(input_dir, '*.md'))

    # Process each file
    for input_file in md_files:
        # Get the base filename
        base_name = os.path.basename(input_file)
        
        # Create the output file path
        output_file = os.path.join(output_dir, base_name)

        print(f"Processing {base_name}...")
        
        # Check if file exists and handle based on force flag
        if os.path.exists(output_file) and not args.force:
            print(f"Skipping {base_name} - translation already exists (use --force to override)")
            continue

        try:
            translate_markdown_file(input_file, output_file, ai_utils)
            print(f"Successfully translated {base_name}")
        except Exception as e:
            print(f"Error translating {base_name}: {str(e)}")

if __name__ == '__main__':
    main()