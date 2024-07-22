import random

class Pokemon:
    def __init__(self, name, max_hp, attack, defense, speed):
        self.name = name
        self.max_hp = max_hp
        self.actual_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        #raise Exception("this software is not aproved by Nintendo")

    def is_alive(self):
        return self.actual_hp > 0

    def take_damage(self, damage):
        self.actual_hp -= damage

        if self.actual_hp < 0:
            self.actual_hp = 0

    def __str__(self):
        return f"{self.name} (HP: {self.actual_hp}/{self.max_hp}, ATK: {self.attack}, "\
        f"DEF: {self.defense}, SPE: {self.speed})"

class Move:
    def __init__(self, name, power):
        self.name = name
        self.power = power

    def calculate_damage(self, attacker, defender):
        random_factor = random.uniform(0.85, 1.0)
        damage = (((self.power * (attacker.attack / defender.defense)) / 2) + 2) * random_factor

        return max(1, int(damage))

class PokeManager:
    def __init__(self):
        self.pokemons = {}

    def add_pokemon(self, pokemon):
        self.pokemons[pokemon.name] = pokemon

    def get_pokemon(self, name):
        return self.pokemons.get(name, None)

class MoveManager:
    def __init__(self):
        self.moves = {}

    def add_move(self, move):
        self.moves[move.name] = move

    def get_move(self, name):
        return self.moves.get(name, None)

def choose_move(pokemon, move_manager):
    print(f"\033[96m{pokemon.name}\033[0m, choose your move:")

    for name, move in move_manager.moves.items():
        print(f"- {name} (Power: {move.power})")
    
    chosen_move_name = input("Enter the move name: ")
    chosen_move = move_manager.get_move(chosen_move_name)

    if chosen_move:
        return chosen_move
    else:
        print("Invalid move, try again.")
        return choose_move(pokemon, move_manager)

class CombatState:
    def __init__(self, name):
        self.name = name

    def execute(self, combat_system):
        pass

class StartCombatState(CombatState):
    def __init__(self):
        super().__init__("StartCombat")

    def execute(self, combat_system):
        print("Starting combat...")
        combat_system.initialize_combat()
        
        return DetermineTurnOrderState()

class DetermineTurnOrderState(CombatState):
    def __init__(self):
        super().__init__("DetermineTurnOrder")

    def execute(self, combat_system):
        print("Determining turn order...")
        combat_system.determine_turn_order()
        return PlayerTurnState(combat_system.turn_order[0])

class PlayerTurnState(CombatState):
    def __init__(self, current_pokemon):
        super().__init__("PlayerTurn")
        self.current_pokemon = current_pokemon

    def execute(self, combat_system):
        print(f"\033[96m{self.current_pokemon.name}'s\033[0m turn...")

        if self.current_pokemon == combat_system.player1_pokemon:
            action = choose_move(combat_system.player1_pokemon, combat_system.move_manager)
            combat_system.push_state(ExecuteActionState(action, combat_system.player1_pokemon, combat_system.player2_pokemon).execute(combat_system))
            next_pokemon = combat_system.player2_pokemon
        else:
            action = choose_move(combat_system.player2_pokemon, combat_system.move_manager)
            combat_system.push_state(ExecuteActionState(action, combat_system.player2_pokemon, combat_system.player1_pokemon).execute(combat_system))
            next_pokemon = combat_system.player1_pokemon
        
        return CheckEndCombatState(next_pokemon)

class ExecuteActionState(CombatState):
    def __init__(self, action, attacker, defender):
        super().__init__("ExecuteAction")
        self.action = action
        self.attacker = attacker
        self.defender = defender

    def execute(self, combat_system):
        print(f"Executing {self.action.name} from {self.attacker.name} to {self.defender.name}...")
        damage = self.action.calculate_damage(self.attacker, self.defender)
        self.defender.take_damage(damage)
        print(f"{self.defender.name} takes {damage} damage and is now at {self.defender.actual_hp} HP")

        return DetermineTurnOrderState()

class CheckEndCombatState(CombatState):
    def __init__(self, next_pokemon):
        super().__init__("CheckEndCombat")
        self.next_pokemon = next_pokemon

    def execute(self, combat_system):
        print("Checking end of combat...")
        if not combat_system.player1_pokemon.is_alive():
            return EndCombatState(combat_system.player2_pokemon)
        elif not combat_system.player2_pokemon.is_alive():
            return EndCombatState(combat_system.player1_pokemon)

        return PlayerTurnState(self.next_pokemon)

class EndCombatState(CombatState):
    def __init__(self, winner):
        super().__init__("EndCombat")
        self.winner = winner

    def execute(self, combat_system):
        print(f"Combat ended. The winner is {self.winner.name}.")

        exit(1)

class CombatSystem:
    def __init__(self, player1_pokemon, player2_pokemon, move_manager):
        self.state_stack = []
        self.player1_pokemon = player1_pokemon
        self.player2_pokemon = player2_pokemon
        self.move_manager = move_manager
        self.turn_order = []

    def push_state(self, state):
        self.state_stack.append(state)

    def pop_state(self):
        if self.state_stack:
            return self.state_stack.pop()
        else:
            return None

    def current_state(self):
        if self.state_stack:
            return self.state_stack[-1]
        else:
            return None

    def run(self):
        while self.state_stack:
            current_state = self.current_state()
            next_state = current_state.execute(self)

            if next_state:
                self.push_state(next_state)
            else:
                self.pop_state()

    def initialize_combat(self):
        print(f"{self.player1_pokemon} vs {self.player2_pokemon}")

    def determine_turn_order(self):
        self.turn_order = sorted([self.player1_pokemon, self.player2_pokemon], key=lambda p: p.speed, reverse=True)

pokemon_manager = PokeManager()
move_manager = MoveManager()

pokemon_manager.add_pokemon(Pokemon("Pikachu", 100, 55, 40, 90))
pokemon_manager.add_pokemon(Pokemon("Mewtwo", 100, 110, 90, 130))

move_manager.add_move(Move("Tackle", 40))
move_manager.add_move(Move("Bite", 75))

player1_pokemon = pokemon_manager.get_pokemon("Pikachu")
player2_pokemon = pokemon_manager.get_pokemon("Mewtwo")

combat_system = CombatSystem(player1_pokemon, player2_pokemon, move_manager)
combat_system.push_state(StartCombatState())
combat_system.run()