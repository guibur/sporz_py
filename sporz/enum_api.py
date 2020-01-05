import enum


class SlotType(enum.Enum):
    FIRST_DAY = enum.auto()
    DAY = enum.auto()
    NIGHT = enum.auto()


class Role(enum.Enum):
    ASTRONAUT = enum.auto()
    BASE_MUTANT = enum.auto()
    DOCTOR = enum.auto()
    COMPUTER_SCIENTIST = enum.auto()
    PSYCHOLOGIST = enum.auto()
    GENETICIST = enum.auto()
    SPY = enum.auto()  # learn what happened to sb
    NARK = enum.auto()  # can know if somebody is a fanatic
    HACKER = enum.auto()  # can steal role of psy, gen or cp
    INSPECTOR = enum.auto()  # spy, but for previous night
    FANATIC = enum.auto()


class Genome(enum.Enum):
    NORMAL = enum.auto()
    RESISTANT = enum.auto()
    HOST = enum.auto()


class Turn(enum.Enum):
    D_CHIEF_ELECTION = enum.auto()
    D_AUTOPSY = enum.auto()
    D_VOTE = enum.auto()
    D_EXECUTION = enum.auto()
    N_MUTANTS = enum.auto()
    N_DOCTORS = enum.auto()
    N_COMPUTER_SCIENTIST = enum.auto()
    N_PSYCHOLOGIST = enum.auto()
    N_GENETICIST = enum.auto()
    N_SPY = enum.auto()
    N_HACKER = enum.auto()
    N_NARK = enum.auto()
    N_INSPECTOR = enum.auto()
