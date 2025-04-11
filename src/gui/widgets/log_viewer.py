"""
ログ表示ウィジェット
"""
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QTextEdit


class LogViewer(QTextEdit):
    """
    ログ表示用のテキストエディタ
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, Menlo, Monaco, "Courier New", monospace;
                font-size: 12px;
                background-color: #f5f5f5;
                color: #333;
            }
        """)
    
    @pyqtSlot(str)
    def append_log(self, text):
        """
        ログを追加する
        
        Args:
            text: 追加するテキスト
        """
        # 自動スクロール
        scrollbar = self.verticalScrollBar()
        at_bottom = scrollbar.value() == scrollbar.maximum()
        
        # テキストを追加
        self.append(text)
        
        # 最下部にスクロールする
        if at_bottom:
            scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """
        ログをクリアする
        """
        self.clear()
