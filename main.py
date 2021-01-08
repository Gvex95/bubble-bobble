from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import main_menu
import enter_names_menu
import sys

class WindowController:

    def __init__(self):
        pass

    def show_main_menu(self):
        self.main_menu = main_menu.MainWindow()
        #If play is pressed we need to show play_menu
        self.main_menu.win_change_signal.connect(self.show_enter_names_menu)
        self.main_menu.show()

    def show_enter_names_menu(self):
        self.enter_names_menu = enter_names_menu.EnterNamesWindow()
        # When play is pressed we need to start game
        self.enter_names_menu.win_change_signal.connect(self.show_game)
        # Close main menu
        self.main_menu.close()
        self.enter_names_menu.show()

    def show_game(self):
        pass

if __name__ == '__main__':
    print("MRS")
    App = QApplication(sys.argv)

    windowController = WindowController()
    
    windowController.show_main_menu()
    
    #start
    sys.exit(App.exec())