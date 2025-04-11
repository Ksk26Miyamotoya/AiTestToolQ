"""
設定ローダーのテスト
"""
import os
import pytest
from unittest.mock import patch, mock_open
from src.config_loader import ConfigLoader

class TestConfigLoader:
    """ConfigLoaderクラスのテスト"""

    def test_init_with_default_paths(self):
        """デフォルトパスでの初期化テスト"""
        with patch('src.config_loader.load_toml') as mock_load_toml:
            mock_load_toml.return_value = {'test_mode': True}
            loader = ConfigLoader()
            assert loader.config == {'test_mode': True}
            mock_load_toml.assert_called_once_with('resources/config.toml')

    def test_init_with_custom_paths(self):
        """カスタムパスでの初期化テスト"""
        with patch('src.config_loader.load_toml') as mock_load_toml:
            mock_load_toml.return_value = {'test_mode': True}
            loader = ConfigLoader(
                config_file='custom_config.toml',
                url_config='custom_url.toml',
                user_config='custom_user.toml',
                scenario_config='custom_scenario.csv'
            )
            assert loader.config == {'test_mode': True}
            assert loader.url_config_path == 'custom_url.toml'
            assert loader.user_config_path == 'custom_user.toml'
            assert loader.scenario_config_path == 'custom_scenario.csv'
            mock_load_toml.assert_called_once_with('custom_config.toml')

    def test_load_url_config(self):
        """URL設定ファイルの読み込みテスト"""
        with patch('src.config_loader.load_toml') as mock_load_toml:
            # メイン設定ファイルの読み込み
            mock_load_toml.return_value = {'test_mode': True}
            loader = ConfigLoader(url_config='test_url')
            
            # URL設定ファイルの読み込み
            mock_load_toml.return_value = {'url': 'http://test.com'}
            result = loader.load_url_config()
            assert result == {'url': 'http://test.com'}
            mock_load_toml.assert_called_with('test_url.toml')

    def test_load_user_config(self):
        """ユーザー設定ファイルの読み込みテスト"""
        with patch('src.config_loader.load_toml') as mock_load_toml:
            # メイン設定ファイルの読み込み
            mock_load_toml.return_value = {'test_mode': True}
            loader = ConfigLoader(user_config='test_user')
            
            # ユーザー設定ファイルの読み込み
            mock_load_toml.return_value = {'users': [{'app_username': 'test'}]}
            result = loader.load_user_config()
            assert result == [{'app_username': 'test'}]
            mock_load_toml.assert_called_with('test_user.toml')

    def test_load_scenario_config(self):
        """シナリオファイルのパス取得テスト"""
        with patch('src.config_loader.load_toml') as mock_load_toml:
            mock_load_toml.return_value = {'test_mode': True}
            loader = ConfigLoader(scenario_config='test_scenario')
            result = loader.load_scenario_config()
            assert result == 'test_scenario.csv'

    def test_get_excel_report_config(self):
        """Excelレポート設定の取得テスト"""
        with patch('src.config_loader.load_toml') as mock_load_toml:
            mock_load_toml.return_value = {
                'screenshot_title_cell_color': '#ff0000'
            }
            loader = ConfigLoader()
            result = loader.get_excel_report_config()
            assert result == {'screenshot_title_cell_color': '#ff0000'}
