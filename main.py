import sys
import pygame
from pygame.locals import *

import ai
import engine

pygame.init()

########## Headers  ############

# Game Setup
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 560
SQ_SIZE = 60
DIMENSION_X = 5
DIMENSION_Y = 6
FPS = 60

# BG color
BACKGROUND = pygame.Color('azure')
BOARD_COLOR_A = (240, 217, 181)  # Light color for light squares
BOARD_COLOR_B = (181, 136, 99)   # Dark color for dark squares
HOVER_COLOR = (210, 140, 80)
TEXT_COLOR = pygame.Color('darkslateblue')


# Button colors
PLAY_BUTTON_COLOR = pygame.Color('mediumseagreen')
PLAY_BUTTON_HOVER_COLOR = pygame.Color('limegreen')
RESTART_BUTTON_COLOR = pygame.Color('tomato')
RESTART_BUTTON_HOVER_COLOR = pygame.Color('firebrick')
BUTTON_TEXT_COLOR = pygame.Color('DeepSkyBlue')
TOGGLE_BUTTON_COLOR = pygame.Color('mediumpurple')

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
BUTTON_FONT = pygame.font.SysFont('Comic Sans MS', 20, bold=True)
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
    move_piece = pygame.mixer.Sound('./audios/move_Piece.mp3')
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
            WINDOW.blit(surface, (col * SQ_SIZE, row * SQ_SIZE))

            # highlight for possible moves
            surface.fill(pygame.Color('gold'))

            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    WINDOW.blit(
                        surface, (SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))

    # Highlight squares for checkmate
    if GAME_STATE.inCheck():
        king_row, king_col = (
            GAME_STATE.whiteKingLocation if GAME_STATE.whiteToMove else GAME_STATE.blackKingLocation)

        surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
        surface.fill(pygame.Color('orange'))
        WINDOW.blit(surface, (king_col * SQ_SIZE, king_row * SQ_SIZE))

    # Highlight the last moved piece
    if len(lastMove) != 0:
        startRow, startCol = lastMove[0]
        endRow, endCol = lastMove[1]

        if startRow is not None and startCol is not None:
            surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)
            surface.fill(pygame.Color('lightgreen'))
            WINDOW.blit(surface, (startCol * SQ_SIZE, startRow * SQ_SIZE))

        if endRow is not None and endCol is not None:
            surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)
            surface.fill(pygame.Color('lightgreen'))
            WINDOW.blit(surface, (endCol * SQ_SIZE, endRow * SQ_SIZE))


def drawGameState(WINDOW, GAME_STATE, validMoves, sqSelected, lastMove, restart):
    drawBoard(WINDOW)
    highlightSquare(WINDOW, GAME_STATE, validMoves, sqSelected, lastMove, restart)
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
                font = pygame.font.SysFont('Comic Sans MS', 15)
                surface = font.render(str(rank), True, TEXT_COLOR)
                WINDOW.blit(surface, (5, row * SQ_SIZE + 5))

            # Render file value in the bottom row
            if row == DIMENSION_Y - 1:
                font = pygame.font.SysFont('Comic Sans MS', 15)
                surface = font.render(file_, True, TEXT_COLOR)
                WINDOW.blit(surface, (col * SQ_SIZE + 53, (DIMENSION_Y - 1) * SQ_SIZE + 45))


def drawPieces(WINDOW, Board):
    IMAGES = loadImages()
    for row in range(DIMENSION_X):
        for col in range(DIMENSION_Y):
            piece = Board[col][row]
            if piece != '--':
                WINDOW.blit(IMAGES[piece], pygame.Rect(
                    row * SQ_SIZE, col * SQ_SIZE, SQ_SIZE, SQ_SIZE))

