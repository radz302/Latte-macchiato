import sys
import sqlite3
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from UI.mainUI import Ui_MainWindow
from UI.addEditCoffeeFormUI import Ui_addEditForm

datap = 'data/coffee.sqlite3'
st = {0: 'молотый',
      1: 'в зёрнах'}
a = 3
tad = '''CREATE TABLE coffee (
    id                  INTEGER        PRIMARY KEY AUTOINCREMENT
                                       UNIQUE
                                       NOT NULL,
    sort_title          TEXT           NOT NULL,
    degree_of_roasting  TEXT           NOT NULL,
    ground_or_grains    INTEGER (0, 1) NOT NULL,
    flavor_description  TEXT,
    price               REAL,
    volume_of_packaging REAL
);'''


def create_empty_file(full_path: str):
    full_path = full_path.replace('\\', '/')
    path = '/'.join(full_path.split('/')[:-1])
    if not os.path.isdir(path):
        os.makedirs(path)
    open(full_path, mode='w').close()


def create_database_if_need():
    if not os.path.isfile(datap):
        create_empty_file(datap)
        con = sqlite3.connect(datap)
        cur = con.cursor()
        cur.execute(tad)
        con.commit()
        con.close()


class CoffeeAddForm(QWidget, Ui_addEditForm):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.submit_btn.clicked.connect(self.submit)
        self.id_box.valueChanged.connect(self.change_data)

    def change_data(self, coffee_id):
        create_database_if_need()
        con = sqlite3.connect(datap)
        cur = con.cursor()
        element = cur.execute('SELECT * FROM coffee WHERE id = ?',
                              (coffee_id,)).fetchone()
        if element is not None:
            element = element[1:]
            self.sort_edit.setText(element[0])
            self.degree_edit.setText(element[1])
            self.ground_or_grains_box.setValue(element[2])
            self.flavor_edit.setText(element[3])
            self.price_box.setValue(element[4])
            self.volume_box.setValue(element[5])
        con.close()

    def submit(self):
        coffee_id = self.id_box.value()
        sort = self.sort_edit.text()
        degree = self.degree_edit.text()
        ground_or_grains = self.ground_or_grains_box.value()
        flavor = self.flavor_edit.text()
        price = self.price_box.value()
        volume = self.volume_box.value()
        create_database_if_need()
        con = sqlite3.connect(datap)
        cur = con.cursor()
        if (cur.execute('SELECT id FROM coffee WHERE id = ?',
                        (coffee_id,)).fetchone() is not None):
            cur.execute('DELETE FROM coffee WHERE id = ?', (coffee_id,))
        if coffee_id != 0:
            cur.execute('INSERT INTO coffee VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (coffee_id, sort, degree, ground_or_grains,
                         flavor, price, volume))
        else:
            cur.execute('INSERT INTO coffee(sort_title,'
                        ' degree_of_roasting,'
                        ' ground_or_grains,'
                        ' flavor_description,'
                        ' price,'
                        ' volume_of_packaging) VALUES (?, ?, ?, ?, ?, ?)',
                        (sort, degree, ground_or_grains,
                         flavor, price, volume))
        con.commit()
        con.close()
        self.main_window.load_table()
        self.deleteLater()


class CoffeeMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.coffee_table: QTableWidget = self.coffee_table
        self.add_form = None
        self.coffee_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.add_edit_btn.clicked.connect(self.add_item)
        self.load_table()

    def load_table(self):
        self.coffee_table.setRowCount(0)
        create_database_if_need()
        con = sqlite3.connect(datap)
        cur = con.cursor()
        data = cur.execute('SELECT * FROM coffee').fetchall()
        self.coffee_table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j in range(len(row)):
                if j == a:
                    value = st[row[j]]
                else:
                    value = str(row[j])
                item = QTableWidgetItem(value)
                item.setFlags(Qt.ItemIsEnabled)
                self.coffee_table.setItem(i, j, item)
        con.close()

    def add_item(self):
        self.add_form = CoffeeAddForm(self)
        self.add_form.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeMainWindow()
    window.show()
    sys.exit(app.exec())
