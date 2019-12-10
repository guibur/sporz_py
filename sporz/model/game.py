from ..enum_api import Role, Genome, Turn
from .turn import create_turn


NIGHT_STATE_ORDER = [
    Turn.N_MUTANTS,
    Turn.N_DOCTORS,
    Turn.N_COMPUTER_SCIENTIST,
    Turn.N_PSYCHOLOGIST,
    Turn.N_GENETICIST,
    Turn.N_SPY,
    Turn.N_HACKER,
]

class Game():
    def __init__(self, player_names, player_roles=None, player_genomes=None):
        self.slots = []
        self.players = [
                {
                    'name': name,
                    'role': None,
                    'genome': None,
                }
                for name in player_names
            ]
        if player_roles and player_genomes:
            self.set_roles_and_genomes(player_roles, player_genomes)
        elif player_roles or player_genomes:
            raise TypeError('Cannot set roles without genomes')

    def set_roles_and_genomes(self, player_roles, player_genomes):
        for i, (role, genome) in enumerate(zip(player_roles, player_genomes)):
            self.players[i]['role'] = role
            self.players[i]['genome'] = genome

    def get_players(self, player_role):
        found_players = []
        for i, p in enumerate(self.players):
             if p['role'] is player_role:
                 found_players.append(i)
        return found_players
        
    def get_player_names(self):
        return [p['name'] for p in self.players]
        
    def get_last_turn(self):
        return self.slots[-1]['turns'][-1]

    def get_next_turn(self, current_turn=None):
        # Starting a game.
        if not self.slots:
            return {'type': Turn.D_CHIEF_ELECTION,
                    'choices': self.get_player_names(),
                    'excluded': self.resolve_state()['dead']}
        if len(self.slots) == 1:
            return {'type': Turn.N_MUTANTS,
                    'players': self.get_mutants()}

        # We are not starting anymore.
        if current_turn is None:
            current_turn = self.get_last_turn().type

        # Night scenario.
        if current_turn is Turn.N_MUTANTS:
            doctors = self.get_players(Role.DOCTOR)
            state = self.resolve_state()
            living_doctors = [p for p in doctors if p not in state['dead']]
            return {'type': Turn.N_DOCTORS,
                    'players': living_doctors,
                    'paralyzed': [(p not in state['mutants'] and p != state['paralyzed'])  for p in living_doctors]}

    def is_game_over(self):
        pass

    def act(self, **kwargs):
        turn_type = self.get_next_turn()['type']
        if not self.slots:
             self.slots.append({
                 'type': 'first_day',
                 'turns': [],
             })
        elif turn_type is Turn.N_MUTANTS:
            self.slots.append({
                 'type': 'night',
                 'turns': [],
             })
        elif ((turn_type is Turn.D_AUTOPSY or turn_type is Turn.D_VOTE)
              and self.slots[-1]['type'] == 'night'):
            self.slots.append({
                'type': 'day',
                'turns': [],
            })
        state_just_before = self.resolve_state()
        self.slots[-1]['turns'].append(create_turn(turn_type, self, **kwargs))
        return self.get_last_turn().act(self.players, state_just_before)

    def resolve_state(self):
        state = {
            'chief': None,
            'mutants': set(),
            'dead': set(),
            'paralyzed': None,
        }
        for i, p in enumerate(self.players):
            if p['role'] is Role.BASE_MUTANT:
                state['mutants'].add(i)
        for slot in self.slots:
            for turn in slot['turns']:
                turn.act(self.players, state)
        return state
        
    def resolve_state_current_slot(self):
        state = {'chief': None, 'mutants': set(), 'dead': set(), 'paralyzed': None}
        for turn in self.slots[-1]['turns']:
            turn.act(state)
        return state
        
    def get_mutants(self):
        return self.resolve_state()['mutants']
        
    def player_is_mutant(self, idx):
        return idx in self.get_mutants()

    def get_turn_list(self):
        pass

    def player_name(self, idx):
        return self.players[idx]['name']

    def player_is_paralyzed(self, idx):
        return idx == self.resolve_state()['paralyzed']

    def get_game_state(self, idx):
        pass
