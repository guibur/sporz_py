import typing as tp
from copy import copy

from ..enum_api import Role, Genome, Turn, SlotType
from ..message_api import State, Slot, Player, PlayerState
from ..message_api import PreActionMessage, ActionMessage, ResultMessage
from .turn import create_turn, AbstractTurn


NIGHT_STATE_ORDER = [
    Turn.N_MUTANTS,
    Turn.N_DOCTORS,
    Turn.N_COMPUTER_SCIENTIST,
    Turn.N_PSYCHOLOGIST,
    Turn.N_GENETICIST,
    Turn.N_NARK,
    Turn.N_HACKER,
    Turn.N_SPY,
    Turn.N_INSPECTOR,
]


class Game:
    def __init__(
        self,
        player_names: tp.List[str],
        player_roles: tp.Optional[tp.List[Role]] = None,
        player_genomes: tp.Optional[tp.List[Genome]] = None,
    ) -> None:
        self.slots: tp.List[Slot] = []
        self.players: tp.List[Player] = [Player(name=name, role=None, genome=None) for name in player_names]
        if player_roles and player_genomes:
            self.set_roles_and_genomes(player_roles, player_genomes)
        elif player_roles or player_genomes:
            raise TypeError("Cannot set roles without genomes")

    def set_roles_and_genomes(self, player_roles: tp.List[Role], player_genomes: tp.List[Genome]) -> None:
        for i, (role, genome) in enumerate(zip(player_roles, player_genomes)):
            self.players[i].role = role
            self.players[i].genome = genome

    def get_players(self, player_role: Role) -> tp.List[int]:
        found_players = []
        for i, p in enumerate(self.players):
            if p.role is player_role:
                found_players.append(i)
        return found_players

    def get_player_names(self) -> tp.List[str]:
        return [p["name"] for p in self.players]  # type: ignore

    def get_last_turn(self) -> AbstractTurn:
        return self.slots[-1].turns[-1]

    def get_next_turn(self, current_turn: tp.Optional[Turn] = None) -> Turn:
        # Starting a game.
        if not self.slots:
            return Turn.D_CHIEF_ELECTION
        if len(self.slots) == 1:
            return Turn.N_MUTANTS

        # We are not starting anymore.
        if current_turn is None:
            current_turn = self.get_last_turn().type

        # Night scenario.
        if current_turn is Turn.N_MUTANTS:
            return Turn.N_DOCTORS
        raise NotImplementedError

    def get_prepare_action_info(self, turn_type: Turn) -> PreActionMessage:
        # Starting a game.
        if turn_type is Turn.D_CHIEF_ELECTION:
            return PreActionMessage(
                type=Turn.D_CHIEF_ELECTION,
                choices=self.get_player_names(),
                excluded=self.resolve_state().deads,
            )
        if turn_type is Turn.N_MUTANTS:
            return PreActionMessage(
                type=Turn.N_MUTANTS,
                players=[self.players[i].name for i in self.get_mutants()],
                choices=self.get_player_names(),
                excluded=self.resolve_state().deads,
            )

        if turn_type is Turn.N_DOCTORS:
            doctors = self.get_players(Role.DOCTOR)
            state = self.resolve_state()
            living_doctors = [p for p in doctors if p not in state.deads]
            return PreActionMessage(
                type=Turn.N_DOCTORS,
                players=[self.players[p].name for p in living_doctors],
                paralyzed=[p != state.paralyzed for p in living_doctors],
                mutated=[p not in state.mutants for p in living_doctors],
                choices=self.get_player_names(),
                excluded=state.deads,
            )
        raise NotImplementedError

    #  def is_game_over(self) -> bool:
    #  pass

    def act(self, action: ActionMessage) -> ResultMessage:
        turn_type = self.get_next_turn()
        if not self.slots:
            self.slots.append(Slot(type=SlotType.FIRST_DAY, turns=[]))
        elif turn_type is Turn.N_MUTANTS:
            self.slots.append(Slot(type=SlotType.NIGHT, turns=[]))
        elif (turn_type is Turn.D_AUTOPSY or turn_type is Turn.D_VOTE) and self.slots[-1].type == SlotType.NIGHT:
            self.slots.append(Slot(type=SlotType.DAY, turns=[]))
        self.slots[-1].turns.append(create_turn(turn_type, action))
        state_just_before = self.resolve_state()
        return self.get_last_turn().act(self.players, state_just_before)

    def resolve_state(self) -> State:
        state: State = State(
            chief=None, mutants=set(), deads=set(), paralyzed=None,
        )
        for i, p in enumerate(self.players):
            if p.role is Role.BASE_MUTANT:
                state.mutants.add(i)
        for slot in self.slots:
            for turn in slot.turns:
                turn.act(self.players, state)
        return state

    def get_full_current_state(self) -> tp.List[PlayerState]:
        state = self.resolve_state()
        full_state = []
        for idx, player in enumerate(self.players):
            full_state.append(PlayerState.copy(player))
            full_state[-1].chief = idx == state.chief
            full_state[-1].mutant = idx in state.mutants
            full_state[-1].dead = idx in state.deads
            full_state[-1].paralyzed = idx == state.paralyzed
        return full_state

    def resolve_state_current_slot(self) -> State:
        state: State = State(chief=None, mutants=set(), deads=set(), paralyzed=None)
        for turn in self.slots[-1].turns:
            turn.act(self.players, state)
        return state

    def get_mutants(self) -> tp.Set[int]:
        return self.resolve_state().mutants

    def player_is_mutant(self, idx: int) -> bool:
        return idx in self.get_mutants()

    #  def get_turn_list(self):
    #  pass

    def player_name(self, idx: int) -> str:
        return self.players[idx].name  # type: ignore

    def player_is_paralyzed(self, idx: int) -> bool:
        return idx == self.resolve_state().paralyzed
