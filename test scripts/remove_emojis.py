#!/usr/bin/env python3
"""
Script to remove emojis from all markdown files in the project.
"""
import os
import re
import glob

def remove_emojis(text):
    """Remove emojis from text using regex patterns."""
    # Common emoji patterns
    emoji_patterns = [
        r'📊|📋|🎯|💰|🏗️|🤖|📈|💼|🔧|📊|🔐|🧪|📚|👥|🚀|💡|📄|⚠️|✅|🟢|📁|📝|✨|🗄️|⚡|🔗|🔄|💡',
        r'🥇|🥈|🥉|📈|📊|🎯|💰|🏛️|🤖|📈|💼|🔧|📊|🔐|🧪|📚|👥|🚀|💡|📄|⚠️|✅|🟢|📁|📝|✨|🗄️|⚡|🔗|🔄',
        r'[\U0001F600-\U0001F64F]',  # Emoticons
        r'[\U0001F300-\U0001F5FF]',  # Symbols & pictographs
        r'[\U0001F680-\U0001F6FF]',  # Transport & map symbols
        r'[\U0001F1E0-\U0001F1FF]',  # Flags (iOS)
        r'[\U00002702-\U000027B0]',  # Dingbats
        r'[\U000024C2-\U0001F251]'   # Enclosed characters
    ]
    
    for pattern in emoji_patterns:
        text = re.sub(pattern, '', text)
    
    return text

def process_markdown_files():
    """Process all markdown files and remove emojis."""
    # Get all markdown files
    md_files = glob.glob("**/*.md", recursive=True)
    
    processed_files = []
    
    for file_path in md_files:
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove emojis
            clean_content = remove_emojis(content)
            
            # Only write if content changed
            if clean_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clean_content)
                processed_files.append(file_path)
                print(f"Processed: {file_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return processed_files

if __name__ == "__main__":
    print("Removing emojis from all markdown files...")
    processed = process_markdown_files()
    print(f"\nProcessed {len(processed)} files:")
    for file in processed:
        print(f"  - {file}")
    print("Done!")
