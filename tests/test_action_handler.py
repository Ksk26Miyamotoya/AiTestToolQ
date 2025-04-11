"""
アクションハンドラーのテスト
"""
import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import WebDriverException
from src.action_handler import ActionHandler
from src.utils.constants import OperationType

class TestActionHandler:
    """ActionHandlerクラスのテスト"""

    def test_init(self, mock_driver, test_user, test_config):
        """初期化のテスト"""
        logger = MagicMock()
        handler = ActionHandler(mock_driver, test_user, test_config, logger, slow_mode=True, action_delay=1.0)
        
        assert handler.driver == mock_driver
        assert handler.user == test_user
        assert handler.config == test_config
        assert handler.logger == logger
        assert handler.timeout == test_config['timeout']
        assert handler.slow_mode is True
        assert handler.action_delay == 1.0

    def test_handle_action_url_move(self, mock_driver, test_user, test_config):
        """URL移動アクションのテスト"""
        logger = MagicMock()
        handler = ActionHandler(mock_driver, test_user, test_config, logger)
        
        action = {
            '操作タイプ': OperationType.URL_MOVE,
            '対象要素': '/login',
            '説明': 'ログインページに移動'
        }
        
        success, error = handler.handle_action(action)
        assert success is True
        assert error is None
        mock_driver.get.assert_called_once()

    def test_handle_action_click(self, mock_driver, test_user, test_config):
        """クリックアクションのテスト"""
        logger = MagicMock()
        handler = ActionHandler(mock_driver, test_user, test_config, logger)
        
        # find_elementのモック
        mock_element = MagicMock()
        mock_driver.find_element.return_value = mock_element
        
        action = {
            '操作タイプ': OperationType.CLICK,
            '対象要素': '#login-button',
            '説明': 'ログインボタンをクリック'
        }
        
        with patch('src.action_handler.find_element', return_value=mock_element):
            success, error = handler.handle_action(action)
            assert success is True
            assert error is None
            mock_element.click.assert_called_once()

    def test_handle_action_text_input(self, mock_driver, test_user, test_config):
        """テキスト入力アクションのテスト"""
        logger = MagicMock()
        handler = ActionHandler(mock_driver, test_user, test_config, logger)
        
        # find_elementのモック
        mock_element = MagicMock()
        mock_driver.find_element.return_value = mock_element
        
        action = {
            '操作タイプ': OperationType.TEXT_INPUT,
            '対象要素': '#username',
            '入力値': '${user.app_username}',
            '説明': 'ユーザー名を入力'
        }
        
        with patch('src.action_handler.find_element', return_value=mock_element):
            success, error = handler.handle_action(action)
            assert success is True
            assert error is None
            mock_element.clear.assert_called_once()
            mock_element.send_keys.assert_called_once_with(test_user['app_username'])

    def test_handle_action_error(self, mock_driver, test_user, test_config):
        """アクション実行エラーのテスト"""
        logger = MagicMock()
        handler = ActionHandler(mock_driver, test_user, test_config, logger)
        
        # find_elementのモックでエラーを発生させる
        with patch('src.action_handler.find_element', side_effect=WebDriverException("Element not found")):
            action = {
                '操作タイプ': OperationType.CLICK,
                '対象要素': '#not-exist',
                '説明': '存在しない要素をクリック'
            }
            
            success, error = handler.handle_action(action)
            assert success is False
            assert error is not None
            assert "Element not found" in error
