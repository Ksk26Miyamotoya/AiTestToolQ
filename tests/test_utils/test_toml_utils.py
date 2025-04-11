"""
TOML操作ユーティリティのテスト
"""
import pytest
from unittest.mock import patch, mock_open
from src.utils.toml_utils import load_toml, get_bool, get_float, get_list

class TestTomlUtils:
    """TOML操作ユーティリティ関数のテスト"""

    def test_load_toml(self):
        """TOMLファイル読み込みのテスト"""
        toml_content = """
        [section]
        key = "value"
        bool_key = true
        int_key = 123
        """
        
        with patch('builtins.open', mock_open(read_data=toml_content)):
            with patch('tomli.load') as mock_tomli_load:
                mock_tomli_load.return_value = {
                    'section': {
                        'key': 'value',
                        'bool_key': True,
                        'int_key': 123
                    }
                }
                
                result = load_toml('test.toml')
                
                assert result == {
                    'section': {
                        'key': 'value',
                        'bool_key': True,
                        'int_key': 123
                    }
                }

    def test_load_toml_file_not_found(self):
        """存在しないTOMLファイル読み込みのテスト"""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = load_toml('not_exist.toml')
            assert result is None

    def test_get_bool(self):
        """ブール値取得のテスト"""
        config = {
            'true_key': True,
            'false_key': False,
            'string_true': 'true',
            'string_false': 'false',
            'yes_key': 'yes',
            'no_key': 'no'
        }
        
        assert get_bool(config, 'true_key', False) is True
        assert get_bool(config, 'false_key', True) is False
        assert get_bool(config, 'string_true', False) is True
        assert get_bool(config, 'string_false', True) is False
        assert get_bool(config, 'yes_key', False) is True
        assert get_bool(config, 'no_key', True) is False
        assert get_bool(config, 'not_exist', True) is True
        assert get_bool(config, 'not_exist', False) is False

    def test_get_float(self):
        """浮動小数点数取得のテスト"""
        config = {
            'float_key': 1.5,
            'int_key': 2,
            'string_key': '3.5'
        }
        
        assert get_float(config, 'float_key', 0.0) == 1.5
        assert get_float(config, 'int_key', 0.0) == 2.0
        assert get_float(config, 'string_key', 0.0) == 3.5
        assert get_float(config, 'not_exist', 4.5) == 4.5

    def test_get_list(self):
        """リスト取得のテスト"""
        config = {
            'list_key': ['a', 'b', 'c'],
            'string_key': 'single',
            'empty_list': []
        }
        
        assert get_list(config, 'list_key', []) == ['a', 'b', 'c']
        assert get_list(config, 'string_key', []) == ['single']
        assert get_list(config, 'empty_list', ['default']) == []
        assert get_list(config, 'not_exist', ['default']) == ['default']
