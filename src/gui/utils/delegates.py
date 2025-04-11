"""
カスタムデリゲートクラス
"""
from PyQt6.QtWidgets import QStyledItemDelegate, QComboBox, QCheckBox, QStyle, QApplication, QStyleOptionButton, QStyleOptionViewItem
from PyQt6.QtCore import Qt, QRect, QEvent, QPoint
from PyQt6.QtGui import QPalette, QPen

class ComboBoxDelegate(QStyledItemDelegate):
    """
    コンボボックスデリゲート
    """
    def __init__(self, parent, items):
        super().__init__(parent)
        self.items = items
    
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.items)
        return editor
    
    def setEditorData(self, editor, index):
        try:
            model = index.model()
            if hasattr(model, 'data') and callable(model.data):
                value = model.data(index, Qt.ItemDataRole.EditRole)
                if value:
                    idx = editor.findText(value)
                    if idx >= 0:
                        editor.setCurrentIndex(idx)
        except Exception as e:
            print(f"ComboBoxDelegate.setEditorData error: {e}")
    
    def setModelData(self, editor, model, index):
        try:
            if hasattr(model, 'setData') and callable(model.setData):
                value = editor.currentText()
                model.setData(index, value, Qt.ItemDataRole.EditRole)
        except Exception as e:
            print(f"ComboBoxDelegate.setModelData error: {e}")
    
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class CheckBoxDelegate(QStyledItemDelegate):
    """
    チェックボックスデリゲート
    """
    def __init__(self, parent):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        editor = QCheckBox(parent)
        return editor
    
    def setEditorData(self, editor, index):
        try:
            model = index.model()
            if hasattr(model, 'data') and callable(model.data):
                value = model.data(index, Qt.ItemDataRole.CheckStateRole)
                if value is not None:
                    editor.setChecked(value == Qt.CheckState.Checked)
        except Exception as e:
            print(f"CheckBoxDelegate.setEditorData error: {e}")
    
    def setModelData(self, editor, model, index):
        try:
            if hasattr(model, 'setData') and callable(model.setData):
                value = Qt.CheckState.Checked if editor.isChecked() else Qt.CheckState.Unchecked
                model.setData(index, value, Qt.ItemDataRole.CheckStateRole)
        except Exception as e:
            print(f"CheckBoxDelegate.setModelData error: {e}")
    
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
    
    def paint(self, painter, option, index):
        """
        チェックボックスを描画する（システムのチェックボックスを使用）
        """
        try:
            # チェックボックスを含まないオプションを作成
            option_copy = QStyleOptionViewItem(option)
            self.initStyleOption(option_copy, index)
            
            # チェックボックス表示を無効化
            option_copy.features &= ~QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator
            
            # 背景と選択状態を描画
            QApplication.style().drawControl(QStyle.ControlElement.CE_ItemViewItem, option_copy, painter, option.widget)
            
            # チェックボックスの状態を取得
            value = index.data(Qt.ItemDataRole.CheckStateRole)
            if value is not None:
                checked = (value == Qt.CheckState.Checked)
                
                # チェックボックスの位置を計算（セルの中央）
                rect = option.rect
                x = rect.center().x() - 7  # チェックボックスの幅の半分程度
                y = rect.center().y() - 7  # チェックボックスの高さの半分程度
                
                # 描画コンテキストを保存
                painter.save()
                
                # チェックボックスを描画
                if checked:
                    # チェックされた状態を描画
                    painter.setPen(QPen(Qt.GlobalColor.black, 2))
                    painter.drawRect(x - 2, y - 2, 14, 14)
                    painter.drawLine(x, y + 5, x + 4, y + 9)
                    painter.drawLine(x + 4, y + 9, x + 10, y - 1)
                else:
                    # チェックされていない状態を描画
                    painter.setPen(QPen(Qt.GlobalColor.black, 1))
                    painter.drawRect(x - 2, y - 2, 14, 14)
                
                # 描画コンテキストを復元
                painter.restore()
                
        except Exception as e:
            print(f"CheckBoxDelegate.paint error: {e}")
            # エラーが発生した場合は、チェックボックス表示を抑制したデフォルト描画を行う
            option_copy = QStyleOptionViewItem(option)
            option_copy.features &= ~QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator
            self.initStyleOption(option_copy, index)
            QApplication.style().drawControl(QStyle.ControlElement.CE_ItemViewItem, option_copy, painter, option.widget)
    
    def editorEvent(self, event, model, option, index):
        """
        マウスクリックでチェックボックスの状態を切り替える
        """
        if event.type() == QEvent.Type.MouseButtonRelease:
            # クリックされた場合、チェック状態を反転
            current_state = index.data(Qt.ItemDataRole.CheckStateRole)
            if current_state == Qt.CheckState.Checked:
                model.setData(index, Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
            else:
                model.setData(index, Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
            return True
        return super().editorEvent(event, model, option, index)
