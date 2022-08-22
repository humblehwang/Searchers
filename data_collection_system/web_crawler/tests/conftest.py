import sys
import pathlib
import pytest
import pymongo
from typing import List
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from model import Article
from bson.objectid import ObjectId


@pytest.fixture
def ptt_internal_server_error() -> str:
    """Mock for tinternal server error of PTT """
    return "500"

@pytest.fixture
def ptt_test_home_page() -> str:
    """Mock for the home page of PTT test """
    return "404"

@pytest.fixture
def ptt_tech_job_home_page() -> str:
    """Mock for the home page of PTT tech job """
    with open("tests/file_test/ptt_tech_job.txt", 'r', encoding="utf-8") as file:
        return file.read()

@pytest.fixture
def ptt_tech_job_1() -> str:
    """Mock for the page 1 of PTT tech job """
    with open("tests/file_test/ptt_tech_job_1.txt", 'r', encoding="utf-8") as file:
        return file.read()

@pytest.fixture
def ptt_tech_job_4002() -> str:
    """Mock for the page 4002 of PTT tech job """
    with open("tests/file_test/ptt_tech_job_4002.txt", 'r', encoding="utf-8") as file:
        return file.read()
#@pytest.fixture
#def db_error() -> None:
#    """Mock for DB error"""
#    raise pymongo.errors.PyMongoError("MongoDB Error")
@pytest.fixture
def article_db_no_match() -> str:
    """Mock for no match row in DB"""
    return ""

@pytest.fixture
def article_db() -> str:
    """Mock the article collection of DB"""
    articles = [
        Article(
            {'_id': ObjectId('62c10634326a3a007a4c27db'),
            'author': 'hermes318 (Scott)',
            'board': 'Tech_Job',
            'title': '[心得] 系統廠基層員工的真實人生經歷分享',
            'date_time': '2022/07/03 10:55:58',
            'source': 'PTT',
            'num_comment': 0,
            'url': 'https://www.ptt.cc/bbs/Tech_Job/M.1660941577.A.833.html',
            'article_id': '627391e2859024e246e3343e766e361b',
            'content': '以前念書時大家都說男生念理工科好，因為成績普普，只去讀了私立學店的電機系\n渾渾噩噩過了四年，成績都是在中間遊走之下畢了業，畢業後08年跑去當兵，熬了\n一年終於退伍\n\n09年退伍後休息一個月就出來找工作，沒想到當時剛好金融海嘯，因為一直找不到\n工作，只好先去與政府合作的公司去先當月領政府22K的"至企業實習方案"實習當\n了一年的助理工程師後來時間到被通知不續聘，因此結束了第一份工作\n\n當時景氣稍微有好一點了，就開始去投一些系統廠的EE RD職缺，第一份工作遇到\n一家小系統廠願意收留我但薪水只願意給29K，當初覺得進來是希望能學東西，\n因此薪資覺得還免強可以過生活就去了，因為是第一年什麼獎金分紅都沒有\n年終也只有少的可憐的接近1個月，因此第一年的年薪大約只有30多萬\n\n這份工作跟在一位資深工程師身邊工作，從一開始畫小板線路熟悉orcad到專案\n量產，這位前輩都願意帶你一起做也願意教，所以這兩年跟在他身邊是真的學到\n了滿多東西，後來這位資深前輩因為家裡一些事情突然離職我也興起了轉職的念頭\n，想往大公司發展看看\n\n因為有了約3年多EE的資歷，在找第三份工作的時候明顯有滿多公司邀約，後來談\n了一間一線系統廠薪資給的不錯，底薪有接近40K就去了，當時做的產品為NB，\n為公司主力產品之一，所以就開始了瘋狂加班的工作期，一待就待了6年多，期間\n獲得主管賞識下職位也往上爬升了兩次，底薪也突破了60K，年薪達到120多萬的\n水準，我也是在這期間結了婚以及把多年存下來的錢買了房\n\n計畫趕不上變化，原本不想那麼早生的我，老婆卻突然懷了孕，有了小孩後負擔\n更大因此興起了轉職的念頭，因為有了帶案子的經驗，也轉職到一家一線廠談了\n基層主管缺就一直做到現在，這幾年薪大約落在150~180之間遊走，因為是單薪\n家庭，這樣的薪資要負擔房貸以及養家其實所能存下的錢也剩不多，就一直撐\n到現在，有了家庭也有了年紀其實也不太敢再亂換工作了，目前的目標大概就是\n假日時好好享受家庭生活，看著小孩能平安順利長大不要學壞大概就是最大的安慰\n\n'
            }
        ),

    ]
    articles.sort(key=lambda art: art.date_time, reverse=True)
    return articles[0].url

