"""
シナリオローダーのテスト
"""
import csv
import pytest
from unittest.mock import patch, mock_open
from src.scenario_loader import ScenarioLoader

class TestScenarioLoader:
    """ScenarioLoaderクラスのテスト"""

    def test_init_and_load_scenario(self):
        """初期化とシナリオ読み込みのテスト"""
        csv_content = (
            "操作ID,操作タイプ,対象要素,入力値,待機時間,説明,Excel出力\n"
            "1,URL移動,/login,,,ログインページに移動,yes\n"
            "2,テキスト入力,#username,test_user,,ユーザー名を入力,no\n"
        )
        
        with patch('builtins.open', mock_open(read_data=csv_content)):
            loader = ScenarioLoader('test.csv')
            actions = loader.get_actions()
            
            assert len(actions) == 2
            assert actions[0]['操作ID'] == '1'
            assert actions[0]['操作タイプ'] == 'URL移動'
            assert actions[0]['対象要素'] == '/login'
            assert actions[0]['Excel出力'] is True
            
            assert actions[1]['操作ID'] == '2'
            assert actions[1]['操作タイプ'] == 'テキスト入力'
            assert actions[1]['対象要素'] == '#username'
            assert actions[1]['入力値'] == 'test_user'
            assert actions[1]['Excel出力'] is False

    def test_file_not_found(self):
        """ファイルが見つからない場合のテスト"""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            with pytest.raises(FileNotFoundError):
                ScenarioLoader('not_exist.csv')

    def test_csv_error(self):
        """CSVの解析エラーのテスト"""
        with patch('builtins.open', mock_open(read_data="invalid,csv")):
            with patch('csv.DictReader', side_effect=csv.Error):
                with pytest.raises(csv.Error):
                    ScenarioLoader('invalid.csv')
