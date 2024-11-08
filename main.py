import sys
import pygame
from pygame.locals import *

import ai
import engine

pygame.init()

########## Headers  ############

# Game Setup
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 550
SQ_SIZE = 60
DIMENSION_X = 5
DIMENSION_Y = 6
FPS = 60

# BG color
BACKGROUND = pygame.Color('azure')
BOARD_COLOR_A = (239, 239, 239)
BOARD_COLOR_B = (149, 141, 148)
HOVER_COLOR = (210, 140, 80)

# Button colors
PLAY_BUTTON_COLOR = pygame.Color('green4')
PLAY_BUTTON_HOEVR_COLOR = pygame.Color('chartreuse1')
RESTART_BUTTON_COLOR = pygame.Color('orangered')
RESTART_BUTTON_HOVER_COLOR = pygame.Color('brown4')
BUTTON_TEXT_COLOR = pygame.Color('white')
TOGGLE_BUTTON_COLOR = pygame.Color('purple')

# Button dimensions and positions
BUTTON_WIDTH = 40
BUTTON_HEIGHT = 40
PLAY_BUTTON_POS = (250, 380)
RESTART_BUTTON_POS = (250, 430)
TOGGLE_BUTTON_1_POS = (150, 380)
TOGGLE_BUTTON_2_POS = (100, 380)
TOGGLE_BUTTON_3_POS = (150, 430)
TOGGLE_BUTTON_4_POS = (100, 430)

# Define button attributes
BUTTON_FONT = pygame.font.SysFont('Arial', 20, bold=True)
BUTTON_RADIUS = 8

# MOVES
MOVE_COUNT = 0
MAX_MOVES = 100
BLACK_AI = False
BLACK_MAN = False
WHITE_AI = False
WHITE_MAN = False
GAME_STARTED = False

#### All functions ##########

def loadSoundEffects():

    effects = {}
    move_piece = pygame.mixer.Sound('./audios/move_pieces.wav')
    undo_move = pygame.mixer.Sound('./audios/undo_moves.wav')
    checkmate = pygame.mixer.Sound('./audios/checkmate_sound.wav')
    effects['move'] = move_piece
    effects['undo'] = undo_move
    effects['checkmate'] = checkmate
    return effects


def loadImages():

    IMAGES = {}
    pieces = ['b_B', 'b_K', 'b_N', 'b_P', 'b_Q', 'b_R',
              'w_B', 'w_K', 'w_N', 'w_P', 'w_Q', 'w_R']

    for piece in pieces:
        image = pygame.image.load('images/' + piece + '.png')
        IMAGES[piece] = pygame.transform.scale(image, (SQ_SIZE, SQ_SIZE))

    return IMAGES


def highlightSquare(WINDOW, GAME_STATE, validMoves, sqSelected, lastMove, restart):

    # Clear all highlighting when restarting the game
    if restart:
        sqSelected.clear()
        lastMove.clear()

    if len(sqSelected) != 0:
        row, col = sqSelected[0]

        # a piece that can be moved
        if GAME_STATE.board[row][col][0] == ('w' if GAME_STATE.whiteToMove else 'b'):

            # highlight square
            surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
            # transparency value (0 - transparent, 255 - solid)
            surface.set_alpha(100)
            surface.fill(pygame.Color('lightblue'))
            WINDOW.blit(surface, (col*SQ_SIZE, row*SQ_SIZE))

            # highlight for possible moves
            surface.fill(pygame.Color('gold'))

            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    WINDOW.blit(
                        surface, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))

    # Highlight squares for checkmate
    if GAME_STATE.inCheck():
        king_row, king_col = (
            GAME_STATE.whiteKingLocation if GAME_STATE.whiteToMove else GAME_STATE.blackKingLocation)

        surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
        surface.fill(pygame.Color('orange'))
        WINDOW.blit(surface, (king_col*SQ_SIZE, king_row*SQ_SIZE))

    # Highlight the last moved piece
    if len(lastMove) != 0:
        startRow, startCol = lastMove[0]
        endRow, endCol = lastMove[1]

        if startRow is not None and startCol is not None:
            surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)
            surface.fill(pygame.Color('lightgreen'))
            WINDOW.blit(surface, (startCol*SQ_SIZE, startRow*SQ_SIZE))

        if endRow is not None and endCol is not None:
            surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)
            surface.fill(pygame.Color('lightgreen'))
            WINDOW.blit(surface, (endCol*SQ_SIZE, endRow*SQ_SIZE))

def drawGameState(WINDOW, GAME_STATE, validMoves, sqSelected, lastMove, restart):
    drawBoard(WINDOW)
    highlightSquare(WINDOW, GAME_STATE, validMoves,
                    sqSelected, lastMove, restart)
    drawPieces(WINDOW, GAME_STATE.board)
    drawButtons(WINDOW, GAME_STATE)


