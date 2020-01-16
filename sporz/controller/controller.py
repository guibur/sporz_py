import typing as tp
import random

from ..model import Game
from ..view.cli_view import CLIView

from ..enum_api import Role, Genome
from ..message_api import ActionMessage


class Controller:
    def __init__(self, view_class: tp.Type[CLIView]) -> None:
        self.view: CLIView = view_class(self)
        self.game: tp.Optional[Game] = None

    def launch(self) -> None:
        self.view.ask_player_names()

    def set_game(self, players: tp.List[str]) -> None:
        assert len(players) > 5
        self.game = Game(players)

        roles = [
            Role.BASE_MUTANT,
            Role.DOCTOR,
            Role.DOCTOR,
            Role.COMPUTER_SCIENTIST,
            Role.PSYCHOLOGIST,
            Role.GENETICIST,
            Role.SPY,
            Role.HACKER,
            Role.FANATIC,
        ]
        if len(players) <= len(roles):
            roles_to_dist = roles[: len(players)]
        else:
            roles_to_dist = roles + [Role.ASTRONAUT] * (len(players) - len(roles))

        random.shuffle(roles_to_dist)

        genomes_to_suggest = [Genome.NORMAL] * len(roles_to_dist)
        genomes_to_suggest[roles_to_dist.index(Role.BASE_MUTANT)] = Genome.HOST
        for genome_to_give in [Genome.HOST, Genome.RESISTANT]:
            while True:
                idx = random.randint(0, len(genomes_to_suggest) - 1)
                if genomes_to_suggest[idx] is not Genome.NORMAL:
                    continue
                if roles_to_dist[idx] is Role.DOCTOR:
                    continue
                genomes_to_suggest[idx] = genome_to_give
                break
        self.view.suggest_roles_genes(self.game.get_player_names(), roles_to_dist, genomes_to_suggest)

    def set_roles_and_genomes_then_start_game(self, roles: tp.List[Role], genomes: tp.List[Genome]) -> None:
        assert isinstance(self.game, Game)
        self.game.set_roles_and_genomes(roles, genomes)
        self.set_next_turn()

    def set_next_turn(self) -> None:
        assert isinstance(self.game, Game)
        next_turn = self.game.get_next_turn()
        self.view.show_next_turn_actions(next_turn)

    def act(self, action: ActionMessage) -> None:
        assert isinstance(self.game, Game)
        action_result = self.game.act(action)
        self.view.show_turn_results(action_result)

    def get_full_game_state(self) -> None:
        assert isinstance(self.game, Game)
        self.view.show_full_state(self.game.get_full_current_state())
