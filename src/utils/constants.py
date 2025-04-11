"""
アプリケーション全体で使用する定数
"""

# 操作タイプ
class OperationType:
    URL_MOVE = "URL移動"
    TEXT_INPUT = "テキスト入力"
    CLICK = "クリック"
    FORCE_CLICK = "強制クリック"
    JS_CLICK = "JSクリック"
    SELECT = "選択"
    WAIT = "待機"
    ASSERT = "アサート"
    SCRIPT = "スクリプト実行"
    
    # 全操作タイプのリスト
    ALL = [URL_MOVE, TEXT_INPUT, CLICK, FORCE_CLICK, JS_CLICK, SELECT, WAIT, ASSERT, SCRIPT]

# シナリオテーブルのカラム
class ScenarioColumn:
    OPERATION_ID = 0
    OPERATION_TYPE = 1
    TARGET_ELEMENT = 2
    INPUT_VALUE = 3
    WAIT_TIME = 4
    DESCRIPTION = 5
    EXCEL_OUTPUT = 6
    
    # カラム名
    HEADERS = ["操作ID", "操作タイプ", "対象要素", "入力値", "待機時間", "説明", "Excel出力"]

# Excel出力の値
class ExcelOutput:
    YES = "yes"
    NO = "no"
    
    # Yesとみなす値のリスト（小文字）
    YES_VALUES = ["yes", "y", "true", "1"]
    
    # Noとみなす値のリスト（小文字）
    NO_VALUES = ["no", "n", "false", "0"]

# ファイルパス
class FilePath:
    DEFAULT_CONFIG = "resources/config.toml"
    DEFAULT_SCENARIO = "resources/scenario/default.csv"
