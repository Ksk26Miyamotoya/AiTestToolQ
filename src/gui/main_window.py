"""
メインウィンドウ
"""
from PyQt6.QtCore import QSettings, QTranslator
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QMessageBox

from .config_editor import ConfigEditor
from .result_viewer import ResultViewer
from .scenario_editor import ScenarioEditor
from .scenario_runner import ScenarioRunner
from .utils.i18n import load_translator


class MainWindow(QMainWindow):
    """
    メインウィンドウ
    """
    def __init__(self, show_messages=False):
        super().__init__()
        
        self.setWindowTitle("AiTestToolQ")
        
        # タブウィジェットの作成
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # 各タブの作成
        self.scenario_editor = ScenarioEditor()
        self.scenario_runner = ScenarioRunner()
        self.result_viewer = ResultViewer()
        self.config_editor = ConfigEditor(show_messages=show_messages)
        
        # タブの追加
        self.tab_widget.addTab(self.scenario_editor, self.tr("シナリオエディタ"))
        self.tab_widget.addTab(self.scenario_runner, self.tr("シナリオ実行"))
        self.tab_widget.addTab(self.result_viewer, self.tr("テスト結果"))
        self.tab_widget.addTab(self.config_editor, self.tr("設定"))
        
        # メニューバーの作成
        self.create_menus()
    
    def create_menus(self):
        """
        メニューバーを作成する
        """
        # ファイルメニュー
        file_menu = self.menuBar().addMenu(self.tr("ファイル"))
        
        # 終了アクション
        exit_action = file_menu.addAction(self.tr("終了"))
        exit_action.triggered.connect(self.close)
        
        # 言語メニュー
        language_menu = self.menuBar().addMenu(self.tr("言語"))
        
        # 言語切り替えアクション
        ja_action = language_menu.addAction(self.tr("日本語"))
        en_action = language_menu.addAction(self.tr("English"))
        
        # アクションの接続
        ja_action.triggered.connect(lambda: self.change_language("ja_JP"))
        en_action.triggered.connect(lambda: self.change_language("en_US"))
        
        # ヘルプメニュー
        help_menu = self.menuBar().addMenu(self.tr("ヘルプ"))
        
        # バージョン情報アクション
        about_action = help_menu.addAction(self.tr("バージョン情報"))
        about_action.triggered.connect(self.show_about)
    
    def change_language(self, language):
        """
        アプリケーションの言語を変更する
        
        Args:
            language: 言語コード (例: 'ja_JP', 'en_US')
        """
        # 設定に言語を保存
        settings = QSettings("AiTestToolQ", "AiTestToolQ")
        settings.setValue("language", language)
        
        # 翻訳の再読み込み
        translator = QTranslator()
        load_translator(translator, language)
        QApplication.instance().installTranslator(translator)
        
        # UIの再翻訳
        self.retranslate_ui()
        
        QMessageBox.information(self, self.tr("言語設定"), 
                              self.tr("言語を変更しました。一部の変更は再起動後に適用されます。"))
    
    def retranslate_ui(self):
        """
        UIテキストの再翻訳
        """
        # タブのタイトル
        self.tab_widget.setTabText(0, self.tr("シナリオエディタ"))
        self.tab_widget.setTabText(1, self.tr("シナリオ実行"))
        self.tab_widget.setTabText(2, self.tr("テスト結果"))
        self.tab_widget.setTabText(3, self.tr("設定"))
        
        # メニュー
        self.menuBar().findChild(QAction, "").setText(self.tr("終了"))
        self.menuBar().findChild(QAction, "").setText(self.tr("日本語"))
        self.menuBar().findChild(QAction, "").setText(self.tr("English"))
        self.menuBar().findChild(QAction, "").setText(self.tr("バージョン情報"))
        
        # 各タブの再翻訳
        self.scenario_editor.retranslate_ui()
        self.scenario_runner.retranslate_ui()
        self.result_viewer.retranslate_ui()
        self.config_editor.retranslate_ui()
    
    def show_about(self):
        """
        バージョン情報ダイアログを表示する
        """
        QMessageBox.about(self, self.tr("AiTestToolQ について"),
                        self.tr("AiTestToolQ バージョン 1.0.0\n\n"
                              "Basic認証サイト対応ブラウザテストツール\n\n"
                              "© 2025 AiTestToolQ Team"))
