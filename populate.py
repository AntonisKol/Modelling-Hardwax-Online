import logging
from parsers import HardwaxReleaseParser
from loader import DatabaseLoader


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add handler to print to console
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)

def main() -> None:
    """Parse Hardwax releases and load into database"""
    try:
        parser = HardwaxReleaseParser()
        releases = parser.parse()
        
        if not releases:
            logger.warning("No releases parsed from Hardwax")
            return
        
        loader = DatabaseLoader()
        count = loader.load(releases, record_store="hardwax")
        loader.close()
        
        logger.info(f"Successfully loaded {count} releases")
        
    except Exception as e:
        logger.error(f"Failed to populate database: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()