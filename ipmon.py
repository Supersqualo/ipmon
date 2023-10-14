import configparser
import subprocess
import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QObject, pyqtSignal

config = configparser.ConfigParser()
config.read("ipmon.ini")

ip_to_monitor = config["General"]["IP"].split(";")
monitor_interval = int(config["General"]["TIME"])  # Tempo in secondi
ping_timeout = config["General"]["PINGTIMEOUT"]

# Percorsi delle icone
ICON_GREEN = "led_green.ico"
ICON_YELLOW = "led_yellow.ico"
ICON_RED = "led_red.ico"
LOGO = "logo.ico"

class IpStatusUpdater(QObject):
    ip_status_updated = pyqtSignal(dict)

    def __init__(self, ip_addresses):
        super().__init__()
        self.ip_addresses = ip_addresses

    def check_ip_status(self):
        while True:
            ip_status = {}
            for ip in self.ip_addresses:
                try:
                    subprocess.Popen(["ping", "-n", "4", ip, "-w", ping_timeout],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     creationflags=subprocess.DETACHED_PROCESS)
                    ip_status[ip] = True
                except subprocess.CalledProcessError:
                    ip_status[ip] = False

            tray.setIcon(QIcon(ICON_GREEN) if all(ip_status[ip] for ip in ip_to_monitor) else
                         QIcon(ICON_YELLOW) if any(ip_status[ip] for ip in ip_to_monitor) else
                         QIcon(ICON_RED))


            if config["General"]["NOTIFY"].upper() == "S":
                show_notification(tray, "IPMon", "IP raggiungibili." if all(ip_status[ip] for ip in ip_to_monitor)
                                  else "Alcuni IP non raggiungibili." if any(ip_status[ip] for ip in ip_to_monitor)
                                  else "IP non raggiungibili.")

            self.ip_status_updated.emit(ip_status)
            time.sleep(monitor_interval)

class IpStatusDialog(QDialog):
    def __init__(self, parent=None):
        super(IpStatusDialog, self).__init__(parent)
        self.setWindowTitle("IPMon")
        self.setFixedWidth(200)
        self.setFixedHeight(720)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Creazione della tabella con due colonne: IP e Icona
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(['Stato', 'IP'])

        # Imposta la politica di stretching delle righe
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.verticalHeader().setVisible(False)

        self.layout.addWidget(self.table_widget)

        # Imposta la larghezza minima della prima colonna
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 100)

    def update_ip_status(self, ip_status):
        # Cancella i contenuti della tabella
        self.table_widget.setRowCount(0)

        for ip, status in ip_status.items():
            # Crea una nuova riga nella tabella
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)

            # Colora la casella se offline o online
            icon_item = QTableWidgetItem()
            if status:
                color = Qt.green
            else:
                color = Qt.red

            icon_item.setBackground(QColor(color))
            self.table_widget.setItem(row_position, 0, icon_item)

            # Blocca il contenuto della colonna 0
            icon_item.setFlags(icon_item.flags() & ~Qt.ItemIsEnabled)

            # Inserisci l'IP nella seconda colonna
            ip_item = QTableWidgetItem(ip)
            self.table_widget.setItem(row_position, 1, ip_item)

def show_notification(tray, title, message):
    tray.showMessage(title, message)

def show_ip_status_dialog(ip_status):
    dialog.update_ip_status(ip_status)

def on_tray_activated(reason):
    if reason == QSystemTrayIcon.Trigger:
        dialog.show()

if __name__ == "__main__":
    # Inizializza l'applicazione Qt
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Crea un'istanza del dialog
    dialog = IpStatusDialog()

    # Crea un'istanza di QSystemTrayIcon
    tray = QSystemTrayIcon(QIcon(LOGO), parent=app)

    # Crea un menu per l'icona nella tray
    menu = QMenu()
    exit_action = QAction("Esci", parent=app)
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)

    # Imposta il menu per l'icona nella tray
    tray.setContextMenu(menu)

    # Mostra l'icona nella tray
    tray.show()

    # Crea un'istanza del thread per aggiornare lo stato degli IP
    ip_status_updater = IpStatusUpdater(ip_to_monitor)
    ip_status_updater_thread = threading.Thread(target=ip_status_updater.check_ip_status, daemon=True)
    ip_status_updater_thread.start()

    # Connessione del segnale per aggiornare il dialog quando lo stato degli IP cambia
    ip_status_updater.ip_status_updated.connect(lambda ip_status: show_ip_status_dialog(ip_status))

    # Connessione del segnale per aprire il dialog quando si fa clic sull'icona della tray
    tray.activated.connect(on_tray_activated)

    # Esegui l'applicazione
    sys.exit(app.exec_())
