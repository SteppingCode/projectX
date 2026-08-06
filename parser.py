import httpx
from bs4 import BeautifulSoup

async def fetch_url_metadata(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else "Без названия"
            
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                        soup.find('meta', attrs={'property': 'og:description'})
            
            description = meta_desc['content'].strip() if meta_desc else "Нет описания" # type: ignore
            
            return {"title": title, "description": description}
            
        except Exception as e:
            return {"title": "Не удалось загрузить", "description": str(e)}