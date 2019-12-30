from sporz.model.turn import *
from sporz.model import Game
from sporz.enum_api import Role, Genome

PLAYER_LIST = ['a', 'b', 'c']
ROLE_LIST = [Role.BASE_MUTANT, Role.DOCTOR, Role.ASTRONAUT]
GENOME_LIST = [Genome.NORMAL, Genome.HOST, Genome.RESISTANT]

def test_chief_election():
    game = Game(PLAYER_LIST, ROLE_LIST, GENOME_LIST)
    turn = ChiefElectionTurn(1)
    assert turn.get_info()['elected'] == 1
    state = {'chief': None, 'mutants': set(), 'dead': set(), 'paralyzed': None}
    turn.act(game.players, state)
    assert state['chief'] == 1
    
def test_mutant_turn():
    game = Game(PLAYER_LIST, ROLE_LIST, GENOME_LIST)
    turn = MutantTurn(2, 'mutate', 0)
    res = turn.get_info()
    assert res['target'] == 2
    assert res['paralyze'] == 0
    assert res['do'] == 'mutate'
    state = {'chief': None, 'mutants': set(), 'dead': set(), 'paralyzed': None}
    res = turn.act(game.players, state)
    assert state['mutants'] == set()
    assert state['paralyzed'] == 0
    assert res['failed_to_mutate'] == "c"
    assert res['mutated'] is None
    
    turn = MutantTurn(1, 'mutate', 0)
    turn.act(game.players, state)
    assert state['mutants'] == {1}
    
def test_doctor_turn():
    game = Game(PLAYER_LIST, ROLE_LIST, GENOME_LIST)
    turn = DoctorTurn([0, 1], ['heal', 'heal'])
    res = turn.get_info()
    assert res['targets'] == [0, 1]
    assert res['dos'] == ['heal', 'heal']
    
    state = {'chief': None, 'mutants': {0, 1, 2}, 'dead': set(), 'paralyzed': None}
    res = turn.act(game.players, state)
    assert state['mutants'] == {1, 2}
    assert res['failed_to_heal'] == [1]
    assert res['healed'] == [0]
