import requests
from abc import ABC, abstractmethod
from models import ReleaseModel
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
        """Parse Hardwax releases"""
        # TODO: Implement Hardwax-specific parsing
        return []


class SpaceHallParser(ReleaseParserBase):
    """Scraper for spacehall-berlin.de"""
    
    def __init__(self) -> None:
        super().__init__(url="https://www.spacehall-berlin.de", record_store="spacehall")
    
    def parse(self) -> list[ReleaseModel]:
        """Parse SpaceHall releases"""
        # TODO: Implement SpaceHall-specific parsing
        return []
