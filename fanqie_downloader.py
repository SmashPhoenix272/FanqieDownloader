import json
import requests
from dotenv import load_dotenv
from cache import NovelCache
from tqdm import tqdm
import time
import re
import os

# Load environment variables
load_dotenv()

# Get API URL from environment variable
API_URL = os.getenv('FANQIE_API_URL')

class FanqieDownloader:
    def __init__(self):
        self.cache = NovelCache()

    def get_website_title(self, novel_id):
        try:
            url = f"https://fanqienovel.com/page/{novel_id}"
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.text
            match = re.search(r'"bookName":"([^"]+)"', html_content)
            if match:
                return match.group(1)
        except requests.RequestException as e:
            print(f"Error fetching website title: {e}")
        return None

    def get_novel_info(self, novel_id):
        cached_info, last_updated = self.cache.get_cached_novel_info(novel_id)
        if cached_info:
            print(f"Using cached novel info (last updated: {time.ctime(last_updated)})")
            return cached_info

        try:
            response = requests.get(f"{API_URL}/info?book_id={novel_id}")
            response.raise_for_status()
            data = response.json()['data']['data']
            
            api_title = data['book_name']
            website_title = self.get_website_title(novel_id)
            
            novel_info = {
                'title': api_title,
                'author': data['author'],
                'chapterCount': int(data['serial_count']),
                'tags': data['tags'],
                'summary': data['abstract'],
                'bookId': data['book_id'],
                'thumb_url': data['thumb_url']
            }
            
            if website_title and website_title != api_title:
                novel_info['website_title'] = website_title
            
            self.cache.update_novel_cache(novel_id, novel_info)
            return novel_info
        except requests.RequestException as e:
            print(f"Error fetching novel information: {e}")
            return None
        except (KeyError, TypeError, ValueError) as e:
            print(f"Error processing novel information: {e}")
            print(f"Response content: {response.text}")
            return None

    def download_chapter(self, novel_id, chapter):
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                cached_content, last_updated = self.cache.get_cached_chapter(novel_id, chapter['item_id'])
                if cached_content:
                    print(f"Using cached chapter content (last updated: {time.ctime(last_updated)})")
                    return cached_content

                chapter_response = requests.get(f"{API_URL}/content?item_id={chapter['item_id']}")
                chapter_response.raise_for_status()
                chapter_content = chapter_response.json()['data']['data']['content']
                
                if chapter_content.strip().lower() == "invalid":
                    if attempt < max_retries - 1:
                        print(f"Invalid content for chapter {chapter['title']}. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        return f"Error: Unable to fetch valid content for chapter {chapter['title']} after {max_retries} attempts."
                
                self.cache.update_chapter_cache(novel_id, chapter['item_id'], chapter_content)
                return chapter_content
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Error downloading chapter {chapter['title']}: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    return f"Error: Failed to download chapter {chapter['title']} after {max_retries} attempts: {e}"

    def download_novel(self, novel_id):
        novel_info = self.get_novel_info(novel_id)
        if not novel_info:
            print("Failed to get novel information.")
            return

        try:
            catalog_response = requests.get(f"{API_URL}/catalog?book_id={novel_id}")
            catalog_response.raise_for_status()
            chapters = catalog_response.json()['data']['data']['item_data_list']

            full_content = f"书名：{novel_info['title']}\n"
            if 'website_title' in novel_info:
                full_content += f"网站标题：{novel_info['website_title']}\n"
            full_content += f"作者：{novel_info['author']}\n小说ID：{novel_info['bookId']}\n总章节数：{novel_info['chapterCount']}\n\n标签：{novel_info['tags']}\n\n简介：{novel_info['summary']}\n\n"

            current_volume = ''
            progress_bar = tqdm(total=len(chapters), desc="Downloading chapters", unit="chapter")
            
            for chapter in chapters:
                if chapter['volume_name'] != current_volume:
                    current_volume = chapter['volume_name']
                    full_content += f"\n{current_volume}\n\n"

                chapter_content = self.download_chapter(novel_id, chapter)
                full_content += f"{chapter['title']}\n\n{chapter_content}\n\n"
                progress_bar.update(1)

            progress_bar.close()

            filename = f"{novel_info['title']}_{novel_info['chapterCount']}章.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(full_content)
            print(f"\nNovel downloaded and saved as {filename}")
        except requests.RequestException as e:
            print(f"Error downloading novel: {e}")
        except (KeyError, TypeError, ValueError) as e:
            print(f"Error processing novel data: {e}")

def main():
    downloader = FanqieDownloader()
    novel_id = input("Enter the novel ID: ")
    
    novel_info = downloader.get_novel_info(novel_id)
    if novel_info:
        print(f"\nNovel Information:")
        print(f"Title: {novel_info['title']}")
        if 'website_title' in novel_info:
            print(f"Website Title: {novel_info['website_title']}")
        print(f"Author: {novel_info['author']}")
        print(f"Chapter Count: {novel_info['chapterCount']}")
        
        confirm = input("\nDo you want to proceed with the download? (y/n): ")
        if confirm.lower() == 'y':
            downloader.download_novel(novel_id)
        else:
            print("Download cancelled.")
    else:
        print("Failed to retrieve novel information. Please check the novel ID and try again.")

if __name__ == "__main__":
    main()