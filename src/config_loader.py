"""
設定ファイルを読み込むモジュール
"""
import logging
import sys
from typing import Dict, Any, Optional

from src.utils.logger import setup_logger
from src.utils.toml_utils import load_toml


class ConfigLoader:
    """設定ファイルを読み込むクラス"""

    def __init__(self, config_file: str = "resources/config.toml",
                 url_config: Optional[str] = None,
                 user_config: Optional[str] = None,
                 scenario_config: Optional[str] = None):
        """
        コンストラクタ

        Args:
            config_file: メイン設定ファイルのパス
            url_config: URL設定ファイルのパス（Noneの場合はメイン設定ファイルから読み込む）
            user_config: ユーザー設定ファイルのパス（Noneの場合はメイン設定ファイルから読み込む）
            scenario_config: シナリオファイルのパス（Noneの場合はメイン設定ファイルから読み込む）
        """
        # 設定ファイルの読み込み
        self.config = self._load_toml(config_file)
        
        # 設定ファイルが読み込めなかった場合は空の辞書を使用
        if self.config is None:
            self.config = {}
            
        # 型変換ユーティリティをインポート
        from src.utils.toml_utils import get_bool, get_list
            
        # デバッグモードの確認
        debug_mode = get_bool(self.config, 'debug_mode', False)
        log_level = logging.DEBUG if debug_mode else logging.INFO
        
        # デバッグモードの状態をログに出力
        print(f"Config debug_mode: {debug_mode}", file=sys.stderr)
        
        self.logger = setup_logger("ConfigLoader", level=log_level)
        self.config_file = config_file
        self.url_config_path = url_config
        self.user_config_path = user_config
        self.scenario_config_path = scenario_config

        # スクリーンショットタイミングの設定を確認
        self.logger.debug(f"設定ファイルから読み込まれたスクリーンショットタイミング: {get_list(self.config, 'screenshot_timing', ['on_error'])}")

        # URL設定ファイルのパスを取得
        if self.url_config_path is None:
            self.url_config_path = self.config.get('url_config', 'resources/url/default.toml')

        # ユーザー設定ファイルのパスを取得
        if self.user_config_path is None:
            self.user_config_path = self.config.get('user_config', 'resources/user/default.toml')

        # シナリオファイルのパスを取得
        if self.scenario_config_path is None:
            self.scenario_config_path = self.config.get('scenario_config', 'resources/scenario/default.csv')

    def _load_toml(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        TOMLファイルを読み込む

        Args:
            file_path: TOMLファイルのパス

        Returns:
            読み込んだ設定（失敗した場合はNone）
        """
        result = load_toml(file_path)
        if result is None:
            print(f"TOMLファイルの読み込みに失敗しました: {file_path}", file=sys.stderr)
            return None
            
        # デバッグ出力
        if 'test_mode' in result:
            print(f"設定ファイルから読み込まれたtest_mode: {result['test_mode']} (型: {type(result['test_mode']).__name__})", file=sys.stderr)
            
        return result

    def load_url_config(self) -> Dict[str, Any]:
        """
        URL設定ファイルを読み込む

        Returns:
            url_config: URL設定の辞書
        """
        # 拡張子の追加
        if not self.url_config_path.endswith('.toml'):
            self.url_config_path += '.toml'

        url_config = self._load_toml(self.url_config_path)
        if url_config is None:
            self.logger.error(f"URL設定ファイルの読み込みに失敗しました: {self.url_config_path}")
            return {"url": ""}

        # 'base_url'または'url'キーを確認
        base_url = url_config.get('base_url', url_config.get('url', ''))
        self.logger.info(f"URL設定ファイル: {self.url_config_path}")
        self.logger.info(f"読み込まれたURL: {base_url}")
        
        # 辞書を返す（'url'キーを含む）
        return {"url": base_url}

    def load_user_config(self) -> list:
        """
        ユーザー設定ファイルを読み込む

        Returns:
            users: ユーザー情報のリスト
        """
        # 拡張子の追加
        if not self.user_config_path.endswith('.toml'):
            self.user_config_path += '.toml'

        user_config = self._load_toml(self.user_config_path)
        if user_config is None:
            self.logger.error(f"ユーザー設定ファイルの読み込みに失敗しました: {self.user_config_path}")
            return []

        users = user_config.get('users', [])
        self.logger.info(f"ユーザー設定ファイル: {self.user_config_path}")
        self.logger.info(f"読み込まれたユーザー数: {len(users)}")
        return users

    def load_scenario_config(self) -> str:
        """
        シナリオファイルのパスを取得する

        Returns:
            scenario_file: シナリオファイルのパス
        """
        # CSVファイルの場合は拡張子を追加しない
        if not self.scenario_config_path.endswith('.csv'):
            self.scenario_config_path += '.csv'

        return self.scenario_config_path
        
    def get_excel_report_config(self) -> Dict[str, Any]:
        """
        Excelレポート設定を取得する

        Returns:
            excel_report_config: Excelレポート設定の辞書
        """
        # デフォルト値
        default_config = {
            "screenshot_title_cell_color": "#ffebcd"  # デフォルトの背景色
        }
        
        # 設定ファイルから値を取得
        screenshot_title_cell_color = self.config.get('screenshot_title_cell_color', default_config["screenshot_title_cell_color"])
        
        return {
            "screenshot_title_cell_color": screenshot_title_cell_color
        }