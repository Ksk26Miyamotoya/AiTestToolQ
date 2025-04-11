# 設定ファイル

AiTestToolQでは、TOML形式の設定ファイルを使用して様々な設定を行います。

## メイン設定ファイル

メイン設定ファイル（デフォルトでは`resources/config.toml`）には、以下の設定項目があります。

### 基本設定

```toml
# 設定ファイルのパス
url_config = "resources/url/default.toml"  # URL設定ファイルのパス
user_config = "resources/user/default.toml"  # ユーザー設定ファイルのパス
scenario_config = "resources/scenario/default.csv"  # シナリオファイルのパス
```

### 実行設定

```toml
# 実行設定
slow_mode = false  # 遅延モード（デバッグ用）
action_delay = 1.5  # アクション間の遅延時間（秒）
timeout = 30  # 要素待機のタイムアウト（秒）
retry_count = 3  # 失敗時のリトライ回数
```

### ブラウザ設定

```toml
# ブラウザ設定
browser = "chrome"  # 使用するブラウザ（"chrome", "firefox", "edge", "safari"）
test_mode = false  # テストモード（ブラウザを表示する）
```

サポートされているブラウザ:
- `chrome`: Google Chrome
- `firefox`: Mozilla Firefox
- `edge`: Microsoft Edge
- `safari`: Apple Safari (macOSのみ)

> **注意**: 
> - Safariを使用する場合は、事前に開発メニューから「リモートオートメーションを許可」を有効にする必要があります。
> - `test_mode`設定は、コマンドライン引数の`--test-mode`と組み合わせて使用できます。どちらかがtrueの場合、テストモードが有効になります。

### スクリーンショット設定

```toml
# スクリーンショット設定
# 撮影タイミング: "before_action"（アクション前）, "after_action"（アクション後）, "on_error"（エラー時）
# 複数設定した場合、指定したすべてのタイミングでスクリーンショットが撮影されます
screenshot_timing = ["before_action", "after_action", "on_error"]
```

### Excelレポート設定

```toml
# Excelレポート設定
report_title = "テスト結果報告書"        # レポートのタイトル
company_name = "株式会社テスト"          # 会社名
project_name = "テストプロジェクト"      # プロジェクト名
report_logo = "resources/template/logo.png"  # ロゴ画像のパス（空の場合は表示しない）
zoom_scale = 50                          # スクリーンショットシートの表示倍率（%）
include_timestamp = true                 # レポートにタイムスタンプを含めるか
timestamp_format = "%Y-%m-%d %H:%M:%S"   # タイムスタンプのフォーマット
header_bg_color = "#4472C4"              # ヘッダー背景色
header_font_color = "#FFFFFF"            # ヘッダーフォント色
alt_row_color = "#E6F0FF"                # 交互行の背景色
success_color = "#C6EFCE"                # 成功セルの背景色
failure_color = "#FFC7CE"                # 失敗セルの背景色
screenshot_title_cell_color = "#ffebcd"  # スクリーンショットシートのタイトル部分の背景色
```

### デバッグ設定

```toml
# デバッグ設定
debug_mode = false  # デバッグモード（詳細なログ出力）
```

## URL設定ファイル

URL設定ファイル（デフォルトでは`resources/url/default.toml`）には、テスト対象のURLを設定します。

```toml
# URL設定
url = "https://example.com"  # テスト対象のURL
```

## ユーザー設定ファイル

ユーザー設定ファイル（デフォルトでは`resources/user/default.toml`）には、テストに使用するユーザー情報を設定します。

```toml
# ユーザー設定
[[users]]
app_username = "user1"  # アプリケーションのユーザー名
app_password = "pass1"  # アプリケーションのパスワード
basic_auth_username = "basic1"  # Basic認証のユーザー名（必要な場合）
basic_auth_password = "basic_pass1"  # Basic認証のパスワード（必要な場合）

[[users]]
app_username = "user2"
app_password = "pass2"
basic_auth_username = "basic2"
basic_auth_password = "basic_pass2"
```

## コマンドライン引数による上書き

コマンドライン引数を使用して、設定ファイルの値を上書きできます。

```bash
# テストモードで実行（ブラウザが表示される）
python -m src --test-mode

# 特定のURL設定とユーザー設定を指定して実行
python -m src --url-config resources/url/staging --user-config resources/user/test_user

# シナリオファイルを指定して実行
python -m src --scenario-config resources/scenario/login_only.csv

# デバッグモードで実行
python -m src --debug
```
