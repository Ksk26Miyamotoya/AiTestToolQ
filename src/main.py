"""
メインエントリーポイントモジュール
"""
import argparse
import logging
import os
import sys

from src.concurrent_tester import ConcurrentTester
from src.config_loader import ConfigLoader
from src.utils.logger import setup_logger

def validate_files(args):
    """
    コマンドライン引数で指定されたファイルの存在を確認する
    
    Args:
        args: コマンドライン引数
        
    Returns:
        エラーメッセージ（エラーがない場合はNone）
    """
    # ロガーを設定
    logger = setup_logger("FileValidator")
    
    # 設定ファイルの存在確認
    config_path = args.config
    if not config_path.endswith('.toml'):
        config_path += '.toml'
    
    if not os.path.exists(config_path):
        return f"エラー: 設定ファイル '{config_path}' が見つかりません"
    
    # URL設定ファイルの存在確認（指定されている場合）
    if args.url_config:
        url_config_path = args.url_config
        if not url_config_path.endswith('.toml'):
            url_config_path += '.toml'
        if not os.path.exists(url_config_path):
            logger.warning(f"URL設定ファイル '{url_config_path}' が見つかりません。デフォルト設定を使用します。")
    
    # ユーザー設定ファイルの存在確認（指定されている場合）
    if args.user_config:
        user_config_path = args.user_config
        if not user_config_path.endswith('.toml'):
            user_config_path += '.toml'
        if not os.path.exists(user_config_path):
            logger.warning(f"ユーザー設定ファイル '{user_config_path}' が見つかりません。デフォルト設定を使用します。")
        
    # シナリオ設定ファイルの存在確認（指定されている場合）
    if args.scenario_config and not os.path.exists(args.scenario_config):
        logger.warning(f"シナリオファイル '{args.scenario_config}' が見つかりません。デフォルト設定を使用します。")
    
    return None
    return None

def main():
    """
    メインエントリーポイント
    """
    # Python 3.12以上が必要
    if sys.version_info < (3, 12):
        print("エラー: Python 3.12以上が必要です")
        return 1
    
    # デフォルトのロガーを設定
    logger = setup_logger("Main")
    
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(
            description='AiTestToolQ Basic認証サイト対応ブラウザテストツール')
    parser.add_argument('--test-mode', action='store_true', help='テストモードで実行（ブラウザが表示される）')
    parser.add_argument('--slow-mode', action='store_true', help='スロー実行モードで実行（各アクション間に遅延を入れる）')
    parser.add_argument('--action-delay', type=float, help='スロー実行モード時のアクション間の遅延時間（秒）')
    parser.add_argument('--browser', help='使用するブラウザ（chrome, firefox, edge, safari）')
    parser.add_argument('--config', default='resources/config.toml', help='設定ファイルのパス（.toml形式）')
    parser.add_argument('--url-config', help='URL設定ファイルのパス（.toml形式、拡張子省略可）')
    parser.add_argument('--user-config', help='ユーザー設定ファイルのパス（.toml形式、拡張子省略可）')
    parser.add_argument('--scenario-config', help='シナリオファイルのパス（CSV形式）')
    parser.add_argument('--debug', action='store_true', help='デバッグモードで実行（詳細なログ出力）')
    parser.add_argument('--gui', action='store_true', help='GUIモードで実行')
    args = parser.parse_args()
    
    # GUIモードの場合はGUIアプリケーションを起動
    if args.gui:
        try:
            from src.gui.app import run_gui
            # GUIモードでは設定読み込み時のメッセージを表示しない
            return run_gui(show_messages=False)
        except ImportError as e:
            logger.error(f"GUIモードの起動に失敗しました: {str(e)}")
            logger.error("PyQt6がインストールされていることを確認してください")
            logger.error("pip install PyQt6")
            return 1
    
    # ファイルの存在確認
    error = validate_files(args)
    if error:
        logger.error(error)
        return 1
    
    try:
        # 設定の読み込み
        config_loader = ConfigLoader(
            config_file=args.config,
            url_config=args.url_config,
            user_config=args.user_config,
            scenario_config=args.scenario_config
        )
        
        # デバッグモードの設定
        if args.debug:
            config_loader.config['debug_mode'] = True
            
        # テストモードの設定
        # コマンドライン引数のtest_modeがTrueなら設定ファイルに反映
        # 設定ファイルのtest_modeはそのまま保持される
        if args.test_mode:
            config_loader.config['test_mode'] = True
            
        # ブラウザタイプの設定
        if args.browser:
            config_loader.config['browser'] = args.browser
            logger.debug(f"コマンドライン引数からブラウザタイプを設定: {args.browser}")
            
        # スローモードの設定
        # コマンドライン引数のslow_modeがTrueなら設定ファイルに反映
        # 設定ファイルのslow_modeはそのまま保持される
        if args.slow_mode:
            config_loader.config['slow_mode'] = True
            
        # アクション遅延時間の設定
        # コマンドライン引数のaction_delayが指定されていれば設定ファイルに反映
        # 設定ファイルのaction_delayはそのまま保持される
        if args.action_delay is not None:
            config_loader.config['action_delay'] = args.action_delay
            
        # 型変換ユーティリティをインポート
        from src.utils.toml_utils import get_bool
            
        # ロガーの設定（設定ファイル読み込み後）
        log_level = logging.DEBUG if get_bool(config_loader.config, 'debug_mode', False) else logging.INFO
        logger = setup_logger("Main", level=log_level)
        
        # テストの実行
        tester = ConcurrentTester(
            config_loader=config_loader,
            test_mode=args.test_mode,  # コマンドライン引数のtest_modeをそのまま渡す
            slow_mode=args.slow_mode,
            action_delay=args.action_delay
        )
        
        # 設定内容のログ出力
        logger.debug(f"設定ファイルのブラウザタイプ: {config_loader.config.get('browser', 'chrome')}")
        
        results = tester.run()
        
        # 結果の表示
        # 結果はsummaryではなくトップレベルに格納されている
        total_sessions = results.get('total_sessions', 0)
        successful_sessions = results.get('successful_sessions', 0)
        failed_sessions = results.get('failed_sessions', 0)
        
        logger.info(f"テスト結果: 合計 {total_sessions} セッション, 成功 {successful_sessions}, 失敗 {failed_sessions}")
        logger.info(f"詳細な結果は '{results.get('output_file', '')}' を参照してください")
        
        return 0 if failed_sessions == 0 else 1
    
    except Exception as e:
        logger.error(f"テスト実行中にエラーが発生しました: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
