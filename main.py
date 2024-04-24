import pygame
import time
import threading
import chess
import chess.svg
import chess.engine
import random
from random import choice
from traceback import format_exc
from sys import stderr
from time import strftime
from copy import deepcopy

pygame.init()

# ------------------------------------------- Constantes pour l'échiquier ------------------------------------------- #
SQUARE_SIDE = 80  # Taille d'une case de l'échiquier

# Couleurs / thèmes pour l'échiquier
RED_CHECK = (240, 150, 150)
GREY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE_LIGHT = (140, 184, 219)
BLUE_DARK = (91, 131, 159)
GRAY_LIGHT = (240, 240, 240)
GRAY_DARK = (200, 200, 200)
CHESSWEBSITE_LIGHT = (212, 202, 190)
CHESSWEBSITE_DARK = (100, 92, 89)
LICHESS_LIGHT = (240, 217, 181)
LICHESS_DARK = (181, 136, 99)
LICHESS_GRAY_LIGHT = (164, 164, 164)
LICHESS_GRAY_DARK = (136, 136, 136)

BOARD_COLORS = [(GRAY_LIGHT, GRAY_DARK),
                (BLUE_LIGHT, BLUE_DARK),
                (WHITE, BLUE_LIGHT),
                (CHESSWEBSITE_LIGHT, CHESSWEBSITE_DARK),
                (LICHESS_LIGHT, LICHESS_DARK),
                (LICHESS_GRAY_LIGHT, LICHESS_GRAY_DARK)]

BOARD_COLOR = choice(BOARD_COLORS)  # Choix d'un thème au lancement du programme

# Images des différentes pièces du jeu
BLACK_KING = pygame.image.load('images/black_king_image.png')
BLACK_QUEEN = pygame.image.load('images/black_queen_image.png')
BLACK_ROOK = pygame.image.load('images/black_rook_image.png')
BLACK_BISHOP = pygame.image.load('images/black_bishop_image.png')
BLACK_KNIGHT = pygame.image.load('images/black_knight_image.png')
BLACK_PAWN = pygame.image.load('images/black_pawn_image.png')

WHITE_KING = pygame.image.load('images/white_king_image.png')
WHITE_QUEEN = pygame.image.load('images/white_queen_image.png')
WHITE_ROOK = pygame.image.load('images/white_rook_image.png')
WHITE_BISHOP = pygame.image.load('images/white_bishop_image.png')
WHITE_KNIGHT = pygame.image.load('images/white_knight_image.png')
WHITE_PAWN = pygame.image.load('images/white_pawn_image.png')

# Ensemble représentant les pièces blanches et les pièces noires
PIECES_IMAGES = {
    chess.WHITE: {
        chess.KING: WHITE_KING,
        chess.QUEEN: WHITE_QUEEN,
        chess.ROOK: WHITE_ROOK,
        chess.BISHOP: WHITE_BISHOP,
        chess.KNIGHT: WHITE_KNIGHT,
        chess.PAWN: WHITE_PAWN,
    },
    chess.BLACK: {
        chess.KING: BLACK_KING,
        chess.QUEEN: BLACK_QUEEN,
        chess.ROOK: BLACK_ROOK,
        chess.BISHOP: BLACK_BISHOP,
        chess.KNIGHT: BLACK_KNIGHT,
        chess.PAWN: BLACK_PAWN,
    }
}

# Ensemble représentant les différentes pièces lors d'une promotion d'un pion
PIECES_PROMOTION = {
    chess.WHITE: {
        'Q': WHITE_QUEEN,
        'N': WHITE_KNIGHT,
        'R': WHITE_ROOK,
        'B': WHITE_BISHOP,
    },
    chess.BLACK: {
        'q': BLACK_QUEEN,
        'n': BLACK_KNIGHT,
        'r': BLACK_ROOK,
        'b': BLACK_BISHOP,
    }
}

# Initialisation de l'horloge et des images par secondes
CLOCK = pygame.time.Clock()
CLOCK_TICK = 60

# Récupération des dimensions de l'écran
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Création de la fenêtre graphique en plein écran
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

# Calcul de la position du coin supérieur gauche de la grille
GRID_X = (SCREEN_WIDTH - 8 * SQUARE_SIDE) // 2
GRID_Y = (SCREEN_HEIGHT - 8 * SQUARE_SIDE) // 2

# Logo et bouton exit
logo_upjv = pygame.image.load("images/logoUPJV.png")
exit_button = pygame.image.load("images/exit_button.png")
pos_exit_button = [SCREEN_WIDTH - SQUARE_SIDE, 20]

# Bouton pour changer le thème de l'échiquier
change_theme_button = pygame.image.load("images/chess_icon.png")
pos_change_theme_button = [GRID_X + 8 * SQUARE_SIDE, GRID_Y + 10]

# Bouton pour réinitialiser les scores
reset_score_button = pygame.image.load("images/reset.png")
pos_reset_score_button = [pos_change_theme_button[0], pos_change_theme_button[1] + 50]


# ---------------------------------------------- Fonctions utilitaires ---------------------------------------------- #
def is_in_board():
    # Fonction vérifiant que le clic de la souris est dans l'échiquier
    mouse_pos = pygame.mouse.get_pos()

    if GRID_X <= mouse_pos[0] <= GRID_X + 8 * SQUARE_SIDE and GRID_Y <= mouse_pos[1] <= GRID_Y + 8 * SQUARE_SIDE:
        return True
    return False


def is_on_play_button(event):
    # Fonction vérifiant que le clic de la souris est sur le bouton play
    if pos_play_button[0] <= event.pos[0] <= pos_play_button[0] + dim_play_button[0] and \
                pos_play_button[1] <= event.pos[1] <= pos_play_button[1] + dim_play_button[1]:
        return True
    return False


def swap_color(color):
    # Fonction permettant de changer la couleur. Si la couleur est blanche, elle devient noire sinon elle sera blanche
    return chess.BLACK if color == chess.WHITE else chess.WHITE


def get_scores(board_result):
    # Fonction permettant de récupérer les résultats de la partie

    result_split = board_result.split('-')
    if len(result_split) != 2:
        return None, None  # Impossible de déterminer les scores

    if result_split[0] == "1/2":
        return 0.5, 0.5

    white_score = int(result_split[0])
    black_score = int(result_split[1])
    return white_score, black_score


def show_title():
    # Fonction permettant l'affichage du titre sur la fenêtre graphique
    texte_objet = pygame.font.SysFont("Comic Sans MS", 52).render("Chess Game", True, BLACK)
    SCREEN.blit(texte_objet, ((SCREEN.get_width() / 2) - texte_objet.get_width() / 2, 40))


