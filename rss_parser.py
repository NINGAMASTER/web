import feedparser
from datetime import datetime
import logging

class RSSParser:
    def __init__(self, rss_url, max_items=3):
        self.rss_url = rss_url
        self.max_items = max_items
        self.logger = logging.getLogger(__name__)

    def parse_feed(self):
        """Парсит RSS-ленту и возвращает структурированные новости"""
        try:
            self.logger.info(f"Fetching RSS feed from {self.rss_url}")
            feed = feedparser.parse(self.rss_url)
            
            news_items = []
            for i, entry in enumerate(feed.entries):
                if i >= self.max_items:
                    break
                    
                # Извлекаем первое изображение из содержимого
                image_url = self._extract_image(entry)
                
                # Форматируем дату
                pub_date = self._parse_publish_date(entry)
                
                news_items.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', '#'),
                    'description': entry.get('description', ''),
                    'image_url': image_url,
                    'published': pub_date.strftime('%Y-%m-%d %H:%M') if pub_date else None
                })
                
            return news_items
        
        except Exception as e:
            self.logger.error(f"Error parsing RSS feed: {str(e)}", exc_info=True)
            return None

    def _extract_image(self, entry):
        """Извлекает URL изображения для rss.app"""
        # 1. Проверяем медиа-вложения (если есть)
        if 'media_content' in entry and len(entry.media_content) > 0:
            for media in entry.media_content:
                if media.get('type', '').startswith('image/'):
                    return media['url']

        # 2. Проверяем <enclosure> (использует rss.app)
        if 'enclosures' in entry and len(entry.enclosures) > 0:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image/'):
                    return enc['href']

        # 3. Парсим HTML-описание (если изображение в тексте)
        if 'description' in entry:
            desc = entry.description
            if '<img' in desc:
                start = desc.find('src="') + 5
                end = desc.find('"', start)
                return desc[start:end]

        return None  # Если изображение не найдено

    def _parse_publish_date(self, entry):
        """Парсит дату публикации"""
        if 'published' not in entry:
            return None
        try:
            return datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        except ValueError:
            return None