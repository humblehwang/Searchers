import cloudscraper

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

def convert_month(month):
    """
    Convert the Engilsh name of month to it's number
    Args:
        month(str)
    Returns:
        number of month(str)
    """
    if month == 'Jan':
        return '01'
    elif month == 'Feb':
        return '02'    
    elif month == 'Mar':
        return '03'  
    elif month == 'Apr':
        return '04'        
    elif month == 'May':
        return '05'        
    elif month == 'Jun':
        return '06'        
    elif month == 'Jul':
        return '07'        
    elif month == 'Aug':
        return '08'        
    elif month == 'Sep':
        return '09'        
    elif month == 'Oct':
        return '10'       
    elif month == 'Nov':
        return '11'     
    elif month == 'Dec':
        return '12'
    else:
        raise ValueError("Wrong month type is given")
    
def padding(value):
    """
    Padding the value of month
    Args:
        value(str)
    Return:
        str
    Example:
        value = "1" -> return "01"
        value = "12" -> return 12
    """
    if len(value) == 1:
        return f"0{value}"
    return value

def process_datetime(date_time):
    """
    Process the datetime
    Delete the white spaces and arrange the value into right format
    Args:
        date_time(str)
    Return:
        datetime in string(str)
    """
    while '' in date_time:
        del date_time[date_time.index('')]
    return f"{date_time[4]}/{padding(convert_month(date_time[1]))}/{padding(date_time[2])} {date_time[3]}"
