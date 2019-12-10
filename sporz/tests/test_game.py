import pytest

from sporz.model import Game
from sporz.model.turn import *
from sporz.enum_api import Role, Genome, Turn

PLAYER_LIST = ['a', 'b', 'c']
ROLE_LIST = [Role.BASE_MUTANT, Role.DOCTOR, Role.ASTRONAUT]
GENOME_LIST = [Genome.NORMAL, Genome.HOST, Genome.RESISTANT]

def test_constructor():
    game = Game(PLAYER_LIST)
    assert len(game.players) == 3
    assert game.players[1]['name'] == 'b'
    assert game.player_name(0) == 'a'

    game2 = Game(PLAYER_LIST, ROLE_LIST, GENOME_LIST)
    state = game2.resolve_state()
    assert state['mutants'] == {0}

def test_role_attribution():
    game = Game(PLAYER_LIST)
    with pytest.raises(TypeError):
        game.set_roles_and_genomes(ROLE_LIST)
    with pytest.raises(TypeError):
        game.set_roles_and_genomes(player_genomes=GENOME_LIST)
    game.set_roles_and_genomes(ROLE_LIST, GENOME_LIST)
    assert game.players[1]['role'] is Role.DOCTOR
    assert game.players[2]['role'] is Role.ASTRONAUT
    assert game.get_players(Role.BASE_MUTANT) == [0]
    assert game.get_players(Role.PSYCHOLOGIST) == []
    assert game.players[0]['genome'] is Genome.NORMAL
    assert game.players[2]['genome'] is Genome.RESISTANT

def test_first_chief_election():
    game = Game(PLAYER_LIST, ROLE_LIST, GENOME_LIST)
    assert game.get_next_turn()['type'] == Turn.D_CHIEF_ELECTION
    assert game.get_next_turn()['type'] == Turn.D_CHIEF_ELECTION
    assert game.get_next_turn()['type'] == Turn.D_CHIEF_ELECTION
    game.act(chief=1)
    assert len(game.slots) == 1
    assert len(game.slots[0]['turns']) == 1
    assert isinstance(game.slots[0]['turns'][0], ChiefElectionTurn)
    assert game.resolve_state()['chief'] == 1
    
def test_state_sequence():
    game = Game(PLAYER_LIST, ROLE_LIST, GENOME_LIST)
    game.act(chief=1)
    assert game.get_next_turn()['type'] is Turn.N_MUTANTS
    res = game.act(target=2, do='mutate', paralyze=0)
    assert len(game.slots) == 2
    assert game.slots[-1]['type'] == 'night'
    assert len(game.slots[-1]['turns']) == 1
    
    assert game.get_next_turn()['type'] is Turn.N_DOCTORS
    assert game.get_next_turn()['players'] == [1]
    
    res = game.act(targets=[0], dos=['heal'])
    assert len(game.slots) == 2
    assert len(game.slots[-1]['turns']) == 2
