import csv
from typing import List, Dict

from src.utils.constants import ExcelOutput


class ScenarioLoader:
    """シナリオファイルを読み込むクラス"""
    
    def __init__(self, scenario_file: str):
        """
        コンストラクタ
        
        Args:
            scenario_file: シナリオファイルのパス
        """
        self.scenario_file = scenario_file
        self.actions = self._load_scenario()
    
    def _load_scenario(self) -> List[Dict[str, str]]:
        """
        シナリオファイルを読み込む
        
        Returns:
            アクションのリスト
        
        Raises:
            FileNotFoundError: シナリオファイルが見つからない場合
            csv.Error: CSVの解析に失敗した場合
        """
        try:
            with open(self.scenario_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                actions = list(reader)
                
                # Excel出力フラグの処理
                for action in actions:
                    if 'Excel出力' in action:
                        # 'yes'または'y'の場合はTrue、それ以外はFalse
                        excel_output = str(action.get('Excel出力', '')).lower()
                        action['Excel出力'] = excel_output in ExcelOutput.YES_VALUES
                    else:
                        action['Excel出力'] = False
                
                return actions
        except FileNotFoundError:
            raise FileNotFoundError(f"シナリオファイル '{self.scenario_file}' が見つかりません")
        except csv.Error as e:
            raise csv.Error(f"シナリオファイルの解析に失敗しました: {str(e)}")
    
    def get_actions(self) -> List[Dict[str, str]]:
        """
        読み込んだアクションのリストを取得する
        
        Returns:
            アクションのリスト
        """
        return self.actions
