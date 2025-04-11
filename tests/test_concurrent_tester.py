"""
同時実行テスターのテスト
"""
import os
import pytest
from unittest.mock import MagicMock, patch
from src.concurrent_tester import ConcurrentTester

class TestConcurrentTester:
    """ConcurrentTesterクラスのテスト"""

    def test_init(self, mock_config_loader):
        """初期化のテスト"""
        with patch('src.concurrent_tester.ScenarioLoader') as mock_scenario_loader_class, \
             patch('src.concurrent_tester.setup_logger'):
            
            # ScenarioLoaderのモック
            mock_scenario_loader = MagicMock()
            mock_scenario_loader_class.return_value = mock_scenario_loader
            mock_scenario_loader.get_actions.return_value = [
                {'操作ID': '1', '操作タイプ': 'URL移動', '対象要素': '/login'}
            ]
            
            tester = ConcurrentTester(mock_config_loader, test_mode=True, slow_mode=True, action_delay=1.0)
            
            assert tester.config_loader == mock_config_loader
            assert tester.scenario_file == mock_config_loader.load_scenario_config()
            assert tester.test_mode is True
            assert tester.slow_mode is True
            assert tester.action_delay == 1.0

    def test_run(self, mock_config_loader, temp_dir):
        """テスト実行のテスト"""
        with patch('src.concurrent_tester.ScenarioLoader') as mock_scenario_loader_class, \
             patch('src.concurrent_tester.setup_logger'), \
             patch('src.concurrent_tester.BrowserSession') as mock_browser_session_class, \
             patch('src.concurrent_tester.create_output_directory', return_value=str(temp_dir)), \
             patch('src.concurrent_tester.save_json'), \
             patch('src.concurrent_tester.generate_excel_report'):
            
            # ScenarioLoaderのモック
            mock_scenario_loader = MagicMock()
            mock_scenario_loader_class.return_value = mock_scenario_loader
            mock_scenario_loader.get_actions.return_value = [
                {'操作ID': '1', '操作タイプ': 'URL移動', '対象要素': '/login'}
            ]
            
            # BrowserSessionのモック
            mock_browser_session = MagicMock()
            mock_browser_session_class.return_value = mock_browser_session
            mock_browser_session.run_scenario.return_value = {
                'success': True,
                'actions': [{'操作ID': '1', 'success': True}]
            }
            
            tester = ConcurrentTester(mock_config_loader)
            results = tester.run()
            
            assert results['total_sessions'] > 0
            assert results['successful_sessions'] > 0
            assert results['failed_sessions'] == 0
            assert 'output_file' in results
