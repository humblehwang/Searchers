import sys
from unittest import mock
import pytest
import pathlib
import pymongo
import pytest_mock
from typing import List
import cloudscraper
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from ptt.ptt_url_getter import pttUrlGetter
from model import Article
from custom_exception import GetWebPageError
import helper
#from mock_kafka import MockKafkaProducer, mock_kafka_producer
from unittest.mock import patch, MagicMock, Mock
#from kafka import KafkaProducer, errors

class TestPttUrlGetter:
    """A class for testing PttUrlGetter"""
    """
    @patch("kafka.KafkaProducer", mock_kafka_producer)
    def test_send_message_to_kafka_success(self) -> None:
        ptt = pttUrlGetter(False, "Tech_Job", mock_kafka_producer)
        ptt.url_list = ["test1", "test2", "test3", "test4"]
        ptt.send_to_kafka()
        assert 'PTT_URL' in mock_kafka_producer.data
        assert len(mock_kafka_producer.data['PTT_URL']) == len(ptt.url_list)
    """
    def test_set_up_with_non_first_call_success(self, 
                            article_db: str,
                            ptt_tech_job_home_page: str,
                            mocker: pytest_mock.MockFixture) -> None:
        mocker.patch(
            'model.db_query.get_latest_url',
            autospec=True,
            return_value=article_db
        )
        mocker.patch(
            'helper.get_web_page',
            autospec=True,
            return_value=ptt_tech_job_home_page
        )
        ptt = pttUrlGetter(False, "Tech_Job")
        ptt.set_up()
        assert ptt.latest_url == (
            "https://www.ptt.cc/bbs/Tech_Job/M.1660941577.A.833.html"
        )

        assert ptt.latest_page_index == "4000"

    def test_get_latest_url_from_db_with_url_return(self, article_db: str,
                                                    mocker: pytest_mock.MockFixture) -> None:
        """test get latest url from db with url return"""
        mocker.patch(
            'model.db_query.get_latest_url',
            autospec=True,
            return_value=article_db
        )
        ptt = pttUrlGetter(False, "Tech_Job")
        assert ptt.get_latest_url_from_db() == (
            'https://www.ptt.cc/bbs/Tech_Job/M.1660941577.A.833.html'
        )

    def test_get_latest_url_from_db_with_empty_string_return(self, article_db_no_match: str,
                                                             mocker: pytest_mock.MockFixture) -> None:
        """test get latest url from db with empty string return"""
        mocker.patch(
            'model.db_query.get_latest_url',
            autospec=True,
            return_value=article_db_no_match
        )
        ptt = pttUrlGetter(False, "Test")
        assert ptt.get_latest_url_from_db() == ""

    def test_param_is_first_is_equal_to_True_the_latest_url_is_None(self, article_db: List[Article],
                                             mocker: pytest_mock.MockFixture) -> None:
        """test the given param is first equal to True"""
        mocker.patch(
            'model.db_query.get_latest_url',
            autospec=True,
            return_value=article_db
        )
        ptt = pttUrlGetter(True, "Test")
        assert ptt.latest_url is None

    def test_get_latest_page_index_with_web_response_200(self, ptt_tech_job_home_page: str,
                                  mocker: pytest_mock.MockFixture) -> None:

        mocker.patch(
            'helper.get_web_page',
            autospec=True,
            return_value=ptt_tech_job_home_page
        )
        
        ptt = pttUrlGetter(True, "Tech_Job")
        assert ptt.get_latest_page_index() == "4000"
    
    def test_get_latest_page_index_with_web_response_not_200(self, ptt_test_home_page: str,
                                  mocker: pytest_mock.MockFixture) -> None:
        mocker.patch(
            'helper.get_web_page',
            autospec=True,
            return_value=ptt_test_home_page
        )
        ptt = pttUrlGetter(True, "QEW")
        with pytest.raises(GetWebPageError):
            ptt.get_latest_page_index()
    
    def test_get_url_list_first_call_get_url_list_success(self) -> None:
        """
        This is not a unit test, but is the best way to test the function
        """

        ptt = pttUrlGetter(True, "Tech_Job")
        ptt.latest_page_index = "0"
        assert len(ptt.get_url_list()) == 20 
    
    def test_get_url_list_not_first_call_get_url_list_success(self, ptt_tech_job_1: str,
                                  mocker: pytest_mock.MockFixture) -> None:
        mocker.patch(
            'helper.get_web_page',
            autospec=True,
            return_value=ptt_tech_job_1
        )
        
        ptt = pttUrlGetter(False, "Tech_Job")
        ptt.latest_url = "https://www.ptt.cc/bbs/Tech_Job/M.1660941577.A.833.html"
        ptt.latest_page_index = 0        
        assert len(ptt.get_url_list()) == 15
