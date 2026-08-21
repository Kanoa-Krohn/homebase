import urllib.request
import xml.etree.ElementTree as ET

from services.cache import save_cache, load_cache

GENERAL_FEED = "https://feeds.npr.org/1001/rss.xml"
TECH_FEED = "https://feeds.npr.org/1019/rss.xml"


def _fetch_rss_items(url, limit):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    items = []
    for item in root.findall('.//item')[:limit]:
        title = item.find('title')
        link = item.find('link')
        if title is not None and title.text:
            items.append({
                'title': title.text.strip(),
                'link': link.text.strip() if link is not None and link.text else None,
            })
    return items


def get_news():
    try:
        general = _fetch_rss_items(GENERAL_FEED, 5)

        try:
            tech = _fetch_rss_items(TECH_FEED, 1)
        except Exception:
            tech = []

        headlines = general + tech
        save_cache('news', headlines)
        return {'headlines': headlines, 'cached': False}
    except Exception:
        cached_headlines = load_cache('news')
        if cached_headlines is None:
            raise
        return {'headlines': cached_headlines, 'cached': True}