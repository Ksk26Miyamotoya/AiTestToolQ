"""
設定エディタ画面
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTextEdit, QFileDialog, QMessageBox,
                            QGroupBox, QFormLayout, QLineEdit, QCheckBox,
                            QComboBox, QSpinBox, QDoubleSpinBox, QColorDialog,
                            QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import os

from src.utils.toml_utils import load_toml, save_toml

class ConfigEditor(QWidget):
    """
    設定エディタ画面
    """
    def __init__(self, parent=None, show_messages=True):
        super().__init__(parent)
        
        # 初期値の設定
        self.current_file = os.path.join('resources', 'config.toml')
        self.show_messages = show_messages
        
        # レイアウトの設定
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # ファイル操作ボタン
        self.create_file_buttons()
        
        # スクロールエリアの作成
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # ウィジェットのサイズ変更を許可
        self.layout.addWidget(scroll_area)
        
        # スクロールエリア内のコンテンツウィジェット
        content_widget = QWidget()
        self.form_layout = QVBoxLayout(content_widget)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        
        # 設定フォーム
        self.create_config_form()
        
        # スクロールエリアにコンテンツウィジェットを設定
        scroll_area.setWidget(content_widget)
        
        # 現在のファイルパス
        self.current_file = "resources/config.toml"
        
        # 設定の読み込み
        self.load_config(show_message=self.show_messages)
    
    def create_file_buttons(self):
        """
        ファイル操作ボタンを作成する
        """
        # レイアウト
        button_layout = QHBoxLayout()
        self.layout.addLayout(button_layout)
        
        # 読み込みボタン
        self.load_button = QPushButton(self.tr("設定を読み込む"))
        self.load_button.clicked.connect(self.load_config)
        button_layout.addWidget(self.load_button)
        
        # 保存ボタン
        self.save_button = QPushButton(self.tr("設定を保存"))
        self.save_button.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_button)
        
        # 別名保存ボタン
        self.save_as_button = QPushButton(self.tr("名前を付けて保存"))
        self.save_as_button.clicked.connect(self.save_config_as)
        button_layout.addWidget(self.save_as_button)
        
        # ファイルパス表示
        self.file_path_label = QLabel()
        button_layout.addWidget(self.file_path_label, 1)
        
        # ファイルパスの更新
        self.update_file_path_label()
    
    def create_config_form(self):
        """
        設定フォームを作成する
        """
        # スクロール可能なフォーム
        self.form_widget = QWidget()
        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        
        # 基本設定グループ
        self.create_basic_settings()
        
        # ブラウザ設定グループ
        self.create_browser_settings()
        
        # スクリーンショット設定グループ
        self.create_screenshot_settings()
        
        # Excelレポート設定グループ
        self.create_excel_report_settings()
        
        # デバッグ設定グループ
        self.create_debug_settings()
        
        # スクロールエリアに追加
        self.layout.addWidget(self.form_widget)
    
    def create_basic_settings(self):
        """
        基本設定グループを作成する
        """
        group = QGroupBox(self.tr("基本設定"))
        self.form_layout.addWidget(group)
        
        form = QFormLayout(group)
        # フォームのラベル位置を左揃えに設定
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        # フィールド位置も左揃えに設定
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        # フォームのレイアウト方向を設定（ラベルを上、フィールドを下に配置）
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        
        # URL設定ファイル
        self.url_config_edit = QLineEdit()
        self.url_config_edit.setMinimumWidth(500)
        form.addRow(self.tr("URL設定ファイル:"), self.url_config_edit)
        
        # ユーザー設定ファイル
        self.user_config_edit = QLineEdit()
        self.user_config_edit.setMinimumWidth(500)
        form.addRow(self.tr("ユーザー設定ファイル:"), self.user_config_edit)
        
        # シナリオファイル
        self.scenario_config_edit = QLineEdit()
        self.scenario_config_edit.setMinimumWidth(500)
        form.addRow(self.tr("シナリオファイル:"), self.scenario_config_edit)
        
        # 遅延モード
        self.slow_mode_check = QCheckBox()
        form.addRow(self.tr("遅延モード:"), self.slow_mode_check)
        
        # アクション間の遅延時間
        self.action_delay_spin = QDoubleSpinBox()
        self.action_delay_spin.setRange(0.1, 10.0)
        self.action_delay_spin.setSingleStep(0.1)
        form.addRow(self.tr("アクション間の遅延時間:"), self.action_delay_spin)
        
        # タイムアウト
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        form.addRow(self.tr("タイムアウト (秒):"), self.timeout_spin)
        
        # リトライ回数
        self.retry_count_spin = QSpinBox()
        self.retry_count_spin.setRange(0, 10)
        form.addRow(self.tr("リトライ回数:"), self.retry_count_spin)
    
    def create_browser_settings(self):
        """
        ブラウザ設定グループを作成する
        """
        group = QGroupBox(self.tr("ブラウザ設定"))
        self.form_layout.addWidget(group)
        
        form = QFormLayout(group)
        # フォームのラベル位置を左揃えに設定
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        # フィールド位置も左揃えに設定
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        # フォームのレイアウト方向を設定（ラベルを上、フィールドを下に配置）
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        
        # ブラウザ
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["chrome", "firefox", "edge", "safari"])
        self.browser_combo.setMinimumWidth(200)  # 最小幅を設定
        form.addRow(self.tr("ブラウザ:"), self.browser_combo)
        
        # テストモード
        self.test_mode_check = QCheckBox()
        form.addRow(self.tr("テストモード:"), self.test_mode_check)
    
    def create_screenshot_settings(self):
        """
        スクリーンショット設定グループを作成する
        """
        group = QGroupBox(self.tr("スクリーンショット設定"))
        self.form_layout.addWidget(group)
        
        form = QFormLayout(group)
        # フォームのラベル位置を左揃えに設定
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        # フィールド位置も左揃えに設定
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        # フォームのレイアウト方向を設定（ラベルを上、フィールドを下に配置）
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        
        # スクリーンショットタイミング
        self.before_action_check = QCheckBox(self.tr("アクション前"))
        self.after_action_check = QCheckBox(self.tr("アクション後"))
        self.on_error_check = QCheckBox(self.tr("エラー時"))
        
        timing_layout = QHBoxLayout()
        timing_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        timing_layout.addWidget(self.before_action_check)
        timing_layout.addWidget(self.after_action_check)
        timing_layout.addWidget(self.on_error_check)
        
        form.addRow(self.tr("撮影タイミング:"), timing_layout)
    
    def create_excel_report_settings(self):
        """
        Excelレポート設定グループを作成する
        """
        group = QGroupBox(self.tr("Excelレポート設定"))
        self.form_layout.addWidget(group)
        
        form = QFormLayout(group)
        # フォームのラベル位置を左揃えに設定
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        # フィールド位置も左揃えに設定
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        # フォームのレイアウト方向を設定（ラベルを上、フィールドを下に配置）
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        
        # レポートタイトル
        self.report_title_edit = QLineEdit()
        self.report_title_edit.setMinimumWidth(300)  # 最小幅を設定
        form.addRow(self.tr("レポートタイトル:"), self.report_title_edit)
        
        # 会社名
        self.company_name_edit = QLineEdit()
        self.company_name_edit.setMinimumWidth(300)  # 最小幅を設定
        form.addRow(self.tr("会社名:"), self.company_name_edit)
        
        # プロジェクト名
        self.project_name_edit = QLineEdit()
        self.project_name_edit.setMinimumWidth(300)  # 最小幅を設定
        form.addRow(self.tr("プロジェクト名:"), self.project_name_edit)
        
        # ロゴ画像
        self.report_logo_edit = QLineEdit()
        self.report_logo_edit.setMinimumWidth(300)  # 最小幅を設定
        form.addRow(self.tr("ロゴ画像:"), self.report_logo_edit)
        
        # ズーム倍率
        self.zoom_scale_spin = QSpinBox()
        self.zoom_scale_spin.setRange(10, 200)
        self.zoom_scale_spin.setMinimumWidth(100)  # 最小幅を設定
        form.addRow(self.tr("ズーム倍率 (%):"), self.zoom_scale_spin)
        
        # タイムスタンプ
        self.include_timestamp_check = QCheckBox()
        form.addRow(self.tr("タイムスタンプを含める:"), self.include_timestamp_check)
        
        # タイムスタンプフォーマット
        self.timestamp_format_edit = QLineEdit()
        self.timestamp_format_edit.setMinimumWidth(200)  # 最小幅を設定
        form.addRow(self.tr("タイムスタンプフォーマット:"), self.timestamp_format_edit)
        
        # 色設定
        self.header_bg_color_button = QPushButton()
        self.header_bg_color_button.setMinimumWidth(100)  # 最小幅を設定
        self.header_bg_color_button.clicked.connect(lambda: self.select_color(self.header_bg_color_button))
        form.addRow(self.tr("ヘッダー背景色:"), self.header_bg_color_button)
        
        self.header_font_color_button = QPushButton()
        self.header_font_color_button.setMinimumWidth(100)  # 最小幅を設定
        self.header_font_color_button.clicked.connect(lambda: self.select_color(self.header_font_color_button))
        form.addRow(self.tr("ヘッダーフォント色:"), self.header_font_color_button)
        
        self.alt_row_color_button = QPushButton()
        self.alt_row_color_button.setMinimumWidth(100)  # 最小幅を設定
        self.alt_row_color_button.clicked.connect(lambda: self.select_color(self.alt_row_color_button))
        form.addRow(self.tr("交互行の背景色:"), self.alt_row_color_button)
        
        self.success_color_button = QPushButton()
        self.success_color_button.clicked.connect(lambda: self.select_color(self.success_color_button))
        form.addRow(self.tr("成功セルの背景色:"), self.success_color_button)
        
        self.failure_color_button = QPushButton()
        self.failure_color_button.clicked.connect(lambda: self.select_color(self.failure_color_button))
        form.addRow(self.tr("失敗セルの背景色:"), self.failure_color_button)
        
        self.screenshot_title_cell_color_button = QPushButton()
        self.screenshot_title_cell_color_button.clicked.connect(lambda: self.select_color(self.screenshot_title_cell_color_button))
        form.addRow(self.tr("スクリーンショットタイトル背景色:"), self.screenshot_title_cell_color_button)
    
    def create_debug_settings(self):
        """
        デバッグ設定グループを作成する
        """
        group = QGroupBox(self.tr("デバッグ設定"))
        self.form_layout.addWidget(group)
        
        form = QFormLayout(group)
        # フォームのラベル位置を左揃えに設定
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        # フィールド位置も左揃えに設定
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        # フォームのレイアウト方向を設定（ラベルを上、フィールドを下に配置）
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        
        # デバッグモード
        self.debug_mode_check = QCheckBox()
        form.addRow(self.tr("デバッグモード:"), self.debug_mode_check)
    
    def update_file_path_label(self):
        """
        ファイルパスラベルを更新する
        """
        self.file_path_label.setText(self.tr("ファイル: ") + self.current_file)
    
    def load_config(self, show_message=True):
        """
        設定ファイルを読み込む
        
        Args:
            show_message: メッセージボックスを表示するかどうか
        """
        try:
            config = load_toml(self.current_file)
            if config is None:
                raise ValueError("設定ファイルの読み込みに失敗しました")
            
            # 基本設定
            self.url_config_edit.setText(str(config.get('url_config', '')))
            self.user_config_edit.setText(str(config.get('user_config', '')))
            self.scenario_config_edit.setText(str(config.get('scenario_config', '')))
            self.slow_mode_check.setChecked(bool(config.get('slow_mode', False)))
            self.action_delay_spin.setValue(float(config.get('action_delay', 1.5)))
            self.timeout_spin.setValue(int(config.get('timeout', 30)))
            self.retry_count_spin.setValue(int(config.get('retry_count', 3)))
            
            # ブラウザ設定
            browser = str(config.get('browser', 'chrome'))
            index = self.browser_combo.findText(browser)
            if index >= 0:
                self.browser_combo.setCurrentIndex(index)
            self.test_mode_check.setChecked(bool(config.get('test_mode', False)))
            
            # スクリーンショット設定
            screenshot_timing = config.get('screenshot_timing', [])
            self.before_action_check.setChecked('before_action' in screenshot_timing)
            self.after_action_check.setChecked('after_action' in screenshot_timing)
            self.on_error_check.setChecked('on_error' in screenshot_timing)
            
            # Excelレポート設定
            self.report_title_edit.setText(str(config.get('report_title', '')))
            self.company_name_edit.setText(str(config.get('company_name', '')))
            self.project_name_edit.setText(str(config.get('project_name', '')))
            self.report_logo_edit.setText(str(config.get('report_logo', '')))
            
            if show_message:
                QMessageBox.information(self, self.tr("設定読み込み"), self.tr("設定を読み込みました"))
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("エラー"), 
                               self.tr("設定ファイルを読み込めませんでした: ") + str(e))
            self.zoom_scale_spin.setValue(config.get('zoom_scale', 50))
            self.include_timestamp_check.setChecked(config.get('include_timestamp', True))
            self.timestamp_format_edit.setText(config.get('timestamp_format', '%Y-%m-%d %H:%M:%S'))
            
            # 色設定
            self.set_button_color(self.header_bg_color_button, config.get('header_bg_color', '#4472C4'))
            self.set_button_color(self.header_font_color_button, config.get('header_font_color', '#FFFFFF'))
            self.set_button_color(self.alt_row_color_button, config.get('alt_row_color', '#E6F0FF'))
            self.set_button_color(self.success_color_button, config.get('success_color', '#C6EFCE'))
            self.set_button_color(self.failure_color_button, config.get('failure_color', '#FFC7CE'))
            self.set_button_color(self.screenshot_title_cell_color_button, config.get('screenshot_title_cell_color', '#ffebcd'))
            
            # デバッグ設定
            self.debug_mode_check.setChecked(config.get('debug_mode', False))
            
            QMessageBox.information(self, self.tr("設定読み込み"), self.tr("設定を読み込みました"))
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("エラー"), 
                               self.tr("設定ファイルを読み込めませんでした: ") + str(e))
    
    def save_config(self):
        """
        設定ファイルを保存する
        """
        try:
            # 設定値を取得
            config_dict = self.get_config_dict()
            
            # 保存
            if save_toml(self.current_file, config_dict):
                QMessageBox.information(self, self.tr("設定保存"), self.tr("設定を保存しました"))
            else:
                raise ValueError("設定ファイルの保存に失敗しました")
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("エラー"), 
                               self.tr("設定ファイルを保存できませんでした: ") + str(e))
    
    def save_config_as(self):
        """
        設定ファイルを別名で保存する
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self, self.tr("設定ファイルを保存"), 
            "resources", self.tr("TOMLファイル (*.toml)")
        )
        
        if file_path:
            old_file = self.current_file
            self.current_file = file_path
            
            try:
                self.save_config()
                self.update_file_path_label()
            except Exception as e:
                self.current_file = old_file
                self.update_file_path_label()
                raise e
    
    def get_config_dict(self):
        """
        設定値を辞書として取得する
        
        Returns:
            dict: 設定値の辞書
        """
        # スクリーンショットタイミング
        screenshot_timing = []
        if self.before_action_check.isChecked():
            screenshot_timing.append("before_action")
        if self.after_action_check.isChecked():
            screenshot_timing.append("after_action")
        if self.on_error_check.isChecked():
            screenshot_timing.append("on_error")
        
        # 設定辞書の作成
        config = {
            # 基本設定
            'url_config': self.url_config_edit.text(),
            'user_config': self.user_config_edit.text(),
            'scenario_config': self.scenario_config_edit.text(),
            'slow_mode': self.slow_mode_check.isChecked(),
            'action_delay': self.action_delay_spin.value(),
            'timeout': self.timeout_spin.value(),
            'retry_count': self.retry_count_spin.value(),
            
            # ブラウザ設定
            'browser': self.browser_combo.currentText(),
            'test_mode': self.test_mode_check.isChecked(),
            
            # スクリーンショット設定
            'screenshot_timing': screenshot_timing,
            
            # Excelレポート設定
            'report_title': self.report_title_edit.text(),
            'company_name': self.company_name_edit.text(),
            'project_name': self.project_name_edit.text(),
            'report_logo': self.report_logo_edit.text(),
            'zoom_scale': self.zoom_scale_spin.value(),
            'include_timestamp': self.include_timestamp_check.isChecked(),
            'timestamp_format': self.timestamp_format_edit.text(),
            'header_bg_color': self.header_bg_color_button.property('color'),
            'header_font_color': self.header_font_color_button.property('color'),
            'alt_row_color': self.alt_row_color_button.property('color'),
            'success_color': self.success_color_button.property('color'),
            'failure_color': self.failure_color_button.property('color'),
            'screenshot_title_cell_color': self.screenshot_title_cell_color_button.property('color'),
            
            # デバッグ設定
            'debug_mode': self.debug_mode_check.isChecked(),
        }
        
        return config
    
    def select_color(self, button):
        """
        色選択ダイアログを表示する
        
        Args:
            button: 色を設定するボタン
        """
        current_color = QColor(button.property('color') or '#FFFFFF')
        color = QColorDialog.getColor(current_color, self, self.tr("色を選択"))
        
        if color.isValid():
            self.set_button_color(button, color.name())
    
    def set_button_color(self, button, color):
        """
        ボタンの背景色を設定する
        
        Args:
            button: 色を設定するボタン
            color: 色コード（例: '#FF0000'）
        """
        button.setProperty('color', color)
        button.setStyleSheet(f"background-color: {color}; color: {'#000000' if is_light_color(color) else '#FFFFFF'}")
        button.setText(color)
    
    def retranslate_ui(self):
        """
        UIテキストの再翻訳
        """
        # ボタンの再翻訳
        self.load_button.setText(self.tr("設定を読み込む"))
        self.save_button.setText(self.tr("設定を保存"))
        self.save_as_button.setText(self.tr("名前を付けて保存"))
        
        # ファイルパスラベルの再翻訳
        self.update_file_path_label()
        
        # グループボックスの再翻訳
        for group in self.findChildren(QGroupBox):
            if group.title() == "Basic Settings":
                group.setTitle(self.tr("基本設定"))
            elif group.title() == "Browser Settings":
                group.setTitle(self.tr("ブラウザ設定"))
            elif group.title() == "Screenshot Settings":
                group.setTitle(self.tr("スクリーンショット設定"))
            elif group.title() == "Excel Report Settings":
                group.setTitle(self.tr("Excelレポート設定"))
            elif group.title() == "Debug Settings":
                group.setTitle(self.tr("デバッグ設定"))
        
        # チェックボックスの再翻訳
        self.before_action_check.setText(self.tr("アクション前"))
        self.after_action_check.setText(self.tr("アクション後"))
        self.on_error_check.setText(self.tr("エラー時"))

def is_light_color(color):
    """
    色が明るいかどうかを判定する
    
    Args:
        color: 色コード（例: '#FF0000'）
    
    Returns:
        bool: 明るい色の場合はTrue
    """
    # #で始まる場合は除去
    if color.startswith('#'):
        color = color[1:]
    
    # 16進数からRGB値に変換
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    # 明るさの計算（YIQ色空間の輝度）
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    
    # 128より大きければ明るい色と判定
    return brightness > 128
