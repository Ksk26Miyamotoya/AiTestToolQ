"""
ブラウザ操作ユーティリティモジュール
"""
import logging
import traceback
from typing import Tuple, Optional, Any
from urllib.parse import urlparse, urlunparse

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def create_browser(browser_type: str = 'chrome', headless: bool = True) -> Optional[webdriver.Remote]:
    """
    ブラウザインスタンスを作成する

    Args:
        browser_type: ブラウザの種類 ('chrome', 'firefox', 'edge', 'safari')
        headless: ヘッドレスモードで実行するかどうか

    Returns:
        作成したブラウザインスタンス（失敗した場合はNone）
    """
    try:
        # browser_typeが文字列でない場合はデフォルト値を使用
        if not isinstance(browser_type, str):
            logging.warning(f"browser_typeが文字列ではありません: {browser_type}, 'chrome'を使用します")
            browser_type = 'chrome'
            
        # headlessがブール値でない場合はデフォルト値を使用
        if not isinstance(headless, bool):
            logging.warning(f"headlessがブール値ではありません: {headless}, Trueを使用します")
            headless = True
            
        logging.info(f"ブラウザ作成: {browser_type}, ヘッドレスモード={headless}")
            
        if browser_type.lower() == 'chrome':
            options = ChromeOptions()
            if headless:
                options.add_argument('--headless=new')  # 新しいヘッドレスモード
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1024,768')  # 画面サイズを1024x768に設定
            driver = webdriver.Chrome(options=options)
        elif browser_type.lower() == 'firefox':
            options = FirefoxOptions()
            if headless:
                options.add_argument('-headless')
            driver = webdriver.Firefox(options=options)
        elif browser_type.lower() == 'edge':
            options = EdgeOptions()
            if headless:
                options.add_argument('--headless')
            driver = webdriver.Edge(options=options)
        elif browser_type.lower() == 'safari':
            driver = webdriver.Safari()
        else:
            logging.error(f"未対応のブラウザタイプ: {browser_type}")
            return None
            
        # ウィンドウサイズを設定
        driver.set_window_size(1024, 768)
        return driver
    except Exception as e:
        logging.error(f"ブラウザの作成に失敗しました: {str(e)}")
        traceback.print_exc()
        return None


def build_url_with_auth(base_url: str, path: str, username: str = '',
        password: str = '') -> str:
    """
    Basic認証情報を含むURLを構築する

    Args:
        base_url: ベースURL
        path: パス
        username: Basic認証のユーザー名
        password: Basic認証のパスワード

    Returns:
        構築したURL
    """
    # 入力チェック
    if not isinstance(base_url, str) or not base_url:
        logging.error(f"無効なベースURL: {base_url}")
        return ""

    # パスが空の場合はベースURLをそのまま返す
    if not path:
        return base_url

    # URLの解析
    parsed_url = urlparse(base_url)

    # スキームがない場合はhttpsを追加
    if not parsed_url.scheme:
        parsed_url = urlparse(f"https://{base_url}")

    # Basic認証情報の追加
    netloc = parsed_url.netloc
    if username and password:
        netloc = f"{username}:{password}@{netloc}"

    # パスの結合
    if path.startswith('/'):
        new_path = path
    else:
        if parsed_url.path.endswith('/'):
            new_path = parsed_url.path + path
        else:
            new_path = parsed_url.path + '/' + path

    # URLの再構築
    return urlunparse((
        parsed_url.scheme,
        netloc,
        new_path,
        parsed_url.params,
        parsed_url.query,
        parsed_url.fragment
    ))


def get_locator(selector: str) -> Tuple[By, str]:
    """
    セレクタからByとセレクタ値を取得する

    Args:
        selector: セレクタ文字列

    Returns:
        (By, セレクタ値)
    """
    if selector.startswith('#'):
        return By.ID, selector[1:]
    elif selector.startswith('//'):
        return By.XPATH, selector
    elif selector.startswith('.'):
        return By.CSS_SELECTOR, selector
    elif selector.startswith('name='):
        return By.NAME, selector[5:]
    elif selector.startswith('tag='):
        return By.TAG_NAME, selector[4:]
    elif selector.startswith('link='):
        return By.LINK_TEXT, selector[5:]
    elif selector.startswith('partial='):
        return By.PARTIAL_LINK_TEXT, selector[8:]
    elif selector.startswith('xpath='):
        return By.XPATH, selector[6:]
    elif selector.startswith('css='):
        return By.CSS_SELECTOR, selector[4:]
    else:
        # デフォルトはCSSセレクタとして扱う
        return By.CSS_SELECTOR, selector


def find_element(driver: webdriver.Remote, selector: str,
        timeout: float = 10, retry_count: int = 0) -> Optional[Any]:
    """
    要素を検索する

    Args:
        driver: WebDriverインスタンス
        selector: セレクタ
        timeout: タイムアウト時間（秒）
        retry_count: リトライ回数

    Returns:
        見つかった要素（見つからない場合はNone）
    """
    attempts = 0
    max_attempts = max(1, retry_count + 1)  # リトライ回数 + 初回試行
    
    while attempts < max_attempts:
        try:
            by, selector_value = get_locator(selector)
            element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by, selector_value))
            )
            return element
        except TimeoutException:
            attempts += 1
            if attempts < max_attempts:
                logging.info(f"要素が見つかりませんでした: {selector} - リトライ {attempts}/{retry_count}")
                # 少し待ってからリトライ
                import time
                time.sleep(1)
            else:
                logging.warning(
                    f"要素が見つかりませんでした: {selector} (タイムアウト: {timeout}秒)")
                return None
        except NoSuchElementException:
            logging.warning(f"要素が見つかりませんでした: {selector}")
            return None
        except Exception as e:
            logging.error(f"要素の検索中にエラーが発生しました: {str(e)}")
            logging.error(f"スタックトレース: {traceback.format_exc()}")
            return None
            
            
def scroll_to_element(driver, element, align="center"):
    """
    指定された要素までスクロールする
    
    Args:
        driver: WebDriverインスタンス
        element: スクロール先の要素
        align: スクロール位置 ("start", "center", "end", "nearest")
        
    Returns:
        成功したかどうか
    """
    try:
        # 要素が表示されるようにスクロール
        driver.execute_script(
            f"arguments[0].scrollIntoView({{behavior: 'smooth', block: '{align}'}});", 
            element
        )
        
        # スクロール後に少し待機
        import time
        time.sleep(0.5)
        
        return True
    except Exception as e:
        logging.error(f"スクロール中にエラーが発生しました: {str(e)}")
        logging.error(f"スタックトレース: {traceback.format_exc()}")
        return False
