'''
Main driver file. Responsible for handling user's input and displaying the current GameState object
'''

import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512  # the size of the window
DIMENSION = 8  # 8x8 dimensions of a chess board
SQ_SIZE = WIDTH // DIMENSION  # square size
MAX_FPS = 15
IMAGES = {}


def load_images():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bp', 'wp', 'wR', 'wN', 'wB', 'wQ', 'wK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('Chess_projects_pics/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))


'''
Handle user's input and updating the graphics
'''


def main():
    p.init() # initialize all imported pygame modules
    screen = p.display.set_mode((WIDTH, HEIGHT)) # initialize the window
    clock = p.time.Clock() # create an object to help track time. We will use that for the animation (for  FPS)
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_all_valid_moves()
    move_made = False  # flag variable for when the move is made
    animate = False  # flag variable for when we should animate
    load_images()
    running = True
    sq_selected = () # keep track of the last click
    player_clicks = [] # keep track of player's clicks ((start_row, start_col), (end_row, end_col))
    game_over = False

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos() # (x, y) mouse position
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, col): # user clicked the same square twice
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2: # if len == 2, you got a start and an end position
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = ()
                                player_clicks = []

                        if not move_made:
                            player_clicks = [sq_selected]

            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when "Z" is pressed
                    gs.undo_move()
                    move_made = True  # to get all valid moves again and go trough all the process again
                    animate = False

        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_all_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, sq_selected)

        if gs.check_mate:
            game_over = True
            if gs.white_to_move:
                draw_text(screen, 'Black wins by checkmate')
            else:
                draw_text(screen, 'White wins by checkmate')
        elif gs.stale_mate:
            game_over = True
            draw_text(screen, 'Stalemate')
        clock.tick(MAX_FPS)
        p.display.flip() # update the display


def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'): # if its white/black to move and you clicked white/black figure
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(120)  # 0 = transparent, 255 = opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE)) # draw one image onto another(highlight it)
            # highlight moves
            s.fill(p.Color('green'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    global colors
    colors = [p.Color('white'), p.Color('gray')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)] # if it's 0 it's white otherwise is gray
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':  # not empty square
                screen.blit(IMAGES[piece], p.Rect(int(c * SQ_SIZE), int(r * SQ_SIZE), SQ_SIZE, SQ_SIZE))


def draw_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, True, p.Color('Gray'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(int(WIDTH / 2 - text_object.get_width() / 2),
                                                     int(HEIGHT / 2 - text_object.get_height() / 2))
    screen.blit(text_object, text_location)
    text_object = font.render(text, True, p.Color('Black'))
    screen.blit(text_object, text_location.move(2, 2))


def animate_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 10
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count +1):
        r, c = (move.start_row + dR * frame / frame_count, move.start_col + dC * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], end_square)

        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(int(c * SQ_SIZE), int(r * SQ_SIZE), SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()

