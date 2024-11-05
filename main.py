import pygame
import sys
from engine import GameState

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 500  # Window size
DIMENSION = 5  # Dimensions of a simplified 5x6 chessboard
SQ_SIZE = HEIGHT // DIMENSION
FPS = 15
IMAGES = {}


# Load images for pieces
def load_images():
    pieces = ["w_P", "w_R", "w_N", "w_B", "w_Q", "w_K", "b_P", "b_R", "b_N", "b_B", "b_Q", "b_K"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE)
        )


# Draw the board with colors and pieces
def draw_board(screen, game_state):
    colors = [pygame.Color("light gray"), pygame.Color("dark green")]
    for r in range(DIMENSION):
        for c in range(DIMENSION + 1):  # +1 for 6x5 board
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            piece = game_state.board[r][c]
            if piece != "--":  # Draw the piece image
                screen.blit(IMAGES[piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# Highlight valid moves for selected piece
def highlight_squares(screen, game_state, valid_moves, selected_square):
    if selected_square != ():
        r, c = selected_square
        if game_state.board[r][c][0] == ('w' if game_state.whiteToMove else 'b'):
            # Highlight selected square
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(pygame.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # Highlight valid moves
            s.fill(pygame.Color('yellow'))
            for move in valid_moves:
                if move[0] == r and move[1] == c:
                    screen.blit(s, (move[3] * SQ_SIZE, move[2] * SQ_SIZE))


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
