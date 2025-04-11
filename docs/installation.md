# インストールと設定

このドキュメントでは、Basic認証サイト同時アクセステストツールのインストール方法と初期設定について説明します。

## 前提条件

- Python 3.12以上
- pip（Pythonパッケージマネージャー）
- インターネット接続（依存パッケージのダウンロード用）

## インストール手順

### 1. リポジトリのクローンまたはダウンロード

```bash
git clone https://github.com/yourusername/SeleniumTestToolQ.git
cd AiTestToolQ
```

または、ZIPファイルをダウンロードして解凍してください。

### 2. 仮想環境の作成と有効化

プロジェクト専用の仮想環境を作成することをお勧めします。これにより、他のプロジェクトとの依存関係の競合を避けることができます。

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化（Windows）
venv\Scripts\activate

# 仮想環境の有効化（macOS/Linux）
source venv/bin/activate
```

仮想環境が有効化されると、コマンドプロンプトやターミナルの先頭に `(venv)` と表示されます。

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

これにより、以下の主要なパッケージがインストールされます：
- selenium: Webブラウザの自動操作用ライブラリ
- webdriver-manager: WebDriverの自動ダウンロードと管理用ライブラリ

### 4. WebDriverの設定

このツールは、WebDriverを自動的にダウンロードして管理する `webdriver-manager` を使用しています。そのため、手動でWebDriverをインストールする必要はありません。

ただし、以下の点に注意してください：

- Chrome、Firefox、Edgeなどのブラウザが事前にインストールされている必要があります
- 初回実行時に、WebDriverが自動的にダウンロードされます
- インターネット接続が必要です

### 5. 設定ファイルの確認

`resources/config.toml` ファイルを確認し、必要に応じて編集してください。

```toml
# 設定ファイルのパス
url_config = "resources/url/default.toml"
user_config = "resources/user/default.toml"
scenario_config = "resources/scenario/default.csv"

# 実行設定
slow_mode = false
action_delay = 1.5
timeout = 30
retry_count = 3

# ブラウザ設定
browser = "chrome"
test_mode = false

# スクリーンショット設定
screenshot_timing = ["before_action", "after_action", "on_error"]
```

### 6. 動作確認

インストールが完了したら、テストモードで動作確認を行います。

```bash
python -m src --test-mode
```

テストモードでブラウザが起動し、テストが実行されれば成功です。

## トラブルシューティング

### WebDriverのエラー

WebDriverの自動ダウンロードに失敗した場合は、手動でインストールすることもできます：

- [ChromeDriverのダウンロードページ](https://sites.google.com/chromium.org/driver/)
- [GeckoDriver (Firefox)のダウンロードページ](https://github.com/mozilla/geckodriver/releases)

ダウンロードしたWebDriverをPATHの通った場所に配置してください。

### 依存パッケージのインストールエラー

特定のパッケージのインストールに失敗した場合は、個別にインストールしてみてください：

```bash
pip install selenium
pip install webdriver-manager
```

### 権限エラー

macOSやLinuxで権限エラーが発生した場合は、以下のコマンドを試してください：

```bash
chmod +x venv/bin/activate
```

## 次のステップ

インストールが完了したら、[使用方法](usage.md)を参照して、テストツールの基本的な使い方を確認してください。
