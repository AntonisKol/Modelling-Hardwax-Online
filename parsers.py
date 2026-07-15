import re
import requests
from abc import ABC, abstractmethod
from models import ReleaseModel, TrackModel
from bs4 import BeautifulSoup


class ReleaseParserBase(ABC):
    """Abstract base class for record store scrapers"""
    
    def __init__(self, url: str, record_store: str) -> None:
        self.url = url
        self.record_store = record_store
        self.session = requests.Session()
    
    def _fetch_data(self) -> BeautifulSoup:
        """Fetch and parse HTML from URL"""
        response = self.session.get(self.url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    
    @abstractmethod
    def parse(self) -> list[ReleaseModel]:
        """Parse releases from HTML - subclasses must implement"""
        raise NotImplementedError


class HardwaxReleaseParser(ReleaseParserBase):
    """Scraper for hardwax.com"""
    
    def __init__(self) -> None:
        super().__init__(url="https://www.hardwax.com", record_store="hardwax")
    
    def parse(self) -> list[ReleaseModel]:
        """Parse Hardwax releases from HTML"""
        soup = self._fetch_data()
        releases = []
        
        # Find all release links (href contains numeric ID like /12345/)
        release_links = soup.find_all('a', href=re.compile(r'/\d+/'))
        
        for link in release_links:
            # Walk up DOM tree to find release container with € and Label
            container = link
            found_container = False
            
            for _ in range(10):
                container = container.find_parent()
                if container:
                    text_content = container.get_text()
                    if '€' in text_content and ('Label' in text_content or 'label' in text_content):
                        found_container = True
                        break
            
            if not found_container:
                continue
            
            # Extract artist and title from <h2>
            h2 = container.find('h2')
            if not h2:
                continue
            
            h2_text = h2.get_text(strip=True)
            
            if ':' not in h2_text:
                continue
            
            artist_name, title = h2_text.split(':', 1)
            artist_name = artist_name.strip()
            title = title.strip()
            
            if not artist_name or not title:
                continue
            
            # Extract tracks from <ul> containing audio links
            tracks = []
            all_uls = container.find_all('ul')
            
            for ul in all_uls:
                # Look for ul with audio links (mp3, aiff, audio)
                has_audio_links = ul.find('a', href=re.compile(r'\.mp3|\.aiff|audio'))
                
                if has_audio_links:
                    for li in ul.find_all('li'):
                        track_link = li.find('a')
                        if track_link:
                            track_text = track_link.get_text(separator=' ', strip=True)
                            track_name = ' '.join(track_text.split())
                            
                            if track_name and len(track_name) > 1:
                                tracks.append(TrackModel(name=track_name))
                    break
            
            if not tracks:
                continue
            
            try:
                release = ReleaseModel(
                    artist=artist_name,
                    title=title,
                    tracks=tracks
                )
                releases.append(release)
            except Exception as e:
                print(f"Error creating ReleaseModel for '{title}': {e}")
                continue
        
        return releases


class SpaceHallParser(ReleaseParserBase):
    """Scraper for spacehall-berlin.de"""
    
    def __init__(self) -> None:
        super().__init__(url="https://www.spacehall-berlin.de", record_store="spacehall")
    
    def parse(self) -> list[ReleaseModel]:
        """Parse SpaceHall releases from HTML"""
        # TODO: Implement SpaceHall-specific parsing
        return []