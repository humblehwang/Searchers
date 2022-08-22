import cloudscraper
from kafka import KafkaProducer
def get_web_page(url: str) -> str:
    """
    Get the web page
    Args:
        url(str)
    Returns:
        response.text(str)
    """
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    if response.status_code == 200:
        return response.text 
    elif response.status_code == 404:
        return "404"
    else:
        return "500"
    