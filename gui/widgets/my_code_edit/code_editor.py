#############################################################################
##
## Copyright (C) 2019 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QTextFormat
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit


class LineNumberArea(QWidget):
    def __init__(self, editor):
        QWidget.__init__(self, editor)
        self._code_editor = editor

    def sizeHint(self):
        return QSize(self._code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._code_editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged[int].connect(self.update_line_number_area_width)
        self.updateRequest[QRect, int].connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num *= 0.1
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cr = self.contentsRect()
        width = self.line_number_area_width()
        rect = QRect(cr.left(), cr.top(), width, cr.height())
        self.line_number_area.setGeometry(rect)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = self.contentOffset()
        top = self.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                width = self.line_number_area.width()
                height = self.fontMetrics().height()
                painter.drawText(0, top, width, height, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    @Slot()
    def update_line_number_area_width(self, newBlockCount):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    @Slot()
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            width = self.line_number_area.width()
            self.line_number_area.update(0, rect.y(), width, rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    @Slot()
    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            line_color = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(line_color)

            selection.format.setProperty(QTextFormat.FullWidthSelection, True)

            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()

            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)


from gui.widgets.py_line_edit import PyLineEdit
import PySide6.QtCore as QtCore
import PySide6.QtWidgets as QtWidgets
import numpy as np


class CodeInputLine(PyLineEdit):
    def __init__(self):
        super().__init__()
        self.code_history = []
        self.iter_code_history=reversed(self.code_history)
        self.code_str=""
        self.returnPressed.connect(self.returnPressedMethod)
        self.history_flag=True

    def addToHistory(self,str):
        try:
            self.code_history.remove(str)
        except Exception:
            pass
        self.code_history.append(str)
        self.iter_code_history = reversed(self.code_history)

    @Slot()
    def returnPressedMethod(self):
        self.code_str = self.text()
        if len(self.code_str)==0:
            return
        if self.history_flag:
            self.addToHistory(self.text())
        self.clear()

    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Up:
            if self.code_history.__len__()!=0:
                try:
                    self.setText(next(self.iter_code_history))
                except StopIteration:
                    self.iter_code_history=reversed(self.code_history)
                    self.setText(next(self.iter_code_history))
        elif event.key()==QtCore.Qt.Key_Down:
            if self.code_history.__len__() != 0:
                self.iter_code_history = reversed(self.code_history)
                self.setText(next(self.iter_code_history))
        super(CodeInputLine, self).keyPressEvent(event)

    def saveHistory(self):
        a = np.array(self.code_history)
        import os
        try:
            np.save("properties/cookie.npy", a)
        except Exception:
            os.makedirs("./properties")
            np.save("properties/cookie.npy", a)

    def loadHistory(self):
        try:
            self.code_history = np.load("properties/cookie.npy").tolist()
        except Exception as e:
            pass


class MyCodeEditor(QWidget):
    def __init__(self):
        super().__init__(None)
        self.code_editor=CodeEditor()
        self.line_edit=CodeInputLine()
        self.code_editor.setReadOnly(True)
        self.line_edit.returnPressed.connect(self.codeEntered)
        self.layout=QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.code_editor)
        self.layout.addWidget(self.line_edit)
        self.loadCookie()

    def appendTextLine(self,text:str,color="black"):
        if text.startswith("<font"):
            self.code_editor.appendHtml(text)
        else:
            self.code_editor.appendHtml(f'<font style="white-space: pre-line;" color=\"{color}\">{text}</font>')

    def enterCode(self,code):
        self.line_edit.setText(code)
        self.line_edit.returnPressed.emit()

    @Slot()
    def codeEntered(self):
        self.code_editor.appendPlainText(f">>{self.getCodeEntered()}")
        if self.getCodeEntered()=="cl" or self.getCodeEntered()=="clear":
            self.clear()

    def getCodeEntered(self):
        return self.line_edit.code_str

    def clear(self):
        self.code_editor.clear()
        self.line_edit.code_str=""

    def saveCookie(self):
        self.line_edit.saveHistory()

    def loadCookie(self):
        self.line_edit.loadHistory()


if __name__ == "__main__":
    import PySide6.QtWidgets as pyqt
    import sys
    app = pyqt.QApplication([])
    editor = MyCodeEditor()
    editor.setWindowTitle("Code Editor Example")
    editor.show()
    #editor.setReadOnly(True)
    print(editor.line_edit.font(), editor.code_editor.font(),
            editor.code_editor.line_number_area.font())

    sys.exit(app.exec())
