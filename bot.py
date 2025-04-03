from pyautogui import *
import pyautogui
import time
import keyboard
import random
import win32api, win32con
import mouse
from colorama import Back, Style, Fore, init
import time
import numpy as np

start_time = time.time()
init(autoreset=True)


"""

World of Minesweeper web settings
Color -> Classic(dark)
Web zoom -> 100%
size -> 24
Brightness -> 90%


uncovered cells(-1) ->⬛
0 cells(0) -> ⬜
flag(9) -> ⛳

"""
dx = [-1, 0, 1,
      -1, 0, 1,
      -1, 0, 1]

dy = [0, 0, 0,
     -1,-1,-1,
      1, 1, 1]
rows, cols, cell_size = 16, 30, 48
playing_board_x, playing_board_y, playing_board_width, playing_board_height = (76,544,1444,772) 

# Initialize board with -1

def print_board():
    print()
    for i in range(0, rows):
        for j in range(0, cols):
            if board[i][j] == -1:
                print(".", end=' ')
            elif board[i][j] == 0:
                print(" ", end=' ')
            elif board[i][j] == 1:
                print(Fore.BLUE + "1", end=' ')
            elif board[i][j] == 2:
                print(Fore.GREEN + "2", end=' ')
            elif board[i][j] == 3:
                print(Fore.RED + "3", end=' ')
            elif board[i][j] == 4:
                print(Fore.MAGENTA + "4", end=' ')
            elif board[i][j] == 5:
                print(Fore.YELLOW + "5", end=' ')
            elif board[i][j] == 6:
                print(Fore.CYAN + "6", end=' ')
            elif board[i][j] == 7:
                print(Fore.LIGHTBLACK_EX + "7", end=' ')
            elif board[i][j] == 8:
                print("8", end=' ')
            elif board[i][j] == 9:
                print(Fore.RED + Style.BRIGHT + "F", end=' ')
        print("")
def mouse_display():
    while keyboard.is_pressed('q') == False:
        time.sleep(0.5)
        print(mouse.get_position())

#whole board (40, 380)    (1550, 1340)
#playing board (78, 545)    (1515, 1312)
#cell   (78, 546)    (123, 592) -> one cell (0,0)   (48, 48)

""" uncovered -> RGB: (70, 76, 82)
        0 -> RGB: (52, 58, 64)
        1 -> RGB: (132, 177, 225)
        2 -> RGB: (85, 115, 83)
        3 -> RGB: (208, 114, 124)
        4 -> RGB: (197, 127, 223)
        5 -> RGB: (189, 155, 62)
        6 -> RGB: (122, 182, 183)
        7 -> 
        8 -> 
        flag -> RGB: (98, 103, 110)
"""

def scan_field(field_rows, field_cols, field_mines):
    global board, cell_size, LU_coordinates, RD_coordinates, field_width, field_height
    board = [[-1 for _ in range(field_cols)] for _ in range(field_rows)]
    iml = pyautogui.screenshot()
    iml.save(r"C:\Users\jakub\OneDrive\Desktop\MS_bot\pictures\board_test1.png")
    try:
        LU_coordinates = pyautogui.locate(f'pictures/LU_corner.png', iml, grayscale= False)
    except ImageNotFoundException:
        return print("LU_corner not located")
    try:
        RD_coordinates = pyautogui.locate(f'pictures/RD_corner.png', iml, grayscale= False)
    except ImageNotFoundException:
        return print("RD_corner not located")

    LU_coordinates = center(LU_coordinates)
    RD_coordinates = center(RD_coordinates)
    field_width = RD_coordinates.x - LU_coordinates.x
    field_height = RD_coordinates.y - LU_coordinates.y
    cell_size = field_width / (field_cols - 1)
    print(LU_coordinates)
    print(RD_coordinates)
    print(cell_size)





def update():
    iml = pyautogui.screenshot(region=(playing_board_x, playing_board_y, playing_board_width, playing_board_height))
    iml.save(r"C:\Users\jakub\OneDrive\Desktop\MS bot\pictures\board.png")
    
    board_image = 'pictures/board.png'
    set_confidence = 0.8

    for i in range(rows):
        for j in range(cols):
            coordinates = (4 + (j * cell_size), 4 + (i * cell_size), cell_size + 2, cell_size + 2)
            cell_value = get_cell_value(board_image, coordinates, set_confidence)
            if cell_value is not None:
                board[i][j] = cell_value
def get_cell_value(board_image, coordinates, confidence):
    image_values = {
        'uncovered': -1,
        '1_mines': 1,
        '2_mines': 2,
        '3_mines': 3,
        '4_mines': 4,
        '5_mines': 5,
        '6_mines': 6,
        '7_mines': 7,
        '8_mines': 8,
        'flag': 9,
        '0_mines': 0
    }

    for image_name, value in image_values.items():
        if locate_image(image_name, board_image, coordinates, confidence):
            return value
    
    return None  # If no match is found

def locate_image(image_name, board_image, coordinates, confidence):
    try:
        return pyautogui.locate(f'pictures/{image_name}.png', board_image, region=coordinates, grayscale=False, confidence=confidence)
    except ImageNotFoundException:
        return None


