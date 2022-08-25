from ptt.ptt_data_processing import PTTDataProcesser
from kafka import KafkaConsumer, errors
from unittest.mock import patch
from mock_kafka import MockMessage
import pytest_mock
from custom_exception import GetWebPageError
import pytest

SOURCE = "PTT"

class TestPTTDataProcesser():
    """A class for testing PTTDataProcesser"""
    

    url = "https://www.ptt.cc/bbs/Tech_Job/M.1661006556.A.C5D.html"

    def test_process_article(self):
        ptt = PTTDataProcesser()
        ptt.url_list = [self.url]
        ptt.process_articles()
        assert len(ptt.article_list) == len(ptt.url_list)
        assert len(ptt.comment_list[0]) == 49
    """
    def test_get_the_web_page_by_url_success(
            self,
            ptt_tech_job_web_page:str,
            mocker: pytest_mock.MockFixture
        ) -> None:

        mocker.patch(
            'helper.get_web_page',
            autospec=True,
            return_value=ptt_tech_job_web_page
        )
        ptt = PTTDataProcesser()
        assert len(ptt.get_web_page_by_url(self.url)) == 14708

    def test_get_the_web_page_by_url_exception_raised(
            self,
            ptt_internal_server_error:str,
            mocker: pytest_mock.MockFixture
        ) -> None:

        mocker.patch(
            'helper.get_web_page',
            autospec=True,
            return_value=ptt_internal_server_error
        )
        ptt = PTTDataProcesser()
        with pytest.raises(GetWebPageError):
            ptt.get_web_page_by_url(self.url)

    def test_extract_article_data_success(            
            self,
            ptt_tech_job_web_page:str,
            mocker:pytest_mock.MockFixture
        ) -> None:

        mocker.patch(
            'helper.get_web_page',
            autospec=True,
            return_value=ptt_tech_job_web_page
        )
        ptt = PTTDataProcesser()
        web_content = ptt.get_web_page_by_url(self.url)
        article, _ = ptt.extract_article_data(self.url, web_content)
        assert article['title'] == "[討論] 新鮮人從台廠IC豬屎起手較好？"

    def test_extract_article_data_header_wo_time_success(            
            self,
            ptt_tech_job_header_wo_time:str,
            mocker:pytest_mock.MockFixture
        ) -> None:

        mocker.patch(
            'helper.get_web_page',
            autospec=True,
            return_value=ptt_tech_job_header_wo_time
        )
        ptt = PTTDataProcesser()
        web_content = ptt.get_web_page_by_url(self.url)
        article, _ = ptt.extract_article_data(self.url, web_content)
        assert article['title'] == "[請益] 職缺"
        assert article['date_time'] == "2017/06/03 10:11:05"

    def test_data_processing(
            self,
            ptt_tech_job_header_wo_time:str,
            mocker:pytest_mock.MockerFixture
        ) -> None:
        mocker.patch(
            'helper.get_web_page',
            autospec=True,
            return_value=ptt_tech_job_header_wo_time
        )
        ptt = PTTDataProcesser()
        ptt.url_list = [self.url] * 2
        ptt.process_articles()
        assert len(ptt.article_list) == len(ptt.url_list)
        assert len(ptt.comment_list[0]) == 44


    def test_data_processing_with_exception_raised(
            self,
            ptt_internal_server_error:str,
            mocker: pytest_mock.MockFixture
        ) -> None:

        mocker.patch(
            'helper.get_web_page',
            autospec=True,
            return_value=ptt_internal_server_error
        )
        ptt = PTTDataProcesser()
        ptt.url_list = [self.url] 
        with pytest.raises(GetWebPageError):
            ptt.process_articles()
    """