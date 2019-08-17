from tkinter import *

''' Config Variables '''
# Window/Board Settings
window_size = 800
num_tiles = 8 # Must be even
rows_starting_pieces = 3
piece_buffer = .1  # Percent of tile to use as buffer between edge of tile and piece

# Game Colors
movable_background_color = "chocolate"     # Default: "chocolate"
immovable_background_color = "DarkOrange"  # Default: "DarkOrange"
player_one_color = "black"                 # Default: "black"
player_two_color = "white"                 # Default: "white"
piece_highlight_color = "yellow"           # Default: "yellow"
piece_jump_highlight_color = "red"         # Default: "red"

''' Core Application '''
# Initialize Canvas/UI
window_width = window_size
window_height = window_size

root = Tk()
root.title("Checkers")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

middle_window_x = window_width / 2
middle_window_y = window_height / 2

window_offset_x = int((screen_width / 2) - (window_width / 2))
window_offset_y = int((screen_height / 2) - (window_height / 2))

root.geometry(str(window_width) + "x" + str(window_height) + "+" + str(window_offset_x) + "+" + str(window_offset_y))
root.resizable(False, False)

canvas = Canvas(root, width=window_width, height=window_height)
canvas.pack()

piece_width = window_size / (num_tiles * 4)


# Game Classes
class Board:
    tiles = []

    def __init__(self, start_x, start_y, board_width, board_height):
        self.start_x = start_x
        self.start_y = start_y
        self.board_width = board_width
        self.board_height = board_height
        self.player_one_color = player_one_color
        self.player_two_color = player_two_color
        self.movable_background_color = movable_background_color
        self.immovable_background_color = immovable_background_color

        self.piece_selected = False
        self.selected_piece_column = None
        self.selected_piece_row = None

        self.turn = player_one_color
        self.extra_jump = False
        self.piece_can_jump = False
        self.is_game_won = False
        self.update_title()

        self.create_tiles()
        self.draw_board()

    def create_tiles(self):
        is_movable_tile = True

        for c in range(num_tiles):
            row = []
            for r in range(num_tiles):
                if is_movable_tile:
                    tile = Tile(is_movable_tile=is_movable_tile, row_index=r, column_index=c,
                                fill_color=self.movable_background_color,
                                outline_color=self.immovable_background_color,
                                board_start_x=self.start_x, board_start_y=self.start_y,
                                board_width=self.board_width, board_height=self.board_height)

                    # Add piece to tile if a valid tile
                    if r < rows_starting_pieces:
                        tile.add_piece(color=self.player_two_color, outline=self.player_one_color)
                    elif r >= num_tiles - rows_starting_pieces:
                        tile.add_piece(color=self.player_one_color, outline=self.player_two_color)

                    row.append(tile)
                    is_movable_tile = False
                else:
                    tile = Tile(is_movable_tile=is_movable_tile, row_index=r, column_index=c,
                                fill_color=self.immovable_background_color,
                                outline_color=self.movable_background_color,
                                board_start_x=self.start_x, board_start_y=self.start_y,
                                board_width=self.board_width, board_height=self.board_height)
                    row.append(tile)
                    is_movable_tile = True

            self.tiles.append(row)

            if is_movable_tile:
                is_movable_tile = False
            else:
                is_movable_tile = True

    def draw_board(self):
        for c in range(num_tiles):
            row = self.tiles[c]
            for r in range(num_tiles):
                row[r].draw_tile()
                row[r].draw_piece()

    def redraw_pieces(self):
        canvas.delete(self.player_one_color)
        canvas.delete(self.player_two_color)

        for c in range(num_tiles):
            row = self.tiles[c]
            for r in range(num_tiles):
                row[r].draw_piece()

        self.check_if_won()

    def change_turn(self):
        if self.turn is self.player_one_color:
            self.turn = self.player_two_color
        else:
            self.turn = self.player_one_color

        self.check_for_kings()
        self.check_for_jumps()

        self.update_title()

    def check_for_kings(self):
        start_index = 0
        end_index = num_tiles - 1

        for c in range(num_tiles):
            if self.tiles[c][start_index].piece is not None:
                piece_color = self.tiles[c][start_index].piece.color
                if piece_color is self.player_one_color:
                    self.tiles[c][start_index].piece.is_king = True
            if self.tiles[c][end_index].piece is not None:
                piece_color = self.tiles[c][end_index].piece.color
                if piece_color is self.player_two_color:
                    self.tiles[c][end_index].piece.is_king = True

    def check_for_jumps(self):
        self.piece_can_jump = False

        for c in range(num_tiles):
            for r in range(num_tiles):
                if self.tiles[c][r].piece is not None and self.tiles[c][r].piece.color is self.turn:
                    self.piece_selected = True
                    self.selected_piece_column = c
                    self.selected_piece_row = r

                    if selected_piece_can_jump():
                        self.tiles[c][r].piece.can_jump = True
                        self.piece_can_jump = True
                    else:
                        self.tiles[c][r].piece.can_jump = False

                    self.piece_selected = False
                elif self.tiles[c][r].piece is not None:
                    self.tiles[c][r].piece.can_jump = False

        self.piece_selected = False
        self.selected_piece_column = None
        self.selected_piece_row = None

    def check_if_won(self):
        player_one_pieces = 0
        player_two_pieces = 0

        for c in range(num_tiles):
            for r in range(num_tiles):
                if self.tiles[c][r].piece is not None:
                    piece_color = self.tiles[c][r].piece.color
                    if piece_color is self.player_one_color:
                        player_one_pieces += 1
                    elif piece_color is self.player_two_color:
                        player_two_pieces += 1

        if player_one_pieces is 0:
            board.is_game_won = True
            font = "Times " + str(int(window_size / 16)) + " bold"
            win_text = canvas.create_text(middle_window_x, middle_window_y, font=font, fill=self.player_one_color,
                                          text=str.capitalize(self.player_two_color) + " Wins!")
            bbox = canvas.bbox(win_text)
            rect_position = self.increase_coord_size(bbox, 16)
            text_outline = canvas.create_rectangle(rect_position, outline=player_two_color, fill=player_two_color)
            canvas.tag_raise(win_text, text_outline)

        if player_two_pieces is 0:
            board.is_game_won = True
            font = "Times " + str(int(window_size / 16)) + " bold"
            win_text = canvas.create_text(middle_window_x, middle_window_y, font=font, fill=self.player_two_color,
                                          text=str.capitalize(self.player_one_color) + " Wins!")
            bbox = canvas.bbox(win_text)
            rect_position = self.increase_coord_size(bbox, 16)
            text_outline = canvas.create_rectangle(rect_position, outline=player_one_color, fill=player_one_color)
            canvas.tag_raise(win_text, text_outline)

    def update_title(self):
        if not self.is_game_won:
            root.title("Checkers - " + str.capitalize(self.turn) + "'s Turn")
        else:
            root.title("Checkers - " + str.capitalize(self.turn) + " Wins!")

    @staticmethod
    def increase_coord_size(bbox, window_fraction):
        window_portion = (window_size / window_fraction)
        c = bbox[0] - window_portion, bbox[1] - window_portion, bbox[2] + window_portion, bbox[3] + window_portion
        return c


