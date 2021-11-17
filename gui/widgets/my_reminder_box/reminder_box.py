from qt_core import *
from gui.widgets import PyPushButton
import PySide6.QtWidgets as QtWidgets

class MyReminderBox(QWidget):
    def __init__(self,
                 text,
                 parent:QtWidgets.QWidget=None,
                 bg_color="#1b1e23",
                 text_font="12pt 'Segoe UI'",
                 color="#8a95aa",
                 border_radius=10,
                 btn_radius=8,
                 btn_color="white",
                 btn_bg_color="#8a95aa",
                 btn_bg_color_hover="#8a95aa",
                 btn_bg_color_pressed="#8a95aa"
                 ):
        super().__init__(parent)
        self.bg_color=bg_color
        self.border_radius=border_radius
        custom_style = """
            QLabel {{
                font: {_text_font};
            }}
            QPushButton {{
                font: {_text_font};
            }}
            """
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.Tool| Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet(custom_style.format(
            _text_font=text_font
        ))
        self.setMinimumWidth(200)
        self.bnt_OK = PyPushButton(
            text="OK",
            radius=btn_radius,
            color=btn_color,
            bg_color=btn_bg_color,
            bg_color_hover=btn_bg_color_hover,
            bg_color_pressed=btn_bg_color_pressed,
        )
        self.bnt_OK.setFixedWidth(75)
        self.bnt_OK.setFixedHeight(25)
        self.layout =QtWidgets.QVBoxLayout(self)
        self.layout_top=QtWidgets.QHBoxLayout()
        self.label=QLabel(self)
        self.label.setText(f'<font color=\"{color}\">{text}</font>')
        self.label_icon = QLabel(self)
        icon:QIcon =QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning)
        self.label_icon.setPixmap(icon.pixmap(int(text_font[:text_font.find("pt")])*2))
        self.layout_top.addWidget(self.label_icon)
        self.layout_top.addWidget(self.label)
        self.layout.addLayout(self.layout_top)
        self.layout.addSpacing(15)
        self.layout.addWidget(self.bnt_OK,alignment=Qt.AlignRight)

        self.timer=QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.start(3000)

        self.bnt_OK.clicked.connect(self.close)
        self.timer.timeout.connect(self.close)

    def paintEvent(self, event):
        p=QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(QColor(self.bg_color)))
        p.setPen(Qt.transparent)
        rect=self.rect()
        rect.setWidth(rect.width()-1)
        rect.setHeight(rect.height()-1)
        p.drawRoundedRect(rect,self.border_radius,self.border_radius)

        pos_p = self.parent().mapToGlobal(QPoint(0,0))
        x = pos_p.x() + self.parent().width() / 2 - self.width() / 2
        y = pos_p.y() + 42
        #print(pos_p.x(), pos_p.y(), self.width(), self.height())
        self.setGeometry(x, y, self.width(), self.height())

        super().paintEvent(event)



if __name__=="__main__":
    import sys
    app = QtWidgets.QApplication([])

    a=MyReminderBox(color="black",
        text="The document has been modified.")
    a.show()
    sys.exit(app.exec())

