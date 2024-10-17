
import cProfile
import pstats
import json
import sys
import traceback
from PyQt6.QtWidgets import *
import qdarkstyle
import pandas as pd
import glob
import os
from project_window import *
from updates.auto_updater import AutoUpdater
from custom_widgets import MainButton , Button
# from sklearn.impute import SimpleImputer



varsion = 1.1

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

        self.updater = AutoUpdater(current_version=varsion, version_url="https://pivott.click/software_version.json")
        
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
                                        QMessageBox.StandardButton.Yes)

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




def handle_exception(exc_type, exc_value, exc_traceback):
    # Format the traceback
    error_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Create a custom dialog to display the error
    error_dialog = QDialog()
    error_dialog.setWindowTitle("Critical Error")
    error_dialog.setFixedSize(600, 300)  # Set fixed size to make it look like an alert

    # Create the layout
    main_layout = QVBoxLayout()

    # Error icon and message layout (to simulate an alert)
    alert_layout = QHBoxLayout()
    
    # Add an icon to make it look like an alert
    icon_label = QLabel()
    icon_label.setPixmap(QIcon.fromTheme("dialog-error").pixmap(QSize(48, 48)))  # Critical error icon
    alert_layout.addWidget(icon_label)

    # Add a brief error message next to the icon
    brief_label = QLabel(f"<b>Error:</b> {exc_type.__name__}: {exc_value}")
    brief_label.setWordWrap(True)
    alert_layout.addWidget(brief_label)

    main_layout.addLayout(alert_layout)

    # Add a text area for the detailed traceback
    detailed_text = QTextEdit()
    detailed_text.setText(error_message)
    detailed_text.setReadOnly(True)
    main_layout.addWidget(detailed_text)

    # Add an OK button to close the dialog
    ok_button = QPushButton("OK")
    ok_button.clicked.connect(error_dialog.accept)
    main_layout.addWidget(ok_button)

    # Set the layout and show the dialog
    error_dialog.setLayout(main_layout)
    error_dialog.exec()



if __name__ == "__main__":
    # Set the custom exception handler
    sys.excepthook = handle_exception
    
    with cProfile.Profile() as profile:
        app = QApplication(sys.argv)
        
        window = MainWindow()
        window.show()
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())

        try:
            app.exec()
        except Exception as e:
            handle_exception(*sys.exc_info())
        
    results = pstats.Stats(profile).sort_stats(pstats.SortKey.TIME)
    results.dump_stats('profile_results.prof')
    
