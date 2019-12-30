from unittest.mock import Mock, patch
from sporz.enum_api import Role, Genome
from sporz.view.cli_view import CLIView
from sporz.controller.controller import Controller

FULL_STATE = [{"name": "abc", "role": Role.DOCTOR, "genome": Genome.NORMAL,
               "dead": False, "paralyzed": False, "chief": True, "mutant": False},
              {"name": "def", "role": Role.BASE_MUTANT, "genome": Genome.HOST,
               "dead": False, "paralyzed": False, "chief": False, "mutant": True},
              {"name": "ijk", "role": Role.GENETICIST, "genome": Genome.NORMAL,
               "dead": False, "paralyzed": False, "chief": False, "mutant": True},
              {"name": "lmn", "role": Role.COMPUTER_SCIENTIST, "genome": Genome.NORMAL,
               "dead": True, "paralyzed": False, "chief": False, "mutant": False},
              {"name": "opq", "role": Role.PSYCHOLOGIST, "genome": Genome.NORMAL,
               "dead": False, "paralyzed": False, "chief": False, "mutant": True},
              {"name": "rst", "role": Role.SPY, "genome": Genome.HOST,
               "dead": False, "paralyzed": False, "chief": False, "mutant": False},
              {"name": "uvw", "role": Role.DOCTOR, "genome": Genome.NORMAL,
               "dead": False, "paralyzed": False, "chief": False, "mutant": False},
              {"name": "xyz", "role": Role.HACKER, "genome": Genome.RESISTANT,
               "dead": False, "paralyzed": True, "chief": False, "mutant": False},
              {"name": "omega", "role": Role.FANATIC, "genome": Genome.NORMAL,
               "dead": True, "paralyzed": False, "chief": True, "mutant": True},
              ]

@patch('sporz.view.cli_view.input', side_effect=['pepe', 's', '3'])
def test_input(mock_input):
    mock_controller = Mock(spec=Controller)
    view = CLIView(mock_controller)
    res = view.input("ahahah")
    assert not mock_controller.get_full_game_state.called
    assert res == "pepe"
    res = view.input("ohohoh")
    assert mock_controller.get_full_game_state.called_once
    assert res == "3"

def test_show_full_state():
    controller = Controller(CLIView)
    view = controller.view
    view.show_full_state(FULL_STATE)
