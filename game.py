from typing import Iterable, IO
import pyautogui
from pyautogui import *
from itertools import product, combinations
from random import Random
import numpy as np
from colorama import Back, Style, Fore, init
from cell import Cell
import time
init(autoreset=True)


class Minesweeper:
    
    
    def __init__(self, rows: int, columns: int, mines: int):
        self.grid: list[list[Cell]] = [[Cell(x, y, -1) for y in range(columns)] for x in range(rows)]
        self.pairs: set[tuple[Cell, Cell]] = set()
        self.stepped: set[Cell] = set()
        self.flagged: set[Cell] = set()
        self.to_flag: set[Cell] = set()
        self.to_step: set[Cell] = set()
        self.to_chord: set[Cell] = set()
        self.to_search: set[Cell] = set()
        self.col_count = columns
        self.row_count = rows
        self.mine_count = mines
        
        self.click_sleep: float = 0.05
        self.face_region: tuple[int, int, int, int] = None
        self.region_coordinates: tuple[int, int, int, int] = None
        self.cell_dimensions: int = None
        self.first_cell_pos: tuple[int, int] = None
        self.field_width: int = None
        self.field_height: int = None
        self.save_rep = r"C:\Users\jakub\OneDrive\Desktop\MS_bot\pictures\board.png"
        self.save_rep2 = r"C:\Users\jakub\OneDrive\Desktop\MS_bot\pictures\big_board.png"
        self.reset()
        self.set_dimensions(self.find_corners())
        
        if self.update(True) == False:
            pass
        self.set_first_cell_pos()



    # resets the game and all its attributes
    def reset(self):
        self.grid = [[Cell(row, col, -1) for col in range(self.col_count)] for row in range(self.row_count)]
        self.stepped = set()
        self.flagged = set()
    
    
    # finds the corners of the game board on screen
    def find_corners(self) -> tuple[tuple[int, int], tuple[int, int]]:
        iml = pyautogui.screenshot()
        iml.save(f"{self.save_rep2}")
        LU_coordinates = pyautogui.locate(f'pictures/LU_corner.png', iml, grayscale=False)
        RD_coordinates = pyautogui.locate(f'pictures/RD_corner.png', iml, grayscale=False)
        face_region = pyautogui.locate(f'pictures/running_game.png', iml, grayscale=False)  
        if LU_coordinates is None:
            raise ValueError("Left_Up_corner not located")
        if RD_coordinates is None:
            raise ValueError("Right_Down_corner not located")
        if face_region is None:
            raise ValueError("Face region not located")
        
        self.face_region = (int(face_region.left - 10),
                            int(face_region.top  - 10), 
                            int(face_region.width + 20), 
                            int(face_region.height + 20))
        print(self.face_region)
        LU_coordinates = center(LU_coordinates)
        RD_coordinates = center(RD_coordinates)
        return ((LU_coordinates.x, LU_coordinates.y), (RD_coordinates.x, RD_coordinates.y))
        
    
    # sets the dimensions of the game board
    def set_dimensions(self, corners: tuple[tuple[int, int], tuple[int, int]]):
        self.field_width = corners[1][0] - corners[0][0]
        self.field_height = corners[1][1] - corners[0][1]
        self.cell_dimensions = int(self.field_width / (self.col_count - 1))
        self.region_coordinates = (int(corners[0][0] - 2 - int((self.cell_dimensions / 2))),
                                   int(corners[0][1] - 2 - int((self.cell_dimensions / 2))),
                                   int(self.field_width + 4 + self.cell_dimensions), 
                                   int(self.field_height + 4 + self.cell_dimensions)
                                   )
    
    
    

    
    # updates the game board based on the current screen
    def update(self, save_image: bool = False) -> bool:
        iml = pyautogui.screenshot(region= self.region_coordinates)
        uml = pyautogui.screenshot(region= self.face_region)
        try:
            sad_face = pyautogui.locate(f'pictures/lost_game.png', uml, grayscale=False)
            if sad_face is not None:
                print("Game lost!")
                return True
        except pyautogui.ImageNotFoundException:
            print("Game not lost")
            pass
        
        if save_image == False:
            iml.save(f"{self.save_rep}")
        img_array = np.array(iml)
        
        for i in range(self.row_count):
            for j in range(self.col_count):
                coordinates_x = int((self.cell_dimensions / 2) + 1 + (j * self.cell_dimensions))
                coordinates_y = int((self.cell_dimensions / 2) + 1 + (i * self.cell_dimensions))
                rgb = img_array[coordinates_y, coordinates_x]
                self.grid[i][j].value = self.scan_cell_value(rgb, self.grid[i][j])
                if self.grid[i][j].value == 9:
                    self.flagged |= {self.grid[i][j]}
                elif self.grid[i][j].value != -1:
                    self.stepped |= {self.grid[i][j]}
    
    
    # sets the [x,y] position of the first cell
    def set_first_cell_pos(self):
        self.first_cell_pos = (self.region_coordinates[0] + int(self.cell_dimensions / 2), self.region_coordinates[1] + int(self.cell_dimensions / 2))
    
    
    # scans the RGB value of a cell and returns its corresponding value
    def scan_cell_value(self, rgb: tuple[int, int, int], cell: Cell) -> int:
        """if cell not in self.stepped:
            raise ValueError("cell value tried unstepped cell " + str(cell))"""
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
        return next((value for key, value in RGB_VALUES.items() if np.all(np.abs(rgb - key) <= 3)), -1)
    
    
    """def find_cell_value(self, cell: Cell) -> int:
        return cell.value"""
    
    
    # returns the number of mines left unflagged
    def mines_left(self) -> int:
        return self.mine_count - len(self.flagged)
    
    
    # if game won -> True, else -> False
    def winning_state(self):
        if len(self.stepped) + len(self.flagged) == self.row_count * self.col_count - self.mine_count:
            return True
        return False
    
    
    # returns the neighbours of a cell
    def neighbours(self, cell: Cell) -> set[Cell]:
        all_neighbours = set((cell.x + row, cell.y + col) for row, col in product(range(-1, 2), repeat=2) if (row, col) != (0, 0))
        neighbours = set()
        for x, y in all_neighbours:
            if 0 <= x < self.row_count and 0 <= y < self.col_count:
                neighbours.add(self.grid[x][y])
        return neighbours
    
    
    # prints the game board to the console
    def print_field(self):
        cell_print_values = {
            -1:('.', ''),
            0: (' ', ''),
            1: ('1', Fore.BLUE),
            2: ('2', Fore.GREEN),
            3: ('3', Fore.RED),
            4: ('4', Fore.MAGENTA),
            5: ('5', Fore.YELLOW),
            6: ('6', Fore.CYAN),
            7: ('7', Fore.LIGHTBLACK_EX),
            8: ('8', ''),
            9: ('@', Fore.RED + Style.BRIGHT)
        }
        print()
        
        for i in range(self.row_count):
            for j in range(self.col_count):
                cell_value = self.grid[i][j].value
                if cell_value in cell_print_values:
                    number, color = cell_print_values[cell_value]
                    print(f"{color}{number}{Style.RESET_ALL}", end=' ') 
                else:
                    print('X', end=' ')
            print()
    
    
    # add a cell to the flagged set
    def to_flag_function(self, cell: Cell):
        if cell in self.flagged:
            raise ValueError("cell already flagged")
        if cell not in self.to_flag:
            self.to_flag |= {cell}
    # add a cell to the stepped set
    def to_step_function(self, cell: Cell):
        if cell in self.stepped:
            raise ValueError("cell already stepped")
        if cell not in self.to_step:
            self.to_step |= {cell}
    # add a cell to the to_chord set
    def to_chord_function(self, cell: Cell):
        if cell not in self.stepped:
            raise ValueError("cell not stepped")
        if cell not in self.to_chord:
            self.to_chord |= {cell}
    
    
    # flag all cells in the to_flag set
    def flag_do(self):
        while len(self.to_flag) > 0:
            cell = self.to_flag.pop()
            if cell.value != -1:
                continue
            time.sleep(self.click_sleep)
            pyautogui.click(cell.y * self.cell_dimensions + self.first_cell_pos[0], cell.x * self.cell_dimensions + self.first_cell_pos[1], button='right', duration= 0.0)
            self.flagged |= {cell}
    # step all cells in the to_step set
    def step_do(self):
        while len(self.to_step) > 0:
            cell = self.to_step.pop()
            if self.neighbours_unstepped(cell) == 0:
                continue
            time.sleep(self.click_sleep)
            pyautogui.click(cell.y * self.cell_dimensions + self.first_cell_pos[0], cell.x * self.cell_dimensions + self.first_cell_pos[1], button= 'left',  duration= 0.0)
            self.stepped |= {cell}
    # chord all cells in the to_chord set
    def chord_do(self):
        while len(self.to_chord) > 0:
            cell = self.to_chord.pop()
            if self.neighbours_unstepped(cell) == 0:
                continue
            new_stepped = self.neighbours_unstepped_set(cell)
            time.sleep(self.click_sleep)
            pyautogui.click(cell.y * self.cell_dimensions + self.first_cell_pos[0], cell.x * self.cell_dimensions + self.first_cell_pos[1], button='left', duration= 0.0)
            self.stepped |= new_stepped
    
    
    # returns the number of flagged neighbours of a cell
    def neighbours_flagged(self, cell: Cell) -> int:
        return sum(1 for neighbour in self.neighbours(cell) if neighbour in self.flagged)
    
    
    # returns the number of unstepped neighbours of a cell
    def neighbours_unstepped(self, cell: Cell) -> int:
        return sum(1 for neighbour in self.neighbours(cell) if neighbour.value == -1)
    
    
    def neighbours_unstepped_set(self, cell: Cell) -> set[Cell]:
        return set(neighbour for neighbour in self.neighbours(cell) if neighbour.value == -1)
    
    
    def neighbours_flagged_set(self, cell: Cell) -> set[Cell]:
        return set(neighbour for neighbour in self.neighbours(cell) if neighbour.value == 9)
    
    
    def neighbours_all(self, cell: Cell) -> set[Cell]:
        all_neighbours = self.neighbours_unstepped_set(cell) | self.big_neighbours(cell)
        return all_neighbours
        
        
        
        
        
    # most simple solving algorithm without any 
    # patterns or instersactions with other cells
    def solve_basic(self):
        for cell in self.to_search:
            if cell.value == self.neighbours_flagged(cell):
                self.to_chord_function(cell)
            if cell.value == self.neighbours_unstepped(cell) + self.neighbours_flagged(cell):
                for neighbour in self.neighbours_unstepped_set(cell):
                    self.to_flag_function(neighbour)
        self.to_search -= self.to_chord
        self.to_search -= self.to_flag
                        
                        
    
    def has_unstepped_intersection(self, cell1: Cell, cell2: Cell) -> bool:
        neighbours1 = self.neighbours_unstepped(cell1)
        neighbours2 = self.neighbours_unstepped(cell2)
        intersection = neighbours1 & neighbours2
        if len(intersection) > 0:
            return True
        return False
    
    
    # returns set of cells that second neighbours to cell, 
    # are stepped and have unstepped intersection with cell
    def big_neighbours(self, cell: Cell) -> set[Cell]:
        big_neighbours = set()
        for neighbour in self.neighbours(cell):
            for neighbour2 in self.neighbours(neighbour):
                if neighbour2 in self.stepped:
                    if self.has_unstepped_intersection(cell, neighbour2):
                        if neighbour2 not in big_neighbours:
                            big_neighbours.add(neighbour2)
        return big_neighbours
            
                
    def find_to_search(self):
        for cell in self.stepped:
            if cell.value > 0:
                if self.neighbours_unstepped(cell) > 0:
                    self.to_search.add(cell)
    
    
    def solve_patterns(self, a: Cell, b: Cell) -> tuple[set[Cell], set[Cell]]:
        to_step = set()
        to_flag = set()
        av = a.value
        bv = b.value
        an = self.neighbours_unstepped_set(a) | self.neighbours_flagged_set(a)
        bn = self.neighbours_unstepped_set(b) | self.neighbours_flagged_set(b)
        af = an & self.flagged
        bf = bn & self.flagged
        vdiff = av - bv
        fdiff = len(af) - len(bf)
        amb = an - bn
        bma = bn - an
        pos_cells = amb - self.stepped
        neg_cells = bma - self.stepped
        pos_cells_no_flags = pos_cells - self.flagged
        neg_cells_no_flags = neg_cells - self.flagged
        if vdiff - fdiff == len(pos_cells_no_flags):
            to_flag |= pos_cells_no_flags
            to_step |= neg_cells_no_flags
        if fdiff - vdiff == len(neg_cells_no_flags):
            to_flag |= neg_cells_no_flags
            to_step |= pos_cells_no_flags
        
        self.to_search -= to_step
        self.to_search -= to_flag
        
        return to_step, to_flag
        
    
    
    def solve_pairs(self):
        for a, b in combinations(self.to_search, 2):
            if len(self.neighbours_unstepped_set(a) & self.neighbours_unstepped_set(b)) > 0:
                new_step, new_flag = self.solve_patterns(a, b)
                self.to_step |= new_step
                self.to_flag |= new_flag
    
    
    
    
    
    def step(self, print: bool = False) -> bool:
        steps = 0
        if print:
            self.print_field()
        
        self.find_to_search()
        self.solve_basic()
        steps_basic = len(self.to_step) + len(self.to_flag) + len(self.to_chord)
        
        if steps_basic == 0:
            self.solve_pairs()
            steps = len(self.to_step) + len(self.to_flag) + len(self.to_chord)
        
        if steps + steps_basic == 0 and not self.winning_state():
            remaining_cells = (self.row_count * self.col_count) - len(self.stepped) - len(self.flagged)
            field = {cell for row in self.grid for cell in row} - self.flagged - self.stepped
            if remaining_cells == 0:
                prob_fail = 1  
            else:
                prob_fail = self.mines_left() / remaining_cells
                
            for cell in self.to_search:
                this_field = self.neighbours_unstepped_set(cell)
                if len(this_field) == 0:
                    continue
                this_prob_fail = (cell.value - self.neighbours_flagged(cell)) / len(this_field)
                if this_prob_fail <= prob_fail:
                    prob_fail = this_prob_fail
                    field = this_field
            tile = Random().choice(tuple(field))
            if self.mines_left() == ((self.row_count*self.col_count) - len(self.stepped) - len(self.flagged)):
                self.to_flag.add(tile)
            else:
                self.to_step.add(tile)
                    
        self.flag_do()
        self.step_do()
        self.chord_do()
        if self.update() == True:
            return False
        return True
        
        
                
    def play(self, number_of_games: int, ) -> tuple[int, int]:
        for i in range(number_of_games):
            self.reset()
            self.set_dimensions(self.find_corners())
            if self.update(True) == True:
                break
            
            
            while not self.winning_state():
                if self.step(True) == False:
                    break
                
            self.print_field()
            if self.update(True) == True:
                pass
            
            if (self.row_count * self.col_count) - len(self.stepped) - len(self.flagged) <= self.mine_count and len(self.flagged) == self.mine_count and len(self.stepped) == (self.row_count * self.col_count) - self.mine_count:
                print(f"Game {i + 1} won!")
                print(f"Stepped: {len(self.stepped)}")
                print(f"Flagged: {len(self.flagged)}")
            else:
                print(f"Game {i + 1} not solved!")
    
    
def main():
    game = Minesweeper(16, 30, 99)
    game.play(1)
    
    
        
if __name__ == "__main__":
    main()
        
                