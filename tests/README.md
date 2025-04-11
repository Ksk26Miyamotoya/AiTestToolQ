# AiTestToolQ テストコード

このディレクトリには、AiTestToolQのテストコードが含まれています。

## テスト実行方法

```bash
# プロジェクトのルートディレクトリから実行
# 全てのテストを実行
pytest tests/

# 特定のテストファイルを実行
pytest tests/test_config_loader.py

# 特定のテストクラスを実行
pytest tests/test_config_loader.py::TestConfigLoader

# 特定のテストメソッドを実行
pytest tests/test_config_loader.py::TestConfigLoader::test_init_with_default_paths

# 詳細な出力で実行
pytest tests/ -v

# カバレッジレポートを生成
pytest tests/ --cov=src
```

## テスト構成

- `conftest.py` - テスト共通の設定とフィクスチャ
- `test_config_loader.py` - 設定ローダーのテスト
- `test_scenario_loader.py` - シナリオローダーのテスト
- `test_action_handler.py` - アクションハンドラーのテスト
- `test_browser_session.py` - ブラウザセッションのテスト
- `test_concurrent_tester.py` - 同時実行テスターのテスト
- `test_utils/` - ユーティリティのテスト
  - `test_browser_utils.py` - ブラウザユーティリティのテスト
  - `test_file_utils.py` - ファイル操作ユーティリティのテスト
  - `test_toml_utils.py` - TOML操作ユーティリティのテスト
  - `test_excel_report.py` - Excelレポート生成のテスト
- `resources/` - テスト用リソース
  - `config.toml` - テスト用設定ファイル
  - `url/test.toml` - テスト用URL設定
  - `user/test.toml` - テスト用ユーザー設定
  - `scenario/test.csv` - テスト用シナリオ

## テスト依存パッケージ

テストを実行するには、以下のパッケージが必要です：

```bash
pip install pytest pytest-mock pytest-cov
```
