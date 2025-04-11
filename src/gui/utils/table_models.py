"""
テーブルモデルクラス
"""
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
import csv
import os

from src.utils.constants import ScenarioColumn, ExcelOutput

class ScenarioTableModel(QAbstractTableModel):
    """
    シナリオファイル用のテーブルモデル
    """
    def __init__(self):
        super().__init__()
        self.headers = []
        self.data = []
        self.clipboard = None
        self.modified = False  # 変更フラグ
    
    def rowCount(self, parent=None):
        return len(self.data)
    
    def columnCount(self, parent=None):
        return len(self.headers) if self.headers else 0
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        if index.row() >= len(self.data) or index.column() >= len(self.headers):
            return None
        
        # データの列数が足りない場合は空文字を返す
        if index.column() >= len(self.data[index.row()]):
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return ""
            return None
        
        # Excel出力列は特別処理
        if index.column() == ScenarioColumn.EXCEL_OUTPUT:
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                # 表示用と編集用の値を返す
                value = self.data[index.row()][index.column()].lower()
                if value in ExcelOutput.YES_VALUES:
                    return "yes"
                else:
                    return "no"
        else:
            # 他の列は通常通り
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return self.data[index.row()][index.column()]
        
        return None
    
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        
        # 操作IDは編集不可
        if index.column() == ScenarioColumn.OPERATION_ID:
            return False
        
        # インデックスの範囲チェック
        if index.row() >= len(self.data):
            return False
        
        # データの列数が足りない場合は拡張
        while index.column() >= len(self.data[index.row()]):
            self.data[index.row()].append("")
        
        if role == Qt.ItemDataRole.EditRole:
            # Excel出力列の場合は値を正規化
            if index.column() == ScenarioColumn.EXCEL_OUTPUT:
                # 大文字小文字を区別せず、yesまたはnoに正規化
                normalized_value = str(value).lower()
                if normalized_value in ExcelOutput.YES_VALUES:
                    value = ExcelOutput.YES
                else:
                    value = ExcelOutput.NO
            
            # 値が変更された場合のみ変更フラグを立てる
            if self.data[index.row()][index.column()] != value:
                self.data[index.row()][index.column()] = value
                self.modified = True
                self.dataChanged.emit(index, index)
            return True
        
        return False
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section] if section < len(self.headers) else None
        return None
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        
        # 操作IDは編集不可
        if index.column() == ScenarioColumn.OPERATION_ID:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        
        # すべての編集可能な列に同じフラグを設定
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
    
    def setHeaders(self, headers):
        self.headers = headers
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(headers) - 1)
    
    def clear(self):
        self.beginResetModel()
        self.data = []
        self.modified = False  # 変更フラグをリセット
        self.endResetModel()
    
    def load_from_csv(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                
                self.beginResetModel()
                self.headers = headers
                self.data = []
                
                for row in reader:
                    # 足りない列を空文字で埋める
                    while len(row) < len(headers):
                        row.append("")
                    self.data.append(row)
                
                self.endResetModel()
                
                # 操作IDの自動採番
                self.renumber_operation_ids()
                
                self.modified = False  # 変更フラグをリセット
                return True
        except Exception as e:
            print(f"CSV読み込みエラー: {e}")
            return False
    
    def save_to_csv(self, file_path):
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
                writer.writerows(self.data)
            
            self.modified = False  # 変更フラグをリセット
            return True
        except Exception as e:
            print(f"CSV保存エラー: {e}")
            return False
    
    def add_row(self, position=None):
        """
        新しい行を追加する
        
        Args:
            position: 追加する位置（指定がない場合は末尾に追加）
        """
        # 新しい行を作成
        row = [""] * len(self.headers)
        row[0] = str(len(self.data) + 1)  # 操作ID（後で自動採番される）
        
        # 追加位置の決定
        if position is None or position < 0 or position > len(self.data):
            position = len(self.data)  # 末尾に追加
        
        # 行の挿入
        self.beginInsertRows(QModelIndex(), position, position)
        self.data.insert(position, row)
        self.endInsertRows()
        
        # 操作IDの自動採番
        self.renumber_operation_ids()
        self.modified = True  # 変更フラグを立てる
        
        # 追加した行の位置を返す
        return position
    
    def delete_row(self, row):
        if 0 <= row < len(self.data):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.data[row]
            self.endRemoveRows()
            
            # 操作IDの自動採番
            self.renumber_operation_ids()
            self.modified = True  # 変更フラグを立てる
    
    def move_row_up(self, row):
        if row > 0:
            self.beginMoveRows(QModelIndex(), row, row, QModelIndex(), row - 1)
            self.data[row], self.data[row - 1] = self.data[row - 1], self.data[row]
            self.endMoveRows()
            
            # 操作IDの自動採番
            self.renumber_operation_ids()
            self.modified = True  # 変更フラグを立てる
    
    def move_row_down(self, row):
        if row < len(self.data) - 1:
            # Qt's beginMoveRows has a different behavior for moving down
            self.beginMoveRows(QModelIndex(), row, row, QModelIndex(), row + 2)
            self.data[row], self.data[row + 1] = self.data[row + 1], self.data[row]
            self.endMoveRows()
            
            # 操作IDの自動採番
            self.renumber_operation_ids()
            self.modified = True  # 変更フラグを立てる
    
    def cut_row(self, row):
        if 0 <= row < len(self.data):
            self.clipboard = self.data[row].copy()
            self.delete_row(row)
            # delete_row内で変更フラグが立てられる
    
    def paste_row(self, row):
        if self.clipboard and 0 <= row < len(self.data):
            new_row = self.clipboard.copy()
            
            self.beginInsertRows(QModelIndex(), row, row)
            self.data.insert(row, new_row)
            self.endInsertRows()
            
            # 操作IDの自動採番
            self.renumber_operation_ids()
            self.modified = True  # 変更フラグを立てる
    
    def renumber_operation_ids(self):
        # 操作IDを1から順に振り直す
        for i in range(len(self.data)):
            self.data[i][0] = str(i + 1)
        
        # データ変更通知
        if self.data:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(len(self.data) - 1, 0)
            )
    
    def is_modified(self):
        """
        変更されているかどうかを返す
        
        Returns:
            bool: 変更されている場合はTrue、そうでない場合はFalse
        """
        return self.modified
