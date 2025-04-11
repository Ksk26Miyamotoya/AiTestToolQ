"""
シナリオ実行画面
"""
from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QGroupBox)

from .widgets.file_selector import FileSelector
from .widgets.log_viewer import LogViewer


class ScenarioRunner(QWidget):
    """
    シナリオ実行画面
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # レイアウトの設定
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # ファイル選択部分
        self.create_file_selectors()
        
        # 実行オプション
        self.create_options()
        
        # 実行ボタン
        self.run_button = QPushButton(self.tr("シナリオ実行"))
        self.run_button.clicked.connect(self.run_scenario)
        self.layout.addWidget(self.run_button)
        
        # ログ表示部分
        self.log_label = QLabel(self.tr("実行ログ:"))
        self.layout.addWidget(self.log_label)
        
        self.log_text = LogViewer()
        self.layout.addWidget(self.log_text)
        
        # プロセス
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
    
    def create_file_selectors(self):
        """
        ファイル選択部分を作成する
        """
        # グループボックス
        group_box = QGroupBox(self.tr("ファイル設定"))
        self.layout.addWidget(group_box)
        
        # グループボックスのレイアウト
        group_layout = QVBoxLayout(group_box)
        
        # シナリオファイル選択
        self.scenario_selector = FileSelector(
            self.tr("シナリオファイル:"), 
            "resources/scenario", 
            "*.csv"
        )
        group_layout.addWidget(self.scenario_selector)
        
        # URL設定ファイル選択
        self.url_selector = FileSelector(
            self.tr("URL設定:"), 
            "resources/url", 
            "*.toml"
        )
        group_layout.addWidget(self.url_selector)
        
        # ユーザー設定ファイル選択
        self.user_selector = FileSelector(
            self.tr("ユーザー設定:"), 
            "resources/user", 
            "*.toml"
        )
        group_layout.addWidget(self.user_selector)
    
    def create_options(self):
        """
        実行オプションを作成する
        """
        # グループボックス
        group_box = QGroupBox(self.tr("実行オプション"))
        self.layout.addWidget(group_box)
        
        # グループボックスのレイアウト
        group_layout = QHBoxLayout(group_box)
        
        # テストモードチェックボックス
        self.test_mode_button = QPushButton(self.tr("テストモード"))
        self.test_mode_button.setCheckable(True)
        self.test_mode_button.setChecked(True)
        group_layout.addWidget(self.test_mode_button)
        
        # スローモードチェックボックス
        self.slow_mode_button = QPushButton(self.tr("スローモード"))
        self.slow_mode_button.setCheckable(True)
        group_layout.addWidget(self.slow_mode_button)
        
        # デバッグモードチェックボックス
        self.debug_mode_button = QPushButton(self.tr("デバッグモード"))
        self.debug_mode_button.setCheckable(True)
        group_layout.addWidget(self.debug_mode_button)
    
    def run_scenario(self):
        """
        シナリオを実行する
        """
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()
            self.run_button.setText(self.tr("シナリオ実行"))
            return
        
        # 選択されたファイルの取得
        scenario_file = self.scenario_selector.get_selected_file()
        url_file = self.url_selector.get_selected_file()
        user_file = self.user_selector.get_selected_file()
        
        if not scenario_file:
            self.log_text.append_log(self.tr("エラー: シナリオファイルが選択されていません"))
            return
        
        # コマンドの構築
        cmd = ["python", "-m", "src"]
        
        if url_file:
            cmd.extend(["--url-config", url_file])
        
        if user_file:
            cmd.extend(["--user-config", user_file])
        
        cmd.extend(["--scenario-config", scenario_file])
        
        # オプションの追加
        if self.test_mode_button.isChecked():
            cmd.append("--test-mode")
        
        if self.slow_mode_button.isChecked():
            cmd.append("--slow-mode")
        
        if self.debug_mode_button.isChecked():
            cmd.append("--debug")
        
        # ログのクリア
        self.log_text.clear_log()
        self.log_text.append_log(self.tr("コマンド: ") + " ".join(cmd))
        self.log_text.append_log("-----------------------------------")
        
        # プロセスの開始
        self.process.start(cmd[0], cmd[1:])
        
        # ボタンのテキスト変更
        self.run_button.setText(self.tr("実行中止"))
    
    def handle_stdout(self):
        """
        標準出力の処理
        """
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode("utf-8")
        self.log_text.append_log(text)
    
    def handle_stderr(self):
        """
        標準エラー出力の処理
        """
        data = self.process.readAllStandardError()
        text = bytes(data).decode("utf-8")
        self.log_text.append_log(text)
    
    def process_finished(self, exit_code, exit_status):
        """
        プロセス終了時の処理
        """
        self.run_button.setText(self.tr("シナリオ実行"))
        
        if exit_code == 0:
            self.log_text.append_log(self.tr("実行が正常に完了しました"))
        else:
            self.log_text.append_log(self.tr("実行がエラーで終了しました (コード: {})").format(exit_code))
    
    def retranslate_ui(self):
        """
        UIテキストの再翻訳
        """
        self.run_button.setText(
            self.tr("実行中止") if self.process.state() == QProcess.ProcessState.Running 
            else self.tr("シナリオ実行")
        )
        self.log_label.setText(self.tr("実行ログ:"))
        
        # グループボックスの再翻訳
        self.findChild(QGroupBox, "").setTitle(self.tr("ファイル設定"))
        self.findChild(QGroupBox, "").setTitle(self.tr("実行オプション"))
        
        # ボタンの再翻訳
        self.test_mode_button.setText(self.tr("テストモード"))
        self.slow_mode_button.setText(self.tr("スローモード"))
        self.debug_mode_button.setText(self.tr("デバッグモード"))
