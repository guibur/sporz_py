from ..enum_api import Turn, Role, Genome
from colorama import init, Fore
init()

class CLIView():
    def __init__(self, controller):
        self.controller = controller
        self.speech_color = Fore.CYAN
        self.disabled_choice_color = Fore.BLUE
        
    def print_speech(self, text):
        print(self.speech_color + text + Fore.RESET)
        
    def ask_player_names(self):
        print("Entrer les noms des joueurs (terminer par une ligne vide):")
        players = []
        name = ''
        while True:
            name = input('{} -> '.format(len(players) + 1))
            if name != '':
                players.append(name)
            else:
                break
        self.controller.set_game(players)
        
    def suggest_roles_genes(self, player_names, roles, genomes):
        for player_name, role, genome in zip(player_names, roles, genomes):
            print('{} -> {} / {}'.format(player_name, role, genome))
        input("L'attribution convient-elle ? [Y]")
        self.controller.set_roles_and_genomes_then_start_game(roles, genomes)
        
    def choose_player(self, players, excluded):
        for index, name in enumerate(players):
            if index in excluded:
                print(self.disabled_choice_color + '{} -> {}'.format(index + 1, name) + Fore.RESET)
            else:
                print('{} -> {}'.format(index + 1, name))
        return (int(input("Choisir un joueur parmi la liste de joueurs ci-dessus (les joueurs en bleu sont exclus) : ")) - 1)
        
    def show_next_turn_actions(self, next_turn):
        print('--------------STARTING {}-----------------'.format(next_turn['type'].name))
        action_function = {
            Turn.D_CHIEF_ELECTION: self.action_chief_election,
        }
        action = action_function[next_turn['type']](next_turn)
        self.controller.act(action)
        
    def show_turn_results(self, turn_results):
        print('--------------SHOWING {}-----------------'.format(next_turn['type'].name))
        show_fuction = {
            Turn.D_CHIEF_ELECTION: self.dont_do_anything,
        }
        show_fuction[next_turn['type']]()
        
        
    def action_chief_election(self, next_turn):
        self.print_speech("Procéder à l'élection du chef (il devra départager en cas d'égalité entre deux joueurs pendant un vote):")
        chief = self.choose_player(next_turn['choices'], next_turn['excluded'])
        return {'chief': chief}
        
    def dont_do_anything(self, turn_results):
        pass
