import chess
import tkinter as tk
from tkinter import messagebox, ttk
from board_evaluator import evaluate
import threading

# Unicode chess pieces
PIECES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Engine - Minimax with Alpha-Beta Pruning")
        self.root.resizable(False, False)
        
        self.board = chess.Board()
        self.selected_square = None
        self.player_color = chess.WHITE
        self.ai_thinking = False
        self.depth = 4
        self.two_player_mode = False
        
        # Configure styles - Blue and White theme
        self.light_square = "#FFFFFF"  # White
        self.dark_square = "#4A90E2"   # Blue
        self.selected_color = "#FFD700"  # Gold
        self.highlight_color = "#CCE5FF"  # Light blue (transparent effect)
        
        self.setup_ui()
        self.draw_board()
        
    def setup_ui(self):
        # Top frame for controls
        control_frame = tk.Frame(self.root, bg="#2C3E50", padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Title
        title = tk.Label(control_frame, text="Chess Engine", 
                        font=("Arial", 20, "bold"), fg="white", bg="#2C3E50")
        title.pack(side=tk.LEFT, padx=10)
        
        # Game mode toggle
        mode_frame = tk.Frame(control_frame, bg="#2C3E50")
        mode_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(mode_frame, text="Mode:", fg="white", bg="#2C3E50").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="AI")
        mode_ai = tk.Radiobutton(mode_frame, text="vs AI", variable=self.mode_var, value="AI",
                                bg="#2C3E50", fg="white", selectcolor="#34495E",
                                command=self.toggle_mode, font=("Arial", 9))
        mode_ai.pack(side=tk.LEFT, padx=2)
        mode_2p = tk.Radiobutton(mode_frame, text="2 Players", variable=self.mode_var, value="2P",
                                bg="#2C3E50", fg="white", selectcolor="#34495E",
                                command=self.toggle_mode, font=("Arial", 9))
        mode_2p.pack(side=tk.LEFT, padx=2)
        
        # Depth control
        self.depth_frame = tk.Frame(control_frame, bg="#2C3E50")
        self.depth_frame.pack(side=tk.LEFT, padx=20)
        
        self.depth_label = tk.Label(self.depth_frame, text="AI Depth:", fg="white", bg="#2C3E50")
        self.depth_label.pack(side=tk.LEFT)
        self.depth_var = tk.StringVar(value="4")
        self.depth_spin = ttk.Spinbox(self.depth_frame, from_=1, to=6, textvariable=self.depth_var, 
                                width=5, command=self.update_depth)
        self.depth_spin.pack(side=tk.LEFT, padx=5)
        
        # New game button
        new_game_btn = tk.Button(control_frame, text="New Game", 
                                command=self.new_game, bg="#3498DB", fg="white",
                                font=("Arial", 10, "bold"), padx=15, pady=5)
        new_game_btn.pack(side=tk.RIGHT, padx=5)
        
        # Flip board button
        flip_btn = tk.Button(control_frame, text="Flip Board", 
                           command=self.flip_board, bg="#9B59B6", fg="white",
                           font=("Arial", 10, "bold"), padx=15, pady=5)
        flip_btn.pack(side=tk.RIGHT, padx=5)
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#34495E")
        main_frame.pack(padx=10, pady=10)
        
        # Board frame
        board_frame = tk.Frame(main_frame, bg="#34495E")
        board_frame.pack(side=tk.LEFT, padx=10)
        
        # Canvas for the chess board
        self.canvas = tk.Canvas(board_frame, width=560, height=560, bg="#34495E", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_square_click)
        
        # Side panel for info
        info_frame = tk.Frame(main_frame, bg="#2C3E50", width=250)
        info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        info_frame.pack_propagate(False)
        
        # Game info
        tk.Label(info_frame, text="Game Info", font=("Arial", 14, "bold"), 
                fg="white", bg="#2C3E50").pack(pady=10)
        
        self.turn_label = tk.Label(info_frame, text="Turn: White", 
                                  font=("Arial", 12), fg="white", bg="#2C3E50")
        self.turn_label.pack(pady=5)
        
        self.status_label = tk.Label(info_frame, text="Your turn!", 
                                    font=("Arial", 10), fg="#2ECC71", bg="#2C3E50")
        self.status_label.pack(pady=5)
        
        # Move history
        tk.Label(info_frame, text="Move History", font=("Arial", 12, "bold"), 
                fg="white", bg="#2C3E50").pack(pady=(20, 5))
        
        history_container = tk.Frame(info_frame, bg="#2C3E50")
        history_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(history_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.move_history = tk.Listbox(history_container, yscrollcommand=scrollbar.set,
                                      bg="#34495E", fg="white", font=("Courier", 10),
                                      selectmode=tk.SINGLE, height=20)
        self.move_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.move_history.yview)
        
        # Evaluation bar
        eval_frame = tk.Frame(info_frame, bg="#2C3E50")
        eval_frame.pack(pady=10)
        
        tk.Label(eval_frame, text="Evaluation:", fg="white", bg="#2C3E50").pack()
        self.eval_label = tk.Label(eval_frame, text="0.0", font=("Arial", 16, "bold"),
                                  fg="#2ECC71", bg="#2C3E50")
        self.eval_label.pack()
        
    def update_depth(self):
        try:
            self.depth = int(self.depth_var.get())
        except ValueError:
            self.depth = 4
    
    def toggle_mode(self):
        mode = self.mode_var.get()
        if mode == "2P":
            self.two_player_mode = True
            # Hide depth controls
            self.depth_label.config(fg="#2C3E50")
            self.depth_spin.config(state="disabled")
        else:
            self.two_player_mode = False
            # Show depth controls
            self.depth_label.config(fg="white")
            self.depth_spin.config(state="normal")
            
    def draw_board(self):
        self.canvas.delete("all")
        square_size = 70
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = col * square_size
                y1 = row * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                
                square_idx = (7 - row) * 8 + col if self.player_color == chess.WHITE else row * 8 + (7 - col)
                
                # Determine square color
                is_light = (row + col) % 2 == 0
                color = self.light_square if is_light else self.dark_square
                
                # Highlight selected square
                if self.selected_square == square_idx:
                    color = self.selected_color
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                
                # Draw circular dots for legal moves
                if self.selected_square is not None:
                    move = chess.Move(self.selected_square, square_idx)
                    if move in self.board.legal_moves or chess.Move(self.selected_square, square_idx, promotion=chess.QUEEN) in self.board.legal_moves:
                        center_x = x1 + square_size // 2
                        center_y = y1 + square_size // 2
                        dot_radius = square_size // 6
                        self.canvas.create_oval(center_x - dot_radius, center_y - dot_radius,
                                                center_x + dot_radius, center_y + dot_radius,
                                                fill="#555555", outline="")
                
                # Draw coordinates
                if col == 0:
                    rank = str(8 - row) if self.player_color == chess.WHITE else str(row + 1)
                    self.canvas.create_text(x1 + 5, y1 + 5, text=rank, font=("Arial", 10), 
                                          fill="#666", anchor="nw")
                if row == 7:
                    file = chr(97 + col) if self.player_color == chess.WHITE else chr(104 - col)
                    self.canvas.create_text(x2 - 5, y2 - 5, text=file, font=("Arial", 10), 
                                          fill="#666", anchor="se")
                
                # Draw pieces - plain Unicode characters, no styling
                piece = self.board.piece_at(square_idx)
                if piece:
                    piece_symbol = piece.symbol()
                    piece_char = PIECES.get(piece_symbol, piece_symbol)
                    center_x = x1 + square_size // 2
                    center_y = y1 + square_size // 2
                    self.canvas.create_text(center_x, center_y, text=piece_char, font=("Arial", 48))
        
        self.update_status()
        
    def on_square_click(self, event):
        if self.ai_thinking or self.board.is_game_over():
            return
        
        col = event.x // 70
        row = event.y // 70
        
        if self.player_color == chess.WHITE:
            square = (7 - row) * 8 + col
        else:
            square = row * 8 + (7 - col)
        
        if square < 0 or square > 63:
            return
        
        # If no square is selected, select this square if it has a piece of the current player's color
        if self.selected_square is None:
            piece = self.board.piece_at(square)
            # In 2-player mode, allow both colors to move based on whose turn it is
            # In AI mode, only allow the player's color
            if self.two_player_mode:
                if piece and piece.color == self.board.turn:
                    self.selected_square = square
                    self.draw_board()
            else:
                if piece and piece.color == (self.board.turn if not self.ai_thinking else not self.board.turn):
                    self.selected_square = square
                    self.draw_board()
        else:
            # Try to make a move
            move = chess.Move(self.selected_square, square)
            promotion_move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
            
            if move in self.board.legal_moves:
                self.make_move(move)
            elif promotion_move in self.board.legal_moves:
                self.make_move(promotion_move)
            else:
                # Deselect or select new piece
                piece = self.board.piece_at(square)
                if piece and piece.color == self.board.turn:
                    self.selected_square = square
                else:
                    self.selected_square = None
                self.draw_board()
    
    def make_move(self, move):
        # Get SAN notation before pushing the move
        san_notation = self.board.san(move)
        self.board.push(move)
        self.selected_square = None
        self.add_move_to_history(san_notation)
        self.draw_board()
        
        if self.board.is_game_over():
            self.show_game_over()
        elif not self.two_player_mode:
            # AI's turn (only if not in 2-player mode)
            self.ai_thinking = True
            self.status_label.config(text="AI is thinking...", fg="#E74C3C")
            self.root.update()
            
            # Run AI in separate thread to keep UI responsive
            threading.Thread(target=self.ai_move, daemon=True).start()
    
    def ai_move(self):
        ai_color = not self.player_color
        # Create a proper copy of the board for AI calculation
        board_copy = self.board.copy()
        best_move = self.determine_best_move(board_copy, ai_color, self.depth)
        
        if best_move:
            # Find the matching move in the actual board's legal moves
            matching_move = None
            for legal_move in self.board.legal_moves:
                if legal_move.from_square == best_move.from_square and legal_move.to_square == best_move.to_square and legal_move.promotion == best_move.promotion:
                    matching_move = legal_move
                    break
            
            if matching_move:
                self.root.after(0, lambda: self.apply_ai_move(matching_move))
            else:
                # Fallback: just use the first legal move
                first_move = next(iter(self.board.legal_moves), None)
                if first_move:
                    self.root.after(0, lambda: self.apply_ai_move(first_move))
        else:
            self.root.after(0, lambda: self.show_game_over())
    
    def apply_ai_move(self, move):
        # Get SAN notation before pushing the move
        san_notation = self.board.san(move)
        self.board.push(move)
        self.add_move_to_history(san_notation)
        self.ai_thinking = False
        self.draw_board()
        
        if self.board.is_game_over():
            self.show_game_over()
    
    def determine_best_move(self, board, is_white, depth=4):
        best_move_value = -100000 if is_white else 100000
        best_final = None
        alpha = -100000
        beta = 100000
        
        for move in board.legal_moves:
            board.push(move)
            value = self.minimax_helper(depth - 1, board, alpha, beta, not is_white)
            board.pop()
            
            if is_white:
                if value > best_move_value:
                    best_move_value = value
                    best_final = move
                alpha = max(alpha, best_move_value)
            else:
                if value < best_move_value:
                    best_move_value = value
                    best_final = move
                beta = min(beta, best_move_value)
        
        return best_final
    
    def minimax_helper(self, depth, board, alpha, beta, is_maximizing):
        if depth <= 0 or board.is_game_over():
            return evaluate(board)
        
        if is_maximizing:
            best_move = -100000
            for move in board.legal_moves:
                board.push(move)
                value = self.minimax_helper(depth - 1, board, alpha, beta, False)
                board.pop()
                best_move = max(best_move, value)
                alpha = max(alpha, best_move)
                if beta <= alpha:
                    break
            return best_move
        else:
            best_move = 100000
            for move in board.legal_moves:
                board.push(move)
                value = self.minimax_helper(depth - 1, board, alpha, beta, True)
                board.pop()
                best_move = min(best_move, value)
                beta = min(beta, best_move)
                if beta <= alpha:
                    break
            return best_move
    
    def add_move_to_history(self, san_notation):
        move_number = len(self.board.move_stack) // 2
        
        if self.board.turn == chess.BLACK:  # White just moved
            entry = f"{move_number}. {san_notation}"
        else:  # Black just moved
            entry = f"{move_number}... {san_notation}"
        
        self.move_history.insert(tk.END, entry)
        self.move_history.see(tk.END)
    
    def update_status(self):
        # Update turn
        turn_text = "White" if self.board.turn == chess.WHITE else "Black"
        self.turn_label.config(text=f"Turn: {turn_text}")
        
        # Update status
        if self.board.is_game_over():
            if self.board.is_checkmate():
                winner = "Black" if self.board.turn == chess.WHITE else "White"
                self.status_label.config(text=f"Checkmate! {winner} wins!", fg="#E74C3C")
            elif self.board.is_stalemate():
                self.status_label.config(text="Stalemate! Draw.", fg="#F39C12")
            else:
                self.status_label.config(text="Game Over - Draw", fg="#F39C12")
        elif self.board.is_check():
            self.status_label.config(text="Check!", fg="#E74C3C")
        elif self.two_player_mode:
            # Two player mode status
            current_player = "White" if self.board.turn == chess.WHITE else "Black"
            self.status_label.config(text=f"{current_player}'s turn!", fg="#2ECC71")
        elif not self.ai_thinking and self.board.turn == self.player_color:
            self.status_label.config(text="Your turn!", fg="#2ECC71")
        elif self.ai_thinking:
            self.status_label.config(text="AI is thinking...", fg="#E74C3C")
        else:
            self.status_label.config(text="Waiting...", fg="#95A5A6")
        
        # Update evaluation
        eval_value = evaluate(self.board)
        eval_display = eval_value / 100.0
        self.eval_label.config(text=f"{eval_display:+.1f}")
        if eval_display > 0:
            self.eval_label.config(fg="#2ECC71")
        elif eval_display < 0:
            self.eval_label.config(fg="#E74C3C")
        else:
            self.eval_label.config(fg="white")
    
    def show_game_over(self):
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            messagebox.showinfo("Game Over", f"Checkmate! {winner} wins!")
        elif self.board.is_stalemate():
            messagebox.showinfo("Game Over", "Stalemate! The game is a draw.")
        elif self.board.is_insufficient_material():
            messagebox.showinfo("Game Over", "Draw by insufficient material.")
        elif self.board.is_seventyfive_moves():
            messagebox.showinfo("Game Over", "Draw by 75-move rule.")
        elif self.board.is_fivefold_repetition():
            messagebox.showinfo("Game Over", "Draw by fivefold repetition.")
        else:
            messagebox.showinfo("Game Over", "The game has ended.")
    
    def new_game(self):
        if not self.two_player_mode:
            # Ask for color selection in AI mode
            choice = messagebox.askyesnocancel("New Game", 
                                              "Do you want to play as White?\n\nYes = White\nNo = Black\nCancel = Cancel")
            
            if choice is None:
                return
            
            self.player_color = chess.WHITE if choice else chess.BLACK
        else:
            # In 2-player mode, just confirm new game
            if not messagebox.askyesno("New Game", "Start a new game?"):
                return
        
        self.board = chess.Board()
        self.selected_square = None
        self.ai_thinking = False
        self.move_history.delete(0, tk.END)
        self.draw_board()
        
        # If player is black in AI mode, AI makes first move
        if not self.two_player_mode and self.player_color == chess.BLACK:
            self.ai_thinking = True
            self.status_label.config(text="AI is thinking...", fg="#E74C3C")
            self.root.update()
            threading.Thread(target=self.ai_move, daemon=True).start()
    
    def flip_board(self):
        self.player_color = not self.player_color
        self.draw_board()

def main():
    root = tk.Tk()
    app = ChessGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'+{x}+{y}')
    
    root.mainloop()

if __name__ == '__main__':
    main()