def show_score(color, white_score, black_score):
    # Fonction permettant l'affichage des scores sur la fenêtre graphique
    texte_white_score = pygame.font.SysFont("Comic Sans MS", 22).render("Score : " + str(white_score), True, BLACK)
    texte_black_score = pygame.font.SysFont("Comic Sans MS", 22).render("Score : " + str(black_score), True, BLACK)

    if color == chess.WHITE:
        SCREEN.blit(texte_white_score, (GRID_X, GRID_Y + 8 * SQUARE_SIDE))
        SCREEN.blit(texte_black_score, (GRID_X, GRID_Y - texte_black_score.get_height()))
    else:
        SCREEN.blit(texte_white_score, (GRID_X, GRID_Y - texte_black_score.get_height()))
        SCREEN.blit(texte_black_score, (GRID_X, GRID_Y + 8 * SQUARE_SIDE))


def loose_on_time(ongoing, white_score, black_score):
    # Fonction gérant la défaite au temps d'un des deux joueurs

    global remaining_timeW, remaining_timeB, pauseW, pauseB

    ongoing = False
    pauseW = pauseB = True

    if remaining_timeW == 0:
        black_score += 1
    else:
        white_score += 1

    return ongoing, white_score, black_score


def show_move_stack(board):
    # Fonction permettant l'affichage de l'historique des coups sur la fenêtre graphique

    move_num = 1
    x, y = GRID_X + 8 * SQUARE_SIDE + 10, GRID_Y + 1.5 * SQUARE_SIDE

    for i, move in enumerate(board.move_stack):
        if i % 2 == 0:  # Coup blanc
            text = f"{move_num}. {move.uci()[2:]}"
        else:  # Coup noir
            text += f" {move.uci()[2:]}"

            render = pygame.font.SysFont("Arial", 18).render(text, True, BLACK)
            SCREEN.blit(render, (x, y))
            x += render.get_width() + 10

            if move_num % 5 == 0:
                x = GRID_X + 8 * SQUARE_SIDE + 10
                y += render.get_height() + 10

            move_num += 1


# ----------------------------------------- Fonctions relatives à l'échiquier -----------------------------------------#
def paint_light_squares(square_color):
    """
    Fonction pour peindre les cases claires de l'échiquier
    :param square_color: Couleur associée aux cases claires de l'échiquier
    """

    # Pour chaque case dans l'ensemble des cases claires de l'échiquier
    for square in chess.SquareSet(chess.BB_LIGHT_SQUARES):
        # Récupère la colonne et la rangée de la case actuelle
        col = chess.square_file(square)
        row = 7 - chess.square_rank(square)

        # Dessine un rectangle de la couleur spécifiée pour la case actuelle
        pygame.draw.rect(SCREEN, square_color,
                         (GRID_X + SQUARE_SIDE * col, GRID_Y + SQUARE_SIDE * row, SQUARE_SIDE, SQUARE_SIDE), 0)


def paint_dark_squares(square_color):
    """
    Fonction pour peindre les cases foncées de l'échiquier
    :param square_color: Couleur associée aux cases foncées de l'échiquier
    """

    # Pour chaque case dans l'ensemble des cases foncées de l'échiquier
    for square in chess.SquareSet(chess.BB_DARK_SQUARES):
        # Récupère la colonne et la rangée de la case actuelle
        col = chess.square_file(square)
        row = 7 - chess.square_rank(square)

        # Dessine un rectangle de la couleur spécifiée pour la case actuelle
        pygame.draw.rect(SCREEN, square_color,
                         (GRID_X + SQUARE_SIDE * col, GRID_Y + SQUARE_SIDE * row, SQUARE_SIDE, SQUARE_SIDE), 0)


def get_square_rect(square, color=chess.WHITE):
    """
    Fonction pour obtenir les coordonnées du rectangle correspondant à une case donnée
    :param square: La case pour laquelle on veut obtenir les coordonnées du rectangle correspondant
    :param color: Couleur du joueur actuel
    :return: Un objet Rect représentant la position et la taille de la case sur l'écran
    """

    # Si la couleur est noire, les colonnes et les rangées doivent être inversées
    if color == chess.BLACK:
        # Récupère la colonne et la rangée de la case actuelle
        col = 7 - chess.square_file(chess.parse_square(square.lower()))
        row = chess.square_rank(chess.parse_square(square.lower()))
    else:
        col = chess.square_file(chess.parse_square(square.lower()))
        row = 7 - chess.square_rank(chess.parse_square(square.lower()))

    return pygame.Rect((GRID_X + col * SQUARE_SIDE, GRID_Y + row * SQUARE_SIDE), (SQUARE_SIDE, SQUARE_SIDE))


def print_empty_board(color=chess.WHITE):
    """
    Fonction permettant l'affichage de l'échiquier vide (sans les pièces)
    :param color: Couleur des pièces de l'utilisateur
    :return: L'échiquier vide
    """

    # Remplissage de l'écran avec la couleur blanche
    SCREEN.fill(WHITE)

    # Dessin des cases claires et foncées de l'échiquier
    paint_light_squares(BOARD_COLOR[0])
    paint_dark_squares(BOARD_COLOR[1])

    # Déclaration d'une police d'écriture de taille 30
    font = pygame.font.Font(None, 30)

    # Ajout des numéros des lignes à gauche de l'échiquier
    for row in range(8):
        if color == chess.WHITE:
            row_number = str(8 - row)
        else:
            row_number = str(row + 1)

        # Alternance de la couleur des numéros pour le contraste avec les cases
        if row % 2 == 0:
            text = font.render(row_number, True, BOARD_COLOR[1])
        else:
            text = font.render(row_number, True, BOARD_COLOR[0])

        # Affichage du texte à l'écran
        SCREEN.blit(text, (GRID_X, GRID_Y + row * SQUARE_SIDE))

    # Ajout des lettres des colonnes en bas de l'échiquier
    for col in range(8):
        if color == chess.WHITE:
            col_letter = chr(ord('a') + col)
        else:
            col_letter = chr(ord('h') - col)

        # Alternance de la couleur des lettres pour le contraste avec les cases
        if col % 2 == 0:
            text = font.render(col_letter, True, BOARD_COLOR[0])
        else:
            text = font.render(col_letter, True, BOARD_COLOR[1])

        # Affichage du texte à l'écran
        SCREEN.blit(text, (GRID_X + col * SQUARE_SIDE + SQUARE_SIDE - 12, GRID_Y + 8 * SQUARE_SIDE - 20))


