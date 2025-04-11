"""
ファイル選択ウィジェット
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QPushButton, QFileDialog, QLabel
from PyQt6.QtCore import pyqtSignal
import os
import glob

class FileSelector(QWidget):
    """
    ファイル選択ウィジェット
    """
    fileSelected = pyqtSignal(str)
    
    def __init__(self, label_text, directory, file_filter="*.*", parent=None):
        super().__init__(parent)
        
        self.directory = directory
        self.file_filter = file_filter
        
        # レイアウト
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ラベル
        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        
        # コンボボックス
        self.combo = QComboBox()
        self.combo.setEditable(True)
        layout.addWidget(self.combo, 1)
        
        # 更新ボタン
        self.refresh_button = QPushButton("更新")
        self.refresh_button.clicked.connect(self.refresh_files)
        layout.addWidget(self.refresh_button)
        
        # 参照ボタン
        self.browse_button = QPushButton("参照...")
        self.browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_button)
        
        # ファイル一覧の更新
        self.refresh_files()
        
        # シグナル接続
        self.combo.currentIndexChanged.connect(self._on_selection_changed)
    
    def refresh_files(self):
        """
        ファイル一覧を更新する
        """
        self.combo.clear()
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(self.directory, exist_ok=True)
        
        # ファイル一覧を取得
        pattern = os.path.join(self.directory, self.file_filter)
        files = glob.glob(pattern)
        
        for file_path in sorted(files):
            self.combo.addItem(os.path.basename(file_path), file_path)
    
    def browse_file(self):
        """
        ファイル選択ダイアログを表示する
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "ファイルを選択", self.directory, f"Files ({self.file_filter})"
        )
        
        if file_path:
            # コンボボックスに追加
            basename = os.path.basename(file_path)
            index = self.combo.findText(basename)
            
            if index >= 0:
                self.combo.setCurrentIndex(index)
            else:
                self.combo.addItem(basename, file_path)
                self.combo.setCurrentIndex(self.combo.count() - 1)
    
    def get_selected_file(self):
        """
        選択されたファイルのパスを取得する
        
        Returns:
            str: ファイルパス
        """
        return self.combo.currentData()
    
    def set_selected_file(self, file_path):
        """
        ファイルを選択する
        
        Args:
            file_path: ファイルパス
        """
        if not file_path:
            return
            
        basename = os.path.basename(file_path)
        index = self.combo.findText(basename)
        
        if index >= 0:
            self.combo.setCurrentIndex(index)
        else:
            self.combo.addItem(basename, file_path)
            self.combo.setCurrentIndex(self.combo.count() - 1)
    
    def _on_selection_changed(self, index):
        """
        選択変更時の処理
        """
        if index >= 0:
            file_path = self.combo.itemData(index)
            self.fileSelected.emit(file_path)
