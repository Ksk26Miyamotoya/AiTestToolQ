"""
GUIモードのエントリーポイント
"""
import sys
from src.gui.app import run_gui

if __name__ == "__main__":
    # Python 3.12以上が必要
    if sys.version_info < (3, 12):
        print("エラー: Python 3.12以上が必要です")
        sys.exit(1)
    
    # GUIアプリケーションを実行（直接実行時はメッセージを表示する）
    sys.exit(run_gui(show_messages=True))
