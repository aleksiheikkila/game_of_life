import os
import time
import random


MARK = "*"
RANDOM_MARK_PROB = 0.05
SLEEP_DUR = 1

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

class Board():
    def __init__(self, num_rows=None, num_cols=None, 
                initial_state=None,
                random_init_prob=RANDOM_MARK_PROB, 
                mark=MARK, sleep_duration=SLEEP_DUR):

        """If initial_state is given, use that. 
        Else use a random initial state (called soup), 
        with random_init_prob probability of each position having a mark.
        
        Initial state is either
            - a list of strings of zeros and ones, where one string is one row (one=mark on that spot)
            - a str containing a path to a file that contains newline separated rows of 0s and 1s
            
        mark is just the single character used in the visualization
        sleep_duration controls the frequency of updates.
        """
        if initial_state is None and (num_rows is None or num_cols is None):
            raise ValueError("Must give either a initial state, or num_rows, num_cols")
        
        self.mark = mark
        self.sleep_duration = sleep_duration
        self.step_num = 0

        if initial_state is not None:
            # either a filepath str, or a list

            if isinstance(initial_state, str):
                print("Trying to read the initial state from file:", initial_state)
                with open(initial_state, "r") as f:
                    initial_state = f.read().splitlines()
            else:
                assert isinstance(initial_state, list)

            self.num_rows = len(initial_state)
            self.num_cols = len(initial_state[0])

            self.grid = {(rowno, colno): mark
                            for rowno, row in enumerate(initial_state) 
                            for colno, char in enumerate(row)
                            if char == "1"
                        }
            # some sanity checking on the dimensions
            # Assumption: if there are missing characters on e.g. some rows, 
            # the missing ones assumed to be empty positions
            assert max(self.grid.keys(), key=lambda x: x[0])[0] <= self.num_rows
            assert max(self.grid.keys(), key=lambda x: x[1])[1] <= self.num_cols


        else:  # do random init
            self.num_rows = num_rows
            self.num_cols = num_cols
            self.grid = {(rowno, colno): mark
                            for rowno in range(self.num_rows) for colno in range(self.num_cols)
                            if random.random() <= random_init_prob
                        }

    def __str__(self):
        s = "Round: {} - Number of cells alive: {}\n".format(self.step_num, len(self.grid))
        s += "=" * (self.num_cols + 2) + "\n"
        for rowno in range(self.num_rows):
            s += "|"
            for colno in range(self.num_cols):
                s += self.grid.get((rowno, colno), " ")
            s += "|\n"
        s += "=" * (self.num_cols + 2)
        return s

    def __repr__(self):
        return self.__str__()

    def get_adj_positions(self, pos):
        """pos is a rowno, colno tuple"""
        adjs = [(pos[0]+row_offset, pos[1]+col_offset) 
                for row_offset in (-1, 0, 1) for col_offset in (-1, 0, 1) 
                if not (row_offset == 0 and col_offset == 0)]

        return adjs


    def calc_num_marks(self, pos_list):
        return sum(1 for pos in pos_list if self.grid.get(pos) == self.mark)

    def calc_num_adj_marks(self, pos):
        adjs = self.get_adj_positions(pos)
        return self.calc_num_marks(adjs)


    def step(self):
        new_grid = self.grid.copy()
        self.step_num += 1

        for rowno in range(self.num_rows):
            for colno in range(self.num_cols):
                pos = (rowno, colno)
                alive = True if self.grid.get(pos) is not None else False
                adj_marks = self.calc_num_adj_marks(pos)

                # then apply the rules
                if alive:
                    if adj_marks <= 1:
                        # underpopulation -> dies
                        del new_grid[pos]
                    #elif adj_marks in (2, 3):
                    #    # stays alive
                    #    pass
                    elif adj_marks > 3:
                        # overpopulation -> dies
                        del new_grid[pos]
                else:  # dead
                    if adj_marks == 3:
                        # becomes alive
                        new_grid[pos] = self.mark

        self.grid = new_grid

    def run_forever(self):
        clear_console()
        print(self)
        while True: 
            time.sleep(self.sleep_duration)
            self.step()
            clear_console()
            print(self)

if __name__ == "__main__":
    # define a board, and the call run_forever()

    #b = Board(30, 100, random_init_prob=.2, sleep_duration=.5)  # random soup
    #b = Board(initial_state="./initial_states/toad.txt", sleep_duration=.5)
    b = Board(initial_state="./initial_states/gosper_glider_gun.txt", sleep_duration=.3)
    b.run_forever()
    