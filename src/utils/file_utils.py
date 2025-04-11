"""
ファイル操作ユーティリティモジュール
"""
import os
import traceback
import json
import tomllib
from datetime import datetime
from typing import Dict, Any
from src.utils.logger import setup_logger

# ロガーの設定
logger = setup_logger("FileUtils")

def create_output_directory(base_dir: str = "output") -> str:
    """
    出力ディレクトリを作成する

    Args:
        base_dir: ベースディレクトリ

    Returns:
        作成した出力ディレクトリのパス
    """
    # ベースディレクトリが存在しない場合は作成
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_dir, timestamp)
    
    try:
        # 必要なディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)
        # resultディレクトリを作成（セッションログ、テスト結果、Excelレポート用）
        os.makedirs(os.path.join(output_dir, "result"), exist_ok=True)
        # スクリーンショット用ディレクトリ
        os.makedirs(os.path.join(output_dir, "screenshot"), exist_ok=True)
        
        # 権限確認のためのテストファイル作成
        test_file_path = os.path.join(output_dir, "test_write.txt")
        with open(test_file_path, 'w') as f:
            f.write("Test write access")
        os.remove(test_file_path)
        
        logger.info(f"出力ディレクトリを作成しました: {output_dir}")
    except Exception as e:
        logger.error(f"出力ディレクトリの作成に失敗しました: {str(e)}")
        # 代替ディレクトリとして現在のディレクトリ内のoutputを使用
        output_dir = os.path.join(os.getcwd(), "output", timestamp)
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "result"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "screenshot"), exist_ok=True)
        logger.info(f"代替出力ディレクトリを使用します: {output_dir}")
    
    return output_dir


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """
    データをJSONファイルに保存する

    Args:
        data: 保存するデータ
        file_path: 保存先のファイルパス
    """
    try:
        # ディレクトリが存在しない場合は作成
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        # ファイルの書き込み
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # ファイルが正常に作成されたか確認
        if os.path.exists(file_path):
            logger.info(f"JSONファイルを保存しました: {file_path}")
        else:
            logger.error(f"JSONファイルの保存に失敗しました: {file_path}")
    except Exception as e:
        logger.error(f"JSONファイルの保存中にエラーが発生しました: {str(e)}")
        logger.error(f"ファイルパス: {file_path}")
        logger.error(f"エラータイプ: {type(e).__name__}")
        # スタックトレースを出力
        logger.error(f"スタックトレース: {traceback.format_exc()}")


def load_toml(file_path: str) -> Dict[str, Any]:
    """
    TOMLファイルからデータを読み込む

    Args:
        file_path: 読み込むファイルのパス

    Returns:
        読み込んだデータ

    Raises:
        FileNotFoundError: ファイルが見つからない場合
        tomllib.TOMLDecodeError: TOMLの解析に失敗した場合
    """
    try:
        with open(file_path, 'rb') as f:
            data = tomllib.load(f)
        logger.debug(f"TOMLファイルを読み込みました: {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"TOMLファイルが見つかりません: {file_path}")
        raise
    except tomllib.TOMLDecodeError as e:
        logger.error(f"TOMLファイルの解析に失敗しました: {file_path}, エラー: {str(e)}")
        raise


def ensure_directory(directory: str) -> None:
    """
    ディレクトリが存在することを確認し、存在しない場合は作成する

    Args:
        directory: 確認するディレクトリのパス
    """
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"ディレクトリを確認/作成しました: {directory}")
        except Exception as e:
            logger.error(f"ディレクトリの作成に失敗しました: {directory}, エラー: {str(e)}")
