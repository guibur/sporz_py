import typing as tp

from ..enum_api import Turn, Role, Genome
from ..message_api import PlayerState
from colorama import init, Fore
from ..controller import Controller


init()


class CLIView:
    def __init__(self, controller: Controller) -> None:
        self.controller: Controller = controller
        self.speech_color: Fore = Fore.CYAN
        self.disabled_choice_color: Fore = Fore.BLUE

    def print_speech(self, text: str) -> None:
        print(self.speech_color + text + Fore.RESET)

    def ask_player_names(self) -> None:
        print("Entrer les noms des joueurs (terminer par une ligne vide):")
        players: tp.List[str] = []
        name = ""
        while True:
            name = input("{} -> ".format(len(players) + 1))
            if name != "":
                players.append(name)
            else:
                break
        self.controller.set_game(players)

    def suggest_roles_genes(self, player_names: tp.List[str], roles: tp.List[Role], genomes: tp.List[Genome]) -> None:
        for player_name, role, genome in zip(player_names, roles, genomes):
            print("{} -> {} / {}".format(player_name, role, genome))
        input("L'attribution convient-elle ? [Y]")
        self.controller.set_roles_and_genomes_then_start_game(roles, genomes)

    def input(self, text: str) -> str:
        res = input(text + "\nEntrez 's' pour voir l'état courant du jeu")
        if res == "s":
            self.controller.get_full_game_state()
            return self.input(text)
        return res

    def choose_player(
        self, players: tp.List[str], excluded: tp.Sequence[str], none_possible: bool = False
    ) -> tp.Optional[int]:
        for index, name in enumerate(players):
            if index in excluded:
                print(self.disabled_choice_color + "{} -> {}".format(index + 1, name) + Fore.RESET)
            else:
                print("{} -> {}".format(index + 1, name))
        while True:
            try:
                res = (
                    int(
                        input(
                            "Choisir un joueur parmi la liste de joueurs ci-dessus (les joueurs en bleu sont exclus{}) : ".format(
                                ", 0 pour ne sélectionner aucun joueur" if none_possible else ""
                            )
                        )
                    )
                    - 1
                )
            except ValueError:
                print("Entrez un numéro correct")
            else:
                if res < 0 or res > len(players) - 1:
                    if res == -1 and none_possible:
                        return None
                    print("Merci d'entrer un nombre entre 1 et {}".format(len(players)))
                elif res in excluded:
                    print("{} n'est pas un choix valable.".format(res + 1))
                else:
                    return res
        return -1

    def make_choice(self, choices: tp.List[str], abbrev: tp.List[str]) -> str:
        while True:
            res = input(
                "Voulez vous {} ? ".format(
                    " ou ".join(["{} ({})".format(choice, ab) for choice, ab in zip(choices, abbrev)])
                )
            )
            if res in abbrev:
                return choices[abbrev.index(res)]
            else:
                print("Choisir parmi {}".format(" ou ".join(abbrev)))
        return ""

    def show_full_state(self, full_state: tp.List[PlayerState]) -> None:
        role_names = {
            Role.ASTRONAUT: "astronaute",
            Role.BASE_MUTANT: "mutant de base",
            Role.DOCTOR: "médecin",
            Role.COMPUTER_SCIENTIST: "informaticien",
            Role.PSYCHOLOGIST: "psychologue",
            Role.GENETICIST: "généticien",
            Role.SPY: "espion",
            Role.HACKER: "hacker",
            Role.FANATIC: "fanatique",
        }
        genome_names = {
            Genome.NORMAL: "",
            Genome.RESISTANT: "résistant",
            Genome.HOST: "hôte",
        }
        for player in full_state:
            if player.dead:
                print(Fore.RED, end="")
            elif player.mutant:
                print(Fore.GREEN, end="")
            print(
                "{:>15s} | {:.<14s}..{:.>9s} ".format(
                    player.name, role_names[player.role], genome_names[player.genome]  # type: ignore
                ),
                end="",
            )
            if player.dead:
                print("\u271D ", end="")
            if player.chief and not player.dead:
                print(Fore.YELLOW + "\u272B" + Fore.RESET, end="")
            if player.paralyzed:
                print(Fore.MAGENTA + "PARALISÉ", end="")

            print(Fore.RESET)

    def show_next_turn_actions(self, next_turn):
        print("--------------STARTING {}-----------------".format(next_turn["type"].name))
        action_function = {
            Turn.D_CHIEF_ELECTION: self.action_chief_election,
            Turn.N_MUTANTS: self.action_mutants,
            Turn.N_DOCTORS: self.action_doctors,
        }
        action = action_function[next_turn["type"]](next_turn)
        self.controller.act(action)

    def show_turn_results(self, turn_results):
        print("--------------SHOWING {}-----------------".format(turn_results["type"].name))
        show_fuction = {
            Turn.D_CHIEF_ELECTION: lambda res: print("Chef élu : {}".format(res["chief_name"])),
            Turn.N_MUTANTS: self.show_mutants,
        }
        show_fuction[turn_results["type"]](turn_results)
        self.controller.set_next_turn()

    def action_chief_election(self, next_turn):
        self.print_speech(
            "Procéder à l'élection du chef (il devra départager en cas d'égalité entre deux joueurs pendant un vote):"
        )
        chief = self.choose_player(next_turn["choices"], next_turn["excluded"])
        return {"chief": chief}

    def action_mutants(self, next_turn):
        self.print_speech("Tout l'équipage du vaisseau s'endort. Les mutants se réveillent.")
        print(" Les mutants sont: {}".format(", ".join([str(p) for p in next_turn["players"]])))
        self.print_speech("Les mutants m'indiquent quel joueur ils veulent muter ou tuer")
        main_target = self.choose_player(next_turn["choices"], next_turn["excluded"], none_possible=True)
        if main_target is not None:
            main_action = self.make_choice(["muter", "tuer"], ["m", "t"])
            main_action = "kill" if main_action == "muter" else "mutate"
        else:
            main_action = None
        self.print_speech(
            "Les mutants m'indiquent quel joueur ils veulent paralyser (il est possible de ne paralyser personne.)"
        )
        paralyze_target = self.choose_player(next_turn["choices"], next_turn["excluded"], none_possible=True)
        return {"target": main_target, "do": main_action, "paralyze": paralyze_target}

    def action_doctors(self, next_turn):
        self.print_speech("Les médecins se réveillent.")
        print("Les médecins sont: {}".format(", ".join([str(p) for p in next_turn["players"]])))
        print(next_turn)
        if any(next_turn["paralyzed"]):
            print("{} est paralysé".format(next_turn["players"][next_turn["paralyzed"].index(True)]))
        if any(next_turn["mutated"]):
            print("{} est muté".format(next_turn["players"][next_turn["mutated"].index(True)]))
        self.print_speech("Les médecins m'indiquent qui ils souhaitent guérir ou euthanasier.")
        targets = []
        actions = []
        for doctor, paralyzed, mutated in zip(next_turn["players"], next_turn["paralyzed"], next_turn["mutated"]):
            if not paralyzed and not mutated:
                t = self.choose_player(next_turn["choices"], next_turn["excluded"].union(targets), none_possible=True)
                if t is not None:
                    action = self.make_choice(["guérir", "euthanasier"], ["g", "e"])
                    actions.append("kill" if action == "euthanasier" else "heal")
                    targets.append(t)
                else:
                    break
        return {"targets": targets, "actions": actions}

    def show_mutants(self, turn_results):
        self.print_speech("Je vais maintenant passer parmi vous et taper:")
        self.print_speech("- une fois sur la tête de la personne paralysée")
        self.print_speech("- deux fois si la mutation a échoué")
        self.print_speech("- trois fois si la personne a été tuée")
        if turn_results["mutated"]:
            print("Taper une fois sur la tête de {} (muté)".format(turn_results["mutated"]))
        if turn_results["failed_to_mutate"]:
            print("Taper deux fois sur la tête de {} (échec de mutation)".format(turn_results["failed_to_mutate"]))
        if turn_results["killed"]:
            print("Taper trois fois sur la tête de {} (mort)".format(turn_results["killed"]))
        self.print_speech("Je vais maintenant taper sur la tête de la personne paralysée.")
        if turn_results["paralyzed"]:
            print("Taper sur la tête de {} (mort)".format(turn_results["paralyzed"]))

    def dont_do_anything(self, turn_results):
        pass
