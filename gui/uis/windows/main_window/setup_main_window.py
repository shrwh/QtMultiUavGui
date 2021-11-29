# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

# IMPORT PACKAGES AND MODULES
# ///////////////////////////////////////////////////////////////
from gui.widgets.py_table_widget.py_table_widget import PyTableWidget
from .functions_main_window import *
import sys
import os

# IMPORT QT CORE
# ///////////////////////////////////////////////////////////////
from qt_core import *

# IMPORT SETTINGS
# ///////////////////////////////////////////////////////////////
from gui.core.json_settings import Settings

# IMPORT THEME COLORS
# ///////////////////////////////////////////////////////////////
from gui.core.json_themes import Themes

# IMPORT PY ONE DARK WIDGETS
# ///////////////////////////////////////////////////////////////
from gui.widgets import *

# LOAD UI MAIN
# ///////////////////////////////////////////////////////////////
from . ui_main import *

# MAIN FUNCTIONS 
# ///////////////////////////////////////////////////////////////
from . functions_main_window import *

# IMPORT FUNCTIONALITY
# ///////////////////////////////////////////////////////////////
from functionality import *

# PY WINDOW
# ///////////////////////////////////////////////////////////////
class SetupMainWindow:
    def __init__(self):
        super().__init__()
        # SETUP MAIN WINDOw
        # Load widgets from "gui\uis\main_window\ui_main.py"
        # ///////////////////////////////////////////////////////////////
        self.ui = UI_MainWindow()#方便编程
    #     self.ui.setup_ui(self)

    # ADD LEFT MENUS
    # ///////////////////////////////////////////////////////////////
    add_left_menus = [
        {
            "btn_icon" : "icon_home.svg",
            "btn_id" : "btn_home",
            "btn_text" : "Home",
            "btn_tooltip" : "Home page",
            "show_top" : True,
            "is_active" : True
        },
        {
            "btn_icon": "icon_signal.svg",
            "btn_id": "btn_page_2",
            "btn_text": "Page 2",
            "btn_tooltip": "Open Page 2",
            "show_top": True,
            "is_active": False
        },
        {
            "btn_icon": "icon_info.svg",
            "btn_id": "btn_page_3",
            "btn_text": "Page 3",
            "btn_tooltip": "Open Page 3",
            "show_top": True,
            "is_active": False
        },
        {
            "btn_icon": "icon_settings.svg",
            "btn_id": "btn_settings",
            "btn_text": "Settings",
            "btn_tooltip": "Open Settings",
            "show_top": False,
            "is_active": False
        }
    ]

     # ADD TITLE BAR MENUS
    # ///////////////////////////////////////////////////////////////
    add_title_bar_menus = [
        {
            "btn_icon" : "icon_search.svg",
            "btn_id" : "btn_search",
            "btn_tooltip" : "Search",
            "is_active" : False
        },
        {
            "btn_icon" : "icon_settings.svg",
            "btn_id" : "btn_top_settings",
            "btn_tooltip" : "Top settings",
            "is_active" : False
        }
    ]

    # SETUP CUSTOM BTNs OF CUSTOM WIDGETS
    # Get sender() function when btn is clicked
    # ///////////////////////////////////////////////////////////////
    @staticmethod
    def setup_btns(self):
        if self.ui.title_bar.sender() != None:
            return self.ui.title_bar.sender()
        elif self.ui.left_menu.sender() != None:
            return self.ui.left_menu.sender()
        elif self.ui.left_column.sender() != None:
            return self.ui.left_column.sender()

    # SETUP MAIN WINDOW WITH CUSTOM PARAMETERS
    # ///////////////////////////////////////////////////////////////
    # @staticmethod(注销方便编程)
    def setup_gui(self):
        # APP TITLE
        # ///////////////////////////////////////////////////////////////
        self.setWindowTitle(self.settings["app_name"])
        
        # REMOVE TITLE BAR
        # ///////////////////////////////////////////////////////////////
        if self.settings["custom_title_bar"]:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)

        # ADD GRIPS
        # ///////////////////////////////////////////////////////////////
        if self.settings["custom_title_bar"]:
            self.left_grip = PyGrips(self, "left", self.hide_grips)
            self.right_grip = PyGrips(self, "right", self.hide_grips)
            self.top_grip = PyGrips(self, "top", self.hide_grips)
            self.bottom_grip = PyGrips(self, "bottom", self.hide_grips)
            self.top_left_grip = PyGrips(self, "top_left", self.hide_grips)
            self.top_right_grip = PyGrips(self, "top_right", self.hide_grips)
            self.bottom_left_grip = PyGrips(self, "bottom_left", self.hide_grips)
            self.bottom_right_grip = PyGrips(self, "bottom_right", self.hide_grips)

        # LEFT MENUS / GET SIGNALS WHEN LEFT MENU BTN IS CLICKED / RELEASED
        # ///////////////////////////////////////////////////////////////
        # ADD MENUS
        self.ui.left_menu.add_menus(SetupMainWindow.add_left_menus)

        # SET SIGNALS
        self.ui.left_menu.clicked.connect(self.btn_clicked)
        self.ui.left_menu.released.connect(self.btn_released)

        # TITLE BAR / ADD EXTRA BUTTONS
        # ///////////////////////////////////////////////////////////////
        # ADD MENUS
        self.ui.title_bar.add_menus(SetupMainWindow.add_title_bar_menus)

        # SET SIGNALS
        self.ui.title_bar.clicked.connect(self.btn_clicked)
        self.ui.title_bar.released.connect(self.btn_released)

        # ADD Title
        if self.settings["custom_title_bar"]:
            self.ui.title_bar.set_title(self.settings["app_name"])
        else:
            self.ui.title_bar.set_title("Welcome to PyOneDark")

        # LEFT COLUMN SET SIGNALS
        # ///////////////////////////////////////////////////////////////
        self.ui.left_column.clicked.connect(self.btn_clicked)
        self.ui.left_column.released.connect(self.btn_released)

        # SET INITIAL PAGE / SET LEFT AND RIGHT COLUMN MENUS
        # ///////////////////////////////////////////////////////////////
        MainFunctions.set_page(self, self.ui.load_pages.page_1)
        MainFunctions.set_left_column_menu(
            self,
            menu = self.ui.left_column.menus.menu_1,
            title = "Settings Left Column",
            icon_path = Functions.set_svg_icon("icon_settings.svg")
        )
        MainFunctions.set_right_column_menu(self, self.ui.right_column.menu_1)

        # ///////////////////////////////////////////////////////////////
        # EXAMPLE CUSTOM WIDGETS
        # Here are added the custom widgets to pages and columns that
        # were created using Qt Designer.
        # This is just an example and should be deleted when creating
        # your application.
        #
        # OBJECTS FOR LOAD PAGES, LEFT AND RIGHT COLUMNS
        # You can access objects inside Qt Designer projects using
        # the objects below:
        #
        # <OBJECTS>
        # LEFT COLUMN: self.ui.left_column.menus
        # RIGHT COLUMN: self.ui.right_column
        # LOAD PAGES: self.ui.load_pages
        # </OBJECTS>
        # ///////////////////////////////////////////////////////////////

        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        settings = Settings()
        self.settings = settings.items

        # LOAD THEME COLOR
        # ///////////////////////////////////////////////////////////////
        themes = Themes()
        self.themes = themes.items

        # Command Sender
        # ///////////////////////////////////////////////////////////////
        self.command_sender = CommandSender()
        self.command_sender.start()
        # Info Receiver
        # ///////////////////////////////////////////////////////////////
        self.info_receiver=InfoReceiverThread("234.2.2.2",8001)
        # Video Receiver
        # ///////////////////////////////////////////////////////////////
        self.video_display_size = (384, 288)  # 640,480 *0.6
        self.video_receiver_1 = VideoReceiverThread(8003, 1,self.info_receiver, self.video_display_size)
        self.video_receiver_2 = VideoReceiverThread(8004,2,self.info_receiver,self.video_display_size)
        # Code Editor
        # ///////////////////////////////////////////////////////////////
        self.code_editor = MyCodeEditor()
        # Info Display Labels
        # ///////////////////////////////////////////////////////////////
        self.labels_info = {}
        # Some Tools
        # ///////////////////////////////////////////////////////////////
        from functionality.logger import logger_config
        logger=logger_config("properties/log.txt","地面站运行数据记录")

        @Slot()
        def sendCommand():#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            command_input=self.code_editor.getCodeEntered()
            if command_input.strip()=="s":
                #print("=" * 50)
                from geographiclib.geodesic import Geodesic
                #params=[37.392915,121.6006549,37.507968,122.129538]
                for each in self.info_receiver.info:
                    params.append(each["pos"]["latitude"])
                    params.append(each["pos"]["longitude"])
                logger.info(Geodesic.WGS84.Inverse(*params))
                #print("=" * 50)
            elif command_input.strip()=="s1":
                from mydronesdk.ddpg_yolo_control import script
                script.script(self.command_sender,self.video_receiver_1)
            elif command_input.strip().find("stop")!=-1:
                if self.command_sender.sendCommandWithResponse(command_input):
                    self.command_sender.sendCommand(command_input.replace("stop","land"))
            else:
                self.command_sender.sendCommand(command_input)

        self.code_editor.line_edit.returnPressed.connect(sendCommand)

        # LEFT COLUMN
        # ///////////////////////////////////////////////////////////////
        @Slot()
        def takeoff_button_clicked():
            self.code_editor.enterCode("takeoff")

        self.bnt_takeoff=PyPushButton(
            text="takeoff",
            radius=8,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_hover=self.themes["app_color"]["dark_three"],
            bg_color_pressed=self.themes["app_color"]["dark_four"],
        )
        self.bnt_takeoff.setMinimumHeight(40)
        self.ui.left_column.menus.btn_1_layout.addWidget(self.bnt_takeoff)
        self.bnt_takeoff.clicked.connect(takeoff_button_clicked)

        @Slot()
        def stop_button_clicked():
            self.code_editor.enterCode("stop")

        self.bnt_stop = PyPushButton(
            text="stop",
            radius=8,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_hover=self.themes["app_color"]["dark_three"],
            bg_color_pressed=self.themes["app_color"]["dark_four"],
        )
        self.bnt_stop.setMinimumHeight(40)
        self.ui.left_column.menus.btn_2_layout.addWidget(self.bnt_stop)
        self.bnt_stop.clicked.connect(stop_button_clicked)

        self.left_column_line_edit = CodeInputLine()
        self.left_column_line_edit.loadHistory()
        self.left_column_line_edit.set_stylesheet(
            radius=4,
            border_size=2,
            color=self.themes["app_color"]["text_foreground"],
            selection_color=self.themes["app_color"]["white"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_active=self.themes["app_color"]["dark_three"],
            context_color=self.themes["app_color"]["context_color"]
        )

        @Slot()
        def leftColumnLineEditReturnPressedMethod():
            self.code_editor.enterCode(self.left_column_line_edit.code_str)

        self.left_column_line_edit.returnPressed.connect(leftColumnLineEditReturnPressedMethod)
        self.ui.left_column.menus.btn_3_layout.addWidget(self.left_column_line_edit)

        self.toggle_save_video = PyToggle(
            width=50,
            bg_color=self.themes["app_color"]["dark_one"],
            circle_color=self.themes["app_color"]["icon_color"],
            active_color=self.themes["app_color"]["context_color"],
        )

        @Slot()
        def changeSaveVideoFlag():
            flag=self.toggle_save_video.isChecked()
            self.video_receiver_1.change_save_video_flag(flag)
            self.video_receiver_2.change_save_video_flag(flag)

        self.toggle_save_video.stateChanged.connect(changeSaveVideoFlag)
        self.ui.left_column.menus.btn_4_layout.addWidget(self.toggle_save_video, 0, Qt.AlignCenter)

        # Page1
        # ///////////////////////////////////////////////////////////////
        self.logo=QSvgWidget(Functions.set_svg_image("my_logo_home.svg"))
        self.ui.load_pages.logo_layout.addWidget(self.logo,0,Qt.AlignCenter)
        self.ui.load_pages.label.setText("Welcome To Multi-UAV-Dev GUI")

        # Page3
        # ///////////////////////////////////////////////////////////////
        # Create a label for the display camera
        self.label_video_1 = self.ui.load_pages.label_video_1
        self.label_video_1.setFixedSize(*self.video_display_size)
        self.label_video_2 = self.ui.load_pages.label_video_2
        self.label_video_2.setFixedSize(*self.video_display_size)

        # Thread in charge of updating the image
        @Slot(QImage,int)
        def setImage(image,port):
            if port==8003:
                if not image.isNull():
                    self.label_video_1.setPixmap(QPixmap.fromImage(image))
                else:
                    self.label_video_1.setText("No Stream")
                    self.label_video_1.setAlignment(Qt.AlignCenter)
            elif port==8004:
                if not image.isNull():
                    self.label_video_2.setPixmap(QPixmap.fromImage(image))
                else:
                    self.label_video_2.setText("No Stream")

        self.video_received_flags={}
        @Slot(int,int)
        def changeMainPage(pageId,port):
            if pageId==3:
                self.video_received_flags[port] = True
                if self.ui.load_pages.pages.currentWidget().objectName()=="page_1":
                    MainFunctions.set_page(self, self.ui.load_pages.page_3)
            elif pageId==1:
                self.video_received_flags[port] = False
                if self.ui.load_pages.pages.currentWidget().objectName() == "page_3" and\
                        not any(self.video_received_flags.values()):
                    MainFunctions.set_page(self, self.ui.load_pages.page_1)

        self.video_receiver_1.updateFrame.connect(setImage)
        self.video_receiver_1.streamReceived.connect(changeMainPage)
        self.video_receiver_1.start()
        self.video_receiver_2.updateFrame.connect(setImage)
        self.video_receiver_2.streamReceived.connect(changeMainPage)
        self.video_receiver_2.start()

        # Page4
        # ///////////////////////////////////////////////////////////////
        # Create a label for the display camera
        def insertInfoDisplay(_key,_value,info_id):
            formLayout_info = None
            if info_id[0] == "1":
                formLayout_info = self.ui.load_pages.formLayout_1
                labels_info=self.labels_info[1]
            elif info_id[0] == "2":
                formLayout_info = self.ui.load_pages.formLayout_2
                labels_info = self.labels_info[2]
            else:
                print("Error: Wrong uavId!")
                return
            _label = PyLineEdit(
                text=_key,
                radius=8,
                border_size=2,
                color=self.themes["app_color"]["text_foreground"],
                selection_color=self.themes["app_color"]["white"],
                bg_color=self.themes["app_color"]["bg_three"],
                bg_color_active=self.themes["app_color"]["bg_three"],
                context_color=self.themes["app_color"]["context_color"]
            )
            _label.setMaximumWidth(120)
            _label.setReadOnly(True)
            if _value is None:
                _value = ""
            labels_info[info_id] = PyLineEdit(
                text=str(_value),
                place_holder_text="No Data",
                radius=8,
                border_size=2,
                color=self.themes["app_color"]["text_foreground"],
                selection_color=self.themes["app_color"]["white"],
                bg_color=self.themes["app_color"]["bg_two"],
                bg_color_active=self.themes["app_color"]["bg_two"],
                context_color=self.themes["app_color"]["context_color"]
            )
            labels_info[info_id].setReadOnly(True)
            labels_info[info_id].setMinimumWidth(200)
            formLayout_info.addRow(_label, labels_info[info_id])

        @Slot(dict)
        def infoDisplay(info):
            if info is not None:
                uavId = info["uavId"]
                if self.labels_info.get(uavId) is None:
                    self.labels_info[uavId] = {}
                labels_info=self.labels_info[uavId]
                update_flag=False
                for key,value in info.items():
                    info_id = str(uavId) + key
                    if value is None or type(value) != dict:
                        value="" if value is None else str(value)
                        if labels_info.get(info_id, None) is not None:
                            labels_info[info_id].setText(value)
                        else:
                            insertInfoDisplay(key, value, info_id)
                            update_flag = True
                    else:
                        for _key,_value in value.items():
                            info_id=info_id + _key
                            if labels_info.get(info_id,None) is not None:
                                labels_info[info_id].setText(str(_value))
                            else:
                                insertInfoDisplay(_key, _value, info_id)
                                update_flag=True
                if update_flag:
                    self.ui.load_pages.page_4.update()

            # elif state==2 and info is None:
            #     for each in self.labels_info.items():
            #         each.setText("")
            else:
                pass
                # print("waiting for info...")

        self.info_receiver.infoReceived.connect(infoDisplay)
        self.info_receiver.start()

        # Page5
        # ///////////////////////////////////////////////////////////////
        self.code_editor.code_editor.setStyleSheet("""
            font-family: Microsoft YaHei UI;
            color: black;
            font-size: 16px;
        """)
        self.code_editor.line_edit.set_stylesheet(
            radius = 4,
            border_size = 2,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"]
        )

        @Slot()
        def addToHistory():
            self.left_column_line_edit.addToHistory(self.code_editor.getCodeEntered())
        self.left_column_line_edit.history_flag=False
        self.code_editor.line_edit.returnPressed.connect(addToHistory)

        @Slot(str)
        def printToCodeEditor(text):
            self.code_editor.appendTextLine(text,"red")

        @Slot(str)
        def printToReminderBox(text):
            rb = MyReminderBox(
                text=text,
                parent=self.ui.title_bar,
                bg_color=self.themes["app_color"]["dark_two"],
                text_font=f'{self.settings["font"]["text_size"]}pt "{self.settings["font"]["family"]}"',
                color=self.themes["app_color"]["text_foreground"],
                border_radius=10,
                btn_radius=8,
                btn_color=self.themes["app_color"]["text_foreground"],
                btn_bg_color=self.themes["app_color"]["dark_one"],
                btn_bg_color_hover=self.themes["app_color"]["dark_three"],
                btn_bg_color_pressed=self.themes["app_color"]["dark_four"])
            rb.show()

        self.command_sender.printToCodeEditor.connect(printToCodeEditor)
        self.video_receiver_1.printToCodeEditor.connect(printToCodeEditor)
        self.video_receiver_2.printToCodeEditor.connect(printToCodeEditor)
        self.command_sender.printToReminderBox.connect(printToReminderBox)
        self.video_receiver_1.printToReminderBox.connect(printToReminderBox)
        self.video_receiver_2.printToReminderBox.connect(printToReminderBox)

        self.ui.load_pages.layout_code.addWidget(self.code_editor)


        # LEFT COLUMN
        # ///////////////////////////////////////////////////////////////

        # # BTN 1
        # self.left_btn_1 = PyPushButton(
        #     text="Btn 1",
        #     radius=8,
        #     color=self.themes["app_color"]["text_foreground"],
        #     bg_color=self.themes["app_color"]["dark_one"],
        #     bg_color_hover=self.themes["app_color"]["dark_three"],
        #     bg_color_pressed=self.themes["app_color"]["dark_four"]
        # )
        # self.left_btn_1.setMaximumHeight(40)
        # self.ui.left_column.menus.btn_1_layout.addWidget(self.left_btn_1)
        #
        # # BTN 2
        # self.left_btn_2 = PyPushButton(
        #     text="Btn With Icon",
        #     radius=8,
        #     color=self.themes["app_color"]["text_foreground"],
        #     bg_color=self.themes["app_color"]["dark_one"],
        #     bg_color_hover=self.themes["app_color"]["dark_three"],
        #     bg_color_pressed=self.themes["app_color"]["dark_four"]
        # )
        # self.icon = QIcon(Functions.set_svg_icon("icon_settings.svg"))
        # self.left_btn_2.setIcon(self.icon)
        # self.left_btn_2.setMaximumHeight(40)
        # self.ui.left_column.menus.btn_2_layout.addWidget(self.left_btn_2)
        #
        # # BTN 3 - Default QPushButton
        # self.left_btn_3 = QPushButton("Default QPushButton")
        # self.left_btn_3.setMaximumHeight(40)
        # self.ui.left_column.menus.btn_3_layout.addWidget(self.left_btn_3)
        #
        # # PAGES
        # # ///////////////////////////////////////////////////////////////
        #
        # # PAGE 1 - ADD LOGO TO MAIN PAGE
        # self.logo_svg = QSvgWidget(Functions.set_svg_image("logo_home.svg"))
        # self.ui.load_pages.logo_layout.addWidget(self.logo_svg, Qt.AlignCenter, Qt.AlignCenter)
        #
        # # PAGE 2
        # # CIRCULAR PROGRESS 1
        # self.circular_progress_1 = PyCircularProgress(
        #     value = 80,
        #     progress_color = self.themes["app_color"]["context_color"],
        #     text_color = self.themes["app_color"]["text_title"],
        #     font_size = 14,
        #     bg_color = self.themes["app_color"]["dark_four"]
        # )
        # self.circular_progress_1.setFixedSize(200,200)
        #
        # # CIRCULAR PROGRESS 2
        # self.circular_progress_2 = PyCircularProgress(
        #     value = 45,
        #     progress_width = 4,
        #     progress_color = self.themes["app_color"]["context_color"],
        #     text_color = self.themes["app_color"]["context_color"],
        #     font_size = 14,
        #     bg_color = self.themes["app_color"]["bg_three"]
        # )
        # self.circular_progress_2.setFixedSize(160,160)
        #
        # # CIRCULAR PROGRESS 3
        # self.circular_progress_3 = PyCircularProgress(
        #     value = 75,
        #     progress_width = 2,
        #     progress_color = self.themes["app_color"]["pink"],
        #     text_color = self.themes["app_color"]["white"],
        #     font_size = 14,
        #     bg_color = self.themes["app_color"]["bg_three"]
        # )
        # self.circular_progress_3.setFixedSize(140,140)
        #
        # # PY SLIDER 1
        # self.vertical_slider_1 = PySlider(
        #     margin=8,
        #     bg_size=10,
        #     bg_radius=5,
        #     handle_margin=-3,
        #     handle_size=16,
        #     handle_radius=8,
        #     bg_color = self.themes["app_color"]["dark_three"],
        #     bg_color_hover = self.themes["app_color"]["dark_four"],
        #     handle_color = self.themes["app_color"]["context_color"],
        #     handle_color_hover = self.themes["app_color"]["context_hover"],
        #     handle_color_pressed = self.themes["app_color"]["context_pressed"]
        # )
        # self.vertical_slider_1.setMinimumHeight(100)
        #
        # # PY SLIDER 2
        # self.vertical_slider_2 = PySlider(
        #     bg_color = self.themes["app_color"]["dark_three"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     handle_color = self.themes["app_color"]["context_color"],
        #     handle_color_hover = self.themes["app_color"]["context_hover"],
        #     handle_color_pressed = self.themes["app_color"]["context_pressed"]
        # )
        # self.vertical_slider_2.setMinimumHeight(100)
        #
        # # PY SLIDER 3
        # self.vertical_slider_3 = PySlider(
        #     margin=8,
        #     bg_size=10,
        #     bg_radius=5,
        #     handle_margin=-3,
        #     handle_size=16,
        #     handle_radius=8,
        #     bg_color = self.themes["app_color"]["dark_three"],
        #     bg_color_hover = self.themes["app_color"]["dark_four"],
        #     handle_color = self.themes["app_color"]["context_color"],
        #     handle_color_hover = self.themes["app_color"]["context_hover"],
        #     handle_color_pressed = self.themes["app_color"]["context_pressed"]
        # )
        # self.vertical_slider_3.setOrientation(Qt.Horizontal)
        # self.vertical_slider_3.setMaximumWidth(200)
        #
        # # PY SLIDER 4
        # self.vertical_slider_4 = PySlider(
        #     bg_color = self.themes["app_color"]["dark_three"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     handle_color = self.themes["app_color"]["context_color"],
        #     handle_color_hover = self.themes["app_color"]["context_hover"],
        #     handle_color_pressed = self.themes["app_color"]["context_pressed"]
        # )
        # self.vertical_slider_4.setOrientation(Qt.Horizontal)
        # self.vertical_slider_4.setMaximumWidth(200)
        #
        # # ICON BUTTON 1
        # self.icon_button_1 = PyIconButton(
        #     icon_path = Functions.set_svg_icon("icon_heart.svg"),
        #     parent = self,
        #     app_parent = self.ui.central_widget,
        #     tooltip_text = "Icon button - Heart",
        #     width = 40,
        #     height = 40,
        #     radius = 20,
        #     dark_one = self.themes["app_color"]["dark_one"],
        #     icon_color = self.themes["app_color"]["icon_color"],
        #     icon_color_hover = self.themes["app_color"]["icon_hover"],
        #     icon_color_pressed = self.themes["app_color"]["icon_active"],
        #     icon_color_active = self.themes["app_color"]["icon_active"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     bg_color_pressed = self.themes["app_color"]["pink"]
        # )
        #
        # # ICON BUTTON 2
        # self.icon_button_2 = PyIconButton(
        #     icon_path = Functions.set_svg_icon("icon_add_user.svg"),
        #     parent = self,
        #     app_parent = self.ui.central_widget,
        #     tooltip_text = "BTN with tooltip",
        #     width = 40,
        #     height = 40,
        #     radius = 8,
        #     dark_one = self.themes["app_color"]["dark_one"],
        #     icon_color = self.themes["app_color"]["icon_color"],
        #     icon_color_hover = self.themes["app_color"]["icon_hover"],
        #     icon_color_pressed = self.themes["app_color"]["white"],
        #     icon_color_active = self.themes["app_color"]["icon_active"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     bg_color_pressed = self.themes["app_color"]["green"],
        # )
        #
        # # ICON BUTTON 3
        # self.icon_button_3 = PyIconButton(
        #     icon_path = Functions.set_svg_icon("icon_add_user.svg"),
        #     parent = self,
        #     app_parent = self.ui.central_widget,
        #     tooltip_text = "BTN actived! (is_actived = True)",
        #     width = 40,
        #     height = 40,
        #     radius = 8,
        #     dark_one = self.themes["app_color"]["dark_one"],
        #     icon_color = self.themes["app_color"]["icon_color"],
        #     icon_color_hover = self.themes["app_color"]["icon_hover"],
        #     icon_color_pressed = self.themes["app_color"]["white"],
        #     icon_color_active = self.themes["app_color"]["icon_active"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     bg_color_pressed = self.themes["app_color"]["context_color"],
        #     is_active = True
        # )
        #
        # # PUSH BUTTON 1
        # self.push_button_1 = PyPushButton(
        #     text = "Button Without Icon",
        #     radius  =8,
        #     color = self.themes["app_color"]["text_foreground"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     bg_color_pressed = self.themes["app_color"]["dark_four"]
        # )
        # self.push_button_1.setMinimumHeight(40)
        #
        # # PUSH BUTTON 2
        # self.push_button_2 = PyPushButton(
        #     text = "Button With Icon",
        #     radius = 8,
        #     color = self.themes["app_color"]["text_foreground"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     bg_color_pressed = self.themes["app_color"]["dark_four"]
        # )
        # self.icon_2 = QIcon(Functions.set_svg_icon("icon_settings.svg"))
        # self.push_button_2.setMinimumHeight(40)
        # self.push_button_2.setIcon(self.icon_2)
        #
        # # PY LINE EDIT
        # self.line_edit = PyLineEdit(
        #     text = "",
        #     place_holder_text = "Place holder text",
        #     radius = 8,
        #     border_size = 2,
        #     color = self.themes["app_color"]["text_foreground"],
        #     selection_color = self.themes["app_color"]["white"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_active = self.themes["app_color"]["dark_three"],
        #     context_color = self.themes["app_color"]["context_color"]
        # )
        # self.line_edit.setMinimumHeight(30)
        #
        # # TOGGLE BUTTON
        # self.toggle_button = PyToggle(
        #     width = 50,
        #     bg_color = self.themes["app_color"]["dark_two"],
        #     circle_color = self.themes["app_color"]["icon_color"],
        #     active_color = self.themes["app_color"]["context_color"]
        # )
        #
        # # TABLE WIDGETS
        # self.table_widget = PyTableWidget(
        #     radius = 8,
        #     color = self.themes["app_color"]["text_foreground"],
        #     selection_color = self.themes["app_color"]["context_color"],
        #     bg_color = self.themes["app_color"]["bg_two"],
        #     header_horizontal_color = self.themes["app_color"]["dark_two"],
        #     header_vertical_color = self.themes["app_color"]["bg_three"],
        #     bottom_line_color = self.themes["app_color"]["bg_three"],
        #     grid_line_color = self.themes["app_color"]["bg_one"],
        #     scroll_bar_bg_color = self.themes["app_color"]["bg_one"],
        #     scroll_bar_btn_color = self.themes["app_color"]["dark_four"],
        #     context_color = self.themes["app_color"]["context_color"]
        # )
        # self.table_widget.setColumnCount(3)
        # self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        #
        # # Columns / Header
        # self.column_1 = QTableWidgetItem()
        # self.column_1.setTextAlignment(Qt.AlignCenter)
        # self.column_1.setText("NAME")
        #
        # self.column_2 = QTableWidgetItem()
        # self.column_2.setTextAlignment(Qt.AlignCenter)
        # self.column_2.setText("NICK")
        #
        # self.column_3 = QTableWidgetItem()
        # self.column_3.setTextAlignment(Qt.AlignCenter)
        # self.column_3.setText("PASS")
        #
        # # Set column
        # self.table_widget.setHorizontalHeaderItem(0, self.column_1)
        # self.table_widget.setHorizontalHeaderItem(1, self.column_2)
        # self.table_widget.setHorizontalHeaderItem(2, self.column_3)
        #
        # for x in range(10):
        #     row_number = self.table_widget.rowCount()
        #     self.table_widget.insertRow(row_number) # Insert row
        #     self.table_widget.setItem(row_number, 0, QTableWidgetItem(str("Wanderson"))) # Add name
        #     self.table_widget.setItem(row_number, 1, QTableWidgetItem(str("vfx_on_fire_" + str(x)))) # Add nick
        #     self.pass_text = QTableWidgetItem()
        #     self.pass_text.setTextAlignment(Qt.AlignCenter)
        #     self.pass_text.setText("12345" + str(x))
        #     self.table_widget.setItem(row_number, 2, self.pass_text) # Add pass
        #     self.table_widget.setRowHeight(row_number, 22)
        #
        # # ADD WIDGETS
        # self.ui.load_pages.row_1_layout.addWidget(self.circular_progress_1)
        # self.ui.load_pages.row_1_layout.addWidget(self.circular_progress_2)
        # self.ui.load_pages.row_1_layout.addWidget(self.circular_progress_3)
        # self.ui.load_pages.row_2_layout.addWidget(self.vertical_slider_1)
        # self.ui.load_pages.row_2_layout.addWidget(self.vertical_slider_2)
        # self.ui.load_pages.row_2_layout.addWidget(self.vertical_slider_3)
        # self.ui.load_pages.row_2_layout.addWidget(self.vertical_slider_4)
        # self.ui.load_pages.row_3_layout.addWidget(self.icon_button_1)
        # self.ui.load_pages.row_3_layout.addWidget(self.icon_button_2)
        # self.ui.load_pages.row_3_layout.addWidget(self.icon_button_3)
        # self.ui.load_pages.row_3_layout.addWidget(self.push_button_1)
        # self.ui.load_pages.row_3_layout.addWidget(self.push_button_2)
        # self.ui.load_pages.row_3_layout.addWidget(self.toggle_button)
        # self.ui.load_pages.row_4_layout.addWidget(self.line_edit)
        # self.ui.load_pages.row_5_layout.addWidget(self.table_widget)
        #
        # # RIGHT COLUMN
        # # ///////////////////////////////////////////////////////////////
        #
        # # BTN 1
        # self.right_btn_1 = PyPushButton(
        #     text="Show Menu 2",
        #     radius=8,
        #     color=self.themes["app_color"]["text_foreground"],
        #     bg_color=self.themes["app_color"]["dark_one"],
        #     bg_color_hover=self.themes["app_color"]["dark_three"],
        #     bg_color_pressed=self.themes["app_color"]["dark_four"]
        # )
        # self.icon_right = QIcon(Functions.set_svg_icon("icon_arrow_right.svg"))
        # self.right_btn_1.setIcon(self.icon_right)
        # self.right_btn_1.setMaximumHeight(40)
        # self.right_btn_1.clicked.connect(lambda: MainFunctions.set_right_column_menu(
        #     self,
        #     self.ui.right_column.menu_2
        # ))
        # self.ui.right_column.btn_1_layout.addWidget(self.right_btn_1)
        #
        # # BTN 2
        # self.right_btn_2 = PyPushButton(
        #     text="Show Menu 1",
        #     radius=8,
        #     color=self.themes["app_color"]["text_foreground"],
        #     bg_color=self.themes["app_color"]["dark_one"],
        #     bg_color_hover=self.themes["app_color"]["dark_three"],
        #     bg_color_pressed=self.themes["app_color"]["dark_four"]
        # )
        # self.icon_left = QIcon(Functions.set_svg_icon("icon_arrow_left.svg"))
        # self.right_btn_2.setIcon(self.icon_left)
        # self.right_btn_2.setMaximumHeight(40)
        # self.right_btn_2.clicked.connect(lambda: MainFunctions.set_right_column_menu(
        #     self,
        #     self.ui.right_column.menu_1
        # ))
        # self.ui.right_column.btn_2_layout.addWidget(self.right_btn_2)

        # ///////////////////////////////////////////////////////////////
        # END - EXAMPLE CUSTOM WIDGETS
        # ///////////////////////////////////////////////////////////////

    # RESIZE GRIPS AND CHANGE POSITION
    # Resize or change position when window is resized
    # ///////////////////////////////////////////////////////////////
    @staticmethod
    def resize_grips(self):
        if self.settings["custom_title_bar"]:
            self.left_grip.setGeometry(5, 10, 10, self.height())
            self.right_grip.setGeometry(self.width() - 15, 10, 10, self.height())
            self.top_grip.setGeometry(5, 5, self.width() - 10, 10)
            self.bottom_grip.setGeometry(5, self.height() - 15, self.width() - 10, 10)
            self.top_right_grip.setGeometry(self.width() - 20, 5, 15, 15)
            self.bottom_left_grip.setGeometry(5, self.height() - 20, 15, 15)
            self.bottom_right_grip.setGeometry(self.width() - 20, self.height() - 20, 15, 15)