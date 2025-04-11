"""
シナリオエディタ画面
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableView, QFileDialog, QMessageBox, QToolBar,
                             QHeaderView)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QItemSelectionModel

from .utils.table_models import ScenarioTableModel
from .utils.delegates import ComboBoxDelegate, CheckBoxDelegate
from src.utils.constants import OperationType, ScenarioColumn

class ScenarioEditor(QWidget):
    """
    シナリオエディタ画面
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # レイアウトの設定
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # ツールバーの作成
        self.create_toolbar()
        
        # テーブルビューの作成
        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)
        
        # モデルの作成
        self.model = ScenarioTableModel()
        self.table_view.setModel(self.model)
        
        # テーブルの設定
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setAlternatingRowColors(True)
        
        # 行選択モードを設定
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        
        # デフォルトのヘッダーを設定
        self.model.setHeaders(ScenarioColumn.HEADERS)
        
        # デリゲートの設定
        self.table_view.setItemDelegateForColumn(ScenarioColumn.OPERATION_TYPE, ComboBoxDelegate(self, OperationType.ALL))
        self.table_view.setItemDelegateForColumn(ScenarioColumn.EXCEL_OUTPUT, ComboBoxDelegate(self, ["yes", "no"]))
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setAlternatingRowColors(True)
        
        # 行選択モードを設定
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        
        # デフォルトのヘッダーを設定
        self.model.setHeaders(ScenarioColumn.HEADERS)
        
        # デリゲートの設定
        self.table_view.setItemDelegateForColumn(ScenarioColumn.OPERATION_TYPE, ComboBoxDelegate(self, OperationType.ALL))
        self.table_view.setItemDelegateForColumn(ScenarioColumn.EXCEL_OUTPUT, ComboBoxDelegate(self, ["yes", "no"]))
        
        # 列幅の初期設定
        self.set_default_column_widths()
        
        # 現在のファイルパス
        self.current_file = None
        
    def create_toolbar(self):
        """
        ツールバーを作成する
        """
        # ツールバー
        toolbar = QToolBar()
        self.layout.addWidget(toolbar)
        
        # 新規作成アクション
        new_action = QAction(self.tr("新規"), self)
        new_action.triggered.connect(self.new_scenario)
        toolbar.addAction(new_action)
        
        # 開くアクション
        open_action = QAction(self.tr("開く"), self)
        open_action.triggered.connect(self.open_scenario)
        toolbar.addAction(open_action)
        
        # 保存アクション
        save_action = QAction(self.tr("保存"), self)
        save_action.triggered.connect(self.save_scenario)
        toolbar.addAction(save_action)
        
        # 名前を付けて保存アクション
        save_as_action = QAction(self.tr("名前を付けて保存"), self)
        save_as_action.triggered.connect(self.save_scenario_as)
        toolbar.addAction(save_as_action)
        
        toolbar.addSeparator()
        
        # 行追加アクション
        add_row_action = QAction(self.tr("行追加"), self)
        add_row_action.triggered.connect(self.add_row)
        toolbar.addAction(add_row_action)
        
        # 行削除アクション
        delete_row_action = QAction(self.tr("行削除"), self)
        delete_row_action.triggered.connect(self.delete_row)
        toolbar.addAction(delete_row_action)
        
        # 上へ移動アクション
        move_up_action = QAction(self.tr("上へ"), self)
        move_up_action.triggered.connect(self.move_row_up)
        toolbar.addAction(move_up_action)
        
        # 下へ移動アクション
        move_down_action = QAction(self.tr("下へ"), self)
        move_down_action.triggered.connect(self.move_row_down)
        toolbar.addAction(move_down_action)
        
        toolbar.addSeparator()
        
        # 切り取りアクション
        cut_action = QAction(self.tr("切り取り"), self)
        cut_action.triggered.connect(self.cut_row)
        toolbar.addAction(cut_action)
        
        # 貼り付けアクション
        paste_action = QAction(self.tr("貼り付け"), self)
        paste_action.triggered.connect(self.paste_row)
        toolbar.addAction(paste_action)
    
    def new_scenario(self):
        """
        新規シナリオを作成する
        """
        # 変更があれば保存確認
        if self.check_unsaved_changes():
            return
        
        # モデルをクリア
        self.model.clear()
        self.current_file = None
    
    def open_scenario(self):
        """
        シナリオファイルを開く
        """
        # 変更があれば保存確認
        if self.check_unsaved_changes():
            return
        
        # ファイル選択ダイアログ
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.tr("シナリオファイルを開く"), "", self.tr("CSVファイル (*.csv)")
        )
        
        if file_path:
            if self.model.load_from_csv(file_path):
                self.current_file = file_path
            else:
                QMessageBox.critical(self, self.tr("エラー"), self.tr("ファイルを開けませんでした"))
    
    def save_scenario(self):
        """
        シナリオファイルを保存する
        """
        if not self.current_file:
            return self.save_scenario_as()
        
        if self.model.save_to_csv(self.current_file):
            QMessageBox.information(self, self.tr("保存完了"), self.tr("ファイルを保存しました"))
            return True
        else:
            QMessageBox.critical(self, self.tr("エラー"), self.tr("ファイルを保存できませんでした"))
            return False
    
    def save_scenario_as(self):
        """
        シナリオファイルを名前を付けて保存する
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self, self.tr("名前を付けて保存"), "", self.tr("CSVファイル (*.csv)")
        )
        
        if file_path:
            # 拡張子がなければ追加
            if not file_path.endswith('.csv'):
                file_path += '.csv'
            
            if self.model.save_to_csv(file_path):
                self.current_file = file_path
                QMessageBox.information(self, self.tr("保存完了"), self.tr("ファイルを保存しました"))
                return True
            else:
                QMessageBox.critical(self, self.tr("エラー"), self.tr("ファイルを保存できませんでした"))
        
        return False
    
    def check_unsaved_changes(self):
        """
        未保存の変更があるか確認する
        
        Returns:
            bool: キャンセルされた場合はTrue、それ以外はFalse
        """
        # 変更フラグをチェック
        if self.model.is_modified():
            reply = QMessageBox.question(
                self, self.tr("確認"), self.tr("未保存の変更があります。保存しますか？"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                return not self.save_scenario()
            elif reply == QMessageBox.StandardButton.Cancel:
                return True
        
        return False
    
    def add_row(self):
        """
        選択された行の下に新しい行を追加する
        行が選択されていない場合は最後に追加する
        """
        # 選択された行を取得
        indexes = self.table_view.selectionModel().selectedRows()
        position = None
        
        if indexes:
            # 選択された行の次の位置に追加
            position = indexes[0].row() + 1
        
        # 行を追加
        new_row_position = self.model.add_row(position)
        
        # 追加した行を選択
        if new_row_position >= 0:
            index = self.model.index(new_row_position, 0)
            self.table_view.selectionModel().select(
                index, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows
            )
    
    def delete_row(self):
        """
        選択された行を削除する
        """
        indexes = self.table_view.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            self.model.delete_row(row)
            
            # 削除後に適切な行を選択
            new_row = min(row, self.model.rowCount() - 1)
            if new_row >= 0:
                index = self.model.index(new_row, 0)
                self.table_view.selectionModel().select(
                    index, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows
                )
    
    def move_row_up(self):
        """
        選択された行を上に移動する
        """
        indexes = self.table_view.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            if row > 0:
                self.model.move_row_up(row)
                
                # 移動後の行を選択
                new_row = row - 1
                index = self.model.index(new_row, 0)
                self.table_view.selectionModel().select(
                    index, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows
                )
    
    def move_row_down(self):
        """
        選択された行を下に移動する
        """
        indexes = self.table_view.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            if row < self.model.rowCount() - 1:
                self.model.move_row_down(row)
                
                # 移動後の行を選択
                new_row = row + 1
                index = self.model.index(new_row, 0)
                self.table_view.selectionModel().select(
                    index, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows
                )
    
    def cut_row(self):
        """
        選択された行を切り取る
        """
        indexes = self.table_view.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            self.model.cut_row(row)
            
            # 削除後に適切な行を選択
            new_row = min(row, self.model.rowCount() - 1)
            if new_row >= 0:
                index = self.model.index(new_row, 0)
                self.table_view.selectionModel().select(
                    index, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows
                )
    
    def paste_row(self):
        """
        クリップボードの行を貼り付ける
        """
        indexes = self.table_view.selectionModel().selectedRows()
        if indexes and self.model.clipboard:
            row = indexes[0].row()
            self.model.paste_row(row)
            
            # 貼り付けた行を選択
            index = self.model.index(row, 0)
            self.table_view.selectionModel().select(
                index, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows
            )
    def set_default_column_widths(self):
        """
        列幅の初期値を設定する
        """
        # 各列の初期幅を設定（ピクセル単位）
        column_widths = {
            ScenarioColumn.OPERATION_ID: 60,      # 操作ID: 狭め
            ScenarioColumn.OPERATION_TYPE: 120,   # 操作タイプ: 中程度
            ScenarioColumn.TARGET_ELEMENT: 200,   # 対象要素: 広め
            ScenarioColumn.INPUT_VALUE: 200,      # 入力値: 広め
            ScenarioColumn.WAIT_TIME: 80,         # 待機時間: 狭め
            ScenarioColumn.DESCRIPTION: 250,      # 説明: 最も広い
            ScenarioColumn.EXCEL_OUTPUT: 80       # Excel出力: 狭め
        }
        
        # 列幅を設定
        for column, width in column_widths.items():
            self.table_view.setColumnWidth(column, width)