def print_board(board, color=chess.WHITE, selected_square=None):
    """
    Fonction permettant l'affichage de l'échiquier (avec les pièces)
    :param board: État actuel de l'échiquier
    :param color: Couleur des pièces de l'utilisateur
    :param selected_square: Case sélectionnée par l'utilisateur
    :return: Échiquier remplit
    """

    # Affichage de l'échiquier vide
    print_empty_board(color)

    # Vérifie si le roi est en échec ou en échec et mat
    if board.is_checkmate() or board.is_check():
        # Récupère la position du roi
        if board.turn == chess.WHITE:
            king_square = board.king(chess.WHITE)
        else:
            king_square = board.king(chess.BLACK)

        # Récupère les coordonnées de la case du roi
        rect = get_square_rect(chess.square_name(king_square), color)

        #  Dessine un rectangle rouge autour de la case du roi
        pygame.draw.rect(SCREEN, RED_CHECK, rect, 0)

    # Parcours de toutes les cases de l'échiquier
    for square in chess.SQUARES:
        # Récupère la pièce sur la case
        piece = board.piece_at(square)

        # Si la case contient une pièce
        if piece is not None:
            piece_color = piece.color  # Récupère la couleur de la pièce
            piece_type = piece.piece_type  # Récupère le type de la pièce
            image = PIECES_IMAGES[piece_color][piece_type]  # Récupère l'image de la pièce

            # Dessine la pièce sur la case
            SCREEN.blit(pygame.transform.scale(image, (SQUARE_SIDE, SQUARE_SIDE)),
                        get_square_rect(chess.square_name(square).lower(), color))

        # Mise en surbrillance des coups légaux pour la pièce sélectionnée
        if selected_square is not None and selected_square == chess.square_name(square).lower():
            # Récupération des coups légaux pour la pièce sélectionnée
            legal_moves = [move.uci() for move in board.legal_moves
                           if chess.square_name(move.from_square).lower() == selected_square]

            # Parcours des coups légaux
            for move in legal_moves:
                """Dans le cas d'une promotion de pion, on ignore la dernière lettre correspondant 
                à la pièce choisie lors de la promotion"""

                # Récupération des coordonnées de la case de destination
                square_rect = get_square_rect(move[2:-1], color) if len(move) > 4 else get_square_rect(move[2:], color)

                # Récupère la position centrale de la case de destination
                center_x = square_rect.left + square_rect.width // 2
                center_y = square_rect.top + square_rect.height // 2

                if len(move) <= 4:
                    # Vérifie si le coup est une capture
                    if board.is_capture(chess.Move(chess.parse_square(move[:2]), chess.parse_square(move[2:]))):
                        # Dessine un cercle rouge autour de la case / des cases de destination
                        pygame.draw.circle(SCREEN, (255, 30, 30), (center_x, center_y), 35, 5)
                    else:
                        # Dessine un cercle gris autour de la case / des cases de destination
                        pygame.draw.circle(SCREEN, (128, 128, 128), (center_x, center_y), 10)
                else:
                    if board.is_capture(chess.Move(chess.parse_square(move[:2]), chess.parse_square(move[2:-1]))):
                        pygame.draw.circle(SCREEN, (255, 30, 30), (center_x, center_y), 35, 5)
                    else:
                        pygame.draw.circle(SCREEN, (128, 128, 128), (center_x, center_y), 10)


# Constantes pour le panel de promotion de pion
panel_x = GRID_X
panel_y = GRID_Y
panel_width = 200
panel_height = 50


def display_promotion_panel(color, file):
    """
    Fonction permettant l'affichage d'un panel pour la promotion d'un pion
    :param color: Couleur des pièces de l'utilisateur
    :param file: Colonne de la promotion de pion
    :return: Pièce choisie pour la promotion
    """

    pos_x = 0
    # Définir la position du panel selon la colonne de promotion
    if color == chess.WHITE:
        if 0 < file < 7:
            pos_x = file * SQUARE_SIDE
        elif file == 7:
            pos_x = 8 * SQUARE_SIDE - panel_width
    else:
        if 0 < file < 7:
            pos_x = (7 - file) * SQUARE_SIDE
        elif file == 0:
            pos_x = 8 * SQUARE_SIDE - panel_width

    # Dessiner le cadre du panel
    pygame.draw.rect(SCREEN, WHITE, (pos_x+panel_x, panel_y, panel_width, panel_height))

    # Initialisation du décalage entre les pièces au sein du panel
    dec = pos_x

    # Affichez les images des pièces de promotion en fonction de la couleur
    for piece, image in PIECES_PROMOTION[color].items():
        SCREEN.blit(pygame.transform.scale(image, (50, 50)), (panel_x+dec, panel_y))
        dec += 50

    # Mis à jour de l'affichage
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifiez si le clic est dans le panel de promotion
                if panel_y < event.pos[1] < (panel_y + panel_height):
                    # Détectez le clic de l'utilisateur et retournez la pièce de promotion choisie
                    column = (event.pos[0] - GRID_X - pos_x) // 50
                    try:
                        selected_promotion = list(PIECES_PROMOTION[color].keys())[column]

                    except:
                        return None

                    return selected_promotion
                else:
                    return None


def promote_pawn(board, move, color):
    """
    Fonction permettant la promotion d'un pion
    :param board: État actuel de l'échiquier
    :param move: Coup joué par l'utilisateur
    :param color: Couleur des pièces de l'utilisateur
    :return: Le pion promu si une pièce a été choisie, None sinon
    """
    # Vérifiez si le pion est sur la huitième ou la première rangée selon la couleur
    if (color == chess.BLACK and chess.square_rank(move.from_square) == 1 and chess.square_rank(move.to_square) == 0) \
            or (color == chess.WHITE and chess.square_rank(move.from_square) == 6
                and chess.square_rank(move.to_square) == 7):

        # Vérifiez si la pièce est un pion
        if board.piece_at(move.from_square) == chess.Piece(chess.PAWN, color):

            # On vérifie que le pion promeut correctement en capturant une pièce en diagonale
            if ((chess.square_file(move.from_square) != chess.square_file(move.to_square)
                 and board.piece_at(move.to_square))
                    or (chess.square_file(move.from_square) == chess.square_file(move.to_square)
                        and not board.piece_at(move.to_square))):
                move.promotion = display_promotion_panel(color, chess.square_file(move.to_square))

    return move.promotion


# --------------------------------------- Fonctions relatives à l'utilisateur --------------------------------------- #
def resign(ongoing, color, white_score, black_score):
    # Fonction permettant l'abandon de l'utilisateur

    global pauseW, pauseB

    ongoing = False
    pauseW = pauseB = True

    if color == chess.WHITE:
        black_score += 1
    else:
        white_score += 1

    return ongoing, white_score, black_score


