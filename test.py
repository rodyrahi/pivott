import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create a vertical layout for buttons
        button_layout = QVBoxLayout()

        # Set spacing between buttons to 5 (you can adjust this)
        button_layout.setSpacing(5)

        # Create three buttons with a fixed width
        button1 = QPushButton('Button 1')
        button2 = QPushButton('Button 2')
        button3 = QPushButton('Button 3')

        # Set a fixed width for the buttons
        button1.setFixedWidth(100)
        button2.setFixedWidth(100)
        button3.setFixedWidth(100)

        # Add buttons to the layout
        button_layout.addWidget(button1)
        button_layout.addWidget(button2)
        button_layout.addWidget(button3)

        # Align the buttons to the left
        button_layout.setAlignment(Qt.AlignCenter)

        # Create a placeholder for the logo
        logo_label = QLabel('Logo')
        logo_label.setStyleSheet("border: 2px solid black;")
        logo_label.setFixedSize(200, 200)  # Set a fixed size for the logo placeholder

        # Create a horizontal layout to hold both the button layout and the logo
        main_layout = QHBoxLayout()

        # Add button layout and logo placeholder to the main layout
        main_layout.addLayout(button_layout)
        main_layout.addWidget(logo_label)

        # Set alignment of the main layout to align items to the left
        main_layout.setAlignment(Qt.AlignCenter)

        # Set the main layout for the window
        self.setLayout(main_layout)

        # Set the window title and size
        self.setWindowTitle('Custom GUI')
        self.setGeometry(100, 100, 600, 400)  # (x, y, width, height)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
