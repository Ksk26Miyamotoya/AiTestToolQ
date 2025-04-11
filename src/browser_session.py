"""
ブラウザセッション管理モジュール
"""
import logging
import os
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from selenium.common.exceptions import WebDriverException

from src.action_handler import ActionHandler
from src.utils.browser_utils import build_url_with_auth
from src.utils.logger import setup_logger

# PILをインポート
try:
    from PIL import Image
except ImportError:
    Image = None


class BrowserSession:
    """ブラウザセッションを管理するクラス"""

    def __init__(self, user: Dict[str, str], config: Dict[str, Any], session_id: int, output_dir: str):
        """
        コンストラクタ
        
        Args:
            user: ユーザー情報
            config: 設定情報
            session_id: セッションID
            output_dir: 出力ディレクトリ
        """
        self.user = user
        self.config = config
        self.session_id = session_id
        self.output_dir = output_dir
        self.driver = None
        self.base_url = config.get('url', '')
        self.logger = self._setup_logger()
        
        # 設定ファイルからスクリーンショットタイミングを取得
        # デフォルトは 'on_error' のみ
        self.screenshot_timing = config.get('screenshot_timing', ['on_error'])
        
        # スクリーンショットタイミングが文字列の場合はリストに変換
        if isinstance(self.screenshot_timing, str):
            self.screenshot_timing = [self.screenshot_timing]
            
        self.logger.debug(f"スクリーンショットタイミング設定: {self.screenshot_timing}")
        
        self.current_action_id = None
        self.current_action = None  # 現在実行中のアクション情報
        
    def _setup_logger(self):
        """
        ロガーの設定
        
        Returns:
            設定済みのロガー
        """
        try:
            # セッションログは result ディレクトリに保存
            result_dir = os.path.join(self.output_dir, "result")
            os.makedirs(result_dir, exist_ok=True)
            log_file = os.path.join(result_dir, f"session_{self.session_id}.log")
            
            # ディレクトリの書き込み権限を確認
            if not os.access(result_dir, os.W_OK):
                print(f"警告: 結果ディレクトリに書き込み権限がありません: {result_dir}")
                # 代替ディレクトリを使用
                alt_dir = os.path.join(os.getcwd(), "output_fallback", "result")
                os.makedirs(alt_dir, exist_ok=True)
                log_file = os.path.join(alt_dir, f"session_{self.session_id}.log")
                print(f"代替ログファイルを使用します: {log_file}")
            
            # デバッグモードの確認
            debug_mode = self.config.get('debug_mode', False)
            log_level = logging.DEBUG if debug_mode else logging.INFO
            
            logger = setup_logger(f"Session{self.session_id}", log_file, level=log_level)
            
            # テストモードの確認（デバッグ用）
            test_mode = self.config.get('test_mode', False)
            logger.debug(f"セッション{self.session_id}のテストモード: {test_mode}")
            
            return logger
        except Exception as e:
            print(f"セッションロガーの設定中にエラーが発生しました: {str(e)}")
            # 代替ロガーを返す（ファイル出力なし）
            return setup_logger(f"Session{self.session_id}", level=logging.INFO)

    def get_user_data(self, key: str, default: str = "") -> str:
        """
        ユーザー情報から指定したキーの値を取得する
        
        Args:
            key: 取得するキー
            default: キーが存在しない場合のデフォルト値
            
        Returns:
            キーに対応する値
        """
        return self.user.get(key, default)

    def initialize(self) -> bool:
        """
        ブラウザを初期化する
        
        Returns:
            初期化に成功した場合True
        """
        try:
            from src.utils.toml_utils import get_str, get_bool
            
            # 設定からブラウザタイプを取得
            browser_type = get_str(self.config, 'browser', 'chrome').lower()
            self.logger.debug(f"設定ファイルから読み込まれたブラウザタイプ: {browser_type}")
            
            # ブラウザタイプの検証
            valid_browsers = ['chrome', 'firefox', 'edge', 'safari']
            if browser_type not in valid_browsers:
                self.logger.warning(f"無効なブラウザタイプ: {browser_type}, 'chrome'を使用します")
                browser_type = 'chrome'
            
            # 設定からテストモードを取得
            test_mode = self.config.get('test_mode', False)
            if not isinstance(test_mode, bool):
                test_mode = bool(test_mode)
                
            self.logger.info(f"テストモード: {test_mode}")
            
            # スクリーンショットタイミングの確認
            self.logger.debug(f"スクリーンショットタイミング設定: {self.screenshot_timing}")
            self.logger.debug(f"デバッグモード: {get_bool(self.config, 'debug_mode', False)}")
            
            # テストモードがTrueの場合はヘッドレスモードをオフにする（ブラウザを表示する）
            headless = not test_mode
            self.logger.debug(f"テストモード: {test_mode}, ヘッドレスモード: {headless}")
            
            # ブラウザドライバーの作成
            from src.utils.browser_utils import create_browser
            self.driver = create_browser(browser_type, headless)
            if not self.driver:
                self.logger.error("ブラウザドライバーの作成に失敗しました")
                return False
            
            # 使用したブラウザタイプをログに出力
            self.logger.info(f"ブラウザ初期化: {browser_type}")
            
            # ウィンドウサイズを1024x768に設定
            self.driver.set_window_size(1024, 768)
            
            # 実際のウィンドウサイズを確認
            window_size = self.driver.get_window_size()
            self.logger.info(f"ウィンドウサイズ: {window_size['width']}x{window_size['height']}")
            
            # スクリーンショット機能のテスト
            try:
                self.logger.debug("スクリーンショット機能のテスト実行")
                # テストスクリーンショットはresultディレクトリに保存せず、一時的に撮影するだけ
                result = self.driver.save_screenshot("/tmp/test_screenshot.png")
                self.logger.debug(f"テストスクリーンショット結果: {result}")
                if os.path.exists("/tmp/test_screenshot.png"):
                    self.logger.debug(f"テストスクリーンショットファイルが正常に作成されました")
                else:
                    self.logger.error(f"テストスクリーンショットファイルが作成されませんでした")
            except Exception as e:
                self.logger.error(f"テストスクリーンショットの撮影に失敗しました: {str(e)}")
                self.logger.error(f"スタックトレース: {traceback.format_exc()}")
            
            self.driver.set_page_load_timeout(self.config.get('timeout', 30))
            self.logger.info(f"ブラウザ初期化: {browser_type}")
            return True
        except WebDriverException as e:
            self.logger.error(f"ブラウザの初期化に失敗しました: {str(e)}")
            self.logger.error(f"スタックトレース: {traceback.format_exc()}")
            return False

    def navigate_to_url(self, path: str) -> bool:
        """
        Basic認証付きURLに移動する
        
        Args:
            path: 移動先のパス
            
        Returns:
            移動に成功した場合True
        """
        if not self.driver:
            self.logger.error("ドライバーが初期化されていません")
            return False
            
        # pathが文字列でない場合はエラーログを出力し、空文字列を使用
        if not isinstance(path, str):
            self.logger.error(f"パスが文字列ではありません: {path}, 空文字列を使用します")
            path = ""
            
        try:
            # Basic認証情報をURLに埋め込む
            basic_auth_username = self.user.get('basic_auth_username', '')
            basic_auth_password = self.user.get('basic_auth_password', '')
            
            # URLの構築
            url = build_url_with_auth(self.base_url, path, basic_auth_username, basic_auth_password)
            
            # URLが無効な場合は処理を中止
            if not url:
                self.logger.error(f"無効なURL: {url}")
                return False
                
            self.logger.info(f"URLに移動: {url}")
            self.driver.get(url)
            return True
        except WebDriverException as e:
            self.logger.error(f"URLへの移動に失敗しました: {str(e)}")
            return False

    def perform_action(self, action: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """
        アクションを実行する
        
        Args:
            action: アクション情報
            
        Returns:
            (成功したかどうか, エラーメッセージ)
        """
        # アクションの説明を取得
        self.current_action_id = action.get('操作ID', 'unknown')
        self.current_action = action  # 現在のアクションを保存
        
        # Excel出力フラグの取得
        excel_output_value = action.get('Excel出力', False)
        if isinstance(excel_output_value, bool):
            excel_output = excel_output_value
        elif isinstance(excel_output_value, str):
            excel_output = excel_output_value.lower() in ['yes', 'true', '1', 'y']
        else:
            self.logger.warning(f"Excel出力の値が不正な型です: {type(excel_output_value)}, 'no'を使用します")
            excel_output = False
            
        # デバッグ用にExcel出力フラグを表示
        self.logger.debug(f"アクション {self.current_action_id} のExcel出力フラグ: {excel_output}")
        
        # スクリーンショットタイミングの確認
        self.logger.debug(f"設定されているスクリーンショットタイミング: {self.screenshot_timing}")
        
        # アクション実行前のスクリーンショット
        if 'before_action' in self.screenshot_timing:
            self.logger.debug(f"アクション実行前のスクリーンショットを撮影します: {self.current_action_id}")
            self.take_screenshot(f"before_{self.current_action_id}_session_{self.session_id}", excel_output)
        
        # スローモードとアクション遅延時間を取得
        slow_mode = self.config.get('slow_mode', False)
        action_delay = self.config.get('action_delay', 0.5)
        timeout = self.config.get('timeout', 30)  # タイムアウト値を設定から取得
        retry_count = self.config.get('retry_count', 3)  # リトライ回数を設定から取得
        
        # アクションハンドラを使用してアクションを実行
        handler = ActionHandler(
            self.driver, 
            self.user, 
            self.config, 
            self.logger,
            slow_mode=slow_mode,
            action_delay=action_delay
        )
        success, error = handler.handle_action(action)
        
        # アクション実行後のスクリーンショット
        if not success and 'on_error' in self.screenshot_timing:
            # エラー時のスクリーンショット
            self.logger.debug(f"エラー発生時のスクリーンショットを撮影します: {self.current_action_id}")
            self.take_screenshot(f"error_{self.current_action_id}_session_{self.session_id}", excel_output)
        elif 'after_action' in self.screenshot_timing:
            # 成功時または on_error が設定されていない失敗時のスクリーンショット
            self.logger.debug(f"アクション実行後のスクリーンショットを撮影します: {self.current_action_id}")
            self.take_screenshot(f"after_{self.current_action_id}_session_{self.session_id}", excel_output)
        
        return success, error

    def take_screenshot(self, prefix: str, excel_output: bool = False) -> Optional[str]:
        """
        スクリーンショットを撮影する
        
        Args:
            prefix: ファイル名のプレフィックス
            excel_output: Excelに出力するかどうか
            
        Returns:
            スクリーンショットのファイルパス（失敗した場合はNone）
        """
        if not self.driver:
            self.logger.error("ドライバーが初期化されていません")
            return None
            
        try:
            # デバッグ情報を追加
            self.logger.debug(f"スクリーンショット撮影開始: {prefix}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.png"
            
            # スクリーンショットディレクトリのパスを構築
            screenshot_dir = os.path.join(self.output_dir, "screenshot")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # ディレクトリの書き込み権限を確認
            if not os.access(screenshot_dir, os.W_OK):
                self.logger.error(f"スクリーンショットディレクトリに書き込み権限がありません: {screenshot_dir}")
                self.logger.error("スクリーンショットの撮影をスキップします")
                return None
            
            # セッションIDごとのディレクトリを作成
            session_dir = os.path.join(screenshot_dir, f"session_{self.session_id}")
            os.makedirs(session_dir, exist_ok=True)
            
            # 操作IDごとのディレクトリを作成（操作IDがある場合）
            if self.current_action_id:
                action_dir = os.path.join(session_dir, f"action_{self.current_action_id}")
                os.makedirs(action_dir, exist_ok=True)
                filepath = os.path.join(action_dir, filename)
            else:
                filepath = os.path.join(session_dir, filename)
            
            self.logger.debug(f"スクリーンショットディレクトリ: {os.path.dirname(filepath)}")
            self.logger.debug(f"スクリーンショットパス: {filepath}")
            
            # スクリーンショットを撮影
            try:
                result = self.driver.save_screenshot(filepath)
                self.logger.debug(f"save_screenshot結果: {result}")
            except Exception as screenshot_error:
                self.logger.error(f"スクリーンショット撮影に失敗しました: {str(screenshot_error)}")
                self.logger.error(f"スクリーンショットパス: {filepath}")
                self.logger.error(f"エラータイプ: {type(screenshot_error).__name__}")
                # スタックトレースを出力
                self.logger.error(f"スタックトレース: {traceback.format_exc()}")
                return None
            
            # ファイルが実際に作成されたか確認
            if os.path.exists(filepath):
                self.logger.debug(f"スクリーンショットファイルが正常に作成されました: {filepath}")
                
                # スクリーンショットをリサイズする（1024x768に）
                try:
                    if Image:  # PILがインポートされている場合のみ
                        # 元の画像を読み込む
                        with Image.open(filepath) as img:
                            # 元のサイズを記録
                            original_size = f"{img.width}x{img.height}"
                            # 1024x768にリサイズ
                            img_resized = img.resize((1024, 768), Image.LANCZOS)
                            # 元のファイルを上書き
                            img_resized.save(filepath)
                            self.logger.debug(f"スクリーンショットをリサイズしました: {original_size} -> 1024x768")
                    else:
                        self.logger.warning("PILモジュールがインポートされていないため、スクリーンショットのリサイズをスキップします")
                except Exception as e:
                    self.logger.error(f"スクリーンショットのリサイズに失敗しました: {str(e)}")
            else:
                self.logger.error(f"スクリーンショットファイルが作成されませんでした: {filepath}")
                return None
            
            # Excel出力フラグをファイル名に含める（メタデータとして）
            if excel_output:
                try:
                    # Excel出力用のマーカーファイルを作成
                    marker_path = filepath + ".excel"
                    with open(marker_path, 'w') as f:
                        f.write("Excel output: yes")
                    self.logger.info(f"Excel出力用マーカーファイル作成: {marker_path}")
                except Exception as e:
                    self.logger.error(f"Excel出力用マーカーファイルの作成に失敗しました: {str(e)}")
            
            self.logger.info(f"スクリーンショット撮影: {os.path.basename(filepath)} (Excel出力: {excel_output})")
            return filepath
        except Exception as e:
            self.logger.error(f"スクリーンショットの撮影に失敗しました: {str(e)}")
            self.logger.error(f"スタックトレース: {traceback.format_exc()}")
            return None

    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("ブラウザを閉じました")
            except Exception as e:
                self.logger.error(f"ブラウザを閉じる際にエラーが発生しました: {str(e)}")
            finally:
                self.driver = None