def drawBoard(WINDOW):

    # Get mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # ADD SHAPES
    for row in range(0, DIMENSION_Y):
        for col in range(0, DIMENSION_X):
            rectangle = pygame.Rect(
                col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)

            # Calculate rank value for the current row
            rank = 6 - row

            # Calculate file value for the current column
            file_ = chr(ord('a') + col)

            # Check if mouse is hovering
            if rectangle.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(WINDOW, HOVER_COLOR, rectangle)
            elif (row + col) % 2 == 0:
                pygame.draw.rect(WINDOW, BOARD_COLOR_A, rectangle)
            else:
                pygame.draw.rect(WINDOW, BOARD_COLOR_B, rectangle)

            # Render rank value in the left cells
            if col == 0:
                font = pygame.font.SysFont('Comic Sans', 15)
                surface = font.render(str(rank), True, 'darkblue')
                WINDOW.blit(surface, (5, row * SQ_SIZE + 5))

            # Render file value in the bottom row
            if row == DIMENSION_Y - 1:
                font = pygame.font.SysFont('Comic Sans', 15)
                surface = font.render(file_, True, 'darkblue')
                WINDOW.blit(surface, (col * SQ_SIZE + 53,
                            (DIMENSION_Y-1) * SQ_SIZE + 45))

def drawPieces(WINDOW, Board):
    IMAGES = loadImages()
    for row in range(DIMENSION_X):
        for col in range(DIMENSION_Y):
            piece = Board[col][row]
            if piece != '--':
                WINDOW.blit(IMAGES[piece], pygame.Rect(
                    row * SQ_SIZE, col * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawButtons(WINDOW, GAME_STATE):
    play_button_rect = ''
    restart_button_rect = ''

    # ==> Show Text (Opponent)
    drawTextMessage(WINDOW, "Black", [10, 392], pygame.Color('darkmagenta'))
    drawTextMessage(WINDOW, "White", [10, 442], pygame.Color('darkmagenta'))
    drawTextMessage(WINDOW, "MoveCount", [10, 490], pygame.Color('darkmagenta'))
    drawTextMessage(WINDOW, MOVE_COUNT, [120, 490], pygame.Color('red'))
    drawUIStatus(WINDOW, GAME_STATE)

    # ==> Restart Button
    icon_image = pygame.image.load('./icons/re2.png')
    restart_button_rect = pygame.Rect(
        RESTART_BUTTON_POS[0], RESTART_BUTTON_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT
    )
    pygame.draw.rect(
        WINDOW, RESTART_BUTTON_COLOR, restart_button_rect, border_radius=BUTTON_RADIUS
    )
    icon_rect = icon_image.get_rect(
        center=(restart_button_rect.centerx, restart_button_rect.centery)
    )
    WINDOW.blit(icon_image, icon_rect)

    # ==> Play Button
    icon_image = pygame.image.load('./icons/play2.png')
    play_button_rect = pygame.Rect(
        PLAY_BUTTON_POS[0], PLAY_BUTTON_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT
    )
    pygame.draw.rect(
        WINDOW, PLAY_BUTTON_COLOR, play_button_rect, border_radius=BUTTON_RADIUS
    )
    icon_rect = icon_image.get_rect(
        center=(play_button_rect.centerx, play_button_rect.centery)
    )
    WINDOW.blit(icon_image, icon_rect)

    # ==> Toggle Button (Black Selection)
    black_ai = pygame.Color('blue') if BLACK_AI else pygame.Color('gainsboro')
    black_man = pygame.Color('blue') if BLACK_MAN else pygame.Color('gainsboro')
    makeButton(
        WINDOW, TOGGLE_BUTTON_2_POS, BUTTON_WIDTH, BUTTON_HEIGHT,
        TEXT='AI', BTN_COLOR=black_ai, BTN_RADIUS=15
    )
    makeButton(
        WINDOW, TOGGLE_BUTTON_1_POS, BUTTON_WIDTH + 50, BUTTON_HEIGHT,
        TEXT='HUMAN', BTN_COLOR=black_man, BTN_RADIUS=15
    )

    # ==> Toggle Button (White Selection)
    white_ai = pygame.Color('blue') if WHITE_AI else pygame.Color('gainsboro')
    white_man = pygame.Color('blue') if WHITE_MAN else pygame.Color('gainsboro')
    makeButton(
        WINDOW, TOGGLE_BUTTON_4_POS, BUTTON_WIDTH, BUTTON_HEIGHT,
        TEXT='AI', BTN_COLOR=white_ai, BTN_RADIUS=15
    )
    makeButton(
        WINDOW, TOGGLE_BUTTON_3_POS, BUTTON_WIDTH + 50, BUTTON_HEIGHT,
        TEXT='HUMAN', BTN_COLOR=white_man, BTN_RADIUS=15
    )


def animateMove(move, WINDOW, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framePerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framePerSquare
    IMAGES = loadImages()

    for frame in range(frameCount + 1):
        row, col = (
            move.startRow + dR * frame / frameCount,
            move.startCol + dC * frame / frameCount
        )

        # Redraw the board
        drawBoard(WINDOW)
        drawPieces(WINDOW, board)

        # Erase piece from ending square
        endSquare = pygame.Rect(
            move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE
        )
        pygame.draw.rect(
            WINDOW,
            BOARD_COLOR_A if (move.endRow + move.endCol) % 2 == 0 else BOARD_COLOR_B,
            endSquare
        )

        # Draw captured piece onto the square
        if move.pieceCaptured != '--':
            WINDOW.blit(IMAGES[move.pieceCaptured], endSquare)

        # Draw moving piece
        WINDOW.blit(IMAGES[move.pieceMoved], pygame.Rect(
            col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE
        ))
        pygame.display.update()
        clock.tick(60)


def drawCheckText(screen, text):
    font = pygame.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, pygame.Color('Red'))
    textLocation = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT).move(
        WINDOW_WIDTH / 2 - textObject.get_width() / 2,
        WINDOW_HEIGHT / 2 - textObject.get_height() * 6
    )
    screen.blit(textObject, textLocation)


def drawGameOverText(screen, text, textColor):
    font = pygame.font.SysFont("Helvetica", 18, True, False)
    textObject = font.render(text, 0, pygame.Color(textColor))
    textLocation = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT).move(
        WINDOW_WIDTH / 2 - textObject.get_width() / 2,
        525
    )
    screen.blit(textObject, textLocation)