class Tile:

    def __init__(self, is_movable_tile, row_index, column_index, fill_color, outline_color,
                 board_start_x, board_start_y, board_width, board_height):
        self.is_movable_tile = is_movable_tile

        self.row_index = row_index
        self.column_index = column_index
        self.fill_color = fill_color
        self.outline_color = outline_color

        self.start_x = board_start_x + ((board_width / num_tiles) * column_index)
        self.start_y = board_start_y + ((board_height / num_tiles) * row_index)
        self.end_x = board_start_x + ((board_width / num_tiles) * (column_index + 1))
        self.end_y = board_start_y + ((board_height / num_tiles) * (row_index + 1))

        self.piece = None
        self.piece_buffer_x = (self.end_x - self.start_x) * (1 - piece_buffer)
        self.piece_buffer_y = (self.end_y - self.start_y) * (1 - piece_buffer)

    def draw_tile(self):
        canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y,
                                fill=self.fill_color, outline=self.outline_color)

    def add_piece(self, color, outline):
        self.piece = Piece(color=color, outline=outline)

    def draw_piece(self):
        if self.piece is not None:
            outline_color = self.piece.outline
            if self.piece.is_selected:
                outline_color = piece_highlight_color
            elif self.piece.can_jump:
                outline_color = piece_jump_highlight_color

            canvas.create_oval(self.start_x + self.piece_buffer_x, self.start_y + self.piece_buffer_y,
                               self.end_x - self.piece_buffer_x, self.end_y - self.piece_buffer_y,
                               fill=self.piece.color, outline=outline_color, tag=self.piece.color)
            if self.piece.is_king:
                if self.piece.color is player_one_color:
                    fill_color = player_two_color
                else:
                    fill_color = player_one_color

                eighth_tile = (self.end_x - self.start_x) / 8
                sixteenth_tile = (self.end_x - self.start_x) / 16

                crown_start_x = self.start_x + eighth_tile * 3
                crown_end_x = self.end_x - eighth_tile * 3
                crown_start_y = self.start_y + eighth_tile * 3
                crown_end_y = self.end_y - eighth_tile * 3

                x1 = crown_start_x
                y1 = crown_end_y

                x2 = crown_start_x - sixteenth_tile
                y2 = crown_start_y

                x3 = crown_start_x + sixteenth_tile
                y3 = crown_end_y - eighth_tile

                x4 = crown_start_x + sixteenth_tile * 2
                y4 = crown_start_y

                x5 = crown_start_x + sixteenth_tile * 3
                y5 = crown_end_y - eighth_tile

                x6 = crown_end_x + sixteenth_tile
                y6 = crown_start_y

                x7 = crown_end_x
                y7 = crown_end_y

                canvas.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, x7, y7,
                                      fill=fill_color, tag=fill_color)


