import sys
import pathlib
import hashlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from classification import Classifyer

if __name__ == '__main__':
    file_name = (
        f"/home/Code/PhD/data_collection_system/file"
        f"/blocklist/non_block.xlsx"
    )
    checker = Classifyer(file_name)
    url = "https://medium.com/@kevin97563/taiwan-google-%E7%A1%AC%E9%AB%94%E8%A8%AD%E8%A8%88%E9%9D%A2%E8%A9%A6%E5%BF%83%E5%BE%97-85572a85db55"
    keyword = "面試心得"
    filename = (
                f"/home/Code/PhD/data_collection_system/file/"
                f"search_result/google_search_content_result/google"
                f"/{hashlib.md5(url.encode('utf-8')).hexdigest()}.txt"
            )
    
    with open(filename, 'r', encoding="utf-8") as file:
        web_content =  file.read()
    label = checker.classify_web_page_content(url, web_content, keyword)
    print(label)