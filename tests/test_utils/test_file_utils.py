"""
ファイル操作ユーティリティのテスト
"""
import os
import json
import pytest
from unittest.mock import patch, mock_open
from src.utils.file_utils import create_output_directory, save_json

class TestFileUtils:
    """ファイル操作ユーティリティ関数のテスト"""

    def test_create_output_directory(self, temp_dir):
        """出力ディレクトリ作成のテスト"""
        with patch('src.utils.file_utils.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20250101_120000'
            
            output_dir = create_output_directory(base_dir=str(temp_dir))
            
            expected_dir = os.path.join(str(temp_dir), '20250101_120000')
            assert output_dir == expected_dir
            assert os.path.exists(os.path.join(expected_dir, 'result'))
            assert os.path.exists(os.path.join(expected_dir, 'screenshot'))

    def test_save_json(self, temp_dir):
        """JSON保存のテスト"""
        test_data = {'test': 'data'}
        file_path = os.path.join(str(temp_dir), 'test.json')
        
        save_json(test_data, file_path)
        
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
            assert saved_data == test_data