#
# def drawButtons(WINDOW, GAME_STATE):
#     play_button_rect = ''
#     restart_button_rect = ''
#
#     # ==> Show Text (Opponent)
#     drawTextMessage(WINDOW, "Black", [10, 392], pygame.Color('darkmagenta'))
#     drawTextMessage(WINDOW, "White", [10, 442], pygame.Color('darkmagenta'))
#     drawTextMessage(WINDOW, "MoveCount", [10, 490], pygame.Color('darkmagenta'))
#     drawTextMessage(WINDOW, MOVE_COUNT, [120, 490], pygame.Color('red'))
#     drawUIStatus(WINDOW, GAME_STATE)
#
#     # ==> Restart Button
#     icon_image = pygame.image.load('./icons/re2.png')
#     restart_button_rect = pygame.Rect(
#         RESTART_BUTTON_POS[0], RESTART_BUTTON_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT
#     )
#     pygame.draw.rect(
#         WINDOW, RESTART_BUTTON_COLOR, restart_button_rect, border_radius=BUTTON_RADIUS
#     )
#     icon_rect = icon_image.get_rect(
#         center=(restart_button_rect.centerx, restart_button_rect.centery)
#     )
#     WINDOW.blit(icon_image, icon_rect)
#
#     # ==> Play Button
#     icon_image = pygame.image.load('./icons/play2.png')
#     play_button_rect = pygame.Rect(
#         PLAY_BUTTON_POS[0], PLAY_BUTTON_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT
#     )
#     pygame.draw.rect(
#         WINDOW, PLAY_BUTTON_COLOR, play_button_rect, border_radius=BUTTON_RADIUS
#     )
#     icon_rect = icon_image.get_rect(
#         center=(play_button_rect.centerx, play_button_rect.centery)
#     )
#     WINDOW.blit(icon_image, icon_rect)
#
#     # ==> Toggle Button (Black Selection)
#     black_ai = pygame.Color('blue') if BLACK_AI else pygame.Color('gainsboro')
#     black_man = pygame.Color('blue') if BLACK_MAN else pygame.Color('gainsboro')
#     makeButton(
#         WINDOW, TOGGLE_BUTTON_2_POS, BUTTON_WIDTH, BUTTON_HEIGHT,
#         TEXT='AI', BTN_COLOR=black_ai, BTN_RADIUS=15
#     )
#     makeButton(
#         WINDOW, TOGGLE_BUTTON_1_POS, BUTTON_WIDTH + 50, BUTTON_HEIGHT,
#         TEXT='HUMAN', BTN_COLOR=black_man, BTN_RADIUS=15
#     )
#
#     # ==> Toggle Button (White Selection)
#     white_ai = pygame.Color('blue') if WHITE_AI else pygame.Color('gainsboro')
#     white_man = pygame.Color('blue') if WHITE_MAN else pygame.Color('gainsboro')
#     makeButton(
#         WINDOW, TOGGLE_BUTTON_4_POS, BUTTON_WIDTH, BUTTON_HEIGHT,
#         TEXT='AI', BTN_COLOR=white_ai, BTN_RADIUS=15
#     )
#     makeButton(
#         WINDOW, TOGGLE_BUTTON_3_POS, BUTTON_WIDTH + 50, BUTTON_HEIGHT,
#         TEXT='HUMAN', BTN_COLOR=white_man, BTN_RADIUS=15
#     )

