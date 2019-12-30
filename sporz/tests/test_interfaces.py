from unittest.mock import Mock, patch

from sporz.view.cli_view import CLIView
from sporz.model.turn import *
from sporz.controller import Controller


def test_chief_election():
    mock_controller = Mock(spec=Controller)
    view = CLIView(mock_controller)
