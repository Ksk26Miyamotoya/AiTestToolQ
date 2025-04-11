"""
ブラウザセッションのテスト
"""
import os
import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import WebDriverException
from src.browser_session import BrowserSession

class TestBrowserSession:
    """BrowserSessionクラスのテスト"""

    def test_init(self, test_user, test_config, temp_dir):
        """初期化のテスト"""
        with patch('src.browser_session.setup_logger') as mock_setup_logger:
            mock_logger = MagicMock()
            mock_setup_logger.return_value = mock_logger
            
            session = BrowserSession(test_user, test_config, 1, str(temp_dir))
            
            assert session.user == test_user
            assert session.config == test_config
            assert session.session_id == 1
            assert session.output_dir == str(temp_dir)
            assert session.base_url == test_config['url']
            assert session.logger == mock_logger
            assert session.screenshot_timing == test_config['screenshot_timing']

    @patch('src.browser_session.webdriver')
    def test_start_browser_chrome(self, mock_webdriver, test_user, test_config, temp_dir):
        """Chromeブラウザの起動テスト"""
        with patch('src.browser_session.setup_logger'):
            session = BrowserSession(test_user, test_config, 1, str(temp_dir))
            mock_chrome_options = MagicMock()
            mock_webdriver.ChromeOptions.return_value = mock_chrome_options
            mock_driver = MagicMock()
            mock_webdriver.Chrome.return_value = mock_driver
            
            session.start_browser()
            
            assert session.driver == mock_driver
            mock_webdriver.Chrome.assert_called_once()

    @patch('src.browser_session.webdriver')
    def test_start_browser_firefox(self, mock_webdriver, test_user, test_config, temp_dir):
        """Firefoxブラウザの起動テスト"""
        with patch('src.browser_session.setup_logger'):
            test_config['browser'] = 'firefox'
            session = BrowserSession(test_user, test_config, 1, str(temp_dir))
            mock_firefox_options = MagicMock()
            mock_webdriver.FirefoxOptions.return_value = mock_firefox_options
            mock_driver = MagicMock()
            mock_webdriver.Firefox.return_value = mock_driver
            
            session.start_browser()
            
            assert session.driver == mock_driver
            mock_webdriver.Firefox.assert_called_once()

    def test_take_screenshot(self, test_user, test_config, temp_dir):
        """スクリーンショット撮影のテスト"""
        with patch('src.browser_session.setup_logger'):
            session = BrowserSession(test_user, test_config, 1, str(temp_dir))
            session.driver = MagicMock()
            session.driver.save_screenshot.return_value = True
            
            # スクリーンショットディレクトリの作成
            screenshot_dir = os.path.join(str(temp_dir), 'screenshot')
            os.makedirs(screenshot_dir, exist_ok=True)
            
            result = session.take_screenshot('test_action', 'before')
            
            assert result is not None
            assert session.driver.save_screenshot.called

    def test_run_scenario(self, test_user, test_config, temp_dir):
        """シナリオ実行のテスト"""
        with patch('src.browser_session.setup_logger'), \
             patch('src.browser_session.ActionHandler') as mock_action_handler_class:
            
            session = BrowserSession(test_user, test_config, 1, str(temp_dir))
            session.driver = MagicMock()
            
            # ActionHandlerのモック
            mock_action_handler = MagicMock()
            mock_action_handler_class.return_value = mock_action_handler
            mock_action_handler.handle_action.return_value = (True, None)
            
            # シナリオアクション
            actions = [
                {'操作ID': '1', '操作タイプ': 'URL移動', '対象要素': '/login', '説明': 'ログインページに移動'},
                {'操作ID': '2', '操作タイプ': 'テキスト入力', '対象要素': '#username', '説明': 'ユーザー名を入力'}
            ]
            
            result = session.run_scenario(actions)
            
            assert result['success'] is True
            assert len(result['actions']) == 2
            assert mock_action_handler.handle_action.call_count == 2
