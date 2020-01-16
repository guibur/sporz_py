import typing as tp
from dataclasses import dataclass

from .enum_api import Turn, Role, Genome, SlotType
from .model.turn import AbstractTurn


@dataclass
class State:
    chief: tp.Optional[int]
    mutants: tp.Set[int]
    deads: tp.Set[int]
    paralyzed: tp.Optional[int]


@dataclass
class Slot:
    type: SlotType
    turns: tp.List[AbstractTurn]


@dataclass
class Player:
    name: str
    role: tp.Optional[Role]
    genome: tp.Optional[Genome]


class PlayerState(Player):
    dead: bool = False
    chief: bool = False
    mutant: bool = False
    paralyzed: bool = False

    @classmethod
    def copy(cls, player: Player) -> "PlayerState":
        return cls(name=player.name, role=player.role, genome=player.genome)


@dataclass
class PreActionMessage:
    type: Turn
    players: tp.Optional[tp.Sequence[str]] = None
    paralyzed: tp.Optional[tp.Union[bool, tp.Sequence[bool]]] = None
    mutated: tp.Optional[tp.Union[bool, tp.Sequence[bool]]] = None
    choices: tp.Optional[tp.Sequence[str]] = None
    excluded: tp.Optional[tp.Set[int]] = None


@dataclass
class ActionMessage:
    target: int
    action: str = ""
    secondary_target: tp.Optional[int] = None


@dataclass
class ResultAction:
    type: Turn
    main_action: tp.Optional[str]
    main_action_failed: tp.Optional[str]
    killed: tp.Optional[str]
    paralyzed: tp.Optional[str] = None


@dataclass
class ResultSimpleObservation:
    type: Turn
    target: tp.Optional[tp.Union[str, Role]] = None
    result: tp.Optional[tp.Union[bool, Genome, int]] = None


@dataclass
class ResultSpyInspector:
    type: Turn
    target: tp.Optional[str]
    mutated: bool
    paralyzed: bool
    healed: bool
    psychologist: bool
    geneticist: bool
    nark: tp.Optional[bool]
    spy_inspector: tp.Optional[bool]


ResultMessage = tp.Union[ResultAction, ResultSimpleObservation, ResultSpyInspector]
