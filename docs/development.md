# 開発者向け情報

このドキュメントでは、AiTestToolQの内部構造と、拡張や修正を行うための情報を提供します。

## モジュール構成

プロジェクトは以下のモジュールで構成されています：

```
src/
├── __init__.py        # パッケージ初期化ファイル
├── __main__.py        # モジュール実行用エントリーポイント
├── main.py            # メインエントリーポイント
├── config_loader.py   # 設定ファイルを読み込むクラス
├── scenario_loader.py # シナリオファイルを読み込むクラス
├── browser_session.py # ブラウザセッションを管理するクラス
├── action_handler.py  # アクション処理を行うクラス
├── concurrent_tester.py # 複数のセッションを同時に実行するクラス
└── utils/             # ユーティリティモジュール
    ├── __init__.py
    ├── logger.py      # ロギングユーティリティ
    ├── file_utils.py  # ファイル操作ユーティリティ
    ├── browser_utils.py # ブラウザ操作ユーティリティ
    └── excel_report.py # Excelレポート生成ユーティリティ
```

## クラス構造

### ConfigLoader

設定ファイルを読み込み、各種設定値を取得するためのクラスです。

```python
class ConfigLoader:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        # 設定ファイルを読み込む
        
    def get_url(self) -> str:
        # URLを取得
        
    def get_users(self) -> List[Dict[str, str]]:
        # ユーザー情報のリストを取得
        
    def is_test_mode(self) -> bool:
        # テストモードかどうかを取得
        
    def get_timeout(self) -> int:
        # タイムアウト時間を取得
        
    def get_retry_count(self) -> int:
        # リトライ回数を取得
        
    def get_browser(self) -> str:
        # ブラウザ種別を取得
        
    def get_scenario_file(self) -> str:
        # シナリオファイルのパスを取得
        
    def get_screenshot_timing(self) -> List[str]:
        # スクリーンショットのタイミングを取得
```

### ScenarioLoader

CSVファイルからテストシナリオを読み込むクラスです。

```python
class ScenarioLoader:
    def __init__(self, scenario_file: str):
        self.scenario_file = scenario_file
        self.actions = self._load_scenario()
        
    def _load_scenario(self) -> List[Dict[str, str]]:
        # シナリオファイルを読み込む
        
    def get_actions(self) -> List[Dict[str, str]]:
        # アクションのリストを取得
        
    def get_action_by_id(self, action_id: str) -> Optional[Dict[str, str]]:
        # 指定したIDのアクションを取得
```

### ActionHandler

アクション処理を行うクラスです。各種操作（クリック、入力、選択など）を実行します。

```python
class ActionHandler:
    def __init__(self, driver: WebDriver, user: Dict[str, str], config: Dict[str, Any], logger: logging.Logger):
        self.driver = driver
        self.user = user
        self.config = config
        self.logger = logger
        
    def perform_action(self, action: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        # アクションタイプに応じた処理を実行
        
    def _process_special_syntax(self, value: str) -> str:
        # 特殊構文を処理
        
    def _click(self, selector: str) -> Tuple[bool, Optional[str]]:
        # 要素をクリック
        
    def _input(self, selector: str, value: str) -> Tuple[bool, Optional[str]]:
        # 要素に値を入力
        
    def _select(self, selector: str, value: str) -> Tuple[bool, Optional[str]]:
        # セレクトボックスから値を選択
        
    def _wait(self, seconds: str) -> Tuple[bool, Optional[str]]:
        # 指定秒数待機
        
    def _assert(self, selector: str, expected: str) -> Tuple[bool, Optional[str]]:
        # 要素の値を検証
```

### BrowserSession

1つのブラウザセッションを管理するクラスです。ブラウザの初期化、ページ操作、スクリーンショット取得などを行います。

