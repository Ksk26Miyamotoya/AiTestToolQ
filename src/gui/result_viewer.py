"""
テスト結果表示画面
"""
import json
import os
import subprocess

from PyQt6.QtCore import Qt, QDir
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTextEdit, QFileDialog, QTreeView,
                             QSplitter,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox)

# PyQt6のバージョンによってQFileSystemModelの場所が異なる場合がある
try:
    from PyQt6.QtWidgets import QFileSystemModel
except ImportError:
    try:
        from PyQt6.QtCore import QFileSystemModel
    except ImportError:
        from PyQt6.QtGui import QFileSystemModel

class ResultViewer(QWidget):
    """
    テスト結果表示画面
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # レイアウトの設定
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # 結果ディレクトリ選択
        self.create_directory_selector()
        
        # スプリッター
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(splitter)
        
        # ファイルツリー
        self.create_file_tree(splitter)
        
        # 結果表示部分
        self.create_result_view(splitter)
        
        # スプリッターの初期サイズ
        splitter.setSizes([200, 600])
        
        # 最新の結果ディレクトリを選択
        self.select_latest_result()
    
    def create_directory_selector(self):
        """
        結果ディレクトリ選択部分を作成する
        """
        # レイアウト
        selector_layout = QHBoxLayout()
        self.layout.addLayout(selector_layout)
        
        # ラベル
        selector_layout.addWidget(QLabel(self.tr("結果ディレクトリ:")))
        
        # コンボボックス
        self.dir_combo = QComboBox()
        self.dir_combo.setEditable(True)
        selector_layout.addWidget(self.dir_combo, 1)
        
        # 更新ボタン
        refresh_button = QPushButton(self.tr("更新"))
        refresh_button.clicked.connect(self.refresh_directories)
        selector_layout.addWidget(refresh_button)
        
        # 参照ボタン
        browse_button = QPushButton(self.tr("参照..."))
        browse_button.clicked.connect(self.browse_directory)
        selector_layout.addWidget(browse_button)
        
        # Finderで開くボタン
        open_finder_button = QPushButton(self.tr("Finderで開く"))
        open_finder_button.clicked.connect(self.open_in_finder)
        selector_layout.addWidget(open_finder_button)
        
        # ディレクトリ一覧の更新
        self.refresh_directories()
        
        # シグナル接続
        self.dir_combo.currentIndexChanged.connect(self.on_directory_changed)
    
    def create_file_tree(self, parent):
        """
        ファイルツリーを作成する
        """
        # ツリービュー
        self.file_tree = QTreeView(parent)
        self.file_tree.setHeaderHidden(True)
        
        # ファイルシステムモデル
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        self.file_tree.setModel(self.file_model)
        
        # 列の設定
        self.file_tree.setColumnHidden(1, True)  # サイズ
        self.file_tree.setColumnHidden(2, True)  # タイプ
        self.file_tree.setColumnHidden(3, True)  # 更新日時
        
        # シグナル接続
        self.file_tree.clicked.connect(self.on_file_selected)
    
    def create_result_view(self, parent):
        """
        結果表示部分を作成する
        """
        # コンテナウィジェット
        result_widget = QWidget(parent)
        result_layout = QVBoxLayout(result_widget)
        result_layout.setContentsMargins(0, 0, 0, 0)
        
        # テーブル
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels([self.tr("項目"), self.tr("値")])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        result_layout.addWidget(self.result_table)
        
        # JSONビューア
        self.json_viewer = QTextEdit()
        self.json_viewer.setReadOnly(True)
        result_layout.addWidget(self.json_viewer)
        
        # 初期状態では非表示
        self.json_viewer.hide()
    
    def refresh_directories(self):
        """
        結果ディレクトリ一覧を更新する
        """
        self.dir_combo.clear()
        
        # 結果ディレクトリの一覧を取得
        output_dir = "output"
        if os.path.exists(output_dir):
            result_dirs = [d for d in os.listdir(output_dir) 
                          if os.path.isdir(os.path.join(output_dir, d))]
            
            # 日付順にソート（新しい順）
            result_dirs.sort(reverse=True)
            
            for dir_name in result_dirs:
                dir_path = os.path.join(output_dir, dir_name)
                self.dir_combo.addItem(dir_name, dir_path)
    
    def browse_directory(self):
        """
        ディレクトリ選択ダイアログを表示する
        """
        dir_path = QFileDialog.getExistingDirectory(
            self, self.tr("結果ディレクトリを選択"), "output"
        )
        
        if dir_path:
            # コンボボックスに追加
            dir_name = os.path.basename(dir_path)
            index = self.dir_combo.findText(dir_name)
            
            if index >= 0:
                self.dir_combo.setCurrentIndex(index)
            else:
                self.dir_combo.addItem(dir_name, dir_path)
                self.dir_combo.setCurrentIndex(self.dir_combo.count() - 1)
    
    def open_in_finder(self):
        """
        Finderで選択中のディレクトリを開く
        """
        dir_path = self.dir_combo.currentData()
        if dir_path and os.path.exists(dir_path):
            if os.name == 'nt':  # Windows
                os.startfile(dir_path)
            elif os.name == 'posix':  # macOS, Linux
                if os.path.exists('/usr/bin/open'):  # macOS
                    subprocess.Popen(['open', dir_path])
                else:  # Linux
                    subprocess.Popen(['xdg-open', dir_path])
    
    def select_latest_result(self):
        """
        最新の結果ディレクトリを選択する
        """
        if self.dir_combo.count() > 0:
            self.dir_combo.setCurrentIndex(0)
    
    def on_directory_changed(self, index):
        """
        ディレクトリ選択変更時の処理
        """
        if index >= 0:
            dir_path = self.dir_combo.itemData(index)
            if dir_path and os.path.exists(dir_path):
                # ファイルツリーのルートパスを設定
                self.file_tree.setRootIndex(self.file_model.index(dir_path))
                
                # test_results.jsonを探して表示
                json_path = os.path.join(dir_path, "result", "test_results.json")
                if os.path.exists(json_path):
                    self.load_json_results(json_path)
    
    def on_file_selected(self, index):
        """
        ファイル選択時の処理
        """
        file_path = self.file_model.filePath(index)
        
        # JSONファイルの場合
        if file_path.endswith('.json'):
            self.load_json_results(file_path)
        # 画像ファイルの場合
        elif file_path.endswith(('.png', '.jpg', '.jpeg')):
            self.open_image(file_path)
        # Excelファイルの場合
        elif file_path.endswith(('.xlsx', '.xls')):
            self.open_excel(file_path)
    
    def load_json_results(self, json_path):
        """
        JSONファイルを読み込んで表示する
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # テーブルをクリア
            self.result_table.setRowCount(0)
            
            # JSONデータをテーブルに表示
            if isinstance(data, dict):
                for i, (key, value) in enumerate(data.items()):
                    self.result_table.insertRow(i)
                    self.result_table.setItem(i, 0, QTableWidgetItem(str(key)))
                    
                    if isinstance(value, (dict, list)):
                        self.result_table.setItem(i, 1, QTableWidgetItem(str(type(value).__name__)))
                    else:
                        self.result_table.setItem(i, 1, QTableWidgetItem(str(value)))
            
            # JSON全体を表示
            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
            self.json_viewer.setText(formatted_json)
            self.json_viewer.show()
            
        except Exception as e:
            self.json_viewer.setText(f"エラー: JSONファイルを読み込めませんでした: {str(e)}")
            self.json_viewer.show()
    
    def open_image(self, image_path):
        """
        画像ファイルを外部ビューアで開く
        """
        if os.name == 'nt':  # Windows
            os.startfile(image_path)
        elif os.name == 'posix':  # macOS, Linux
            if os.path.exists('/usr/bin/open'):  # macOS
                subprocess.Popen(['open', image_path])
            else:  # Linux
                subprocess.Popen(['xdg-open', image_path])
    
    def open_excel(self, excel_path):
        """
        Excelファイルを外部ビューアで開く
        """
        if os.name == 'nt':  # Windows
            os.startfile(excel_path)
        elif os.name == 'posix':  # macOS, Linux
            if os.path.exists('/usr/bin/open'):  # macOS
                subprocess.Popen(['open', excel_path])
            else:  # Linux
                subprocess.Popen(['xdg-open', excel_path])
    
    def retranslate_ui(self):
        """
        UIテキストの再翻訳
        """
        # ボタンの再翻訳
        self.findChild(QPushButton, "").setText(self.tr("更新"))
        self.findChild(QPushButton, "").setText(self.tr("参照..."))
        self.findChild(QPushButton, "").setText(self.tr("Finderで開く"))
        
        # テーブルヘッダーの再翻訳
        self.result_table.setHorizontalHeaderLabels([self.tr("項目"), self.tr("値")])
