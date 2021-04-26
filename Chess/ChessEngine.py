'''
Responsible for storing all the information about the current state of a chess game.
Also responsible for determining the valid moves at the current state
'''


class GameState:
    board = [
        ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
        ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
        ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
    ]

    # "--" represents an empty space
    # first character represents the color
    # second character represents the type

    def __init__(self):

        self.board = GameState.board
        self.move_function = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                              'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.check_mate = False
        self.stale_mate = False
        self.en_passant_possible_at = ()  # coordinates for the square where its possible
        self.currents_castling_rights = CastleRights(True, True, True, True)
        self.castling_log = [CastleRights(self.currents_castling_rights.wks, self.currents_castling_rights.bks,
                                          self.currents_castling_rights.wqs, self.currents_castling_rights.bqs)]

    def make_move(self, move):

        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # add it to the move log so we can undo it later
        self.white_to_move = not self.white_to_move  # swap players

        # update king location if moved
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'
            # grab the color of the moved piece and add the 'Q' for Queen to make it wQ/bQ

        # enpassant/ en passant(IDK) move
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--'  # capturing the pawn

        # update en_passant_possible_at variable
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:  # 2 square pawn move
            self.en_passant_possible_at = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_possible_at = ()
        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # king side castle move
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]  # moves rook
                self.board[move.end_row][move.end_col + 1] = '--'
            else:  # queen side castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]  # moves rook
                self.board[move.end_row][move.end_col - 2] = '--'
            # update castling rights
        self.update_castling_rights(move)
        self.castling_log.append(CastleRights(self.currents_castling_rights.wks, self.currents_castling_rights.bks,
                                              self.currents_castling_rights.wqs, self.currents_castling_rights.bqs))

    def undo_move(self):
        if len(self.move_log) > 0:  # make sure that there is a move to undo
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move  # switch turns back
            # update King's position if needed
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

            # undo enpassant
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--'  # leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.en_passant_possible_at = (move.end_row, move.end_col)
            # undo 2 square pawn step
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible_at = ()

            # undo castling rights
            self.castling_log.pop()
            new_rights = self.castling_log[-1]
            self.currents_castling_rights = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)

            # undo the castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # kingsside
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'

                else:  # queenside
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

    def update_castling_rights(self, move):
        if move.piece_moved == 'wK':
            self.currents_castling_rights.wks = False
            self.currents_castling_rights.wqs = False
        if move.piece_moved == 'bK':
            self.currents_castling_rights.bks = False
            self.currents_castling_rights.bqs = False
        if move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.currents_castling_rights.wqs = False
                if move.start_col == 7:  # right rook
                    self.currents_castling_rights.wks = False
        if move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.currents_castling_rights.bqs = False
                if move.start_col == 7:  # right rook
                    self.currents_castling_rights.bks = False

    def get_all_valid_moves(self):
        temp_enpassant_possible = self.en_passant_possible_at
        temp_castle_rights = CastleRights(self.currents_castling_rights.wks, self.currents_castling_rights.bks,
                                          self.currents_castling_rights.wqs, self.currents_castling_rights.bqs)
        # 1. Generate all possible moves
        moves = self.get_all_possible_moves()
        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        # 2. For each move make move
        for i in range(len(moves) - 1, -1,
                       -1):  # when removing from list its better to remove backwards, otherwise bug can happen
            self.make_move(moves[i])
            # 3. Generate all opposite moves
            # 4. See if someone attacks your King
            self.white_to_move = not self.white_to_move  # when you make a move it switch turns
            if self.in_check():
                moves.remove(moves[i])  # 5. If it attack your king is invalid move
            self.white_to_move = not self.white_to_move  # undo_move also switch turns
            self.undo_move()

        if len(moves) == 0:  # checkmate or stalemate
            if self.in_check():
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.check_mate = False
            self.stale_mate = False
            # if we undo move and make other move just to be sure that check_mate and stale_mate are still False
        self.en_passant_possible_at = temp_enpassant_possible
        self.currents_castling_rights = temp_castle_rights
        return moves


    '''
    Checks if the player is in check
    '''


    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])


    '''
    Checks if the enemy can attack the square r,c
    '''


    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move  # switch to opponent's turn
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move  # switch turn back
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:  # square is under attack
                return True
        return False


    '''
    All moves without considering checks
    '''


    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)): # num of rows (8)
            for c in range(len(self.board[r])): # num of cols in the row (8)
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_function[piece](r, c, moves) # calls the appropriate move function based on piece type
        return moves


    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r - 1][c] == '--':  # 1 square pawn advice
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':  # 2 square pawn advice
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # captures left
                if self.board[r - 1][c - 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.en_passant_possible_at:

                    moves.append(Move((r, c), (r - 1, c - 1), self.board, is_enpassant_move=True))
            if c + 1 <= 7:  # captures right
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.en_passant_possible_at:

                    moves.append(Move((r, c), (r - 1, c + 1), self.board, is_enpassant_move=True))
        # black perspective
        else:
            if self.board[r + 1][c] == '--':
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == '--':
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # captures
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.en_passant_possible_at:

                    moves.append(Move((r, c), (r + 1, c - 1), self.board, is_enpassant_move=True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.en_passant_possible_at:

                    moves.append(Move((r, c), (r + 1, c + 1), self.board, is_enpassant_move=True))


    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left,down,right
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: # on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--': # empty piece is valid move
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color: # enemy piece is valid move
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else: # ally piece is invalid
                        break
                else: # off board is invalid
                    break


    def get_knight_moves(self, r, c, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.white_to_move else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # empty or enemy piece
                    moves.append(Move((r, c), (end_row, end_col), self.board))


    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, 1), (1, -1), (1, 1), (-1, -1)) # 4 diagonals
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break


    def get_queen_moves(self, r, c, moves):
        self.get_bishop_moves(r, c, moves)
        self.get_rook_moves(r, c, moves)


    def get_king_moves(self, r, c, moves):
        king_moves = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, 1), (1, -1), (1, 1), (-1, -1))
        ally_color = 'w' if self.white_to_move else 'b'
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))


    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return  # nothing, you cant castle if you are in check
        if (self.white_to_move and self.currents_castling_rights.wks) or (
                not self.white_to_move and self.currents_castling_rights.bks):
            self.get_kings_castle_moves(r, c, moves)
        if (self.white_to_move and self.currents_castling_rights.wqs) or (
                not self.white_to_move and self.currents_castling_rights.bqs):
            self.get_queens_castle_moves(r, c, moves)


    def get_kings_castle_moves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle_move=True))


    def get_queens_castle_moves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle_move=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # maps keys to values
    # key : value
    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    ranksToRows = {v: k for k, v in ranksToRows.items()}
    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    filesToCols = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row = startSq[0]
        self.start_col = startSq[1]
        self.end_row = endSq[0]
        self.end_col = endSq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        # pawn promotion
        self.is_pawn_promotion = False
        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or (
                self.piece_moved == 'bp' and self.end_row == 7)
        # en passant
        self.is_enpassant_move = is_enpassant_move
        # castle move
        self.is_castle_move = is_castle_move

        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col  # something like HASH

    '''
    Overriding the equal method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.filesToCols[c] + self.ranksToRows[r]

