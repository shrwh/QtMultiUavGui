# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'left_columnmRoAGn.ui'
##
## Created by: Qt User Interface Compiler version 6.1.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################
from qt_core import *


class Ui_LeftColumn(object):
    def setupUi(self, LeftColumn):
        if not LeftColumn.objectName():
            LeftColumn.setObjectName(u"LeftColumn")
        LeftColumn.resize(240, 600)
        self.main_pages_layout = QVBoxLayout(LeftColumn)
        self.main_pages_layout.setSpacing(0)
        self.main_pages_layout.setObjectName(u"main_pages_layout")
        self.main_pages_layout.setContentsMargins(5, 5, 5, 5)
        self.menus = QStackedWidget(LeftColumn)
        self.menus.setObjectName(u"menus")
        self.menu_1 = QWidget()
        self.menu_1.setObjectName(u"menu_1")
        self.verticalLayout = QVBoxLayout(self.menu_1)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.frame_btn_1 = QFrame(self.menu_1)
        self.frame_btn_1.setObjectName(u"frame_btn_1")
        self.frame_btn_1.setMinimumSize(QSize(0, 40))
        self.frame_btn_1.setMaximumSize(QSize(16777215, 40))
        self.frame_btn_1.setFrameShape(QFrame.NoFrame)
        self.frame_btn_1.setFrameShadow(QFrame.Raised)
        self.btn_1_layout = QVBoxLayout(self.frame_btn_1)
        self.btn_1_layout.setSpacing(0)
        self.btn_1_layout.setObjectName(u"btn_1_layout")
        self.btn_1_layout.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout.addWidget(self.frame_btn_1)

        self.frame_btn_2 = QFrame(self.menu_1)
        self.frame_btn_2.setObjectName(u"frame_btn_2")
        self.frame_btn_2.setMinimumSize(QSize(0, 40))
        self.frame_btn_2.setMaximumSize(QSize(16777215, 40))
        self.frame_btn_2.setFrameShape(QFrame.NoFrame)
        self.frame_btn_2.setFrameShadow(QFrame.Raised)
        self.btn_2_layout = QVBoxLayout(self.frame_btn_2)
        self.btn_2_layout.setSpacing(0)
        self.btn_2_layout.setObjectName(u"btn_2_layout")
        self.btn_2_layout.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout.addWidget(self.frame_btn_2)

        self.frame_btn_3 = QFrame(self.menu_1)
        self.frame_btn_3.setObjectName(u"frame_btn_3")
        self.frame_btn_3.setMinimumSize(QSize(0, 40))
        self.frame_btn_3.setMaximumSize(QSize(16777215, 40))
        self.frame_btn_3.setFrameShape(QFrame.NoFrame)
        self.frame_btn_3.setFrameShadow(QFrame.Raised)
        self.btn_3_layout = QVBoxLayout(self.frame_btn_3)
        self.btn_3_layout.setSpacing(0)
        self.btn_3_layout.setObjectName(u"btn_3_layout")
        self.btn_3_layout.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout.addWidget(self.frame_btn_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.menus.addWidget(self.menu_1)
        self.menu_2 = QWidget()
        self.menu_2.setObjectName(u"menu_2")
        self.verticalLayout_2 = QVBoxLayout(self.menu_2)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.label_2 = QLabel(self.menu_2)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setPointSize(16)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(u"font-size: 16pt")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_2)

        self.menus.addWidget(self.menu_2)

        self.main_pages_layout.addWidget(self.menus)


        self.retranslateUi(LeftColumn)

        self.menus.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(LeftColumn)
    # setupUi

    def retranslateUi(self, LeftColumn):
        LeftColumn.setWindowTitle(QCoreApplication.translate("LeftColumn", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("LeftColumn", u"Menu 2 - Left Menu", None))
    # retranslateUi

