import sys
import os
import subprocess
import psutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QFormLayout,
    QWidget, QPushButton, QLabel, QComboBox, QSpinBox, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QMovie


class Isci(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, girdi_dosyasi, cikti_dosyasi, cozum, cpu_cekirdekleri):
        super().__init__()
        self.girdi_dosyasi = girdi_dosyasi
        self.cikti_dosyasi = cikti_dosyasi
        self.cozum = cozum
        self.cpu_cekirdekleri = cpu_cekirdekleri

    def run(self):
        komut = [
            'ffmpeg', '-i', self.girdi_dosyasi,
            '-vf', f'scale={self.cozum}',
            '-c:a', 'copy',
            '-preset', 'ultrafast',
            '-threads', str(self.cpu_cekirdekleri),
            self.cikti_dosyasi,
        ]
        process = subprocess.Popen(komut, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        self.finished_signal.emit()


class VideoCozumYukseltici(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Çözünürlük Yükseltici")
        self.setGeometry(300, 100, 1000, 700)

        self.ana_widget = QWidget(self)
        self.setCentralWidget(self.ana_widget)
        layout = QVBoxLayout()

        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())

        self.dosya_secim_frame = QFrame(self)
        self.dosya_secim_frame.setFrameShape(QFrame.StyledPanel)
        dosya_secim_layout = QVBoxLayout()

        self.dosya_buraya_surukle_label = QLabel("__________________________________________", self)
        self.dosya_buraya_surukle_label.setAlignment(Qt.AlignCenter)
        self.dosya_buraya_surukle_label.setStyleSheet("padding: 10px;")
        dosya_secim_layout.addWidget(self.dosya_buraya_surukle_label)

        self.dosya_secim_butonu = QPushButton("Video Dosyasını Aç", self)
        self.dosya_secim_butonu.clicked.connect(self.girdi_videosunu_sectir)
        dosya_secim_layout.addWidget(self.dosya_secim_butonu)

        self.dosya_secim_frame.setLayout(dosya_secim_layout)
        layout.addWidget(self.dosya_secim_frame)

        self.secili_dosya_label = QLabel("Seçilen video dosyasının yolu: (Henüz seçilmedi)", self)
        layout.addWidget(self.secili_dosya_label)

        self.cozum_frame = QFrame(self)
        self.cozum_frame.setFrameShape(QFrame.StyledPanel)
        cozum_layout = QFormLayout()

        self.cozum_combo = QComboBox(self)
        self.cozum_combo.addItem("144p (256x144)")
        self.cozum_combo.addItem("240p (426x240)")
        self.cozum_combo.addItem("360p (640x360)")
        self.cozum_combo.addItem("720p HD (1280x720)")
        self.cozum_combo.addItem("1080p Full HD (1920x1080)")
        self.cozum_combo.addItem("2K (2048x1080)")
        self.cozum_combo.addItem("4K (3840x2160)")
        self.cozum_combo.addItem("8K (7680x4320)")
        cozum_layout.addRow("Çözünürlük Seç:", self.cozum_combo)
        self.cozum_frame.setLayout(cozum_layout)
        layout.addWidget(self.cozum_frame)

        self.cpu_frame = QFrame(self)
        self.cpu_frame.setFrameShape(QFrame.StyledPanel)
        cpu_layout = QFormLayout()

        self.cpu_cekirdekleri_spinbox = QSpinBox(self)
        self.cpu_cekirdekleri_spinbox.setRange(1, psutil.cpu_count(logical=False))
        self.cpu_cekirdekleri_spinbox.setValue(psutil.cpu_count(logical=False))
        cpu_layout.addRow("CPU Çekirdek Sayısı:", self.cpu_cekirdekleri_spinbox)

        self.cpu_frame.setLayout(cpu_layout)
        layout.addWidget(self.cpu_frame)

        self.cikti_frame = QFrame(self)
        self.cikti_frame.setFrameShape(QFrame.StyledPanel)
        cikti_layout = QFormLayout()

        self.cikti_dosyasi_butonu = QPushButton("Çıktı Dosyasını Aç", self)
        self.cikti_dosyasi_butonu.clicked.connect(self.cikti_dosyasi_sectir)
        self.cikti_yolu_label = QLabel("Çıktı dosyasının yolu seçilmedi.", self)
        cikti_layout.addRow(self.cikti_dosyasi_butonu, self.cikti_yolu_label)

        self.cikti_frame.setLayout(cikti_layout)
        layout.addWidget(self.cikti_frame)

        self.yuklenme_label = QLabel(self)
        self.yuklenme_label.setAlignment(Qt.AlignCenter)
        self.yuklenme_label.setVisible(False)
        layout.addWidget(self.yuklenme_label)

        self.baslat_butonu = QPushButton("Başlat", self)
        self.baslat_butonu.setEnabled(False)
        self.baslat_butonu.clicked.connect(self.donusturme_islemini_baslat)
        layout.addWidget(self.baslat_butonu)

        self.ana_widget.setLayout(layout)

        self.movie = QMovie("loading.gif")
        self.yuklenme_label.setMovie(self.movie)

    def girdi_videosunu_sectir(self):
        options = QFileDialog.Options()
        girdi_video, _ = QFileDialog.getOpenFileName(self, "Video Dosyasını Seç", "", "Video Dosyaları (*.mp4 *.avi *.mkv *.mov)", options=options)
        if girdi_video:
            self.girdi_dosyasi = girdi_video
            self.secili_dosya_label.setText(f"Seçilen video dosyasının yolu: {girdi_video}")
            self.girdi_kontrol()

    def girdi_kontrol(self):
        if hasattr(self, 'girdi_dosyasi') and self.cozum_combo.currentText() and self.cikti_yolu_label.text() != "Çıktı dosyasının yolu seçilmedi.":
            self.baslat_butonu.setEnabled(True)
        else:
            self.baslat_butonu.setEnabled(False)

    def cikti_dosyasi_sectir(self):
        options = QFileDialog.Options()
        cikti_dosyasi, _ = QFileDialog.getSaveFileName(self, "Çıktı Dosyasını Seç", "", "Video Dosyaları (*.mp4 *.avi *.mkv *.mov)", options=options)
        if cikti_dosyasi:
            self.cikti_dosyasi = cikti_dosyasi
            self.cikti_yolu_label.setText(f"Seçilen yol: {cikti_dosyasi}")
            self.girdi_kontrol()

    def arayuzu_etkinlestir(self, etkin):
        self.dosya_secim_butonu.setEnabled(etkin)
        self.cozum_combo.setEnabled(etkin)
        self.cpu_cekirdekleri_spinbox.setEnabled(etkin)
        self.cikti_dosyasi_butonu.setEnabled(etkin)
        self.baslat_butonu.setEnabled(etkin)

    def donusturme_islemini_baslat(self):
        self.arayuzu_etkinlestir(False)
        self.yuklenme_label.setVisible(True)
        self.movie.start()

        cozum_mapping = {
            "144p (256x144)": "256x144",
            "240p (426x240)": "426x240",
            "360p (640x360)": "640x360",
            "720p HD (1280x720)": "1280x720",
            "1080p Full HD (1920x1080)": "1920x1080",
            "2K (2048x1080)": "2048x1080",
            "4K (3840x2160)": "3840x2160",
            "8K (7680x4320)": "7680x4320",
        }
        secilen_cozum = self.cozum_combo.currentText()
        cozum = cozum_mapping[secilen_cozum]

        self.isci = Isci(self.girdi_dosyasi, self.cikti_dosyasi, cozum, self.cpu_cekirdekleri_spinbox.value())
        self.isci.finished_signal.connect(self.donusturma_tamamlandi)
        self.isci.start()

    def donusturma_tamamlandi(self):
        QMessageBox.information(self, "Tamamlandı", "Video dönüştürme işlemi tamamlandı.")
        self.arayuzu_etkinlestir(True)
        self.yuklenme_label.setVisible(False)
        self.movie.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = VideoCozumYukseltici()
    pencere.show()
    sys.exit(app.exec_())
