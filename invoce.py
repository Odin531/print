import sys
from random import randint
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QMessageBox
)


class InvoiceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Generator")
        self.setGeometry(300, 100, 600, 500)
        self.setFixedSize(600, 500)  # fixed window size

        # ---------- Client Info ----------
        self.client_name = QLineEdit()
        self.client_mobile = QLineEdit()

        # connect Enter key behaviour
        self.client_name.returnPressed.connect(self.focus_mobile)
        self.client_mobile.returnPressed.connect(self.focus_table)

        # ---------- Product Table ----------
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Item", "Quantity", "Price per Unit"])

        # ---------- Buttons ----------
        add_btn = QPushButton("➕ Add Product")
        add_btn.clicked.connect(self.add_product)

        generate_btn = QPushButton("📄 Generate Invoice PDF")
        generate_btn.clicked.connect(self.generate_invoice)

        # ---------- Layout ----------
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Client Name:"))
        layout.addWidget(self.client_name)
        layout.addWidget(QLabel("Mobile No:"))
        layout.addWidget(self.client_mobile)

        layout.addWidget(QLabel("Products:"))
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(generate_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # ---------- Apply Dark Theme ----------
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
                font-size: 14px;
            }
            QLabel {
                font-weight: bold;
                color: #ff4c4c;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #ff4c4c;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background-color: #ff4c4c;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #ff1a1a;
            }
            QTableWidget {
                background-color: #1e1e1e;
                color: white;
                gridline-color: #ff4c4c;
                selection-background-color: #ff3333;
                border: 1px solid #ff4c4c;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #ff4c4c;
                color: white;
                padding: 6px;
                border: none;
            }
        """)

    # -------- focus methods ----------
    def focus_mobile(self):
        """Move cursor to Mobile No field when Enter pressed in Name"""
        self.client_mobile.setFocus()

    def focus_table(self):
        """Move cursor to Products table when Enter pressed in Mobile"""
        if self.table.rowCount() == 0:
            self.add_product()
        self.table.setFocus()
        self.table.setCurrentCell(0, 0)

    # -------- table ----------
    def add_product(self):
        """Add empty row for new product entry"""
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)

    # -------- PDF generation ----------
    def generate_invoice(self):
        name = self.client_name.text()
        mobile_no = self.client_mobile.text()

        if not name or not mobile_no:
            QMessageBox.warning(self, "Error", "Client info is required")
            return

        products = []
        for row in range(self.table.rowCount()):
            item_name_item = self.table.item(row, 0)
            qty_item = self.table.item(row, 1)
            price_item = self.table.item(row, 2)

            if item_name_item and qty_item and price_item:
                try:
                    item_name = item_name_item.text()
                    quantity = int(qty_item.text())
                    price = float(price_item.text())
                    total = quantity * price
                    products.append([item_name, quantity, price, total])
                except ValueError:
                    QMessageBox.warning(self, "Error", f"Invalid entry in row {row + 1}")
                    return

        if not products:
            QMessageBox.warning(self, "Error", "Please add at least one product")
            return

        # ---------- Invoice Info ----------
        invoice_no = randint(77777, 99999)
        debit_date = date.today()

        # ---------- Create PDF ----------
        file_name = f"Invoice_{invoice_no}.pdf"
        c = canvas.Canvas(file_name, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, height - 50, "Debit Note / Invoice")

        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Invoice No.: {invoice_no}")
        c.drawString(300, height - 100, f"Date: {debit_date}")
        c.drawString(50, height - 130, f"Client: {name}")
        c.drawString(300, height - 130, f"Mobile: {mobile_no}")

        # Table headers
        c.drawImage("logo.png", 50, height - 80, width=60, height=60, mask='auto')

        c.setFont("Helvetica-Bold", 12)
        y = height - 180
        c.drawString(50, y, "Item")
        c.drawString(200, y, "Qty")
        c.drawString(260, y, "Price")
        c.drawString(350, y, "Total")
        c.line(50, y - 5, 500, y - 5)

        # Table rows
        c.setFont("Helvetica", 12)
        subtotal = 0
        y -= 30
        for item_name, quantity, price, total in products:
            c.drawString(50, y, str(item_name))
            c.drawString(200, y, str(quantity))
            c.drawString(260, y, f"{price:.2f}")
            c.drawString(350, y, f"{total:.2f}")
            subtotal += total
            y -= 25

        # Totals
        c.setFont("Helvetica-Bold", 12)
        c.drawString(260, y - 20, "Subtotal:")
        c.drawString(350, y - 20, f"{subtotal:.2f}")

        grand_total = subtotal
        c.drawString(260, y - 70, "Grand Total:")
        c.drawString(350, y - 70, f"{grand_total:.2f}")

        c.save()
        QMessageBox.information(self, "Success", f"✅ Invoice saved as {file_name}")


# ---------- Run App ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InvoiceApp()
    window.show()
    sys.exit(app.exec_())