def drawButtons(WINDOW, GAME_STATE):
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # ==> Show Text (Opponent)
    drawTextMessage(WINDOW, "Black", [10, 392], pygame.Color('darkslateblue'))
    drawTextMessage(WINDOW, "White", [10, 442], pygame.Color('darkslateblue'))
    drawTextMessage(WINDOW, "MoveCount", [10, 490], pygame.Color('darkslateblue'))
    drawTextMessage(WINDOW, MOVE_COUNT, [120, 490], pygame.Color('crimson'))
    drawUIStatus(WINDOW, GAME_STATE)

    # ==> Restart Button
    icon_image = pygame.image.load('./icons/re2.png')
    restart_button_rect = pygame.Rect(
        RESTART_BUTTON_POS[0], RESTART_BUTTON_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT
    )
    if restart_button_rect.collidepoint(mouse_x, mouse_y):
        zoomed_restart_button(WINDOW, restart_button_rect, pygame.Color('DodgerBlue'), BUTTON_RADIUS)
    else:
        zoomed_restart_button(WINDOW, restart_button_rect, RESTART_BUTTON_COLOR, BUTTON_RADIUS)
    icon_rect = icon_image.get_rect(center=(restart_button_rect.centerx, restart_button_rect.centery))
    WINDOW.blit(icon_image, icon_rect)

    # ==> Play Button
    icon_image = pygame.image.load('./icons/play2.png')
    play_button_rect = pygame.Rect(
        PLAY_BUTTON_POS[0], PLAY_BUTTON_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT
    )
    if play_button_rect.collidepoint(mouse_x, mouse_y):
        zoomed_play_button(WINDOW, play_button_rect, pygame.Color('DodgerBlue'), BUTTON_RADIUS)
    else:
        zoomed_play_button(WINDOW, play_button_rect, PLAY_BUTTON_COLOR, BUTTON_RADIUS)
    icon_rect = icon_image.get_rect(center=(play_button_rect.centerx, play_button_rect.centery))
    WINDOW.blit(icon_image, icon_rect)

    # ==> Toggle Button (Black Selection)
    black_ai = pygame.Color('midnightblue') if BLACK_AI else pygame.Color('lightgrey')
    black_man = pygame.Color('midnightblue') if BLACK_MAN else pygame.Color('lightgrey')
    makeButton(
        WINDOW, TOGGLE_BUTTON_2_POS, BUTTON_WIDTH, BUTTON_HEIGHT,
        TEXT='AI', BTN_COLOR=black_ai, BTN_RADIUS=15
    )
    makeButton(
        WINDOW, TOGGLE_BUTTON_1_POS, BUTTON_WIDTH + 50, BUTTON_HEIGHT,
        TEXT='HUMAN', BTN_COLOR=black_man, BTN_RADIUS=15
    )

    # ==> Toggle Button (White Selection)
    white_ai = pygame.Color('midnightblue') if WHITE_AI else pygame.Color('lightgrey')
    white_man = pygame.Color('midnightblue') if WHITE_MAN else pygame.Color('lightgrey')
    makeButton(
        WINDOW, TOGGLE_BUTTON_4_POS, BUTTON_WIDTH, BUTTON_HEIGHT,
        TEXT='AI', BTN_COLOR=white_ai, BTN_RADIUS=15
    )
    makeButton(
        WINDOW, TOGGLE_BUTTON_3_POS, BUTTON_WIDTH + 50, BUTTON_HEIGHT,
        TEXT='HUMAN', BTN_COLOR=white_man, BTN_RADIUS=15
    )

def zoomed_play_button(WINDOW, rect, color, radius):
    zoom_factor = 1.1  # Lightly zoom in by 10%
    new_rect = pygame.Rect(
        rect.left - (rect.width * (zoom_factor - 1) / 2),
        rect.top - (rect.height * (zoom_factor - 1) / 2),
        rect.width * zoom_factor,
        rect.height * zoom_factor
    )
    pygame.draw.rect(WINDOW, color, new_rect, border_radius=radius)

def zoomed_restart_button(WINDOW, rect, color, radius):
    zoom_factor = 1.1  # Lightly zoom in by 10%
    new_rect = pygame.Rect(
        rect.left - (rect.width * (zoom_factor - 1) / 2),
        rect.top - (rect.height * (zoom_factor - 1) / 2),
        rect.width * zoom_factor,
        rect.height * zoom_factor
    )
    pygame.draw.rect(WINDOW, color, new_rect, border_radius=radius)


