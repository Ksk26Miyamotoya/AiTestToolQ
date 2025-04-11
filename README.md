# AiTestToolQ ドキュメント

このディレクトリには、AiTestToolQの詳細なドキュメントが含まれています。

## 必要条件

- Python 3.12以上
- 設定ファイルはTOML形式のみサポート
- GUIモードにはPyQt6が必要

## ドキュメント一覧

- [概要と機能](docs/overview.md) - ツールの概要と主要機能の説明
- [インストールと設定](docs/installation.md) - インストール方法と初期設定
- [使用方法](docs/usage.md) - 基本的な使用方法とコマンドライン引数
- [設定ファイル](docs/configuration.md) - 設定ファイルの詳細な説明
- [シナリオファイル](docs/scenario.md) - シナリオファイルの書き方と操作タイプの説明
- [出力とレポート](docs/output.md) - テスト結果の出力形式と解釈方法
- [スクロール機能](docs/scroll_feature.md) - 画面外要素へのスクロール機能の説明
- [トラブルシューティング](docs/troubleshooting.md) - よくある問題と解決方法
- [FAQ](docs/faq.md) - よくある質問と回答
- [開発者向け情報](docs/development.md) - モジュール構成とクラス説明
- [Safari設定ガイド](docs/safari_setup.md) - Safariブラウザでのテスト実行設定

## クイックスタート

```bash
# Pythonバージョンの確認（3.12以上が必要）
python --version

# 仮想環境の作成と有効化
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 必要なパッケージをインストール
pip install -r requirements.txt

# コマンドラインモードで実行
python -m src

# GUIモードで実行
python -m src --gui
# または
python -m src.gui_main

# テストモードで実行（ブラウザが表示される）
python -m src --test-mode

# 特定のURL設定とユーザー設定を指定して実行
python -m src --url-config resources/url/staging --user-config resources/user/test_user

# シナリオファイルを指定して実行
python -m src --scenario-config resources/scenario/original_scenario.csv
```

> **注意**: 
> - Pythonモジュールとして実行する場合は、必ずプロジェクトのルートディレクトリから実行してください。
> - 設定ファイルは必ずTOML形式（.toml拡張子）で作成してください。拡張子がない場合は自動的に.tomlが追加されます。

## ディレクトリ構造

```
AiTestToolQ/
├── src/
│   ├── __init__.py
│   ├── __main__.py        # モジュール実行用エントリーポイント
│   ├── browser_session.py # ブラウザセッション管理
│   ├── concurrent_tester.py # 同時実行テスト
│   ├── config_loader.py   # 設定ファイル読み込み
│   ├── scenario_loader.py # シナリオファイル読み込み
│   ├── action_handler.py  # アクション処理
│   ├── main.py            # メインエントリーポイント
│   ├── gui_main.py        # GUIモード実行用エントリーポイント
│   ├── gui/               # GUIモジュール
│   │   ├── __init__.py
│   │   ├── app.py         # アプリケーションクラス
│   │   ├── main_window.py # メインウィンドウ
│   │   ├── config_editor.py # 設定エディタ
│   │   ├── scenario_editor.py # シナリオエディタ
│   │   ├── result_viewer.py # 結果ビューア
│   │   ├── scenario_runner.py # シナリオ実行
│   │   ├── widgets/       # カスタムウィジェット
│   │   └── utils/         # GUI用ユーティリティ
│   └── utils/             # ユーティリティモジュール
│       ├── __init__.py
│       ├── logger.py      # ロギングユーティリティ
│       ├── file_utils.py  # ファイル操作ユーティリティ
│       ├── browser_utils.py # ブラウザ操作ユーティリティ
│       ├── excel_report.py # Excelレポート生成ユーティリティ
│       ├── toml_utils.py  # TOML設定ファイル操作ユーティリティ
│       └── constants.py   # 定数定義
├── docs/                  # 詳細ドキュメント
├── resources/
│   ├── config.toml        # メイン設定ファイル
│   ├── template/          # Excelテンプレート
│   ├── url/               # URL設定ファイル
│   │   ├── default.toml
│   │   └── staging.toml
│   ├── user/              # ユーザー設定ファイル
│   │   ├── default.toml
│   │   └── test_user.toml
│   ├── scenario/          # シナリオファイル
│   │   ├── default.csv
│   │   └── login_only.csv
├── output/                # テスト結果の出力先
│   └── [タイムスタンプ]/
│       ├── result/        # テスト結果とExcelレポート
│       └── screenshot/    # スクリーンショット
├── venv/                  # 仮想環境（Gitでは無視）
├── requirements.txt       # 依存パッケージリスト
└── .gitignore             # Gitで無視するファイル
```
