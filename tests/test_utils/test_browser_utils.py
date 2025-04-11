"""
ブラウザユーティリティのテスト
"""
import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import WebDriverException
from src.utils.browser_utils import build_url_with_auth, find_element, scroll_to_element

class TestBrowserUtils:
    """ブラウザユーティリティ関数のテスト"""

    def test_build_url_with_auth_no_auth(self):
        """Basic認証なしのURL構築テスト"""
        url = build_url_with_auth('http://example.com', '', '')
        assert url == 'http://example.com'

    def test_build_url_with_auth_with_auth(self):
        """Basic認証ありのURL構築テスト"""
        url = build_url_with_auth('http://example.com', 'user', 'pass')
        assert url == 'http://user:pass@example.com'

    def test_find_element_by_css(self):
        """CSSセレクタによる要素検索テスト"""
        driver = MagicMock()
        mock_element = MagicMock()
        driver.find_element.return_value = mock_element
        
        element = find_element(driver, '#test', timeout=1)
        
        assert element == mock_element
        driver.find_element.assert_called_once()

    def test_find_element_not_found(self):
        """要素が見つからない場合のテスト"""
        driver = MagicMock()
        driver.find_element.side_effect = WebDriverException("Element not found")
        
        with pytest.raises(WebDriverException):
            find_element(driver, '#not-exist', timeout=1)

    def test_scroll_to_element(self):
        """要素へのスクロールテスト"""
        driver = MagicMock()
        element = MagicMock()
        
        scroll_to_element(driver, element)
        
        driver.execute_script.assert_called_once()
