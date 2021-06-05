from PyQt5.QtWidgets import QPlainTextEdit, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
import subprocess as sp


class Terminal(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.hasRunningProcess = False
        self.command = ''
        self.settings = {}
        self.oldHistory = []
        self.newHistory = []
        self._set()
        self._readHistory()

    def _set(self):
        self.cursor = self.textCursor()
        self.setStyleSheet(
            'color: white; border-radius: 0; background-color: black; font-size: 15px;')
        self.setUndoRedoEnabled(False)
        self._setText()

    def _setText(self, text="$"):
        self.text = f'<span style="color: green; font-size: 16px;">{text}</span> '
        self.appendHtml(self.text)
        self.startPos = self.cursor.positionInBlock()

    def keyPressEvent(self, e):
        # up, down
        k = e.key()
        if k == Qt.Key_Backspace:
            pos = self.cursor.positionInBlock()
            if pos <= self.startPos:
                e.ignore()
            else:
                QPlainTextEdit.keyPressEvent(self, e)
        elif k == Qt.Key_Return:
            if self.cursor.hasSelection():
                self.command = self.cursor.selectedText()[2:].rstrip()
                self.newHistory.append(self.command)
                self._writeCommand(self.command)
                self._execCommand(self.command)
            else:
                self._setText()
        elif k == Qt.Key_Up:
            if self.cursor.hasSelection():
                self.cursor.removeSelectedText()
                self.cursor.insertHtml(self.text)
                self.cursor.insertText(self.newHistory[-1])
            return
        else:
            QPlainTextEdit.keyPressEvent(self, e)
            self.cursor.select(QTextCursor.LineUnderCursor)

    def _execCommand(self, command):
        if command == 'clear' or command == 'cls':
            self.clear()
            self._setText()
            return
        elif command == 'history':
            self.appendPlainText(self.oldHistory)
            self._setText()
            return
        # elif sudo
        # elif cd
        else:
            self.hasRunningProcess = True
            output = sp.Popen(
                command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            result = output.communicate()
            text = result[0] if result[0] else result[1]
            self.appendPlainText(text.decode('utf-8'))
        self.cursor.clearSelection()
        self._setText()
        # write history
        # read history
        # shortcuts[up, down, (ctrl+c (2 functions)) ]
        # update JIT

    def _writeCommand(self, command):
        with open('./assets/history/data.txt', 'a') as f:
            f.write(f'{command}\n')
        self._readHistory()

    def _readHistory(self):
        with open('./assets/history/data.txt', 'r') as f:
            self.oldHistory = f.read()
