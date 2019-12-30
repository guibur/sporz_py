from ..enum_api import Turn, Genome


class AbstractTurn:
    def __init__(self, turn_type):
        self.type = turn_type

    def act(self, players, state):
        pass

    def get_info(self):
        pass


class ChiefElectionTurn(AbstractTurn):
    def __init__(self, chief):
        super().__init__(Turn.D_CHIEF_ELECTION)
        self.chief = chief

    def act(self, players, state):
        state["chief"] = self.chief
        return {"type": Turn.D_CHIEF_ELECTION, "chief_idx": self.chief, "chief_name": players[self.chief]["name"]}

    def get_info(self):
        return {"type": Turn.D_CHIEF_ELECTION, "elected": self.chief}


class MutantTurn(AbstractTurn):
    def __init__(self, target, do, paralyze):
        super().__init__(Turn.N_MUTANTS)
        self.target = target
        self.do = do
        self.paralyze = paralyze

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
    def __init__(self, targets, dos):
        super().__init__(Turn.N_DOCTORS)
        self.targets = targets
        self.dos = dos

    def act(self, players, state):
        result_actions = {"type": Turn.N_DOCTORS, "healed": [], "failed_to_heal": [], "killed": None}
        for p, d in zip(self.targets, self.dos):
            if d == "heal":
                if players[p]["genome"] is not Genome.HOST:
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
    def __init__(self, target):
        super().__init__(Turn.N_COMPUTER_SCIENTIST)
        self.target = target

    def act(self, players, state):
        return {"type": Turn.N_COMPUTER_SCIENTIST, "n_mutants": len(state["mutants"])}

    def get_info(self):
        return {"target": self.target}


def create_turn(turn_type, **kwargs):
    TURN_CLASSES = {
        Turn.D_CHIEF_ELECTION: ChiefElectionTurn,
        Turn.D_AUTOPSY: None,
        Turn.D_VOTE: None,
        Turn.D_EXECUTION: None,
        Turn.N_MUTANTS: MutantTurn,
        Turn.N_DOCTORS: DoctorTurn,
        Turn.N_COMPUTER_SCIENTIST: ComputerScientistTurn,
        Turn.N_PSYCHOLOGIST: None,
        Turn.N_GENETICIST: None,
        Turn.N_SPY: None,
        Turn.N_HACKER: None,
    }
    return TURN_CLASSES[turn_type](**kwargs)
