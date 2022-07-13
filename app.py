import os
import sys
import qrcode
from barcode import EAN13
from barcode.writer import ImageWriter
import urllib.parse
import base64
import datetime

from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QStatusBar, QVBoxLayout, QHBoxLayout, QRadioButton, QFileDialog
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtCore import Qt



class QRCodeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(700, 550)
        self.setWindowTitle("Генерація QR коду")
        self.initUI()

    def initUI(self):
        font = QFont("Open Sans", 14)

        mainLayout = QVBoxLayout()
        entryLayout = QVBoxLayout()
        paramsLayount = QVBoxLayout()
        radioLayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()
        imageLayout = QVBoxLayout()
        imageLayout.addStretch()

        labelDomain = QLabel("Введіть значення (для BAR коду мінімум 12 сиволів):")
        labelDomain.setFont(font)
        
        self.domainEntry = QLineEdit()
        self.domainEntry.setFont(font)

        entryLayout.addWidget(labelDomain)
        entryLayout.addWidget(self.domainEntry)

# Params Layout    
        labelParams = QLabel("Введіть параметри (опціонально): ")
        labelParams.setFont(font)

        self.labelUrl = QLabel("")
        self.labelUrl.setFont(font)
        self.labelUrl.setMinimumSize(300, 20)
        self.labelUrl.setWordWrap(True)

        self.paramsEntry = QLineEdit()
        self.paramsEntry.setFont(font)

        self.radio_none_decode = QRadioButton()
        self.radio_none_decode.setText("Без кодування")
        self.radio_none_decode.setFont(font)
        self.radio_none_decode.setChecked(True)

        self.radio_url_decode = QRadioButton()
        self.radio_url_decode.setText("URL Decode")
        self.radio_url_decode.setFont(font)

        self.radio_base64_decode = QRadioButton()
        self.radio_base64_decode.setText("Base64 Decode")
        self.radio_base64_decode.setFont(font)

        self.copy_link_button = QPushButton('Зберегти посилання', clicked=self.copy_link_to_buffer)

        paramsLayount.addWidget(labelParams)
        
        radioLayout.addWidget(self.radio_none_decode)
        radioLayout.addWidget(self.radio_url_decode)
        radioLayout.addWidget(self.radio_base64_decode)

        paramsLayount.addLayout(radioLayout)
        paramsLayount.addWidget(self.paramsEntry)
        paramsLayount.addWidget(self.labelUrl)
        paramsLayount.addWidget(self.copy_link_button)

        entryLayout.addLayout(paramsLayount)

        mainLayout.addLayout(entryLayout)

        
# Buttons
        self.buttonQRGenerate = QPushButton("Сгенерувати QR код")
        self.buttonQRGenerate.clicked.connect(self.create_qr_code)

        self.buttonBARGenerate = QPushButton("Сгенерувати BAR код")
        self.buttonBARGenerate.clicked.connect(self.create_bar_code)

        self.buttonSaveImage = QPushButton("Зберегти QR код")
        self.buttonSaveImage.clicked.connect(self.save_code)

        self.buttonClear = QPushButton("Очистити")
        self.buttonClear.clicked.connect(self.clear_fields)

        buttonLayout.addWidget(self.buttonQRGenerate)
        buttonLayout.addWidget(self.buttonBARGenerate)
        buttonLayout.addWidget(self.buttonSaveImage)
        buttonLayout.addWidget(self.buttonClear)

        mainLayout.addLayout(buttonLayout)

        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        imageLayout.addWidget(self.imageLabel)
        mainLayout.addLayout(imageLayout)

        self.statusBar = QStatusBar()
        mainLayout.addWidget(self.statusBar)

        self.setLayout(mainLayout)

    def clear_fields(self):
            self.domainEntry.clear()
            self.paramsEntry.clear()
            self.labelUrl.clear()
            self.imageLabel.clear()
            self.statusBar.clearMessage()

    
    def url_decoding(self):
        if self.radio_none_decode.isChecked():
            url = self.domainEntry.text() + self.paramsEntry.text()
        elif self.radio_url_decode.isChecked():
            url = self.domainEntry.text() + urllib.parse.quote(self.paramsEntry.text())
        elif self.radio_base64_decode.isChecked():
            params_decoded = base64.b64encode(self.paramsEntry.text().encode("UTF-8")).decode("UTF-8")
            url = self.domainEntry.text() + params_decoded
        else:
             url = self.domainEntry.text()
        return url


    def create_qr_code(self):
        text = self.domainEntry.text()
        self.labelUrl.setText(self.url_decoding())

        if text:
            img = qrcode.make(self.url_decoding())
            qr = ImageQt(img)
            pix = QPixmap.fromImage(qr)  
            self.imageLabel.setPixmap(pix)

   
    def create_bar_code(self):
        number = self.domainEntry.text()
        
        if len(number) == 12:
            bar_code = EAN13(number, writer=ImageWriter())
            bar_code.save("bar_code")
            pix = QPixmap("bar_code.png") 
            self.imageLabel.setPixmap(pix)
        else:
            self.labelUrl.setText("BAR код повинен складатися з 12 символів")

    def save_code(self):

        default_file_name = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        default_file_path = os.path.join(os.getcwd(), default_file_name + ".png")
        file_name = QFileDialog.getSaveFileName(self, "Зберегти QR код", default_file_path, "Images Files (*.png);;All Files (*)")
        self.imageLabel.pixmap().save(file_name[0])
        self.statusBar.showMessage("Зображення збережено в папці:{0}".format(file_name[0]))


    def copy_link_to_buffer(self):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.labelUrl.text(), mode=cb.Clipboard)
        self.statusBar.showMessage("Посилання скопійовано")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QPushButton{Heigth: 30px; font-size: 16px}")
    demo = QRCodeApp()
    demo.show()

    sys.exit(app.exec_())
