import typing as tp

from ..enum_api import Turn, Genome
from ..message_api import Player, State, ActionMessage
from ..message_api import ResultMessage, ResultAction, ResultSimpleObservation, ResultSpyInspector


class AbstractTurn:
    def __init__(self, turn_type: Turn):
        self.type = turn_type

    def act(self, players: tp.List[Player], state: State) -> ResultMessage:
        pass

    def get_info(self):
        pass


class ChiefElectionTurn(AbstractTurn):
    def __init__(self, action: ActionMessage):
        super().__init__(Turn.D_CHIEF_ELECTION)
        self.chief = action.target

    def act(self, players: tp.List[Player], state: State) -> ResultSimpleObservation:
        state["chief"] = self.chief
        return {"type": Turn.D_CHIEF_ELECTION, "chief_idx": self.chief, "chief_name": players[self.chief]["name"]}

    def get_info(self):
        return {"type": Turn.D_CHIEF_ELECTION, "elected": self.chief}


class MutantTurn(AbstractTurn):
    def __init__(self, action: ActionMessage):
        super().__init__(Turn.N_MUTANTS)
        self.target = action.target
        self.do = action.action
        self.paralyze = action.secondary_target

    def act(self, players, state):
        result_actions = {
            "type": Turn.N_MUTANTS,
            "paralyzed": None,
            "mutated": None,
            "failed_to_mutate": None,
            "killed": None,
        }
        state["paralyzed"] = self.paralyze
        result_actions["paralyzed"] = players[self.paralyze]["name"]

        if self.target is None:
            return result_actions

        if self.do == "kill":
            state["dead"].add(self.target)
            result_actions["killed"] = players[self.target]["name"]
        elif self.do == "mutate":
            if players[self.target]["genome"] is not Genome.RESISTANT:
                state["mutants"].add(self.target)
                result_actions["mutated"] = players[self.target]["name"]
            else:
                result_actions["failed_to_mutate"] = players[self.target]["name"]
        else:
            raise ValueError("Unknown action: {}".format(self.do))
        return result_actions

    def get_info(self):
        return {"target": self.target, "do": self.do, "paralyze": self.paralyze}


class DoctorTurn(AbstractTurn):
    def __init__(self, action: ActionMessage):
        super().__init__(Turn.N_DOCTORS)
        self.targets = [action.target]
        if action.secondary_target is not None:
            self.targets.append(action.secondary_target)
        self.dos = action.action.split()

    def act(self, players: tp.List[Player], state):
        result_actions = {"type": Turn.N_DOCTORS, "healed": [], "failed_to_heal": [], "killed": None}
        for p, d in zip(self.targets, self.dos):
            if d == "heal":
                if players[p]["genome"] is not Genome.HOST and p in state["mutants"]:
                    state["mutants"].remove(p)
                    result_actions["healed"].append(p)
                else:
                    result_actions["failed_to_heal"].append(p)
            elif d == "kill":
                state["dead"].add(p)
                result_actions["killed"].append(p)
        return result_actions

    def get_info(self):
        return {"targets": self.targets, "dos": self.dos}


class ComputerScientistTurn(AbstractTurn):
    def __init__(self, action: ActionMessage) -> None:
        super().__init__(Turn.N_COMPUTER_SCIENTIST)
        self.target = action.target

    def act(self, players, state):
        return {"type": Turn.N_COMPUTER_SCIENTIST, "n_mutants": len(state["mutants"])}

    def get_info(self):
        return {"target": self.target}


def create_turn(turn_type: Turn, action: ActionMessage) -> AbstractTurn:
    TURN_CLASSES = {
        Turn.D_CHIEF_ELECTION: ChiefElectionTurn,
        #  Turn.D_AUTOPSY: None,
        #  Turn.D_VOTE: None,
        #  Turn.D_EXECUTION: None,
        Turn.N_MUTANTS: MutantTurn,
        Turn.N_DOCTORS: DoctorTurn,
        Turn.N_COMPUTER_SCIENTIST: ComputerScientistTurn,
        #  Turn.N_PSYCHOLOGIST: None,
        #  Turn.N_GENETICIST: None,
        #  Turn.N_SPY: None,
        #  Turn.N_HACKER: None,
    }
    return TURN_CLASSES[turn_type](action)
