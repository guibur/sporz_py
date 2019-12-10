from sporz.controller import Controller
from sporz.view.cli_view import CLIView

if __name__ == '__main__':
    controller = Controller(CLIView)
    controller.launch()