```python
class BrowserSession:
    def __init__(self, user: Dict[str, str], config: Dict[str, Any], session_id: int, output_dir: str):
        self.user = user
        self.config = config
        self.session_id = session_id
        self.output_dir = output_dir
        self.driver = None
        self.base_url = config.get('url', '')
        self.logger = self._setup_logger()
        self.screenshot_timing = config.get('screenshot_timing', ['on_error'])
        self.current_action_id = None
        self.action_handler = None
        
    def _setup_logger(self) -> logging.Logger:
        # ロガーの設定
        
    def get_user_data(self, key: str, default: str = "") -> str:
        # ユーザー情報から指定したキーの値を取得
        
    def initialize(self) -> bool:
        # ブラウザを初期化
        
    def navigate_to_url(self, path: str) -> bool:
        # Basic認証付きURLに移動
        
    def perform_action(self, action: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        # 1つのアクションを実行
        
    def take_screenshot(self, prefix: str = "") -> Optional[str]:
        # スクリーンショットを撮影
        
    def close(self) -> None:
        # ブラウザを閉じる
```

### ConcurrentTester

複数のブラウザセッションを同時に実行し、テスト結果を集計するクラスです。

```python
class ConcurrentTester:
    def __init__(self, config_file: str, scenario_file: str = None, test_mode: bool = None, 
                 url_config: str = None, user_config: str = None):
        self.config_loader = ConfigLoader(config_file)
        self.scenario_file = scenario_file or self.config_loader.get_scenario_file()
        self.scenario_loader = ScenarioLoader(self.scenario_file)
        self.test_mode = test_mode if test_mode is not None else self.config_loader.is_test_mode()
        self.url_config = url_config
        self.user_config = user_config
        self.logger = self._setup_logger()
        self.output_dir = self._create_output_dir()
        
    def _setup_logger(self) -> logging.Logger:
        # ロガーの設定
        
    def _create_output_dir(self) -> str:
        # 出力ディレクトリの作成
        
    def _run_session(self, user: Dict[str, str], session_id: int) -> Dict[str, Any]:
        # 1つのセッションを実行
        
    def run(self) -> Dict[str, Any]:
        # テストを実行
        
    def _save_results(self, results: Dict[str, Any]) -> str:
        # テスト結果をJSONファイルに保存
        
    def _generate_excel_report(self, results: Dict[str, Any]) -> str:
        # Excelレポートを生成
```

## 処理フロー

1. `__main__.py` からエントリーポイント `main.py` の `main()` 関数が呼び出されます
2. コマンドライン引数が解析され、`ConcurrentTester` が初期化されます
3. `ConcurrentTester.run()` が呼び出され、テストが実行されます
4. 各ユーザーに対して `BrowserSession` が作成され、並行して実行されます
5. 各セッションは、シナリオに従ってアクションを順番に実行します
6. `ActionHandler`がアクションタイプに応じた処理を実行します
7. テスト結果が収集され、JSONファイルとExcelレポートに保存されます

## 拡張方法

### 新しい操作タイプの追加

新しい操作タイプを追加するには、`ActionHandler`クラスに新しいメソッドを追加し、`perform_action()`メソッドを修正します：

```python
def perform_action(self, action: Dict[str, str]) -> Tuple[bool, Optional[str]]:
    # 既存のコード...
    
    # アクションタイプに応じた処理
    if action_type == '新しい操作タイプ':
        return self._new_action_type(target, value)
        
    # 既存のコード...
    
def _new_action_type(self, selector: str, value: str) -> Tuple[bool, Optional[str]]:
    # 新しい操作タイプの処理を実装
    self.logger.info(f"新しい操作タイプ: {selector} に対して処理を実行しました")
    # 処理の実装
    return True, None
```

### 特殊構文の拡張

新しい特殊構文を追加するには、`ActionHandler._process_special_syntax()` メソッドを修正します：

```python
def _process_special_syntax(self, value: str) -> str:
    if not value or not isinstance(value, str):
        return value
        
    # 既存の特殊構文処理...
    
    # 新しい特殊構文の処理
    if "${new_syntax." in value:
        import re
        matches = re.findall(r'\${new_syntax\.([^}]+)}', value)
        for match in matches:
            # 新しい特殊構文の処理を実装
            new_value = "置換後の値"
            value = value.replace(f"${{new_syntax.{match}}}", new_value)
            self.logger.info(f"新しい特殊構文を置換しました: ${{new_syntax.{match}}} -> {new_value}")
            
    return value
```

