"""
Excelレポート生成のテスト
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from src.utils.excel_report import generate_excel_report

class TestExcelReport:
    """Excelレポート生成関数のテスト"""

    def test_generate_excel_report(self, temp_dir):
        """Excelレポート生成のテスト"""
        # openpyxlのモック
        with patch('src.utils.excel_report.Workbook') as mock_workbook_class, \
             patch('src.utils.excel_report.load_workbook') as mock_load_workbook, \
             patch('src.utils.excel_report.Image') as mock_image_class, \
             patch('src.utils.excel_report.os.path.exists', return_value=True):
            
            # ワークブックのモック
            mock_workbook = MagicMock()
            mock_workbook_class.return_value = mock_workbook
            mock_load_workbook.return_value = mock_workbook
            
            # シートのモック
            mock_sheet = MagicMock()
            mock_workbook.create_sheet.return_value = mock_sheet
            mock_workbook.active = mock_sheet
            
            # テストデータ
            test_results = {
                'sessions': [
                    {
                        'user': {'app_username': 'test_user1'},
                        'success': True,
                        'actions': [
                            {
                                '操作ID': '1',
                                '操作タイプ': 'URL移動',
                                '対象要素': '/login',
                                '説明': 'ログインページに移動',
                                'success': True,
                                'error': None,
                                'screenshot': 'screenshot1.png'
                            }
                        ]
                    }
                ],
                'total_sessions': 1,
                'successful_sessions': 1,
                'failed_sessions': 0
            }
            
            # 設定
            config = {
                'report_title': 'テスト結果',
                'company_name': 'テスト会社',
                'project_name': 'テストプロジェクト',
                'zoom_scale': 50,
                'include_timestamp': True,
                'timestamp_format': '%Y-%m-%d %H:%M:%S',
                'header_bg_color': '#4472C4',
                'header_font_color': '#FFFFFF',
                'alt_row_color': '#E6F0FF',
                'success_color': '#C6EFCE',
                'failure_color': '#FFC7CE',
                'screenshot_title_cell_color': '#ffebcd'
            }
            
            # 出力ファイルパス
            output_file = os.path.join(str(temp_dir), 'test_report.xlsx')
            
            # 関数実行
            result = generate_excel_report(
                test_results,
                config,
                output_file,
                str(temp_dir),
                template_file=None
            )
            
            # 検証
            assert result == output_file
            mock_workbook.save.assert_called_once_with(output_file)
