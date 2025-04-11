"""
テスト共通の設定とフィクスチャ
"""
import os
import sys
import pytest
from unittest.mock import MagicMock
from selenium import webdriver

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def test_config():
    """テスト用の設定を返す"""
    return {
        'browser': 'chrome',
        'test_mode': True,
        'slow_mode': False,
        'action_delay': 0.1,
        'timeout': 5,
        'screenshot_timing': ['on_error'],
        'url': 'http://localhost:8080',
        'debug_mode': True
    }

@pytest.fixture
def test_user():
    """テスト用のユーザー情報を返す"""
    return {
        'basic_auth_username': '',
        'basic_auth_password': '',
        'app_username': 'test_user',
        'app_password': 'test_pass'
    }

@pytest.fixture
def test_action():
    """テスト用のアクション情報を返す"""
    return {
        '操作ID': '1',
        '操作タイプ': 'URL移動',
        '対象要素': '/login',
        '入力値': '',
        '待機時間': '0',
        '説明': 'ログインページに移動',
        'Excel出力': True
    }

@pytest.fixture
def mock_driver():
    """モック化されたWebDriverを返す"""
    driver = MagicMock()
    # find_elementのモック
    mock_element = MagicMock()
    driver.find_element.return_value = mock_element
    # 他のメソッドのモック
    driver.get.return_value = None
    driver.save_screenshot.return_value = True
    driver.execute_script.return_value = None
    return driver

@pytest.fixture
def mock_config_loader():
    """モック化された設定ローダーを返す"""
    loader = MagicMock()
    loader.config = {
        'browser': 'chrome',
        'test_mode': True,
        'slow_mode': False,
        'action_delay': 0.1,
        'timeout': 5,
        'screenshot_timing': ['on_error'],
        'url': 'http://localhost:8080',
        'debug_mode': True
    }
    loader.load_url_config.return_value = {'url': 'http://localhost:8080'}
    loader.load_user_config.return_value = [
        {
            'basic_auth_username': '',
            'basic_auth_password': '',
            'app_username': 'test_user1',
            'app_password': 'test_pass1'
        },
        {
            'basic_auth_username': '',
            'basic_auth_password': '',
            'app_username': 'test_user2',
            'app_password': 'test_pass2'
        }
    ]
    loader.load_scenario_config.return_value = 'tests/resources/scenario/test.csv'
    return loader

@pytest.fixture
def temp_dir(tmpdir):
    """一時ディレクトリを作成して返す"""
    return tmpdir
