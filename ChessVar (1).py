# Author: Elisha Roche
# GitHub username: ellecpu
# Date: March 14th, 2025
# Description: This code defines a ChessVar class that simulates a chess game, including handling board setup, move validation, piece capturing, and updating the game state based on the moves made, with support for both players and different piece types.
class ChessVar:
    def __init__(self):
        """
        Initialize the board, set the first turn to white, and set the initial game state.
        Also, initialize captured pieces and place the initial pieces on the board.
        """
        self.board = [[' ' for _ in range(8)] for _ in range(8)]  # 8x8 board
        self.turn = 'WHITE'  # White moves first
        self.game_state = 'UNFINISHED'  # Initial game state
        self.captured_pieces = {'WHITE': [], 'BLACK': []}  # Track captured pieces
        self.place_init_pieces()  # Place pieces in their initial positions

    def place_init_pieces(self):
        """
        Place the initial pieces on the board in standard chess positions.
        Top rows (0,1) for Black (lowercase), bottom rows (6,7) for White (uppercase).
        """
        # Black pieces
        self.board[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']  # Row 0
        self.board[1] = ['p'] * 8                                  # Row 1 (pawns)

        # White pieces
        self.board[7] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']  # Row 7
        self.board[6] = ['P'] * 8                                  # Row 6 (pawns)

    def get_game_state(self):
        """
        Return the current game state: 'UNFINISHED', 'WHITE_WON', or 'BLACK_WON'.
        """
        return self.game_state

    def get_board(self):
        """
        Return the current state of the board as a nested list (8x8).
        """
        return self.board

    def make_move(self, from_square, to_square):
        """
        Validate and execute a move in algebraic notation, e.g., 'e2' -> 'e4'.
        Returns True if the move is valid and executed, False otherwise.
        """
        # 1) If the game is over, no further moves are allowed
        if self.game_state != 'UNFINISHED':
            return False

        # 2) Check valid square notation
        if not self._is_valid_square(from_square) or not self._is_valid_square(to_square):
            return False

        # 3) Convert algebraic notation to board indices
        from_row, from_col = self._algebraic_to_indices(from_square)
        to_row, to_col = self._algebraic_to_indices(to_square)

        # 4) Indices must be on the board
        if not (0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8):
            return False

        moving_piece = self.board[from_row][from_col]
        target_piece = self.board[to_row][to_col]

        # 5) There must be an actual piece at from_square
        if moving_piece == ' ':
            return False

        # 6) Check that it’s the correct player’s piece (uppercase = White, lowercase = Black)
        if (self.turn == 'WHITE' and not moving_piece.isupper()) or \
           (self.turn == 'BLACK' and not moving_piece.islower()):
            return False

        # 7) Validate move rules for this piece type
        if not self._is_valid_move(from_row, from_col, to_row, to_col):
            return False

        # 8) Execute capture if there is an enemy piece on the target square
        #    (In your original code, the logic to allow capturing was reversed.)
        if target_piece != ' ':
            # If target is the same color, it's invalid; if enemy color, capture is valid.
            if (self.turn == 'WHITE' and target_piece.isupper()) or \
               (self.turn == 'BLACK' and target_piece.islower()):
                return False  # Cannot capture your own piece
            # Otherwise, it's an enemy piece; capture it.
            self.captured_pieces[self.turn].append(target_piece)

        # 9) Move the piece on the board
        self.board[to_row][to_col] = moving_piece
        self.board[from_row][from_col] = ' '

        # 10) Update game state (check if a king reached the center or was captured)
        self._update_game_state(to_row, to_col, target_piece)

        # 11) Switch turn
        self.turn = 'BLACK' if self.turn == 'WHITE' else 'WHITE'
        return True

    def _is_valid_square(self, square):
        """
        Check if the input is a valid algebraic notation like 'e4'.
        """
        return len(square) == 2 and square[0].lower() in 'abcdefgh' and square[1] in '12345678'

    def _algebraic_to_indices(self, square):
        """
        Convert algebraic notation (e.g., 'e4') to (row, col) indices on self.board.
        'a1' -> (7,0), 'h8' -> (0,7), etc.
        """
        col = ord(square[0].lower()) - ord('a')  # 'a' -> 0, 'b' -> 1, ...
        row = 8 - int(square[1])                # '1' -> 7, '2' -> 6, ...
        return (row, col)

    def _is_valid_move(self, from_row, from_col, to_row, to_col):
        """
        Validate the move based on the piece type and movement rules.
        """
        piece = self.board[from_row][from_col].lower()

        # Dispatch to piece-specific validation
        if piece == 'p':
            return self._is_valid_pawn_move(from_row, from_col, to_row, to_col)
        elif piece == 'r':
            return self._is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece == 'n':
            return self._is_valid_knight_move(from_row, from_col, to_row, to_col)
        elif piece == 'b':
            return self._is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece == 'q':
            return self._is_valid_queen_move(from_row, from_col, to_row, to_col)
        elif piece == 'k':
            return self._is_valid_king_move(from_row, from_col, to_row, to_col)
        return False

    def _is_valid_pawn_move(self, from_row, from_col, to_row, to_col):
        """
        Validate a pawn's move. Pawns can move:
          - One square forward if empty.
          - Two squares forward from their initial row if both squares are empty.
          - One square diagonally forward to capture an enemy piece.
        White pawns move upward (row decreases), Black pawns move downward (row increases).
        """
        direction = -1 if self.turn == 'WHITE' else 1
        start_row = 6 if self.turn == 'WHITE' else 1

        # Forward move (one or two squares) with no capture
        if from_col == to_col:
            # One step forward
            if to_row == from_row + direction and self.board[to_row][to_col] == ' ':
                return True
            # Two steps forward from the starting position
            if from_row == start_row and to_row == from_row + 2 * direction:
                mid_row = from_row + direction
                if self.board[mid_row][from_col] == ' ' and self.board[to_row][to_col] == ' ':
                    return True
            return False

        # Diagonal capture (exactly one column to the left or right)
        if abs(from_col - to_col) == 1 and to_row == from_row + direction:
            target_piece = self.board[to_row][to_col]
            # Must be an enemy piece there to capture
            if target_piece != ' ':
                # White capturing black or black capturing white
                if (self.turn == 'WHITE' and target_piece.islower()) or \
                   (self.turn == 'BLACK' and target_piece.isupper()):
                    return True
            return False

        return False

    def _is_valid_rook_move(self, from_row, from_col, to_row, to_col):
        """
        Validate rook movement: horizontal or vertical with a clear path.
        """
        if from_row != to_row and from_col != to_col:
            return False  # Rooks move in straight lines only
        return self._is_path_clear(from_row, from_col, to_row, to_col)

    def _is_valid_knight_move(self, from_row, from_col, to_row, to_col):
        """
        Validate knight movement: 'L' shape (2 squares in one direction, 1 in the other).
        Knights can jump over pieces, so no path check needed.
        """
        dx = abs(to_col - from_col)
        dy = abs(to_row - from_row)
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

    def _is_valid_bishop_move(self, from_row, from_col, to_row, to_col):
        """
        Validate bishop movement: diagonal only with a clear path.
        """
        if abs(from_row - to_row) != abs(from_col - to_col):
            return False
        return self._is_path_clear(from_row, from_col, to_row, to_col)

    def _is_valid_queen_move(self, from_row, from_col, to_row, to_col):
        """
        Validate queen movement: rook-like or bishop-like.
        """
        # Combine rook + bishop logic
        if self._is_valid_rook_move(from_row, from_col, to_row, to_col):
            return True
        if self._is_valid_bishop_move(from_row, from_col, to_row, to_col):
            return True
        return False

    def _is_valid_king_move(self, from_row, from_col, to_row, to_col):
        """
        Validate king movement: 1 square in any direction (no castling in this variant).
        """
        dx = abs(to_col - from_col)
        dy = abs(to_row - from_row)
        return (dx <= 1 and dy <= 1)

    def _is_path_clear(self, from_row, from_col, to_row, to_col):
        """
        For rooks, bishops, and queens, ensure no pieces lie between the start and end squares.
        """
        # Determine step for row and column
        dr = 0 if to_row == from_row else (1 if to_row > from_row else -1)
        dc = 0 if to_col == from_col else (1 if to_col > from_col else -1)

        r = from_row + dr
        c = from_col + dc
        while (r, c) != (to_row, to_col):
            if self.board[r][c] != ' ':
                return False
            r += dr
            c += dc
        return True

    def _update_game_state(self, to_row, to_col, target_piece):
        """
        Update the game state based on the move just made:
          - If a king moves to one of the center squares (d4, e4, d5, e5), that side wins.
          - If the move captured the opponent's king, that side wins.
        """
        # Center squares in row-col notation: d4->(4,3), e4->(4,4), d5->(3,3), e5->(3,4)
        center_squares = {(3, 3), (3, 4), (4, 3), (4, 4)}
        piece_just_moved = self.board[to_row][to_col]

        # 1) Check if a king landed on a center square
        if (to_row, to_col) in center_squares and piece_just_moved.lower() == 'k':
            if self.turn == 'WHITE':
                self.game_state = 'WHITE_WON'
            else:
                self.game_state = 'BLACK_WON'
            return

        # 2) Check if we captured the opponent's king
        if target_piece.lower() == 'k':
            if self.turn == 'WHITE':
                self.game_state = 'WHITE_WON'
            else:
                self.game_state = 'BLACK_WON'

    def print_board(self):
        """
        Print the board in a simple text-based format (optional helper for debugging).
        """
        for row in self.board:
            print(' '.join(row))