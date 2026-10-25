#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


POSITIONS = ("King", "Queen", "Jack", "First Square")
POSITION_POINTS = (4, 3, 2, 1)
KEY_TO_INDEX = {"4": 0, "3": 1, "2": 2, "1": 3}


class FourSquareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("4-Square Tournament")
        self.root.geometry("1000x700")
        self.root.minsize(780, 560)
        self.players = []
        self.scores = {}
        self.events = []
        self.history = []
        self.round_number = 0
        self.game_active = False
        self.status = tk.StringVar()
        self.root.bind_all("<Key>", self.on_key)
        self.show_setup()

    def clear_window(self):
        for child in self.root.winfo_children():
            child.destroy()

    def show_setup(self):
        self.game_active = False
        self.clear_window()
        frame = ttk.Frame(self.root, padding=24)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="4-Square Tournament", font=("", 20, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text="Add players in starting order: King, Queen, Jack, First Square, then the queue. "
            "At least four players are required.",
            wraplength=650,
        ).pack(anchor="w", pady=(8, 18))

        entry_row = ttk.Frame(frame)
        entry_row.pack(fill="x")
        self.name_entry = ttk.Entry(entry_row)
        self.name_entry.pack(side="left", fill="x", expand=True)
        self.name_entry.bind("<Return>", lambda _event: self.add_player())
        ttk.Button(entry_row, text="Add player", command=self.add_player).pack(side="left", padx=(8, 0))

        self.setup_list = tk.Listbox(frame, height=14, activestyle="dotbox")
        self.setup_list.pack(fill="both", expand=True, pady=12)
        controls = ttk.Frame(frame)
        controls.pack(fill="x")
        self.player_count = ttk.Label(controls, text="0 players")
        self.player_count.pack(side="left")
        self.start_button = ttk.Button(
            controls, text="Start tournament", command=self.start_tournament, state="disabled"
        )
        self.start_button.pack(side="right")
        self.name_entry.focus_set()

    def add_player(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        existing_names = [self.setup_list.get(i) for i in range(self.setup_list.size())]
        if name in existing_names:
            messagebox.showerror("Duplicate player", "Each player must have a unique name.", parent=self.root)
            return
        self.setup_list.insert("end", name)
        self.name_entry.delete(0, "end")
        count = self.setup_list.size()
        self.player_count.configure(text=f"{count} player{'s' if count != 1 else ''}")
        if count >= 4:
            self.start_button.configure(state="normal")

    def start_tournament(self):
        if self.setup_list.size() < 4:
            return
        self.players = list(self.setup_list.get(0, "end"))
        self.scores = {name: 0 for name in self.players}
        self.events = [f"Tournament started: {', '.join(self.players)}."]
        self.history = []
        self.round_number = 0
        self.build_game()

    def build_game(self):
        self.game_active = True
        self.clear_window()
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        left = ttk.Frame(self.root, padding=14)
        left.grid(row=0, column=0, sticky="nsew")
        for column in range(2):
            left.columnconfigure(column, weight=1)
        for row in (1, 2):
            left.rowconfigure(row, weight=1)
        ttk.Label(left, text="Current board", font=("", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        self.square_cards = []
        for index, position in enumerate(POSITIONS):
            card = ttk.LabelFrame(left, text=f"[{4 - index}] {position}", padding=12)
            card.grid(row=1 + index // 2, column=index % 2, sticky="nsew", padx=5, pady=5)
            name_label = ttk.Label(card, font=("", 14, "bold"))
            name_label.pack(anchor="w", pady=(0, 4))
            score_label = ttk.Label(card)
            score_label.pack(anchor="w", pady=(0, 10))
            eliminate_button = ttk.Button(
                card, text="Eliminate from square", command=lambda i=index: self.open_round_dialog(i)
            )
            eliminate_button.pack(anchor="w")
            self.square_cards.append((name_label, score_label, eliminate_button))

        right = ttk.Frame(self.root, padding=(4, 14, 14, 14))
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(3, weight=1)
        right.columnconfigure(0, weight=1)
        ttk.Label(right, text="Queue", font=("", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.queue_list = tk.Listbox(right, height=6, activestyle="none")
        self.queue_list.grid(row=1, column=0, sticky="ew", pady=(4, 12))

        ttk.Label(right, text="Tournament log", font=("", 14, "bold")).grid(
            row=2, column=0, sticky="w"
        )
        log_frame = ttk.Frame(right)
        log_frame.grid(row=3, column=0, sticky="nsew", pady=(4, 8))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_text = tk.Text(log_frame, height=12, wrap="word", state="disabled")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll.grid(row=0, column=1, sticky="ns")

        actions = ttk.Frame(right)
        actions.grid(row=4, column=0, sticky="ew")
        for col in range(2):
            actions.columnconfigure(col, weight=1)
        ttk.Button(actions, text="Edit game state", command=self.open_state_editor).grid(
            row=0, column=0, sticky="ew", padx=(0, 4), pady=3
        )
        ttk.Button(actions, text="Undo last change (U)", command=self.undo_last).grid(
            row=0, column=1, sticky="ew", padx=(4, 0), pady=3
        )
        ttk.Button(actions, text="Standings (S)", command=self.show_standings).grid(
            row=1, column=0, sticky="ew", padx=(0, 4), pady=3
        )
        ttk.Button(actions, text="Save log...", command=self.save_log).grid(
            row=1, column=1, sticky="ew", padx=(4, 0), pady=3
        )
        ttk.Button(actions, text="Reset (R)", command=self.confirm_reset).grid(
            row=2, column=0, sticky="ew", padx=(0, 4), pady=3
        )
        ttk.Button(actions, text="Exit (X)", command=self.root.destroy).grid(
            row=2, column=1, sticky="ew", padx=(4, 0), pady=3
        )
        self.status_label = ttk.Label(right, textvariable=self.status, wraplength=370)
        self.status_label.grid(row=5, column=0, sticky="w", pady=(8, 0))
        self.refresh_game()

    def refresh_game(self):
        for index, (name_label, score_label, _button) in enumerate(self.square_cards):
            if index < len(self.players):
                name = self.players[index]
                name_label.configure(text=name)
                score_label.configure(text=f"{self.scores[name]} points")
            else:
                name_label.configure(text="Empty")
                score_label.configure(text="")
        self.queue_list.delete(0, "end")
        for index, name in enumerate(self.players[4:], start=5):
            self.queue_list.insert("end", f"[{index}] {name} - {self.scores[name]} points")
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", "\n".join(self.events))
        self.log_text.configure(state="disabled")
        self.log_text.see("end")
        self.status.set(
            f"Round {self.round_number + 1} | {len(self.players)} players | "
            "Keys 4/3/2/1 eliminate from a square; U undoes."
        )

    def on_key(self, event):
        if not self.game_active or self.root.grab_current() is not None:
            return
        if event.keysym in KEY_TO_INDEX:
            self.open_round_dialog(KEY_TO_INDEX[event.keysym])
        elif event.keysym.lower() == "s":
            self.show_standings()
        elif event.keysym.lower() == "r":
            self.confirm_reset()
        elif event.keysym.lower() == "u":
            self.undo_last()
        elif event.keysym.lower() == "x":
            self.root.destroy()
        else:
            return
        return "break"

    def open_round_dialog(self, eliminated_index):
        if eliminated_index >= len(self.players):
            return
        eliminated = self.players[eliminated_index]
        dialog = tk.Toplevel(self.root)
        dialog.title("Record round")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        frame = ttk.Frame(dialog, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(
            frame, text=f"{eliminated} is eliminated. Record any bonus or penalty:"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        elim_choices = [name for name in self.players if name != eliminated]
        penalty_choices = self.players[:4]
        elim_choice = tk.StringVar(value="")
        penalty_choice = tk.StringVar(value="")
        ttk.Label(frame, text="Elimination point (+1)").grid(row=1, column=0, sticky="w", pady=4)
        elim_menu = ttk.Combobox(
            frame, textvariable=elim_choice, values=("", *elim_choices), state="readonly"
        )
        elim_menu.grid(
            row=1, column=1, sticky="ew", pady=4
        )
        ttk.Label(frame, text="Penalty (-1)").grid(row=2, column=0, sticky="w", pady=4)
        penalty_menu = ttk.Combobox(
            frame, textvariable=penalty_choice, values=("", *penalty_choices), state="readonly"
        )
        penalty_menu.grid(
            row=2, column=1, sticky="ew", pady=4
        )
        ttk.Label(
            frame,
            text="Use 4/3/2/1 for squares and 5+ for queue players; Tab switches fields, Enter records.",
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))
        buttons = ttk.Frame(frame)
        buttons.grid(row=4, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="right")
        ttk.Button(
            buttons,
            text="Record round",
            command=lambda: self.apply_round(
                eliminated_index,
                elim_choice.get() or None,
                penalty_choice.get() or None,
                dialog,
            ),
        ).pack(side="right", padx=(0, 8))
        frame.columnconfigure(1, weight=1)

        def record_round(_event=None):
            self.apply_round(
                eliminated_index,
                elim_choice.get() or None,
                penalty_choice.get() or None,
                dialog,
            )
            return "break"

        def select_by_number(event, choices, choice_var):
            key = event.keysym
            if key.startswith("KP_") and len(key) == 4:
                key = key[-1]
            if key not in KEY_TO_INDEX and not key.isdigit():
                return
            player_index = KEY_TO_INDEX.get(key)
            if player_index is None:
                player_index = int(key) - 1
            if 0 <= player_index < len(self.players):
                name = self.players[player_index]
                if name in choices:
                    choice_var.set(name)
            return "break"

        elim_menu.bind(
            "<KeyPress>",
            lambda event: select_by_number(event, elim_choices, elim_choice),
        )
        penalty_menu.bind(
            "<KeyPress>",
            lambda event: select_by_number(event, penalty_choices, penalty_choice),
        )
        dialog.bind("<Return>", record_round)
        dialog.bind("<Escape>", lambda _event: dialog.destroy())
        dialog.grab_set()
        elim_menu.focus_set()

    def save_snapshot(self):
        self.history.append((self.players.copy(), self.scores.copy(), self.round_number, len(self.events)))

    def apply_round(self, eliminated_index, elim_player, penalty_player, dialog):
        if eliminated_index >= len(self.players):
            dialog.destroy()
            return
        self.save_snapshot()
        eliminated = self.players[eliminated_index]
        details = [f"Round {self.round_number + 1}: {eliminated} eliminated."]
        if elim_player is not None:
            self.scores[elim_player] += 1
            details.append(f"{elim_player} +1 elimination point")
        if penalty_player is not None:
            self.scores[penalty_player] -= 1
            details.append(f"{penalty_player} -1 penalty")
        for index, points in enumerate(POSITION_POINTS):
            if index != eliminated_index:
                player = self.players[index]
                self.scores[player] += points
                details.append(f"{player} +{points} position points")
        self.players.pop(eliminated_index)
        self.players.append(eliminated)
        self.round_number += 1
        details.append(f"Board rotated; {eliminated} moves to the queue.")
        self.events.append(" ".join(details))
        dialog.destroy()
        self.refresh_game()

    def open_state_editor(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit game state")
        dialog.transient(self.root)
        dialog.geometry("430x420")
        dialog.rowconfigure(1, weight=1)
        dialog.columnconfigure(0, weight=1)
        ttk.Label(
            dialog,
            text="Change the score and move players to correct the current board order.",
            wraplength=390,
            padding=(12, 12, 12, 8),
        ).grid(row=0, column=0, sticky="w")
        content = ttk.Frame(dialog, padding=(12, 0, 12, 8))
        content.grid(row=1, column=0, sticky="nsew")
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        order_list = tk.Listbox(content, exportselection=False, activestyle="dotbox")
        order_list.grid(row=0, column=0, sticky="nsew")
        for name in self.players:
            order_list.insert("end", name)
        score_frame = ttk.Frame(content)
        score_frame.grid(row=0, column=1, sticky="ns", padx=(12, 0))
        ttk.Label(score_frame, text="Selected player's score").pack(anchor="w")
        score_value = tk.StringVar()
        score_entry = ttk.Entry(score_frame, textvariable=score_value, width=12)
        score_entry.pack(anchor="w", pady=(4, 12))
        selected_name = [None]
        working_scores = self.scores.copy()

        def show_selection(_event=None):
            selection = order_list.curselection()
            if selection:
                name = order_list.get(selection[0])
                previous_name = selected_name[0]
                if previous_name is not None and previous_name != name:
                    try:
                        working_scores[previous_name] = int(score_value.get())
                    except ValueError:
                        messagebox.showerror(
                            "Invalid score", "Enter a whole-number score.", parent=dialog
                        )
                        previous_index = list(order_list.get(0, "end")).index(previous_name)
                        order_list.selection_clear(0, "end")
                        order_list.selection_set(previous_index)
                        return
                selected_name[0] = name
                score_value.set(str(working_scores[name]))

        def move_selected(offset):
            selection = order_list.curselection()
            if not selection:
                return
            try:
                if selected_name[0] is not None:
                    working_scores[selected_name[0]] = int(score_value.get())
            except ValueError:
                messagebox.showerror("Invalid score", "Enter a whole-number score.", parent=dialog)
                return
            old_index = selection[0]
            new_index = old_index + offset
            if not 0 <= new_index < order_list.size():
                return
            name = order_list.get(old_index)
            order_list.delete(old_index)
            order_list.insert(new_index, name)
            order_list.selection_set(new_index)
            show_selection()

        order_list.bind("<<ListboxSelect>>", show_selection)
        order_list.selection_set(0)
        show_selection()
        ttk.Button(score_frame, text="Move up", command=lambda: move_selected(-1)).pack(
            anchor="w", fill="x", pady=2
        )
        ttk.Button(score_frame, text="Move down", command=lambda: move_selected(1)).pack(
            anchor="w", fill="x", pady=2
        )
        buttons = ttk.Frame(dialog, padding=(12, 0, 12, 12))
        buttons.grid(row=2, column=0, sticky="e")
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="right")

        def save_state():
            try:
                if selected_name[0] is not None:
                    working_scores[selected_name[0]] = int(score_value.get())
            except ValueError:
                messagebox.showerror("Invalid score", "Enter a whole-number score.", parent=dialog)
                return
            new_players = list(order_list.get(0, "end"))
            old_order = self.players.copy()
            old_scores = self.scores.copy()
            if new_players == old_order and working_scores == old_scores:
                dialog.destroy()
                return
            self.save_snapshot()
            self.players = new_players
            self.scores = working_scores
            changes = []
            for name in self.players:
                if self.scores[name] != old_scores[name]:
                    changes.append(f"{name} score {old_scores[name]} -> {self.scores[name]}")
            if self.players != old_order:
                changes.append("board order updated")
            self.events.append("Manual correction: " + "; ".join(changes) + ".")
            dialog.destroy()
            self.refresh_game()

        ttk.Button(buttons, text="Save changes", command=save_state).pack(side="right", padx=(0, 8))
        score_entry.bind("<Return>", lambda _event: save_state())
        dialog.grab_set()

    def undo_last(self):
        if not self.history:
            self.status.set("There are no changes to undo.")
            return
        self.players, self.scores, self.round_number, event_count = self.history.pop()
        del self.events[event_count:]
        self.refresh_game()
        self.status.set("Last round or manual correction undone.")

    def show_standings(self):
        if not self.players:
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Standings")
        dialog.transient(self.root)
        frame = ttk.Frame(dialog, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Tournament standings", font=("", 16, "bold")).pack(anchor="w", pady=(0, 8))
        standings = ttk.Treeview(frame, columns=("player", "score"), show="headings", height=12)
        standings.heading("player", text="Player")
        standings.heading("score", text="Score")
        standings.column("player", width=220)
        standings.column("score", width=80, anchor="center")
        standings.pack(fill="both", expand=True)
        sorted_scores = sorted(self.scores.items(), key=lambda item: item[1], reverse=True)
        for rank, (name, score) in enumerate(sorted_scores, start=1):
            standings.insert("", "end", values=(f"{rank}. {name}", score))
        ttk.Button(frame, text="Close", command=dialog.destroy).pack(anchor="e", pady=(10, 0))
        dialog.bind("<Escape>", lambda _event: dialog.destroy())
        dialog.grab_set()

    def save_log(self):
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save tournament log",
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as log_file:
                log_file.write("\n".join(self.events) + "\n")
        except OSError as error:
            messagebox.showerror("Could not save log", str(error), parent=self.root)
            return
        self.status.set(f"Log saved to {path}")

    def confirm_reset(self):
        if messagebox.askyesno("Reset tournament", "Reset the tournament and start over?", parent=self.root):
            self.players = []
            self.scores = {}
            self.events = []
            self.history = []
            self.round_number = 0
            self.show_setup()


if __name__ == "__main__":
    root = tk.Tk()
    app = FourSquareApp(root)
    root.mainloop()
