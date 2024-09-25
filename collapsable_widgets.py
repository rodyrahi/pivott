from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from custom_widgets import Button , CollapsibleButton



class CollapsableWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.feature_widgets = None
        self.main_interface = None
        self.initUI()
        self.widgets_set = False

    def initUI(self):
        self.main_layout = QVBoxLayout(self)

        # Create a button to toggle the collapsible content
        self.toggle_button = CollapsibleButton(self.title, self)
        self.toggle_button.clicked.connect(self.toggleContent)
        self.main_layout.addWidget(self.toggle_button)

        # Create a scroll area for the checkboxes
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)  # Initially hidden
        # self.scroll_area.setMaximumHeight(500)  # Set maximum height

        # Create a widget to hold the checkboxes
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)

        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area)

    def setWidgets(self):
        if not self.widgets_set:

            
            feature = self.feature_widgets(main_interface=self.main_interface)
            feature.initUI()    

            self.content_layout.addWidget(feature)

            # Set the width of the scroll area to fit checkboxes
            self.content_widget.adjustSize()
            self.scroll_area.setFixedWidth(self.content_widget.width() + self.scroll_area.verticalScrollBar().width())

            # Set the height of the scroll area to fit the content
            self.scroll_area.setFixedHeight(self.content_widget.height()+10)
            self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.setLayout(self.main_layout)

            self.widgets_set = True
            

    def toggleContent(self):
        # Toggle the visibility of the scroll area
        if self.scroll_area.isVisible():
            self.scroll_area.setVisible(False)
        else:
            self.setWidgets()
            self.scroll_area.setVisible(True)