def gradient_play_button(WINDOW, rect, color1, color2, radius):
    surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for i in range(rect.height):
        ratio = i / rect.height
        color = (
            int(color1.r + (color2.r - color1.r) * ratio),
            int(color1.g + (color2.g - color1.g) * ratio),
            int(color1.b + (color2.b - color1.b) * ratio)
        )
        pygame.draw.line(surface, color, (0, i), (rect.width, i))
    WINDOW.blit(surface, rect.topleft)
    pygame.draw.rect(WINDOW, color1, rect, border_radius=radius)


def gradient_restart_button(WINDOW, rect, color1, color2, radius):
    surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for i in range(rect.height):
        ratio = i / rect.height
        color = (
            int(color1.r + (color2.r - color1.r) * ratio),
            int(color1.g + (color2.g - color1.g) * ratio),
            int(color1.b + (color2.b - color1.b) * ratio)
        )
        pygame.draw.line(surface, color, (0, i), (rect.width, i))
    WINDOW.blit(surface, rect.topleft)
    pygame.draw.rect(WINDOW, color1, rect, border_radius=radius)


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
    font = pygame.font.SysFont('Comic Sans MS', 18, bold=True)
    toggle_text = font.render(TEXT, True, pygame.Color('ivory'))
    toggle_text_rect = toggle_text.get_rect(center=toggle_button_rect.center)
    WINDOW.blit(toggle_text, toggle_text_rect)

def drawTextMessage(WINDOW, TEXT, POSITION, TEXT_COLOR, TEXT_SIZE=16):
    font = pygame.font.SysFont("Comic Sans MS", TEXT_SIZE, bold=True)
    textObject = font.render(str(TEXT), 1, TEXT_COLOR)
    textLocation = pygame.Rect(POSITION[0], POSITION[1], WINDOW_WIDTH, WINDOW_HEIGHT)
    WINDOW.blit(textObject, textLocation)

def drawUIStatus(WINDOW, GAME_STATE):
    if BLACK_AI == BLACK_MAN == WHITE_AI == WHITE_MAN == False:
        turn = 'Select AI/Human for each piece'
        drawTextMessage(WINDOW, turn, [12, 525], pygame.Color('teal'), TEXT_SIZE=16)

    elif GAME_STATE.checkMate or GAME_STATE.staleMate:
        drawTextMessage(WINDOW, '', [80, 525], pygame.Color('ivory'), TEXT_SIZE=16)

    elif (BLACK_AI or BLACK_MAN) and (WHITE_AI or WHITE_MAN) and not GAME_STARTED:
        turn = 'Click Play to Start!'
        drawTextMessage(WINDOW, turn, [80, 525], pygame.Color('teal'), TEXT_SIZE=16)

    elif (BLACK_AI or BLACK_MAN) and not GAME_STARTED:
        turn = "Select AI/Human for White Pieces"
        drawTextMessage(WINDOW, turn, [12, 525], pygame.Color('teal'), TEXT_SIZE=16)

    elif (WHITE_AI or WHITE_MAN) and not GAME_STARTED:
        turn = "Select AI/Human for Black Pieces"
        drawTextMessage(WINDOW, turn, [12, 525], pygame.Color('teal'), TEXT_SIZE=16)

    elif GAME_STARTED:
        turn = "Black's Turn..." if not GAME_STATE.whiteToMove else "White's Turn..."
        drawTextMessage(WINDOW, turn, [100, 525], pygame.Color('teal'), TEXT_SIZE=16)