def makeButton(WINDOW, POSITION, WIDTH, HEIGHT, TEXT, BTN_COLOR, BTN_RADIUS=0):
    # Define toggle button rectangle
    toggle_button_rect = pygame.Rect(POSITION[0], POSITION[1], WIDTH, HEIGHT)
    pygame.draw.rect(WINDOW, BTN_COLOR, toggle_button_rect, border_radius=BTN_RADIUS)

    # Draw text on the button
    font = pygame.font.Font(None, 24)
    toggle_text = font.render(TEXT, True, pygame.Color('white'))
    toggle_text_rect = toggle_text.get_rect(center=toggle_button_rect.center)
    WINDOW.blit(toggle_text, toggle_text_rect)


def drawTextMessage(WINDOW, TEXT, POSITION, TEXT_COLOR):
    font = pygame.font.SysFont("Arial", 17, True, False)
    textObject = font.render(str(TEXT), 1, TEXT_COLOR)
    textLocation = pygame.Rect(POSITION[0], POSITION[1], WINDOW_WIDTH, WINDOW_HEIGHT)
    WINDOW.blit(textObject, textLocation)


def drawUIStatus(WINDOW, GAME_STATE):
    if BLACK_AI == BLACK_MAN == WHITE_AI == WHITE_MAN == False:
        turn = 'Select AI/Human for each piece'
        drawTextMessage(WINDOW, turn, [12, 525], pygame.Color('olivedrab4'))

    elif GAME_STATE.checkMate or GAME_STATE.staleMate:
        drawTextMessage(WINDOW, '', [80, 525], pygame.Color('white'))

    elif (BLACK_AI or BLACK_MAN) and (WHITE_AI or WHITE_MAN) and not GAME_STARTED:
        turn = 'Click Play to Start!'
        drawTextMessage(WINDOW, turn, [80, 525], pygame.Color('olivedrab4'))

    elif (BLACK_AI or BLACK_MAN) and not GAME_STARTED:
        turn = "Select AI/Human for White Pieces"
        drawTextMessage(WINDOW, turn, [12, 525], pygame.Color('olivedrab4'))

    elif (WHITE_AI or WHITE_MAN) and not GAME_STARTED:
        turn = "Select AI/Human for Black Pieces"
        drawTextMessage(WINDOW, turn, [12, 525], pygame.Color('olivedrab4'))

    elif GAME_STARTED:
        turn = "Black's Turn..." if not GAME_STATE.whiteToMove else "White's Turn..."
        drawTextMessage(WINDOW, turn, [100, 525], pygame.Color('olivedrab4'))


################################


# Main function to run the game loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()
    game_state = GameState()
    valid_moves = game_state.getValidMoves()
    selected_square = ()  # Keep track of the last square clicked
    load_images()  # Load images once

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()  # (x, y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if selected_square == (row, col):  # Deselect if clicked twice
                    selected_square = ()
                else:
                    selected_square = (row, col)
                    valid_moves = game_state.getValidMoves()  # Update valid moves after selection

        # Draw board and pieces
        draw_board(screen, game_state)
        highlight_squares(screen, game_state, valid_moves, selected_square)

        # Update display and tick clock
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
