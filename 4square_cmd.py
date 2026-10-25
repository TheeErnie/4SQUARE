#!/usr/bin/env python3
import os

class FourSquareTourney:
    def __init__(self):
        self.players = [] 
        self.scores = {}

    def clear_screen(self):
        # Clears the terminal for a clean UI on Fedora/Linux
        os.system('clear')

    def setup(self):
        self.clear_screen()
        print("=== 4-SQUARE TOURNAMENT SETUP ===")
        print("Enter player names in their starting order (King first, then Queen, Jack, First, and Queue).")
        print("Press [Enter] on a blank line when you are finished adding players.\n")
        
        while True:
            name = input(f"Player {len(self.players) + 1}: ").strip()
            if not name:
                if len(self.players) >= 4:
                    break
                else:
                    print("You need at least 4 players to play!")
                    continue
            
            if name in self.players:
                print("Name already exists. Add a last initial to make it unique.")
                continue
                
            self.players.append(name)
            self.scores[name] = 0

    def display_state(self):
        self.clear_screen()
        print("=== CURRENT BOARD & SCORES ===")
        positions = ['[4] King', '[3] Queen', '[2] Jack', '[1] First Square']
        
        for i in range(4):
            p = self.players[i]
            print(f"{positions[i]:<18}: {p} ({self.scores[p]} pts)")
        
        print("\n--- QUEUE ---")
        if len(self.players) > 4:
            for i in range(4, len(self.players)):
                p = self.players[i]
                # Display 5, 6, 7... for the queue so it doesn't conflict with squares
                print(f"[{i+1}] {p} ({self.scores[p]} pts)")
        else:
            print("Queue is empty.")
        
        print("\n=== ACTIONS ===")
        print(" 4, 3, 2, 1 : Eliminate player in that square (Triggers round scoring)")
        print(" S          : Show final standings (Sorted by score)")
        print(" R          : Reset Tournament")
        print(" X          : Exit Application")

    def run(self):
        self.setup()
        
        while True:
            self.display_state()
            choice = input("\nEnter Action: ").strip().upper()
            
            if choice in ['4', '3', '2', '1']:
                self.process_round(choice)
            elif choice == 'S':
                self.show_standings()
            elif choice == 'R':
                if input("Are you sure you want to reset everything? (y/n): ").strip().lower() == 'y':
                    self.players = []
                    self.scores = {}
                    self.setup()
            elif choice == 'X':
                self.clear_screen()
                print("Tourney ended. Final Standings:")
                self.show_standings(pause=False)
                break

    def parse_target(self, target):
        """Helper to convert keyboard input into a player's current index in the list."""
        try:
            num = int(target)
            if num == 4: return 0  # King
            if num == 3: return 1  # Queen
            if num == 2: return 2  # Jack
            if num == 1: return 3  # First Square
            
            # Queue players start at index 4 (number 5 on the UI)
            if 5 <= num <= len(self.players):
                return num - 1
        except ValueError:
            pass
        return None

    def process_round(self, eliminated_square):
        mapping = {'4': 0, '3': 1, '2': 2, '1': 3}
        elim_idx = mapping[eliminated_square]
        elim_player = self.players[elim_idx]
        
        print(f"\n--- Round Ended: {elim_player} is out! ---")
        
        # 1. Ask for Elim Points
        ep = input("Did anyone earn an Elim Point (+1)? (Enter 4,3,2,1, Queue #, or press Enter for none): ").strip()
        if ep:
            idx = self.parse_target(ep)
            if idx is not None:
                self.scores[self.players[idx]] += 1
                print(f" -> +1 point awarded to {self.players[idx]}")
            else:
                print(" -> Invalid input, skipping elim point.")
        
        # 2. Ask for Penalties
        pen = input("Did anyone get a Penalty (-1)? (Enter 4,3,2,1, Queue #, or press Enter for none): ").strip()
        if pen:
            idx = self.parse_target(pen)
            if idx is not None:
                self.scores[self.players[idx]] -= 1
                print(f" -> -1 point penalty applied to {self.players[idx]}")
            else:
                print(" -> Invalid input, skipping penalty.")

        # 3. Apply positional points to the remaining players in the squares
        point_values = [4, 3, 2, 1] # King, Queen, Jack, First
        for i in range(4):
            if i != elim_idx:
                p = self.players[i]
                self.scores[p] += point_values[i]
        
        # 4. Rotate: Remove eliminated player and put them at the end of the queue.
        self.players.pop(elim_idx)
        self.players.append(elim_player)
        
        input("\nScores updated and squares rotated! Press [Enter] to start next round...")

    def show_standings(self, pause=True):
        self.clear_screen()
        print("=== FINAL STANDINGS ===")
        # Sort dictionary by score descending
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (name, score) in enumerate(sorted_scores, 1):
            print(f"{rank}. {name} - {score} pts")
            
        if pause:
            input("\nPress [Enter] to return to the game...")

if __name__ == "__main__":
    app = FourSquareTourney()
    app.run()