class Piece:

    def __init__(self, color, outline):
        self.color = color
        self.outline = outline
        self.is_selected = False
        self.is_king = False
        self.can_jump = False

    def get_direction(self):
        if self.color == board.player_one_color:
            return -1
        elif self.color == board.player_two_color:
            return 1
        else:
            return None


# pos_x and pos_y are the x,y coordinates of the window, whereas x and y are the tile index
def get_location(x_pos, y_pos):
    col = None
    row = None

    for x in range(num_tiles):
        start_x = board.tiles[x][0].start_x
        end_x = board.tiles[x][0].end_x
        if start_x < x_pos < end_x:
            col = x
            break

    for y in range(num_tiles):
        start_y = board.tiles[0][y].start_y
        end_y = board.tiles[0][y].end_y
        if start_y < y_pos < end_y:
            row = y
            break
    return col, row


def mouse_click(event):
    selected_indices = get_location(x_pos=event.x, y_pos=event.y)
    c = selected_indices[0]
    r = selected_indices[1]

    if board.tiles[c][r].piece is not None and not board.extra_jump:
        if board.tiles[c][r].piece.color is board.turn:
            if board.piece_can_jump and not board.tiles[c][r].piece.can_jump:
                return

            if board.piece_selected:
                board.tiles[board.selected_piece_column][board.selected_piece_row].piece.is_selected = False
            board.selected_piece_row = r
            board.selected_piece_column = c
            board.piece_selected = True
            board.tiles[c][r].piece.is_selected = True

            board.redraw_pieces()

    elif board.piece_selected and board.tiles[c][r].is_movable_tile and board.tiles[c][r].piece is None:
        piece_jumped = check_valid_move(desired_row=r, desired_column=c)

        if piece_jumped is not None:
            if board.extra_jump and not piece_jumped:
                return
            if not piece_jumped and board.piece_can_jump:
                return

            board.tiles[c][r].piece = board.tiles[board.selected_piece_column][board.selected_piece_row].piece
            board.tiles[board.selected_piece_column][board.selected_piece_row].piece = None

            if piece_jumped:
                jumped_piece_column = int(board.selected_piece_column + ((c - board.selected_piece_column) / 2))
                jumped_piece_row = int(board.selected_piece_row + ((r - board.selected_piece_row) / 2))
                board.tiles[jumped_piece_column][jumped_piece_row].piece = None

                board.selected_piece_row = r
                board.selected_piece_column = c
                board.piece_selected = True
                board.tiles[c][r].piece.is_selected = True

                if selected_piece_can_jump():
                    board.extra_jump = True
                else:
                    board.extra_jump = False

            if not board.extra_jump:
                board.selected_piece_row = r
                board.selected_piece_column = c
                board.piece_selected = None
                board.tiles[c][r].piece.is_selected = None

                board.change_turn()

            board.redraw_pieces()


