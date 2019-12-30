from unittest.mock import Mock
from sporz.enum_api import Role, Genome
from sporz.controller.controller import Controller
from sporz.view.cli_view import CLIView


def test_set_game():
    for _ in range(10):
        mock_view = Mock(spec=CLIView)
        players = [str(i) for i in range(6)]
        controller = Controller(mock_view)
        controller.set_game(players)
        assert controller.view.suggest_roles_genes.called
        arguments = controller.view.suggest_roles_genes.call_args
        names = arguments[0][0] if len(arguments[0]) > 0 else arguments[1]["player_names"]
        roles = arguments[0][1] if len(arguments[0]) > 1 else arguments[1]["roles"]
        genomes = arguments[0][2] if len(arguments[0]) > 2 else arguments[1]["genomes"]
        assert len(names) == len(roles)
        assert len(names) == len(genomes)
        assert len([r for r in roles if r is Role.DOCTOR]) == 2
        assert len([r for r in roles if r is Role.BASE_MUTANT]) == 1
        assert genomes[roles.index(Role.BASE_MUTANT)] is Genome.HOST
        assert all((r != Role.DOCTOR or g == Genome.NORMAL) for r, g in zip(roles, genomes))
        assert len([g for g in genomes if g is Genome.HOST]) == 2
        assert len([g for g in genomes if g is Genome.RESISTANT]) == 1
