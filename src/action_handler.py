"""
アクション処理ハンドラモジュール
"""
import time
import re
import logging
from typing import Dict, Any, Tuple, Optional

from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException

from src.utils.browser_utils import find_element, scroll_to_element
from src.utils.constants import OperationType

class ActionHandler:
    """アクション処理を行うクラス"""
    
    def __init__(self, driver: WebDriver, user: Dict[str, str], config: Dict[str, Any], logger: logging.Logger, 
                 slow_mode: bool = False, action_delay: float = 0.5):
        """
        コンストラクタ
        
        Args:
            driver: WebDriverインスタンス
            user: ユーザー情報
            config: 設定情報
            logger: ロガー
            slow_mode: スロー実行モードフラグ
            action_delay: アクション間の遅延時間（秒）
        """
        self.driver = driver
        self.user = user
        self.config = config
        self.logger = logger
        self.timeout = config.get('timeout', 30)
        self.slow_mode = slow_mode
        self.action_delay = action_delay
    
    def handle_action(self, action: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """
        アクションを処理する
        
        Args:
            action: アクション情報
            
        Returns:
            (成功したかどうか, エラーメッセージ)
        """
        # 型チェック
        if not isinstance(action, dict):
            self.logger.error(f"アクションがディクショナリではありません: {action}")
            return False, "アクションの形式が不正です"
        
        # 必須項目のチェック
        operation_id = action.get('操作ID', '')
        operation_type = action.get('操作タイプ', '')
        target_element = action.get('対象要素', '')
        input_value = action.get('入力値', '')
        wait_time = action.get('待機時間', '')
        description = action.get('説明', '')
        
        self.logger.info(f"操作ID: {operation_id}, 操作タイプ: {operation_type}, 説明: {description}")
        
        # 待機時間の処理
        if wait_time:
            try:
                wait_seconds = float(wait_time)
                self.logger.debug(f"{wait_seconds}秒待機します")
                time.sleep(wait_seconds)
            except ValueError:
                self.logger.warning(f"待機時間の値が不正です: {wait_time}")
        
        # 変数の置換処理
        target_element = self._replace_variables(target_element)
        input_value = self._replace_variables(input_value)
        
        # 操作タイプに応じた処理
        try:
            result = None
            error = None
            
            if operation_type == OperationType.URL_MOVE:
                result, error = self._handle_url_move(target_element)  # 対象要素からURLを取得
            elif operation_type == OperationType.TEXT_INPUT:
                result, error = self._handle_text_input(target_element, input_value)
            elif operation_type == OperationType.CLICK:
                result, error = self._handle_click(target_element)
            elif operation_type == OperationType.FORCE_CLICK:
                result, error = self._handle_force_click(target_element)
            elif operation_type == OperationType.JS_CLICK:
                result, error = self._handle_js_click(target_element)
            elif operation_type == OperationType.SELECT:
                result, error = self._handle_select(target_element, input_value)
            elif operation_type == OperationType.WAIT:
                result, error = self._handle_wait(target_element)
            elif operation_type == OperationType.ASSERT:
                result, error = self._handle_assert(target_element, input_value)
            elif operation_type == OperationType.SCRIPT:
                result, error = self._handle_script(input_value)
            else:
                self.logger.error(f"未対応の操作タイプです: {operation_type}")
                return False, f"未対応の操作タイプ: {operation_type}"
                
            # スローモードが有効な場合、アクション間に遅延を入れる
            if self.slow_mode and result:
                self.logger.debug(f"スローモード: {self.action_delay}秒待機します")
                time.sleep(self.action_delay)
                
            return result, error
        except Exception as e:
            self.logger.error(f"アクション実行中にエラーが発生しました: {str(e)}")
            return False, str(e)
    
    def _handle_url_move(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        URL移動処理
        
        Args:
            url: 移動先URL
            
        Returns:
            (成功したかどうか, エラーメッセージ)
        """
        try:
            # 設定からベースURLを取得
            base_url = self.config.get('url', '')

            # Basic認証情報を取得
            basic_auth_username = self.user.get('basic_auth_username', '')
            basic_auth_password = self.user.get('basic_auth_password', '')
            
            # URLの構築（Basic認証情報を含む）
            from src.utils.browser_utils import build_url_with_auth
            full_url = build_url_with_auth(base_url, url, basic_auth_username, basic_auth_password)

            if not full_url:
                self.logger.error(f"URLの構築に失敗しました: base_url={base_url}, path={url}")
                return False, "URLの構築に失敗しました"

            self.logger.debug(f"構築されたURL: {full_url}")
            self.driver.get(full_url)
            return True, None
        except Exception as e:
            return False, f"URL移動に失敗しました: {str(e)}"

    def _handle_text_input(self, selector: str, value: str) -> Tuple[bool, Optional[str]]:
        """
        テキスト入力処理
        
        Args:
            selector: 要素セレクタ
            value: 入力値
            
        Returns:
            (成功したかどうか, エラーメッセージ)
        """
        try:
            # 設定からリトライ回数を取得
            retry_count = self.config.get('retry_count', 0)
            
            # 要素を検索
            element = find_element(self.driver, selector, self.timeout, retry_count)
            if not element:
                return False, f"要素が見つかりません: {selector}"
            
            # 入力前にクリア
            element.clear()
            
            # テキスト入力
            element.send_keys(value)
            self.logger.debug(f"テキスト入力: {selector} に {value} を入力")
            return True, None
        except WebDriverException as e:
            return False, f"テキスト入力に失敗しました: {str(e)}"
    
    def _handle_click(self, selector: str) -> Tuple[bool, Optional[str]]:
        """
        クリック処理
        
        Args:
            selector: 要素セレクタ
            
        Returns:
            (成功したかどうか, エラーメッセージ)
        """
        try:
            # 設定からリトライ回数を取得
            retry_count = self.config.get('retry_count', 0)
            
            # 要素を検索
            element = find_element(self.driver, selector, self.timeout, retry_count)
            if not element:
                return False, f"要素が見つかりません: {selector}"
            
            # 要素が表示されるようにスクロール
            scroll_to_element(self.driver, element)
            
            # クリック
            element.click()
            self.logger.debug(f"クリック: {selector}")
            return True, None
        except WebDriverException as e:
            return False, f"クリックに失敗しました: {str(e)}"
    
    def _handle_force_click(self, selector: str) -> Tuple[bool, Optional[str]]:
        """
        強制クリック処理（JavaScriptを使用）
        
        Args:
            selector: 要素セレクタ
            
        Returns:
            (成功したかどうか, エラーメッセージ)
        """
        try:
            # 設定からリトライ回数を取得
            retry_count = self.config.get('retry_count', 0)
            
            # 要素を検索
            element = find_element(self.driver, selector, self.timeout, retry_count)
            if not element:
                return False, f"要素が見つかりません: {selector}"
            
            # 要素が表示されるようにスクロール
            scroll_to_element(self.driver, element)
            
            # JavaScriptでクリック
            self.driver.execute_script("arguments[0].click();", element)
            self.logger.debug(f"強制クリック: {selector}")
            return True, None
        except WebDriverException as e:
            return False, f"強制クリックに失敗しました: {str(e)}"
    
    def _handle_js_click(self, selector: str) -> Tuple[bool, Optional[str]]:
        """
        JavaScriptクリック処理（セレクタを直接使用）
        
        Args:
            selector: 要素セレクタ（CSSセレクタのみ対応）
            
        Returns:
            (成功したかどうか, エラーメッセージ)
        """
        try:
            # CSSセレクタでJavaScriptを実行
            result = self.driver.execute_script(f"document.querySelector('{selector}').click(); return true;")
            if result:
                self.logger.debug(f"JSクリック: {selector}")
                return True, None
            else:
                return False, f"JSクリックに失敗しました: {selector}"
        except WebDriverException as e:
            return False, f"JSクリックに失敗しました: {str(e)}"
    
    def _handle_select(self, selector: str, value: str) -> Tuple[bool, Optional[str]]:
        """
        セレクト処理
        
        Args:
            selector: 要素セレクタ
            value: 選択値
            
        Returns:
            (成功したかどうか, エラーメッセージ)
        """
        try:
            # 設定からリトライ回数を取得
            retry_count = self.config.get('retry_count', 0)
            
            # 要素を検索
            element = find_element(self.driver, selector, self.timeout, retry_count)
            if not element:
                return False, f"要素が見つかりません: {selector}"
            
            # Selectオブジェクトを作成
            select = Select(element)
            
            # 値、表示テキスト、インデックスのいずれかで選択
            if value.startswith("value:"):
                select.select_by_value(value[6:])
            elif value.startswith("text:"):
                select.select_by_visible_text(value[5:])
            elif value.startswith("index:"):
                select.select_by_index(int(value[6:]))
            else:
                # デフォルトは表示テキストで選択
                select.select_by_visible_text(value)
            
            self.logger.debug(f"選択: {selector} で {value} を選択")
            return True, None
        except WebDriverException as e:
            return False, f"選択に失敗しました: {str(e)}"
    
    def _handle_wait(self, selector: str) -> Tuple[bool, Optional[str]]:
        """
        要素待機処理または時間待機処理
        
        Args:
            selector: 要素セレクタ（空の場合は時間待機）
            
        Returns:
            (成功したかどうか, エラーメッセージ)
        """
        try:
            # セレクタが空の場合は単純に待機時間を使用
            if not selector or selector.strip() == "":
                import time
                wait_time = self.timeout if self.timeout > 0 else 2  # デフォルト2秒
                self.logger.debug(f"時間待機: {wait_time}秒")
                time.sleep(wait_time)
                return True, None
                
            # セレクタがある場合は要素を待機
            # 設定からリトライ回数を取得
            retry_count = self.config.get('retry_count', 0)
            
            # 要素を検索（タイムアウトまで待機）
            element = find_element(self.driver, selector, self.timeout, retry_count)
            if element:
                self.logger.debug(f"待機完了: {selector}")
                return True, None
            else:
                return False, f"要素が見つかりませんでした: {selector}"
        except WebDriverException as e:
            return False, f"待機処理に失敗しました: {str(e)}"
    
    def _handle_assert(self, selector: str, expected_value: str) -> Tuple[bool, Optional[str]]:
        """
        アサート処理
        
        Args:
            selector: 要素セレクタ
            expected_value: 期待値
            
        Returns:
            (成功したかどうか, エラーメッセージ)
        """
        try:
            # 設定からリトライ回数を取得
            retry_count = self.config.get('retry_count', 0)
            
            # 要素を検索
            element = find_element(self.driver, selector, self.timeout, retry_count)
            if not element:
                return False, f"要素が見つかりません: {selector}"
            
            # テキスト取得
            actual_value = element.text
            
            # 比較
            if expected_value.startswith("contains:"):
                # 部分一致
                expected_text = expected_value[9:]
                if expected_text in actual_value:
                    self.logger.debug(f"アサート成功: {selector} に {expected_text} が含まれています")
                    return True, None
                else:
                    return False, f"アサート失敗: {selector} に {expected_text} が含まれていません。実際の値: {actual_value}"
            else:
                # 完全一致
                if actual_value == expected_value:
                    self.logger.debug(f"アサート成功: {selector} の値が {expected_value} と一致")
                    return True, None
                else:
                    return False, f"アサート失敗: {selector} の値が一致しません。期待値: {expected_value}, 実際の値: {actual_value}"
        except WebDriverException as e:
            return False, f"アサート処理に失敗しました: {str(e)}"
    
    def _handle_script(self, script: str) -> Tuple[bool, Optional[str]]:
        """
        JavaScriptスクリプト実行処理
        
        Args:
            script: 実行するJavaScript
            
        Returns:
            (成功したかどうか, エラーメッセージ)
        """
        try:
            # スクリプト実行
            result = self.driver.execute_script(script)
            self.logger.debug(f"スクリプト実行: {script[:50]}... 結果: {result}")
            return True, None
        except WebDriverException as e:
            return False, f"スクリプト実行に失敗しました: {str(e)}"
    
    def _replace_variables(self, text: str) -> str:
        """
        変数を置換する
        
        Args:
            text: 置換対象テキスト
            
        Returns:
            置換後のテキスト
        """
        if not text or not isinstance(text, str):
            return text
        
        # ${変数名}形式の変数を置換
        pattern = r'\${([^}]+)}'
        
        def replace_var(match):
            var_expr = match.group(1)
            
            # ユーザー変数の処理
            if var_expr.startswith('user.'):
                var_name = var_expr[5:]  # 'user.'を除去
                
                # エイリアスの処理
                if var_name == 'username' and 'app_username' in self.user:
                    var_name = 'app_username'
                elif var_name == 'password' and 'app_password' in self.user:
                    var_name = 'app_password'
                
                if var_name in self.user:
                    return self.user[var_name]
                else:
                    self.logger.warning(f"未定義のユーザー変数: {var_expr}")
                    return match.group(0)
            else:
                self.logger.warning(f"未対応の変数形式: {var_expr}")
                return match.group(0)
        
        return re.sub(pattern, replace_var, text)
        
    # メソッド名の統一
    _replace_user_variables = _replace_variables
