"""
複数のブラウザセッションを同時に実行するモジュール
"""
import concurrent.futures
import logging
import os
import traceback
from datetime import datetime
from typing import Dict, Any

from src.browser_session import BrowserSession
from src.config_loader import ConfigLoader
from src.scenario_loader import ScenarioLoader
from src.utils.excel_report import generate_excel_report
from src.utils.file_utils import create_output_directory, save_json
from src.utils.logger import setup_logger


class ConcurrentTester:
    """複数のブラウザセッションを同時に実行するクラス"""
    
    def __init__(self, config_loader: ConfigLoader, test_mode: bool = None, 
                 slow_mode: bool = None, action_delay: float = None):
        """
        コンストラクタ
        
        Args:
            config_loader: 設定ローダーのインスタンス
            test_mode: テストモードフラグ（Noneの場合は設定ファイルから読み込む）
            slow_mode: スロー実行モードフラグ（Noneの場合は設定ファイルから読み込む）
            action_delay: アクション間の遅延時間（Noneの場合は設定ファイルから読み込む）
        """
        # 設定ローダーの初期化
        self.config_loader = config_loader
        
        # シナリオファイルの読み込み
        self.scenario_file = self.config_loader.load_scenario_config()
        self.scenario_loader = ScenarioLoader(self.scenario_file)
        
        # 型変換ユーティリティをインポート
        from src.utils.toml_utils import get_bool, get_float
        
        # ロガーの設定
        self.logger = setup_logger("ConcurrentTester")
        
        # 設定値の取得（コマンドライン引数とconfig.tomlのどちらかがtrueならtrueとする）
        # test_modeがNoneでない場合はコマンドライン引数から取得した値を使用
        # Noneの場合は設定ファイルから読み込む
        config_test_mode = get_bool(self.config_loader.config, 'test_mode', False)
        
        # コマンドライン引数のtest_modeがTrueまたは設定ファイルのtest_modeがTrueならTrue
        if test_mode is True or config_test_mode is True:
            self.test_mode = True
        else:
            self.test_mode = False
            
        # デバッグ出力
        self.logger.debug(f"コマンドライン引数のtest_mode: {test_mode}")
        self.logger.debug(f"設定ファイルのtest_mode: {config_test_mode}")
        self.logger.debug(f"最終的なtest_mode: {self.test_mode}")
        
        # スローモードの設定（コマンドライン引数とconfig.tomlのどちらかがtrueならtrueとする）
        config_slow_mode = get_bool(self.config_loader.config, 'slow_mode', False)
        if slow_mode is True or config_slow_mode is True:
            self.slow_mode = True
        else:
            self.slow_mode = False
            
        # デバッグ出力
        self.logger.debug(f"コマンドライン引数のslow_mode: {slow_mode}")
        self.logger.debug(f"設定ファイルのslow_mode: {config_slow_mode}")
        self.logger.debug(f"最終的なslow_mode: {self.slow_mode}")
        
        # アクション遅延時間の設定（コマンドライン引数が優先）
        config_action_delay = get_float(self.config_loader.config, 'action_delay', 0.5)
        self.action_delay = action_delay if action_delay is not None else config_action_delay
        
        # デバッグ出力
        self.logger.debug(f"コマンドライン引数のaction_delay: {action_delay}")
        self.logger.debug(f"設定ファイルのaction_delay: {config_action_delay}")
        self.logger.debug(f"最終的なaction_delay: {self.action_delay}")
        
        # デバッグモードの確認
        debug_mode = get_bool(self.config_loader.config, 'debug_mode', False)
        log_level = logging.DEBUG if debug_mode else logging.INFO
        
        # ロガーと出力ディレクトリの設定
        self.logger = setup_logger("ConcurrentTester", level=log_level)
        
        try:
            # 出力ディレクトリの作成
            self.output_dir = create_output_directory()
            
            # ファイルハンドラの追加
            result_dir = os.path.join(self.output_dir, "result")
            os.makedirs(result_dir, exist_ok=True)
            log_file = os.path.join(result_dir, "concurrent_test.log")
            self.logger = setup_logger("ConcurrentTester", log_file, level=logging.DEBUG)
            
            # 出力ディレクトリの確認
            self.logger.info(f"出力ディレクトリ: {self.output_dir}")
            self.logger.info(f"結果ディレクトリ: {result_dir}")
            
            # ディレクトリの存在確認
            if not os.path.exists(result_dir):
                self.logger.error(f"結果ディレクトリが存在しません: {result_dir}")
                os.makedirs(result_dir, exist_ok=True)
                self.logger.info(f"結果ディレクトリを再作成しました: {result_dir}")
        except Exception as e:
            self.logger.error(f"出力ディレクトリの設定中にエラーが発生しました: {str(e)}")
            self.logger.error(f"スタックトレース: {traceback.format_exc()}")
            # 代替ディレクトリを使用
            self.output_dir = os.path.join(os.getcwd(), "output_fallback")
            os.makedirs(self.output_dir, exist_ok=True)
            os.makedirs(os.path.join(self.output_dir, "result"), exist_ok=True)
            os.makedirs(os.path.join(self.output_dir, "screenshot"), exist_ok=True)
            self.logger.info(f"代替出力ディレクトリを使用します: {self.output_dir}")
        
        # URL設定の読み込み
        try:
            url_config = self.config_loader.load_url_config()
            base_url = url_config.get('url', '')
            
            # 設定ファイルのパスを出力
            self.logger.info(f"URL設定ファイル: {self.config_loader.url_config_path or self.config_loader.config.get('url_config', 'resources/url/default.toml')}")
            self.logger.info(f"読み込まれたURL: {base_url}")
            
            if not isinstance(base_url, str):
                self.logger.warning(f"URLが文字列ではありません: {base_url}, 空文字列を使用します")
                base_url = ''
            elif not base_url:
                self.logger.warning("URLが空です")
            elif not base_url.startswith(('http://', 'https://')):
                self.logger.warning(f"URLにプロトコルが含まれていません: {base_url}")
                base_url = 'https://' + base_url
                self.logger.info(f"プロトコルを追加しました: {base_url}")
        except Exception as e:
            self.logger.error(f"URL設定の読み込みに失敗しました: {str(e)}")
            self.logger.error(f"スタックトレース: {traceback.format_exc()}")
            base_url = ''
        
        # 型変換ユーティリティをインポート
        from src.utils.toml_utils import get_int, get_list, get_str
        
        # 設定ファイルの内容をコピー
        self.config = {
            'url': base_url,
            'test_mode': self.test_mode,  # 既に正しく変換された値を使用
            'slow_mode': self.slow_mode,  # 既に正しく変換された値を使用
            'action_delay': self.action_delay,  # 既に正しく変換された値を使用
            'timeout': get_int(self.config_loader.config, 'timeout', 30),
            'screenshot_timing': get_list(self.config_loader.config, 'screenshot_timing', ['on_error']),
            'browser': get_str(self.config_loader.config, 'browser', 'chrome')  # ブラウザタイプを追加
        }
        
        # ブラウザタイプのデバッグ出力
        self.logger.debug(f"設定ファイルのブラウザタイプ: {self.config['browser']}")
        
        # デバッグ出力
        self.logger.debug(f"最終的な設定: test_mode={self.config['test_mode']}, slow_mode={self.config['slow_mode']}, browser={self.config['browser']}")
        
    def _run_session(self, user: Dict[str, str], session_id: int) -> Dict[str, Any]:
        """
        1つのセッションを実行する
        
        Args:
            user: ユーザー情報
            session_id: セッションID
            
        Returns:
            セッションの実行結果
        """
        # セッション用のログファイルのみを作成し、ディレクトリは作成しない
        result_dir = os.path.join(self.output_dir, "result")
        os.makedirs(result_dir, exist_ok=True)
        
        self.logger.info(f"セッション{session_id}開始: {user.get('app_username', '')}")
        
        start_time = datetime.now()
        
        # 設定のコピーを作成し、テストモードを明示的に設定
        session_config = self.config.copy()
        
        # テストモードを確実に設定
        session_config['test_mode'] = self.test_mode
        
        session = BrowserSession(user, session_config, session_id, self.output_dir)
        
        result = {
            "session_id": session_id,
            "user_id": user.get('app_username', ''),
            "success": False,
            "start_time": start_time.isoformat(),
            "end_time": None,
            "duration": 0,
            "screenshots": [],
            "actions": [],
            "errors": []
        }
        
        try:
            # ブラウザの初期化
            if not session.initialize():
                result["errors"].append("ブラウザの初期化に失敗しました")
                return result
            
            # シナリオの実行
            actions = self.scenario_loader.get_actions()
            for action in actions:
                action_id = action.get('操作ID', '')
                description = action.get('説明', action.get('操作タイプ', ''))
                
                success, error = session.perform_action(action)
                
                action_result = {
                    "action_id": action_id,
                    "description": description,
                    "success": success,
                    "error": error,
                    # アクション情報をそのまま保持
                    **action
                }
                
                result["actions"].append(action_result)
                
                if not success:
                    result["errors"].append(f"アクション {action_id} の実行に失敗しました: {error}")
                    break
            
            # スクリーンショットの収集
            screenshots = []
            screenshot_dir = os.path.join(self.output_dir, "screenshot")
            
            # スクリーンショットを検索
            if os.path.exists(screenshot_dir):
                # セッションディレクトリを検索
                session_dir = os.path.join(screenshot_dir, f"session_{session_id}")
                if os.path.exists(session_dir):
                    # セッションディレクトリ内のすべてのスクリーンショットを再帰的に検索
                    for root, _, files in os.walk(session_dir):
                        for file in files:
                            if file.endswith('.png'):
                                # 相対パスを保存
                                rel_path = os.path.relpath(os.path.join(root, file), self.output_dir)
                                screenshots.append(rel_path)
                else:
                    self.logger.warning(f"セッションディレクトリが見つかりませんでした: {session_dir}")
            else:
                self.logger.warning(f"スクリーンショットディレクトリが見つかりませんでした: {screenshot_dir}")
            
            result["screenshots"] = screenshots
            result["success"] = len(result["errors"]) == 0
            
        except Exception as e:
            result["errors"].append(f"セッション実行中にエラーが発生しました: {str(e)}")
            # 例外発生時にもスクリーンショットを撮影
            try:
                if session and session.driver:
                    error_screenshot = session.take_screenshot(f"exception", True)
                    if error_screenshot:
                        if "screenshots" not in result:
                            result["screenshots"] = []
                        rel_path = os.path.relpath(error_screenshot, self.output_dir)
                        result["screenshots"].append(rel_path)
                        self.logger.info(f"例外発生時のスクリーンショットを撮影しました: {rel_path}")
            except Exception as screenshot_error:
                self.logger.error(f"例外発生時のスクリーンショット撮影に失敗しました: {str(screenshot_error)}")
            
        finally:
            # ブラウザを閉じる
            if session:
                session.close()
                
            # 終了時間と実行時間を記録
            end_time = datetime.now()
            result["end_time"] = end_time.isoformat()
            result["duration"] = (end_time - start_time).total_seconds()
            
            # 成功/失敗のログ出力
            status = "成功" if result["success"] else "失敗"
            self.logger.info(f"セッション{session_id}終了: {result.get('user_id', '')} (結果: {status})")
            
        return result
        
    def run(self) -> Dict[str, Any]:
        """
        テストを実行する
        
        Returns:
            テスト結果
        """
        # ユーザー設定の読み込み
        users = self.config_loader.load_user_config()
        
        # ユーザー数の確認
        if not users:
            self.logger.error("ユーザーが設定されていません")
            return {"success": False, "error": "ユーザーが設定されていません"}
            
        # 開始時間の記録
        start_time = datetime.now()
        self.logger.info(f"テスト開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"URL: {self.config['url']}")
        self.logger.info(f"シナリオファイル: {self.scenario_file}")
        self.logger.info(f"ユーザー数: {len(users)}")
        
        # 結果の初期化
        results = {
            "success": True,
            "start_time": start_time.isoformat(),
            "end_time": None,
            "duration": 0,
            "total_sessions": len(users),
            "successful_sessions": 0,
            "failed_sessions": 0,
            "sessions": []
        }
        
        # アプリケーションユーザー情報を追加
        app_users = [user.get('app_username', '') for user in users]
        results["app_users"] = app_users
        
        # 同時実行数の設定
        max_workers = min(len(users), self.config_loader.config.get('max_concurrent_sessions', 5))
        
        # セッションの実行
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # セッションの実行
            future_to_session = {
                executor.submit(self._run_session, user, i+1): (i+1, user)
                for i, user in enumerate(users)
            }
            
            # 結果の収集
            for future in concurrent.futures.as_completed(future_to_session):
                session_id, user = future_to_session[future]
                try:
                    session_result = future.result()
                    results["sessions"].append(session_result)
                    
                    # 成功/失敗のカウント
                    if session_result["success"]:
                        results["successful_sessions"] += 1
                    else:
                        results["failed_sessions"] += 1
                        results["success"] = False
                except Exception as e:
                    self.logger.error(f"セッション{session_id}の実行中にエラーが発生しました: {str(e)}")
                    self.logger.error(f"スタックトレース: {traceback.format_exc()}")
                    
                    # エラー情報を追加
                    error_result = {
                        "session_id": session_id,
                        "user_id": user.get('app_username', ''),
                        "success": False,
                        "start_time": start_time.isoformat(),
                        "end_time": datetime.now().isoformat(),
                        "duration": 0,
                        "screenshots": [],
                        "actions": [],
                        "errors": [f"セッション実行中に例外が発生しました: {str(e)}"]
                    }
                    results["sessions"].append(error_result)
                    results["failed_sessions"] += 1
                    results["success"] = False
        
        # 終了時間と実行時間を記録
        end_time = datetime.now()
        results["end_time"] = end_time.isoformat()
        results["duration"] = (end_time - start_time).total_seconds()
        
        # 結果をJSONファイルに保存
        try:
            result_dir = os.path.join(self.output_dir, "result")
            os.makedirs(result_dir, exist_ok=True)
            result_file = os.path.join(result_dir, "test_results.json")
            save_json(results, result_file)
            self.logger.info(f"テスト結果保存: {result_file}")
            
            # ファイルが実際に作成されたか確認
            if os.path.exists(result_file):
                self.logger.info(f"テスト結果ファイルが正常に作成されました: {result_file}")
            else:
                self.logger.error(f"テスト結果ファイルが作成されませんでした: {result_file}")
                # 代替ファイルパスを使用
                alt_result_file = os.path.join(os.getcwd(), "output_fallback", "test_results.json")
                os.makedirs(os.path.dirname(alt_result_file), exist_ok=True)
                save_json(results, alt_result_file)
                self.logger.info(f"代替ファイルパスに保存しました: {alt_result_file}")
                result_file = alt_result_file
        except Exception as e:
            self.logger.error(f"テスト結果の保存中にエラーが発生しました: {str(e)}")
            self.logger.error(f"スタックトレース: {traceback.format_exc()}")
            # 代替ファイルパスを使用
            alt_result_file = os.path.join(os.getcwd(), "output_fallback", "test_results.json")
            try:
                os.makedirs(os.path.dirname(alt_result_file), exist_ok=True)
                save_json(results, alt_result_file)
                self.logger.info(f"代替ファイルパスに保存しました: {alt_result_file}")
                result_file = alt_result_file
            except Exception as e2:
                self.logger.error(f"代替ファイルパスへの保存にも失敗しました: {str(e2)}")
                result_file = "保存に失敗しました"
        
        # 結果にファイルパスを追加
        results["output_file"] = result_file
        
        # Excelレポートの生成
        try:
            # 設定値を明示的に出力
            self.logger.info("=== Excel Report Config ===")
            self.logger.info(f"report_title: {self.config_loader.config.get('report_title', 'デフォルトタイトル')}")
            self.logger.info(f"company_name: {self.config_loader.config.get('company_name', '')}")
            self.logger.info(f"project_name: {self.config_loader.config.get('project_name', '')}")
            self.logger.info(f"include_timestamp: {self.config_loader.config.get('include_timestamp', True)}")
            self.logger.info("=========================")
            
            # 設定値を直接渡す
            excel_config = {
                "report_title": self.config_loader.config.get("report_title", "テスト実行結果報告書"),
                "company_name": self.config_loader.config.get("company_name", ""),
                "project_name": self.config_loader.config.get("project_name", ""),
                "report_logo": self.config_loader.config.get("report_logo", ""),
                "zoom_scale": self.config_loader.config.get("zoom_scale", 50),
                "include_timestamp": self.config_loader.config.get("include_timestamp", True),
                "timestamp_format": self.config_loader.config.get("timestamp_format", "%Y-%m-%d %H:%M:%S"),
                "header_bg_color": self.config_loader.config.get("header_bg_color", "#4472C4"),
                "header_font_color": self.config_loader.config.get("header_font_color", "#FFFFFF"),
                "alt_row_color": self.config_loader.config.get("alt_row_color", "#E6F0FF"),
                "success_color": self.config_loader.config.get("success_color", "#C6EFCE"),
                "failure_color": self.config_loader.config.get("failure_color", "#FFC7CE"),
                "screenshot_title_cell_color": self.config_loader.config.get("screenshot_title_cell_color", "#ffebcd")
            }
            
            excel_report_file = generate_excel_report(results, self.output_dir, excel_config)
            if os.path.exists(excel_report_file):
                self.logger.info(f"Excelレポートが正常に生成されました: {excel_report_file}")
                # Excelレポートのパスも結果に追加
                results["excel_report"] = excel_report_file
            else:
                self.logger.error(f"Excelレポートが生成されませんでした: {excel_report_file}")
        except Exception as e:
            self.logger.error(f"Excelレポートの生成に失敗しました: {str(e)}")
            self.logger.error(f"スタックトレース: {traceback.format_exc()}")
            
            # 代替ファイルパスでの再試行
            try:
                alt_output_dir = os.path.join(os.getcwd(), "output_fallback")
                excel_report_file = generate_excel_report(results, alt_output_dir, excel_config)
                self.logger.info(f"代替パスでExcelレポートを生成しました: {excel_report_file}")
                results["excel_report"] = excel_report_file
            except Exception as e2:
                self.logger.error(f"代替パスでのExcelレポート生成にも失敗しました: {str(e2)}")
                results["excel_report"] = "生成に失敗しました"
        
        # 終了ログ
        self.logger.info(f"テスト終了: {end_time.strftime('%Y-%m-%d %H:%M:%S')} (所要時間: {results['duration']:.2f}秒)")
        
        return results
