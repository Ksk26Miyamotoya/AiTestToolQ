"""
国際化（i18n）ユーティリティ
"""
import os
from PyQt6.QtCore import QTranslator, QLocale, QSettings

def load_translator(translator, language=None):
    """
    指定された言語の翻訳ファイルを読み込む
    
    Args:
        translator: QTranslatorオブジェクト
        language: 言語コード（例: 'ja_JP', 'en_US'）
    
    Returns:
        bool: 翻訳ファイルの読み込みに成功したかどうか
    """
    if language is None:
        # 設定から言語を読み込むか、システムのデフォルト言語を使用
        settings = QSettings("AiTestToolQ", "AiTestToolQ")
        language = settings.value("language", QLocale.system().name())
    
    # 言語設定を保存
    settings = QSettings("AiTestToolQ", "AiTestToolQ")
    settings.setValue("language", language)
    
    # 翻訳ファイルのパス
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    translations_dir = os.path.join(base_dir, "resources", "translations")
    
    # 翻訳ファイルの読み込み
    translation_file = f"aitesttoolq_{language}"
    result = translator.load(translation_file, translations_dir)
    
    # 翻訳ファイルが見つからない場合は英語をデフォルトとする
    if not result and language != "en_US":
        return translator.load("aitesttoolq_en_US", translations_dir)
    
    return result