# Returns None if there is no move
# Returns False if there is a move without capturing
# Returns True if there is a move involving capturing
def check_valid_move(desired_row, desired_column):
    if not board.piece_selected:
        return None
    if (not 0 <= desired_row < num_tiles) or (not 0 <= desired_column < num_tiles):
        return None
    if board.tiles[desired_column][desired_row].piece is not None:
        return None

    piece = board.tiles[board.selected_piece_column][board.selected_piece_row].piece
    direction = piece.get_direction()

    return check_move_spaces(piece, direction, desired_row, desired_column)


def check_move_spaces(piece, direction, desired_row, desired_column):
    if board.selected_piece_row + direction is desired_row:
        if board.selected_piece_column + 1 is desired_column or board.selected_piece_column - 1 is desired_column:
            return False

    if can_jump_pieces(direction, desired_row, desired_column):
        return True

    if piece.is_king and direction is piece.get_direction():
        return check_move_spaces(piece, direction * -1, desired_row, desired_column)

    return None


def selected_piece_can_jump():
    direction = board.tiles[board.selected_piece_column][board.selected_piece_row].piece.get_direction()
    desired_column_left = board.selected_piece_column - 2
    desired_column_right = board.selected_piece_column + 2
    desired_row = board.selected_piece_row + (direction * 2)
    desired_king_row = board.selected_piece_row + (direction * -2)

    check_left_move = check_valid_move(desired_row, desired_column_left)
    check_right_move = check_valid_move(desired_row, desired_column_right)
    check_left_king_move = None
    check_right_king_move = None
    if board.tiles[board.selected_piece_column][board.selected_piece_row].piece.is_king:
        check_left_king_move = check_valid_move(desired_king_row, desired_column_left)
        check_right_king_move = check_valid_move(desired_king_row, desired_column_right)

    return check_left_move or check_right_move or check_left_king_move or check_right_king_move


def can_jump_pieces(direction, desired_row, desired_column):
    if board.selected_piece_row + (2 * direction) is desired_row:
        left_check = board.selected_piece_column - 2 is desired_column
        left_check_in_bounds = desired_column >= 0
        right_check = board.selected_piece_column + 2 is desired_column
        right_check_in_bounds = desired_column < num_tiles

        if right_check_in_bounds and right_check:
            jumped_piece = board.tiles[board.selected_piece_column + 1][board.selected_piece_row + direction].piece
            selected_piece = board.tiles[board.selected_piece_column][board.selected_piece_row].piece
            if jumped_piece is not None:
                if jumped_piece.color is not selected_piece.color:
                    return True

        elif left_check_in_bounds and left_check:
            jumped_piece = board.tiles[board.selected_piece_column - 1][board.selected_piece_row + direction].piece
            selected_piece = board.tiles[board.selected_piece_column][board.selected_piece_row].piece
            if jumped_piece is not None:
                if jumped_piece.color is not selected_piece.color:
                    return True

    return False


# Start game logic
board = Board(start_x=0, start_y=0, board_width=window_width, board_height=window_height)
board.draw_board()

canvas.bind("<1>", mouse_click)

root.mainloop()
