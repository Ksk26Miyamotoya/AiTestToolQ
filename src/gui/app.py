"""
メインアプリケーション
"""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale, QSettings
import sys

from .main_window import MainWindow
from .utils.i18n import load_translator

class AiTestToolQApp(QApplication):
    """
    AiTestToolQアプリケーション
    """
    def __init__(self, argv, show_messages=False):
        super().__init__(argv)
        
        # アプリケーション情報の設定
        self.setApplicationName("AiTestToolQ")
        self.setOrganizationName("AiTestToolQ")
        
        # 翻訳の初期化
        self.translator = QTranslator()
        self.load_language()
        
        # メインウィンドウの作成
        self.main_window = MainWindow(show_messages=show_messages)
        self.main_window.show()
    
    def load_language(self, language=None):
        """
        言語設定を読み込む
        
        Args:
            language: 言語コード（例: 'ja_JP', 'en_US'）
        """
        # 設定から言語を読み込むか、システムのデフォルト言語を使用
        if language is None:
            settings = QSettings("AiTestToolQ", "AiTestToolQ")
            language = settings.value("language", QLocale.system().name())
        
        # 翻訳ファイルの読み込み
        load_translator(self.translator, language)
        self.installTranslator(self.translator)

def run_gui(show_messages=False):
    """
    GUIアプリケーションを実行する
    
    Args:
        show_messages: 設定読み込み時などにメッセージボックスを表示するかどうか
    """
    app = AiTestToolQApp(sys.argv, show_messages=show_messages)
    return app.exec()