def coord2str(mouse_pos, color):
    """
    Fonction permettant de convertir les coordonnées de la souris en case de l'échiquier
    :param mouse_pos: Coordonnées de la souris
    :param color: Couleur des pièces de l'utilisateur
    :return: Case de l'échiquier en notation échecs (ex "a1", "h8")
    """

    mouse_pos = (mouse_pos[0] - GRID_X, mouse_pos[1] - GRID_Y)

    # Récupération de la colonne et de la rangée de la case en fonction des coordonnées de la souris
    col = 7 - (mouse_pos[0] // SQUARE_SIDE) if color == chess.BLACK else (mouse_pos[0] // SQUARE_SIDE)
    row = 7 - (mouse_pos[1] // SQUARE_SIDE) if color == chess.WHITE else (mouse_pos[1] // SQUARE_SIDE)

    # Convertir la colonne en lettre (par exemple 0 --> 'a', 1 --> 'b', etc.)
    col_letter = chr(ord('a') + col)

    # Convertir la rangée en chiffre
    row_number = row + 1

    # Concaténer la lettre de la colonne et le chiffre de la rangée pour former la notation d'échecs
    return f"{col_letter}{row_number}"


def try_move(board, move, color):
    """
    Fonction permettant de jouer un coup s'il est légal
    :param board: État actuel de l'échiquier
    :param move: Coup joué par l'utilisateur
    :param color: Couleur de l'utilisateur
    :return: L'échiquier avec le coup joué si le coup est légal sinon l'échiquier sans le coup joué
    """
    try:
        # Vérifie si le coup se trouve dans l'ensemble des coups légaux de l'état actuel de l'échiquier
        if move in board.legal_moves:
            # Joue le coup
            board.push(move)

            # Mis à jour des pendules
            update_time(color)

            return board
        else:
            # Le coup n'est pas légal
            print("Mouvement invalide. Veuillez réessayer.")
            return board

    except ValueError:
        # Le format du mouvement n'est pas valide (format valide : e2e4)
        print("Format de mouvement invalide. Veuillez réessayer.")
        return board


# ----------------------------------------------- Algorithme de jeux  ----------------------------------------------- #
def make_random_AI_move(board):
    # Fonction permettant à l'IA de jouer des coups aléatoires

    legal_moves = list(board.legal_moves)  # Liste de coups légaux

    if not legal_moves:  # S'il n'y a pas de coup, c'est sûrement qu'il y a échec et mat ou égalité
        return board

    # Choix d'un coup aléatoire
    random_move = random.choice(legal_moves)

    # Création d'une copie de l'état actuel de l'échiquier
    new_board = board.copy()

    # Joue le coup aléatoire
    new_board.push(random_move)

    return new_board


PIECES_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9
}

development_coefficients = {
    chess.PAWN: 2,
    chess.KNIGHT: 0.5,
    chess.BISHOP: 0.5,
    chess.ROOK: 0.15,
    chess.QUEEN: 0.1
}


def is_pawn_supported(board, square, color):
    """
    Fonction vérifiant si le pion à une case donnée est supporté par un autre pion de même couleur
    :param board: État actuel de l'échiquier
    :param square: Case où se trouve le pion
    :param color: Couleur du pion
    :return: Vrai si le pion est supporté, faux sinon
    """

    # Récupération de la colonne et de la rangée
    file, rank = chess.square_file(square), chess.square_rank(square)
    adjacent_files = [file - 1, file + 1]  # Les colonnes adjacentes

    # Parcours des colonnes adjacentes
    for adj_file in adjacent_files:

        # Vérifiez si la colonne est valide
        if adj_file in range(8):
            adj_square = chess.square(adj_file, rank)
            adj_piece = board.piece_at(adj_square)

            # Vérifiez si le pion est supporté
            if adj_piece is not None and adj_piece.piece_type == chess.PAWN and adj_piece.color == color:
                return True

    return False


def evaluate_board(board, color):
    """
    Fonction heuristique permettant l'évaluation de l'état actuel d'un échiquier
    :param board: État actuel de l'échiquier
    :param color: Couleur du joueur actuel
    :return: Score total d'évaluation de l'état actuel de l'échiquier
    """

    # Liste des cases centrales de l'échiquier
    center_squares = [
        chess.C4, chess.D4, chess.E4, chess.C5, chess.D5, chess.E5
    ]

    total_score = 0

    # Valeurs et coefficients des pièces en fonction de la couleur du joueur actuel
    values = PIECES_VALUES
    coeff = development_coefficients

    # Récupération des cases des pièces du joueur actuel sur l'échiquier
    squares_pieces = (board.pieces(chess.PAWN, color) | board.pieces(chess.KNIGHT, color) |
                      board.pieces(chess.BISHOP, color) | board.pieces(chess.ROOK, color) |
                      board.pieces(chess.QUEEN, color) | board.pieces(chess.KING, color))

    # Parcours des cases où se trouvent les pièces du joueur actuel
    for square in squares_pieces:
        # Récupération de la pièce se trouvant à la case actuelle
        piece = board.piece_at(square)

        if piece is not None:
            # Récupération de la valeur associée à la pièce
            piece_value = values.get(piece.piece_type, 0)

            # Valorisation du développement des pièces
            if (color == chess.WHITE and square < 16) or (color == chess.BLACK and square > 47):
                if piece.piece_type == chess.KING:
                    piece_value -= 1

                    # Valorisation du roque
                    if board.has_kingside_castling_rights(color) or board.has_queenside_castling_rights(color):
                        piece_value += 1
                else:
                    piece_value += coeff[piece.piece_type] * (7 - chess.square_rank(square))

            # Pénalité pour les pions isolés
            if piece.piece_type == chess.PAWN:
                if not is_pawn_supported(board, square, color):
                    piece_value -= 1
                if is_pawn_supported(board, square, color):
                    piece_value += 1

            # Ajout de la valeur de la pièce au score total
            if piece.color == color:
                total_score += piece_value
            else:
                total_score -= piece_value

    # Contrôle du centre du plateau
    center_control = 0
    for square in center_squares:
        if board.piece_at(square) is not None and board.piece_at(square).color == color:
            center_control += 1
        else:
            center_control -= 1

    total_score += center_control

    # Défense du Roi
    king_safety = 0
    king_square = board.king(color)

    if not board.is_attacked_by(color, king_square):
        king_safety += 1
    else:
        king_safety -= 1

    total_score += king_safety

    return total_score


def minimax_alpha_beta(board, color, depth, alpha, beta, maximizing_player):
    """
    Fonction d'évaluation minimax avec élagage alpha-bêta pour déterminer le meilleur coup à jouer
    :param board: État actuel de l'échiquier
    :param color: Couleur de l'ordinateur
    :param depth: Profondeur de recherche de l'arbre de jeu
    :param alpha: Valeur alpha pour l'élagage alpha-bêta
    :param beta: Valeur bêta pour l'élagage alpha-bêta
    :param maximizing_player: Booléen indiquant si le joueur actuel est le joueur maximisant(True) ou minimisant(False)
    :return: Score d'évaluation du meilleur coup à jouer et le meilleur coup à jouer
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board, color), None

    legal_moves = list(board.legal_moves)
    if maximizing_player:
        max_value = float('-inf')
        best_move = None
        for move in legal_moves:
            board.push(move)
            value, _ = minimax_alpha_beta(board, color, depth - 1, alpha, beta, False)
            board.pop()
            if value > max_value:
                max_value = value
                best_move = move
            alpha = max(alpha, max_value)
            if alpha >= beta:
                break
        return max_value, best_move
    else:
        min_value = float('inf')
        best_move = None
        for move in legal_moves:
            board.push(move)
            value, _ = minimax_alpha_beta(board, color, depth - 1, alpha, beta, True)
            board.pop()
            if value < min_value:
                min_value = value
                best_move = move
            beta = min(beta, min_value)
            if beta <= alpha:
                break
        return min_value, best_move


def make_MINMAX_AI_move(board, depth, color):
    """
    Fonction permettant à l'ordinateur de jouer le meilleur coup selon l'algorithme minmax
    :param board: État actuel de l'échiquier
    :param depth: Profondeur de recherche de l'arbre de jeu
    :param color: Couleur de l'ordinateur
    :return: Échiquier avec le meilleur coup joué selon l'algorithme minmax
    """

    # Initialise les valeurs alpha et bêta pour l'élagage alpha-bêta
    alpha = -float('inf')
    beta = float('inf')

    # Appel de la fonction minimax_alpha_beta pour déterminer le meilleur coup à jouer et sa valeur d'évaluation
    value, best_move = minimax_alpha_beta(board, color, depth, alpha, beta, True)
    # print("Color:", color, value, best_move)

    # Création d'une copie de l'état actuel de l'échiquier
    new_board = board.copy()

    # Joue le meilleur coup déterminé par la fonction minimax_alpha_beta sur la copie de l'échiquier
    new_board.push(best_move)

    return new_board


# ------------------------------- Bouton jouer, cadence et choix couleur et difficulté ------------------------------- #
# Différentes couleurs du bouton jouer
GREEN_PLAY = (4, 191, 98)  # Pour commencer une partie
RED_RESIGN = (244, 56, 40)  # Pour abandonner
play_button_color = GREEN_PLAY

# Définir la police pour le texte du bouton play
play_font = pygame.font.SysFont("Arial", 32)

# Créer le texte du bouton play
play_button = play_font.render('PLAY', True, BLACK)

# Définir la position et les dimensions du bouton play
dim_play_button = [4 * SQUARE_SIDE, play_button.get_height()]
pos_play_button = [2 * SQUARE_SIDE, GRID_Y]
play_button_rect = pygame.Rect(pos_play_button, dim_play_button)


def show_play_button():
    # Fonction permettant l'affichage du bouton play

    global play_button_color
    pygame.draw.rect(SCREEN, play_button_color, play_button_rect, border_radius=20)
    SCREEN.blit(play_button,
                (pos_play_button[0] + (dim_play_button[0] / 2) - (play_button.get_width() / 2), pos_play_button[1]))


# Définir les dimensions des boutons de choix de couleur, de cadence de jeu et d'incrémentation
BUTTON_WIDTH = 75
BUTTON_HEIGHT = 50

# Définir les positions des boutons pour le choix de couleur
white_button_rect = None
black_button_rect = None
random_button_rect = None

COLOR_CHOICE_BUTTON_X = pos_play_button[0]
COLOR_CHOICE_BUTTON_Y = pos_play_button[1] + 0.75 * SQUARE_SIDE

POS_WHITE_CC = (COLOR_CHOICE_BUTTON_X, COLOR_CHOICE_BUTTON_Y)
POS_BLACK_CC = (COLOR_CHOICE_BUTTON_X + 2 * SQUARE_SIDE - BUTTON_WIDTH / 2, COLOR_CHOICE_BUTTON_Y)
POS_RANDOM_CC = (COLOR_CHOICE_BUTTON_X + 4 * SQUARE_SIDE - BUTTON_WIDTH, COLOR_CHOICE_BUTTON_Y)
DIM_CC_BUTTON = (BUTTON_WIDTH, BUTTON_HEIGHT)

# Charger les images pour les boutons
white_cc_image = pygame.image.load('images/white_button.png')
black_cc_image = pygame.image.load('images/black_button.png')
random_cc_image = pygame.image.load('images/random_button.jpg')


def show_color_choice():
    # Fonction permettant l'affichage des couleurs des pièces

    global white_button_rect, black_button_rect, random_button_rect
    # Dessiner les boutons sur la surface de l'écran
    white_button_rect = pygame.draw.rect(SCREEN, WHITE, pygame.Rect(POS_WHITE_CC, DIM_CC_BUTTON))
    black_button_rect = pygame.draw.rect(SCREEN, WHITE, pygame.Rect(POS_BLACK_CC, DIM_CC_BUTTON))
    random_button_rect = pygame.draw.rect(SCREEN, WHITE, pygame.Rect(POS_RANDOM_CC, DIM_CC_BUTTON))

    # Dessiner les images sur les boutons
    SCREEN.blit(white_cc_image, POS_WHITE_CC)
    SCREEN.blit(black_cc_image, POS_BLACK_CC)
    SCREEN.blit(random_cc_image, POS_RANDOM_CC)


# Définir la police pour les cadences de jeu et les incrémentations
tc_increment_font = pygame.font.SysFont("Arial", 24)

# Définir les cadences de jeu
TIME_CONTROLS = [1, 3, 5, 15]
INCREMENT_TIME = [1, 2, 5, 10]

# Définir les positions des boutons
TC_BUTTON_X = COLOR_CHOICE_BUTTON_X - 2.5
TC_BUTTON_Y = COLOR_CHOICE_BUTTON_Y + SQUARE_SIDE

INCREMENT_BUTTON_X = TC_BUTTON_X
INCREMENT_BUTTON_Y = TC_BUTTON_Y + 60


def show_time_controls():
    # Fonction permettant l'affichage des cadences de jeu

    global initial_time
    # Dessiner les boutons pour les cadences de jeu
    for i, time_control in enumerate(TIME_CONTROLS):
        button_rect = pygame.draw.rect(SCREEN, WHITE, pygame.Rect(TC_BUTTON_X + i * (BUTTON_WIDTH + 5), TC_BUTTON_Y,
                                                                  BUTTON_WIDTH, BUTTON_HEIGHT))
        pygame.draw.rect(SCREEN, GREY, button_rect, 2)
        button_text = tc_increment_font.render(str(time_control) + "min", True, BLACK)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        SCREEN.blit(button_text, button_text_rect)

        # Vérifier si le bouton est sélectionné
        if initial_time == time_control * 60:
            selected_button = button_rect

            # Remplir le bouton sélectionné
            if selected_button:
                pygame.draw.rect(SCREEN, (255, 0, 0), button_rect, 2)


def show_increment_time():
    # Fonction permettant l'affichage des incrémentations

    global increment
    # Dessiner les boutons pour les incrémentations
    for i, increment_time in enumerate(INCREMENT_TIME):
        button_rect = pygame.draw.rect(SCREEN, WHITE, pygame.Rect(INCREMENT_BUTTON_X + i * (BUTTON_WIDTH + 5),
                                                                  INCREMENT_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT))
        pygame.draw.rect(SCREEN, GREY, button_rect, 2)
        button_text = tc_increment_font.render(str(increment_time) + "sec", True, BLACK)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        SCREEN.blit(button_text, button_text_rect)

        if increment == increment_time:
            selected_button = button_rect

            # Remplir le bouton sélectionné
            if selected_button:
                pygame.draw.rect(SCREEN, (255, 0, 0), button_rect, 2)


# Définir la police pour la difficulté
difficulty_font = pygame.font.SysFont("Comic Sans MS", 24)

# Définir les cadences de jeu
TIME_CONTROLS = [1, 3, 5, 15]
INCREMENT_TIME = [1, 2, 5, 10]

# Définir les positions des boutons
DIFFICULTY_BUTTON_X = INCREMENT_BUTTON_X
DIFFICULTY_BUTTON_Y = INCREMENT_BUTTON_Y + 70

easy_rect = None
hard_rect = None


def show_difficulty_button():
    # Fonction permettant l'affichage des difficultés

    global easy_rect, hard_rect, difficulty

    difficulty_text = difficulty_font.render("Difficulty :", True, BLACK)
    SCREEN.blit(difficulty_text, (DIFFICULTY_BUTTON_X, DIFFICULTY_BUTTON_Y))

    if difficulty == "easy":
        easy_text = difficulty_font.render("Easy", True, BLACK)
        easy_rect = pygame.draw.rect(SCREEN, (255, 0, 0),
                         (DIFFICULTY_BUTTON_X + difficulty_text.get_width() + 10, DIFFICULTY_BUTTON_Y,
                          easy_text.get_width() + 20, easy_text.get_height()), 2)
        SCREEN.blit(easy_text, (DIFFICULTY_BUTTON_X + difficulty_text.get_width() + 20, DIFFICULTY_BUTTON_Y))
        hard_text = difficulty_font.render("Hard", True, BLACK)
        hard_rect = pygame.draw.rect(SCREEN, GREY,
                                     (DIFFICULTY_BUTTON_X + difficulty_text.get_width() + easy_text.get_width() + 40,
                                      DIFFICULTY_BUTTON_Y,
                                      hard_text.get_width() + 20, hard_text.get_height()), 2)
        SCREEN.blit(hard_text, (
        DIFFICULTY_BUTTON_X + difficulty_text.get_width() + easy_text.get_width() + 50, DIFFICULTY_BUTTON_Y))
    else:
        easy_text = difficulty_font.render("Easy", True, BLACK)
        easy_rect = pygame.draw.rect(SCREEN, GREY,
                         (DIFFICULTY_BUTTON_X + difficulty_text.get_width() + 10, DIFFICULTY_BUTTON_Y,
                          easy_text.get_width() + 20, easy_text.get_height()), 2)
        SCREEN.blit(easy_text, (DIFFICULTY_BUTTON_X + difficulty_text.get_width() + 20, DIFFICULTY_BUTTON_Y))

        hard_text = difficulty_font.render("Hard", True, BLACK)
        hard_rect = pygame.draw.rect(SCREEN, (255, 0, 0),
                         (DIFFICULTY_BUTTON_X + difficulty_text.get_width() + easy_text.get_width() + 40, DIFFICULTY_BUTTON_Y,
                          hard_text.get_width() + 20, hard_text.get_height()), 2)
        SCREEN.blit(hard_text, (DIFFICULTY_BUTTON_X + difficulty_text.get_width() + easy_text.get_width() + 50, DIFFICULTY_BUTTON_Y))


def is_on_easy_difficulty(event):
    if easy_rect.collidepoint(event.pos):
        return True
    return False


def is_on_hard_difficulty(event):
    if hard_rect.collidepoint(event.pos):
        return True
    return False

# ---------------------------------------------------- Pendules  ---------------------------------------------------- #
# Définir la police pour les pendules
clock_font = pygame.font.SysFont("Arial", 30)

# Définir les positions des horloges
dim_clock = [0, 0]
pos_clock_upboard = (GRID_X + 8 * SQUARE_SIDE - dim_clock[0], GRID_Y - clock_font.get_height())
pos_clock_downboard = (GRID_X + 8 * SQUARE_SIDE - dim_clock[0], GRID_Y + 8 * SQUARE_SIDE)

# Définir le temps initial pour chaque horloge (en secondes)
initial_time = 180
increment = 2  # Incrémentation

# Définir le temps restant pour chaque horloge
remaining_timeW = initial_time
remaining_timeB = initial_time

# Booléen définissant si c'est la pendule blanche ou noire qui doit décrémenter
pauseW = True
pauseB = True
has_time = True  # Booléen pour savoir si un des deux joueurs n'a plus de temps


def white_clock():
    # Fonction pour la pendule des pièces blanches
    global remaining_timeW, pauseW, has_time
    while has_time:
        time.sleep(1)
        if not pauseW:
            remaining_timeW -= 1
            if remaining_timeW <= 0:
                has_time = False


def black_clock():
    # Fonction pour la pendule des pièces noires
    global remaining_timeB, pauseB, has_time
    while has_time:
        time.sleep(1)
        if not pauseB:
            remaining_timeB -= 1
            if remaining_timeB <= 0:
                has_time = False


# Création des threads pour les pendules
thread_white_clock = threading.Thread(target=white_clock)
thread_white_clock.start()
thread_black_clock = threading.Thread(target=black_clock)
thread_black_clock.start()


def convert_seconds(secondes):
    # Fonction permettant la conversion de secondes en minutes et secondes

    global increment
    minutes = secondes // 60
    secondes_restantes = secondes % 60
    return f"{minutes}:{secondes_restantes:02d}"


def show_text(texte, couleur, surface, x, y):
    # Fonction pour afficher le texte du minuteur
    global dim_clock

    texte_objet = clock_font.render(texte, True, couleur)
    dim_clock = [texte_objet.get_width() + 40, clock_font.get_height()]
    texture_rect = texte_objet.get_rect()
    texture_rect.topleft = (x, y)
    surface.blit(texte_objet, texture_rect)


def show_clock(color):
    # Fonction permettant l'affichage des pendules

    pygame.draw.rect(SCREEN, LICHESS_GRAY_LIGHT,
                     pygame.Rect((pos_clock_upboard[0] - dim_clock[0], pos_clock_upboard[1]), dim_clock))

    pygame.draw.rect(SCREEN, LICHESS_GRAY_LIGHT,
                     pygame.Rect((pos_clock_downboard[0] - dim_clock[0], pos_clock_downboard[1]), dim_clock))

    texteW = convert_seconds(remaining_timeW)  # Conversion des secondes en minutes et secondes pour les blancs
    texteB = convert_seconds(remaining_timeB)  # Conversion des secondes en minutes et secondes pour les noirs

    # Selon la couleur de l'utilisateur, la pendule blanche sera soit en haut ou en bas de l'écran
    if color == chess.WHITE:
        # Afficher le texte de la pendule blanche
        show_text(texteW, BLACK, SCREEN, pos_clock_downboard[0] - dim_clock[0] + 20, pos_clock_downboard[1])

        # Afficher le texte de la pendule noire
        show_text(texteB, BLACK, SCREEN, pos_clock_upboard[0] - dim_clock[0] + 20, pos_clock_upboard[1])
    else:
        show_text(texteW, BLACK, SCREEN, pos_clock_upboard[0] - dim_clock[0] + 20, pos_clock_upboard[1])
        show_text(texteB, BLACK, SCREEN, pos_clock_downboard[0] - dim_clock[0] + 20, pos_clock_downboard[1])


def update_time(color):
    # Fonction permettant de gérer le temps des pendules selon quel joueur joue

    global pauseW, remaining_timeW, pauseB, remaining_timeB, increment

    if color == chess.WHITE:
        pauseW = True
        pauseB = False
        remaining_timeW += increment
    else:
        pauseB = True
        pauseW = False
        remaining_timeB += increment


# ----------------------------------------------- Programme principale ----------------------------------------------- #
selected = False
difficulty = "easy"


def refresh(board, color, selected_square, white_score, black_score):
    # Fonction permettant le rafraichissement de l'interface graphique et de tous ses élements

    global selected, difficulty

    if selected:
        print_board(board, color, selected_square)  # Affichage des coups légaux pour la case sélectionnée
    else:
        print_board(board, color)  # Affichage de l'échiquier

    show_title()  # Affichage du titre
    SCREEN.blit(pygame.transform.scale(logo_upjv, (125, 136)), (0, 0))  # Affichage du logo de l'UPJV
    SCREEN.blit(exit_button, (SCREEN_WIDTH - SQUARE_SIDE, 20))  # Affichage du bouton exit

    show_play_button()  # Affichage du bouton play
    show_color_choice()  # Affichage des boutons pour le choix de la couleur des pièces
    show_time_controls()  # Affichage des cadences de jeu
    show_increment_time()  # Affichage des incrémentations
    show_difficulty_button()  # Affichage des difficultés

    show_score(color, white_score, black_score)  # Affichage du score
    show_clock(color)  # Affichage des pendules
    show_move_stack(board)  # Affichage de l'historique des coups

    # Affichage du bouton pour changer le thème de l'échiquier
    SCREEN.blit(pygame.transform.scale(change_theme_button, (40, 40)), pos_change_theme_button)

    # Affichage du bouton pour reset les scores
    SCREEN.blit(pygame.transform.scale(reset_score_button, (40, 40)), pos_reset_score_button)

    pygame.display.flip()  # Mis à jour de la fenêtre graphique


def play_as(board, color):
    global BOARD_COLOR, play_button, play_button_color
    global selected
    global pauseW, pauseB, remaining_timeW, remaining_timeB, initial_time, increment
    global thread_white_clock, thread_black_clock, has_time
    global white_button_rect, black_button_rect, random_button_rect
    run = True
    lance = ongoing = False
    leaving_square = arriving_square = selected_square = None
    white_score = black_score = 0
    has_resigned = False
    second_click = False
    global difficulty

    opposing_color = chess.BLACK if color == chess.WHITE else chess.WHITE

    try:
        while run:
            CLOCK.tick(CLOCK_TICK)

            # Si le temps s'est écoulé pour l'une des deux pendules, il faut relancer un thread
            if not thread_white_clock.is_alive():
                thread_white_clock = threading.Thread(target=white_clock)
                thread_white_clock.start()

            if not thread_black_clock.is_alive():
                thread_black_clock = threading.Thread(target=black_clock)
                thread_black_clock.start()

            if pauseW == pauseB:
                if has_resigned:
                    play_button_color = LICHESS_GRAY_LIGHT
                else:
                    play_button_color = GREEN_PLAY
            else:
                play_button_color = RED_RESIGN

            if play_button_color == GREEN_PLAY:
                play_button = play_font.render('PLAY', True, BLACK)
            elif play_button_color == RED_RESIGN:
                play_button = play_font.render('RESIGN', True, BLACK)
            elif play_button_color == LICHESS_GRAY_LIGHT:
                play_button = play_font.render('PLAY AGAIN', True, BLACK)

            refresh(board, color, selected_square, white_score, black_score)

            while lance is False:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        lance = True
                        has_time = run = False

                    if event.type == pygame.MOUSEMOTION:
                        # Vérifier si la souris est sur le bouton play
                        if is_on_play_button(event):
                            play_button_color = RED_RESIGN
                        else:
                            play_button_color = GREEN_PLAY

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Exit
                        if (pos_exit_button[0] <= event.pos[0] <= pos_exit_button[0] + exit_button.get_width()
                                and pos_exit_button[1] <= event.pos[1] <= pos_exit_button[1] + exit_button.get_height()):
                            lance = True
                            has_time = run = False

                        # Changer le thème de l'échiquier
                        if (pos_change_theme_button[0] <= event.pos[0] <= pos_change_theme_button[0] + 40
                                and pos_change_theme_button[1] <= event.pos[1] <= pos_change_theme_button[1] + 40):
                            new_colors = deepcopy(BOARD_COLORS)
                            new_colors.remove(BOARD_COLOR)
                            BOARD_COLOR = choice(new_colors)

                        if (pos_reset_score_button[0] <= event.pos[0] <= pos_reset_score_button[0] + 40
                                and pos_reset_score_button[1] <= event.pos[1] <= pos_reset_score_button[1] + 40):
                            white_score = black_score = 0

                        if is_on_easy_difficulty(event):
                            difficulty = "easy"

                        if is_on_hard_difficulty(event):
                            difficulty = "hard"

                        # Vérifier si le clic est dans la zone du bouton play
                        if is_on_play_button(event):
                            # Lancer la partie
                            lance = ongoing = True
                            pauseW = False

                        # Sélection de la cadence de jeu
                        for i, time_control in enumerate(TIME_CONTROLS):
                            if TC_BUTTON_X + i * (BUTTON_WIDTH + 5) <= event.pos[0] <= TC_BUTTON_X + (i + 1) * (
                                    BUTTON_WIDTH + 5) and TC_BUTTON_Y <= event.pos[1] <= TC_BUTTON_Y + BUTTON_HEIGHT:
                                initial_time = time_control * 60
                                remaining_timeW = remaining_timeB = initial_time

                        # Sélection de l'incrémentation
                        for i, increment_time in enumerate(INCREMENT_TIME):
                            if (INCREMENT_BUTTON_X + i * (BUTTON_WIDTH + 5) <= event.pos[0] <= INCREMENT_BUTTON_X +
                                    (i + 1) * (BUTTON_WIDTH + 5)
                                    and INCREMENT_BUTTON_Y <= event.pos[1] <= INCREMENT_BUTTON_Y + BUTTON_HEIGHT):
                                increment = increment_time

                        # Sélection de la couleur des pièces
                        if white_button_rect.collidepoint(event.pos):
                            color = chess.WHITE
                        elif black_button_rect.collidepoint(event.pos):
                            color = chess.BLACK
                        elif random_button_rect.collidepoint(event.pos):
                            color = random.choice([chess.WHITE, chess.BLACK])

                        tmp = swap_color(color)
                        if tmp != opposing_color:
                            opposing_color = tmp
                            white_score, black_score = black_score, white_score

                    if event.type == pygame.KEYDOWN:
                        # Quitter le jeu
                        if event.key == pygame.K_ESCAPE:  # escape key
                            lance = True
                            has_time = run = False

                        # Changer le thème de l'échiquier
                        if event.key == 99:  # c key
                            new_colors = deepcopy(BOARD_COLORS)
                            new_colors.remove(BOARD_COLOR)
                            BOARD_COLOR = choice(new_colors)

                        # Lancer la partie
                        if event.key == 108:  # l key
                            lance = ongoing = True
                            pauseW = False

                        # Changer la couleur des pièces jouées
                        if event.key == 114:  # r key
                            color = swap_color(color)
                            opposing_color = swap_color(color)
                            white_score, black_score = black_score, white_score

                refresh(board, color, selected_square, white_score, black_score)

            if not has_time and ongoing:
                has_resigned = True
                ongoing, white_score, black_score = loose_on_time(ongoing, white_score, black_score)
                board.push(chess.Move.null())  # Ajout du coup null pour signifier la fin de partie
                refresh(board, color, selected_square, white_score, black_score)

            if has_time and ongoing and board.is_game_over():  # Fin de partie
                tmp_white, tmp_black = get_scores(board.result())
                white_score += tmp_white
                black_score += tmp_black
                has_resigned = pauseW = pauseB = True
                refresh(board, color, selected_square, white_score, black_score)
                ongoing = False

            if has_time and ongoing and board.turn == opposing_color:  # Tour de l'ordinateur
                if difficulty == "easy" :
                    board = make_random_AI_move(board)
                elif difficulty == "hard":
                    board = make_MINMAX_AI_move(board, 4, opposing_color)
                update_time(opposing_color)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    has_time = run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Exit
                    if (pos_exit_button[0] <= event.pos[0] <= pos_exit_button[0] + exit_button.get_width()
                            and pos_exit_button[1] <= event.pos[1] <= pos_exit_button[1] + exit_button.get_height()):
                        lance = True
                        has_time = run = False

                    # Changer le thème de l'échiquier
                    if (pos_change_theme_button[0] <= event.pos[0] <= pos_change_theme_button[0]
                            + change_theme_button.get_width() and pos_change_theme_button[1] <= event.pos[1]
                            <= pos_change_theme_button[1] + 40):
                        new_colors = deepcopy(BOARD_COLORS)
                        new_colors.remove(BOARD_COLOR)
                        BOARD_COLOR = choice(new_colors)

                    if is_on_play_button(event):
                        if not ongoing:
                            # Nouvelle partie
                            remaining_timeW = remaining_timeB = initial_time
                            board = chess.Board()
                            lance = False
                            has_resigned = False
                            has_time = True
                            leaving_square = arriving_square = selected_square = None
                            selected = second_click = False
                        else:
                            # Abandon
                            has_resigned = True
                            ongoing, white_score, black_score = resign(ongoing, color, white_score, black_score)
                            board.push(chess.Move.null())  # Ajout du coup null pour signifier la fin de partie
                            refresh(board, color, selected_square, white_score, black_score)

                    if is_in_board():
                        if not second_click:
                            leaving_square = coord2str(event.pos, color)
                            selected_square = leaving_square

                if event.type == pygame.MOUSEBUTTONUP:
                    if is_in_board():
                        arriving_square = coord2str(event.pos, color)

                    if leaving_square is not None and arriving_square is not None:
                        if leaving_square == arriving_square:
                            selected = not selected
                            if second_click:
                                second_click = False
                            else:
                                second_click = True
                        else:
                            second_click = False
                            selected = False

                        if has_time and ongoing and board.turn == color:
                            if leaving_square != arriving_square and arriving_square is not None:
                                move = chess.Move.from_uci(leaving_square + arriving_square)
                                promotion = promote_pawn(board, move, color)

                                if promotion is not None:
                                    move = chess.Move.from_uci(leaving_square + arriving_square + str(promotion).lower())

                                # Vérifiez si le coup est légal
                                board = try_move(board, move, color)

                                leaving_square = None
                                second_click = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == 113:
                        has_time = run = False

                    if event.key == 97:  # a key
                        # Abandon
                        has_resigned = True
                        ongoing, white_score, black_score = resign(ongoing, color, white_score, black_score)
                        board.push(chess.Move.null())  # Ajout du coup null pour signifier la fin de partie
                        refresh(board, color, selected_square, white_score, black_score)

                    if event.key == 99:  # c key
                        # Changer le thème de l'échiquier
                        new_colors = deepcopy(BOARD_COLORS)
                        new_colors.remove(BOARD_COLOR)
                        BOARD_COLOR = choice(new_colors)

                    if event.key == 104 and ongoing and board.turn == color:  # h key
                        # Coup de l'ordi
                        board = make_random_AI_move(board)
                        update_time(color)

                    if event.key == 106 and not ongoing:  # j key
                        # Nouvelle partie
                        remaining_timeW = remaining_timeB = initial_time
                        board = chess.Board()
                        lance = False
                        has_resigned = False
                        has_time = True
                        leaving_square = arriving_square = selected_square = None
                        selected = second_click = False

                    if event.key == 117:  # u key
                        if board.move_stack.__len__() > 1:
                            board.pop()  # Annulation du coup de la machine
                            board.pop()  # Annulation du coup de l'utilisateur

    except:
        print(format_exc(), file=stderr)
        bug_file = open('bug_report.txt', 'a')
        bug_file.write('----- ' + strftime('%x %X') + ' -----\n')
        bug_file.write(format_exc())
        bug_file.write('\nPlaying as WHITE:\n\t' if color == chess.WHITE else '\nPlaying as BLACK:\n\t')
        bug_file.write(str(board.move_stack) + '\n\t')
        bug_file.write('\n-----------------------------\n\n')
        bug_file.close()


def play_random_color():
    # Fonction permettant à l'utilisateur de jouer aléatoirement les pièces blanches ou noires
    color = choice([chess.WHITE, chess.BLACK])
    play_as(chess.Board(), color)


play_random_color()
