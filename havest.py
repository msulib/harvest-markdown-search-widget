import requests
from bs4 import BeautifulSoup
import html2text
import os
from urllib.parse import urlparse
from typing import Dict, List, Tuple

class WebpageToMarkdown:
    def __init__(self):
        # Configure html2text
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.ignore_images = False
        self.converter.ignore_tables = False
        self.converter.body_width = 0  # Don't wrap text

    def fetch_webpage(self, url: str) -> Tuple[str, str]:
        """
        Fetch webpage content and return both HTML and page title
        """
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else urlparse(url).path
            return response.text, title.strip()
        except Exception as e:
            raise Exception(f"Error fetching {url}: {str(e)}")

    def convert_to_markdown(self, html: str) -> str:
        """
        Convert HTML content to markdown
        """
        return self.converter.handle(html)

    def process_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        Process multiple URLs and return list of dictionaries containing
        title, url, and markdown content
        """
        results = []
        for url in urls:
            try:
                html, title = self.fetch_webpage(url)
                markdown = self.convert_to_markdown(html)
                results.append({
                    'title': title,
                    'url': url,
                    'content': markdown
                })
                print(f"Successfully processed: {url}")
            except Exception as e:
                print(f"Failed to process {url}: {str(e)}")
        return results

# Example usage
if __name__ == "__main__":
    converter = WebpageToMarkdown()

    # Read URLs from comma-delimited text file
    with open('urls.txt', 'r') as file:
        content = file.read()
        urls = [url.strip().strip('"').strip("'") for url in content.split(',') if url.strip()]
    
    results = converter.process_urls(urls)
    
    # Create content directory if it doesn't exist
    if not os.path.exists('content'):
        os.makedirs('content')

    # Save files to content directory
    for result in results:
        filename = os.path.join('content', f"{result['title']}.md".replace(" ", "_"))
        with open(filename, 'w', encoding='utf-8') as f:
            # Add YAML frontmatter with URL
            f.write('---\n')
            f.write(f'url: {result["url"]}\n')
            f.write('---\n\n')
            # Write the markdown content
            f.write(result['content'])