# Main function to run the game loop
def main():
    # Initialize pygame
    pygame.init()

    # Variables
    pieceClickCount = 0
    selectedSq = []
    animate = False
    playerOne = True  # human -> TRUE, AI -> FALSE (white)
    playerTwo = True  # -Do- (black)
    lastMove = []
    humanPlayer = True
    global MOVE_COUNT, MAX_MOVES, BLACK_AI, BLACK_MAN, WHITE_AI, WHITE_MAN, GAME_STARTED

    # Set Display
    WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('♟️ Mini Chess ♟️')
    clock = pygame.time.Clock()

    # Set GameState
    GAME_STATE = engine.GameState()
    validMoves = GAME_STATE.getValidMoves()
    moveMade = False
    gameOver = False

    # Define the board area rect
    board_rect = pygame.Rect(0, 0, DIMENSION_X * SQ_SIZE, DIMENSION_Y * SQ_SIZE)

    # Button Rects
    play_button_rect = pygame.Rect(PLAY_BUTTON_POS[0], PLAY_BUTTON_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT)
    restart_button_rect = pygame.Rect(RESTART_BUTTON_POS[0], RESTART_BUTTON_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT)
    black_human_rect = pygame.Rect(TOGGLE_BUTTON_1_POS[0], TOGGLE_BUTTON_1_POS[1], BUTTON_WIDTH + 50, BUTTON_HEIGHT)
    black_ai_rect = pygame.Rect(TOGGLE_BUTTON_2_POS[0], TOGGLE_BUTTON_2_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT)

    white_human_rect = pygame.Rect(TOGGLE_BUTTON_3_POS[0], TOGGLE_BUTTON_3_POS[1], BUTTON_WIDTH + 50, BUTTON_HEIGHT)
    white_ai_rect = pygame.Rect(TOGGLE_BUTTON_4_POS[0], TOGGLE_BUTTON_4_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT)
    # Main game loop
    running = True
    while running:

        # Draw game elements
        WINDOW.fill(BACKGROUND)
        clock.tick(FPS)
        restart = False

        if GAME_STARTED:
            humanPlayer = (GAME_STATE.whiteToMove and playerOne) or (
                    not GAME_STATE.whiteToMove and playerTwo)

        # Process events
        for event in pygame.event.get():

            # Exit the game
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # Manage piece movement
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not gameOver:
                    # Click on squares to select/move piece
                    if board_rect.collidepoint(event.pos):
                        if GAME_STARTED:
                            if humanPlayer:
                                y_coord = event.pos[0] // SQ_SIZE
                                x_coord = event.pos[1] // SQ_SIZE

                                # Reset if the same square is clicked twice
                                if selectedSq == (x_coord, y_coord):
                                    selectedSq = ()
                                    pieceClickCount = 0
                                else:
                                    selectedSq.append((x_coord, y_coord))
                                    pieceClickCount += 1

                                # Execute move when two squares are selected
                                if pieceClickCount == 2:
                                    move = engine.Move(
                                        selectedSq[0], selectedSq[1], GAME_STATE.board)
                                    # print(move.getChessNotation())

                                    # Make move if valid
                                    for i in range(len(validMoves)):
                                        if move == validMoves[i]:
                                            GAME_STATE.makeMove(move)
                                            moveMade = True
                                            animate = True
                                            lastMove = selectedSq
                                            MOVE_COUNT += 1

                                            # Play move sound effect
                                            sound_effects = loadSoundEffects()
                                            sound_effects['move'].play()

                                            pieceClickCount = 0
                                            selectedSq = []

                                    if not moveMade:
                                        pieceClickCount = 1
                                        selectedSq.remove(selectedSq[0])

                    # Opponent selection
                    if black_ai_rect.collidepoint(event.pos):
                        BLACK_AI = True
                        BLACK_MAN = False
                        playerTwo = False

                        # Reset game state
                        GAME_STATE = engine.GameState()
                        validMoves = GAME_STATE.getValidMoves()
                        selectedSq = []
                        pieceClickCount = 0
                        moveMade = False
                        animate = False
                        restart = True
                        gameOver = False
                        MOVE_COUNT = 0
                        GAME_STARTED = False

                    if black_human_rect.collidepoint(event.pos):
                        BLACK_MAN = True
                        BLACK_AI = False
                        playerTwo = True

                        # Reset game state
                        GAME_STATE = engine.GameState()
                        validMoves = GAME_STATE.getValidMoves()
                        selectedSq = []
                        pieceClickCount = 0
                        moveMade = False
                        animate = False
                        restart = True
                        gameOver = False
                        MOVE_COUNT = 0
                        GAME_STARTED = False

                    if white_ai_rect.collidepoint(event.pos):
                        WHITE_AI = True
                        WHITE_MAN = False
                        playerOne = False

                        # Reset game state
                        GAME_STATE = engine.GameState()
                        validMoves = GAME_STATE.getValidMoves()
                        selectedSq = []
                        pieceClickCount = 0
                        moveMade = False
                        animate = False
                        restart = True
                        gameOver = False
                        MOVE_COUNT = 0
                        GAME_STARTED = False

                    if white_human_rect.collidepoint(event.pos):
                        WHITE_MAN = True
                        WHITE_AI = False
                        playerOne = True

                        # Reset game state
                        GAME_STATE = engine.GameState()
                        validMoves = GAME_STATE.getValidMoves()
                        selectedSq = []
                        pieceClickCount = 0
                        moveMade = False
                        animate = False
                        restart = True
                        gameOver = False
                        MOVE_COUNT = 0
                        GAME_STARTED = False

                    if play_button_rect.collidepoint(event.pos):
                        if BLACK_AI == BLACK_MAN == WHITE_AI == WHITE_MAN == False:
                            continue
                        elif (BLACK_AI or BLACK_MAN) and (WHITE_AI or WHITE_MAN):
                            GAME_STARTED = True

                    if restart_button_rect.collidepoint(event.pos):
                        GAME_STATE = engine.GameState()
                        validMoves = GAME_STATE.getValidMoves()
                        selectedSq = []
                        pieceClickCount = 0
                        moveMade = False
                        animate = False
                        restart = True
                        gameOver = False
                        humanPlayer = True
                        BLACK_AI = BLACK_MAN = WHITE_AI = WHITE_MAN = GAME_STARTED = False
                        MOVE_COUNT = 0

                # Manage undo moves
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:  # Undo on 'z' key press
                        # Ensure at least two moves exist to undo
                        if len(GAME_STATE.moveLog) >= 2:
                            # Undo the last two moves (one AI and one human)
                            move = GAME_STATE.undoMove(2)
                            moveMade = True
                            animate = False
                            sound_effects = loadSoundEffects()
                            sound_effects['undo'].play()
                            lastMove = [(move.startRow, move.startCol),
                                        (move.endRow, move.endCol)]
                        else:
                            print("Insufficient moves to undo.")

        # AI move execution
        if GAME_STARTED:
            if not humanPlayer:
                if not gameOver:
                    aiMove = ai.findBestMove(
                        GAME_STATE, validMoves)  # Optimal move choice

                    if aiMove is None:
                        aiMove = validMoves[0]
                        print("GAME OVER")

                    GAME_STATE.makeMove(aiMove)
                    moveMade = True
                    animate = True
                    MOVE_COUNT += 1

                    # Play piece movement sound
                    sound_effects = loadSoundEffects()
                    sound_effects['move'].play()

                    # Record last move
                    lastMove = [(aiMove.startRow, aiMove.startCol),
                                (aiMove.endRow, aiMove.endCol)]

        # Refresh valid moves
        if moveMade:
            if animate:
                animateMove(GAME_STATE.moveLog[-1],
                            WINDOW, GAME_STATE.board, clock)
            validMoves = GAME_STATE.getValidMoves()
            moveMade = False
            animate = False

        # Render current game state
        drawGameState(WINDOW, GAME_STATE, validMoves,
                      selectedSq, lastMove, restart)

        # game over handling section
        if GAME_STATE.checkMate:
            gameOver = True
            if GAME_STATE.whiteToMove:
                drawGameOverText(WINDOW, 'Black wins by Checkmate', 'DarkRed')
            else:
                drawGameOverText(WINDOW, 'White wins by Checkmate', 'DarkGreen')

        if GAME_STATE.staleMate:
            gameOver = True
            drawGameOverText(WINDOW, 'Stalemate', 'Red')

            # Refresh window display
        pygame.display.update()


if __name__ == '__main__':
    main()