### ブラウザオプションの拡張

ブラウザオプションを追加するには、`utils/browser_utils.py`の`create_browser()`関数を修正します：

```python
def create_browser(browser_type: str, test_mode: bool = False, **kwargs) -> WebDriver:
    """
    ブラウザを作成する
    
    Args:
        browser_type: ブラウザの種類 (chrome, firefox, edge)
        test_mode: テストモードかどうか (True: ヘッドレスモードにしない)
        **kwargs: その他のオプション
        
    Returns:
        WebDriver: 作成したWebDriverインスタンス
    """
    browser_type = browser_type.lower()
    
    if browser_type == 'chrome':
        options = ChromeOptions()
        if not test_mode:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # 新しいオプションを追加
        if kwargs.get('new_option', False):
            options.add_argument('--new-option')
            
        return webdriver.Chrome(options=options)
    
    # 既存のコード...
```

## テスト方法

### ユニットテスト

ユニットテストを追加するには、`tests` ディレクトリを作成し、各モジュールに対応するテストファイルを作成します：

```
tests/
├── __init__.py
├── test_config_loader.py
├── test_scenario_loader.py
├── test_action_handler.py
├── test_browser_session.py
└── test_concurrent_tester.py
```

テストの実行には `unittest` または `pytest` を使用できます：

```bash
# unittestを使用
python -m unittest discover tests

# pytestを使用
pytest tests/
```

### 統合テスト

統合テストを追加するには、`tests/integration` ディレクトリを作成し、テストファイルを作成します：

```
tests/integration/
├── __init__.py
└── test_full_flow.py
```

統合テストでは、実際のブラウザを使用してテストを実行します。テスト用のモックサーバーを使用することをお勧めします。

## コーディング規約

このプロジェクトでは、以下のコーディング規約に従うことをお勧めします：

1. **PEP 8**: Pythonの標準的なコーディングスタイルガイド
2. **型ヒント**: 関数やメソッドの引数と戻り値に型ヒントを使用
3. **ドキュメンテーション**: 関数やクラスにはdocstringを使用して説明を追加
4. **エラーハンドリング**: 適切な例外処理を行い、エラーメッセージを明確に
5. **ロギング**: `print` ではなく `logging` モジュールを使用

## 依存関係の管理

依存関係は `requirements.txt` ファイルで管理します：

```
selenium>=4.0.0
pillow>=9.0.0
openpyxl>=3.0.0
toml>=0.10.0
```

新しい依存関係を追加する場合は、`requirements.txt` を更新し、以下のコマンドでインストールします：

```bash
pip install -r requirements.txt
```

## デバッグのヒント

1. **ログレベルの変更**: より詳細なログを取得するために、ログレベルを DEBUG に変更します：

```python
logger.setLevel(logging.DEBUG)
```

2. **テストモードでの実行**: `--test-mode` オプションを使用して、ブラウザの動作を視覚的に確認します

3. **ブレークポイントの設定**: デバッグが必要な箇所に `import pdb; pdb.set_trace()` を追加します

4. **スクリーンショットの活用**: 問題が発生した箇所でスクリーンショットを撮影して確認します：

```python
session.take_screenshot(f"debug_{session.current_action_id}")
```

## パフォーマンスの最適化

1. **待機時間の最適化**: 明示的な待機を使用して、不要な待機時間を削減します

2. **リソースの解放**: テスト終了後に確実にブラウザを閉じるようにします

3. **並行処理の調整**: 同時に実行するセッション数を適切に調整します

4. **スクリーンショットの最適化**: 必要なタイミングでのみスクリーンショットを撮影します

5. **Excelレポート生成の最適化**: 大量のデータを処理する場合は、メモリ使用量に注意します
