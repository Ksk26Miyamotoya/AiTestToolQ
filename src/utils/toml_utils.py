"""
TOML操作ユーティリティ
"""
import os
from typing import Dict, Any, Optional, TypeVar, Union, List
import tomlkit

T = TypeVar('T')

def load_toml(file_path: str) -> Optional[Dict[str, Any]]:
    """
    TOMLファイルを読み込む

    Args:
        file_path: TOMLファイルのパス

    Returns:
        Dict[str, Any]: 読み込んだ設定（失敗した場合はNone）
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return tomlkit.parse(f.read())
    except Exception as e:
        print(f"TOMLファイルの読み込みに失敗しました: {file_path}, エラー: {str(e)}")
        return None


def save_toml(file_path: str, data: Dict[str, Any], preserve_structure: bool = True) -> bool:
    """
    TOMLファイルを保存する

    Args:
        file_path: TOMLファイルのパス
        data: 保存するデータ
        preserve_structure: 既存のファイル構造を保持するかどうか

    Returns:
        bool: 保存に成功したかどうか
    """
    try:
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if preserve_structure and os.path.exists(file_path):
            # 既存のファイル構造を保持
            with open(file_path, "r", encoding="utf-8") as f:
                config = tomlkit.parse(f.read())
            
            # データを更新
            for key, value in data.items():
                config[key] = value
            
            # 保存
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(tomlkit.dumps(config))
        else:
            # 新規作成または上書き
            doc = tomlkit.document()
            for key, value in data.items():
                doc[key] = value
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(tomlkit.dumps(doc))
        
        return True
    except Exception as e:
        print(f"TOMLファイルの保存に失敗しました: {file_path}, エラー: {str(e)}")
        return False


def get_value(config: Dict[str, Any], key: str, default: T) -> T:
    """
    設定から値を取得し、適切な型に変換する

    Args:
        config: 設定辞書
        key: キー
        default: デフォルト値（型の判断にも使用）

    Returns:
        取得した値（デフォルト値と同じ型に変換）
    """
    if key not in config:
        return default
    
    value = config.get(key)
    
    # デフォルト値の型に基づいて変換
    if isinstance(default, bool):
        return bool(value)
    elif isinstance(default, int):
        return int(value)
    elif isinstance(default, float):
        return float(value)
    elif isinstance(default, str):
        return str(value)
    elif isinstance(default, list):
        # リストの場合、tomlkitの型からPythonのリストに変換
        if isinstance(value, list) or hasattr(value, '__iter__'):
            return list(value)
        return default
    else:
        # その他の型はそのまま返す
        return value


def get_bool(config: Dict[str, Any], key: str, default: bool = False) -> bool:
    """
    設定から真偽値を取得する

    Args:
        config: 設定辞書
        key: キー
        default: デフォルト値

    Returns:
        bool: 真偽値
    """
    if key not in config:
        return default
    
    value = config.get(key)
    
    # tomlkitの真偽値オブジェクトを処理
    if hasattr(value, 'unwrap'):
        try:
            value = value.unwrap()
        except:
            pass
    
    # 文字列の場合は特別処理
    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ('true', 'yes', '1', 'on'):
            return True
        elif value_lower in ('false', 'no', '0', 'off'):
            return False
        return bool(value)
    
    return bool(value)


def get_int(config: Dict[str, Any], key: str, default: int = 0) -> int:
    """
    設定から整数値を取得する

    Args:
        config: 設定辞書
        key: キー
        default: デフォルト値

    Returns:
        int: 整数値
    """
    if key not in config:
        return default
    
    value = config.get(key)
    return int(value)


def get_float(config: Dict[str, Any], key: str, default: float = 0.0) -> float:
    """
    設定から浮動小数点値を取得する

    Args:
        config: 設定辞書
        key: キー
        default: デフォルト値

    Returns:
        float: 浮動小数点値
    """
    if key not in config:
        return default
    
    value = config.get(key)
    return float(value)


def get_str(config: Dict[str, Any], key: str, default: str = "") -> str:
    """
    設定から文字列を取得する

    Args:
        config: 設定辞書
        key: キー
        default: デフォルト値

    Returns:
        str: 文字列
    """
    if key not in config:
        return default
    
    value = config.get(key)
    return str(value)


def get_list(config: Dict[str, Any], key: str, default: List[Any] = None) -> List[Any]:
    """
    設定からリストを取得する

    Args:
        config: 設定辞書
        key: キー
        default: デフォルト値

    Returns:
        List[Any]: リスト
    """
    if default is None:
        default = []
    
    if key not in config:
        return default
    
    value = config.get(key)
    if isinstance(value, list) or hasattr(value, '__iter__'):
        return list(value)
    
    return default
