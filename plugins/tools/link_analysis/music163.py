import aiohttp
from bs4 import BeautifulSoup


async def music163(url):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      html = await response.text()
      soup = BeautifulSoup(html, "html.parser")

      picture_elem = soup.select_one(".m-lycifo img")
      title_elem = soup.select_one(".cnt .hd em")
      artist_elem = soup.select_one(".cnt .des span")
      album_elem = soup.select_one(".cnt .des > a")

      picture = picture_elem["src"] if picture_elem else None
      title = title_elem.text if title_elem else None
      artist = artist_elem.text if artist_elem else None
      album = album_elem.text if album_elem else None

      return {"picture": picture, "title": title, "artist": artist, "album": album}
