
import cProfile
import pstats
import json
import sys
from PyQt6.QtWidgets import *
import qdarkstyle
import pandas as pd
import glob
import os
from project_window import *
from updates.auto_updater import AutoUpdater
from custom_widgets import MainButton , Button
# from sklearn.impute import SimpleImputer




class DownloadThread(QThread):
    # Custom signal to emit when download is complete
    download_complete = pyqtSignal(str)

    def __init__(self, update_url, updater):
        super().__init__()
        self.update_url = update_url
        self.updater = updater

    def run(self):
        # Perform the download operation in the thread
        installer_path = self.updater.download_update(self.update_url)
        self.download_complete.emit(installer_path)  # Emit signal when done


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.project_path = ""

        self.updater = AutoUpdater(current_version="0.3", version_url="https://pivott.click/software_version.json")
        
        self.setWindowTitle('Two Column Main Window')
        self.setWindowIcon(QIcon('icon.png'))

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout for central widget
        self.main_layout = QHBoxLayout(central_widget)

        project_widget = ProjectWidget(main_parent = self)
        self.main_layout.addWidget(project_widget)

        self.header_layout = QHBoxLayout()

        # Add the close button to the top right
        close_button = QPushButton("×")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton#closeButton {
                background-color: transparent;
                border: none;
                color: #808080;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton#closeButton:hover {
                color: white;
            }
        """)
        close_button.clicked.connect(self.close)

        self.header_layout.addStretch(1)  # Push close button to the right
        self.header_layout.addWidget(close_button)

        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Add the header layout with close button at the top
        self.main_layout.addLayout(self.header_layout)
        


        # Set the window properties
        self.setWindowTitle('Pivot')
        self.setFixedSize(800, 600)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint , True)
               # Make the window draggable
        self.drag_position = QPoint()

        self.check_for_updates()

    # Function to enable dragging the frameless window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drag_position:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
    
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept() 


    def toggle_frame(self):

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, False)
        self.setFixedSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
        self.drag_position = None
        
        # Remove all widgets from main_layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif isinstance(item, QLayout):
                self.clearLayout(item)
        
        
        
        
        self.showNormal() 





    def check_for_updates(self):
        """Check for updates and download if available."""
        update_url = self.updater.check_for_updates()

        if update_url:
            reply = QMessageBox.question(self, "Update Available",
                                        "A new update is available. Do you want to download and install it?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                # Create a simple dialog window with a progress message
                progress_window = QDialog(self)
                progress_window.setWindowTitle("Downloading Update")
                layout = QVBoxLayout()

                # Add a label to show the message
                message_label = QLabel("Downloading update, please wait...")
                layout.addWidget(message_label)

                progress_window.setLayout(layout)
                progress_window.setFixedSize(300, 100)
                progress_window.show()

                # Create the download thread and start it
                self.download_thread = DownloadThread(update_url, self.updater)
                self.download_thread.download_complete.connect(self.on_download_complete)
                self.download_thread.start()

                # Keep showing the dialog until download is complete
                self.progress_window = progress_window
        else:
            pass

    def on_download_complete(self, installer_path):
        """Handle actions after the download is complete."""
        self.progress_window.close()  # Close the progress dialog

        if installer_path:
            QMessageBox.information(self, "Update Downloaded", "Update downloaded. Installing now...")
            self.updater.apply_update(installer_path)

    def clearLayout(self, layout):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                elif isinstance(item, QLayout):
                    self.clearLayout(item)





if __name__ == "__main__":
  
    with cProfile.Profile() as profile:  
        app = QApplication(sys.argv)
        
        window = MainWindow()
        window.show()
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
        
        app.exec()
        
    results = pstats.Stats(profile).sort_stats(pstats.SortKey.TIME)
    results.dump_stats('profile_results.prof')