def update_new():
    set_tolerance = 3
    
    for i in range(rows):
        for j in range(cols):
            coordinates_x = playing_board_x + 25 + (j * cell_size)
            coordinates_y = playing_board_y + 25 + (i * cell_size)
            cell_value = get_cell_value_new(coordinates_x, coordinates_y, set_tolerance)
            if cell_value is not None:
                board[i][j] = cell_value

def get_cell_value_new(coordinates_x, coordinates_y, tolerance):
    RGB_values = {
        (70, 76, 82): -1,
        (132, 177, 225): 1,
        (85, 115, 83): 2,
        (208, 114, 124): 3,
        (197, 127, 223): 4,
        (189, 155, 62): 5,
        (122, 182, 183): 6,
        (255, 255, 255): 7, #not set
        (255, 255, 255): 8, #not set
        (98, 103, 110): 9,
        (52, 58, 64): 0
    }
    for RGB_value, value in RGB_values.items():
        if pyautogui.pixelMatchesColor(coordinates_x, coordinates_y, RGB_value, tolerance= tolerance) == True:
            return value
    return print("get_cell_value -> RGB not found")


RGB_VALUES = {
    (70, 76, 82): -1,
    (132, 177, 225): 1,
    (85, 115, 83): 2,
    (119, 173, 102): 2,
    (208, 114, 124): 3,
    (197, 127, 223): 4,
    (189, 155, 62): 5,
    (122, 182, 183): 6,
    (138, 138, 138): 7,
    (196, 202, 208): 9,
    (98, 103, 110): 9,
    (52, 58, 64): 0
}

def update_new_new():
    iml = pyautogui.screenshot(region=(int(LU_coordinates.x - 2 - (int(cell_size) / 2)), int(LU_coordinates.y - 2 - (int(cell_size) / 2)), int(field_width + 4 + cell_size), int(field_height + 4 + cell_size)))
    iml.save(r"C:\Users\jakub\OneDrive\Desktop\MS_bot\pictures\board.png")
    img_array = np.array(iml)
    board_image = 'pictures/board.png'
    set_tolerance = 3
    
    for i in range(rows):
        for j in range(cols):
            coordinates_x = int(25 + (j * cell_size))
            coordinates_y = int(25 + (i * cell_size))
            rgb = img_array[coordinates_y, coordinates_x]
            board[i][j] = get_cell_value_new(rgb)    
def get_cell_value_new(rgb):
    return next((value for key, value in RGB_VALUES.items() if np.all(np.abs(rgb - key) <= 3)), None)


def screenshot_test():
    for i in range(0, rows):
        for j in range(0, cols):
            coordinates = ((j*cell_size), (i*cell_size), cell_size+5, cell_size+5)                 
            iml = pyautogui.screenshot(region=(playing_board_x+ 6 +(j*cell_size), playing_board_y+ 6 +(i*cell_size), cell_size-7, cell_size-7))
            iml.save(rf"C:\Users\jakub\OneDrive\Desktop\MS_bot\pictures\test\{i}_{j}.png")
def color_check():
    for i in range(rows):
        for j in range(cols):
            pix = pyautogui.pixel(playing_board_x+ 25 + (j * cell_size), playing_board_y + 25 + (i * cell_size))
            print(f"Position [{i}][{j}] RGB: {pix}")

def solve_basic():
    count = 0
    for j in range(cols):
        for i in range(rows):
            if board[i][j] <= 0: continue
            count_flagged_mine = 0
            count_uncovered = 0
            for k in range(9):
                if i + dx[k] >= 0 and i + dx[k] < rows and j + dy[k] >= 0 and j + dy[k] < cols:
                    if board[i + dx[k]][j + dy[k]] == 9:
                        count_flagged_mine += 1
                    if board[i + dx[k]][j + dy[k]] == -1:
                        count_uncovered += 1
            
            if board[i][j] == count_flagged_mine:
                if count_uncovered == 0: continue
                else:
                    mouse.move(LU_coordinates.x + (j * cell_size), LU_coordinates.y + (i * cell_size), absolute= True, duration= 0.1)
                    mouse.click('left')
                    time.sleep(0.15)
                    count += 1
            
            elif board[i][j] == count_flagged_mine + count_uncovered:
                for k in range(9):
                    if i + dx[k] >= 0 and i + dx[k] < rows and j + dy[k] >= 0 and j + dy[k] < cols:
                        if board[i + dx[k]][j + dy[k]] == -1:
                            mouse.move(((j + dy[k]) * cell_size) + LU_coordinates.x, ((i + dx[k]) * cell_size) + LU_coordinates.y, absolute= True, duration= 0.1)
                            mouse.click('right')
                            time.sleep(0.15)
                            count += 1
                            board[i + dx[k]][j + dy[k]] = 9
                            
    mouse.move(LU_coordinates.x, LU_coordinates.y)
    return count

def main():
    time.sleep(2)
    count = 1
    scan_field(16,30,99)
    print("now")
    time.sleep(5)
    while count != 0:
        count = 0
        update_new_new()
        print_board()
        count = solve_basic()
    
    

main()

#color_check()
"""while 1:
    pos = mouse.get_position()
    pix = pyautogui.pixel(pos[0], pos[1])
    print(f"Position [{pos[0]}][{pos[1]}] RGB: {pix}")
    time.sleep(0.5)"""

#mouse.move(playing_board_x+ 25 + (8 * cell_size), playing_board_y + 25 + (1 * cell_size),)
end_time = time.time()
print(f"Process finished --- {end_time - start_time} seconds ---")