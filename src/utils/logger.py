"""
ロギングユーティリティモジュール
"""
import os
import logging
import sys
from typing import Optional


def setup_logger(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    ロガーを設定する

    Args:
        name: ロガー名
        log_file: ログファイルのパス（Noneの場合はコンソールのみ）
        level: ログレベル

    Returns:
        設定済みのロガー
    """
    # debug_modeの設定を確認
    try:
        import tomllib
        with open("resources/config.toml", "rb") as f:
            config = tomllib.load(f)
            debug_mode = config.get("debug_mode", False)
            if debug_mode:
                # debug_modeがtrueの場合は、DEBUGレベルを強制
                level = logging.DEBUG
                print(f"DEBUG MODE ENABLED for {name}", file=sys.stderr)
            elif level == logging.DEBUG:
                # debug_modeがfalseで、DEBUGレベルが指定されている場合はINFOに変更
                level = logging.INFO
    except Exception as e:
        # 設定ファイルが読めない場合はデフォルト値を使用
        pass
        
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 既存のハンドラをクリア
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # コンソールハンドラの設定
    console_handler = logging.StreamHandler(sys.stderr)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # ルートロガーの伝播を無効化して二重出力を防止
    logger.propagate = False

    # ファイルハンドラの設定（指定されている場合）
    if log_file:
        # ディレクトリが存在しない場合は作成
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
