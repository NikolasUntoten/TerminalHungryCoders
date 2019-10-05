import gamelib
import json


class TestAlgo(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        self.grid_map = []
        j_start = 13
        j_end = 15
        for i in range(0, 14):
            self.grid_map.append([0]*(j_end - j_start))
            j_start -= 1
            j_end += 1
        j_start = 0
        j_end = 28
        for i in range(14, 28):
            self.grid_map.append([0]*(j_end - j_start))
            j_start += 1
            j_end -= 1

    def convert_list_index_to_board_index(self, y, x):
        row = 27 - y
        print(row)
        if y in range(0,14):
            col = 13 + x - y
        else:
            col = 13 + x - row
        return [col, row]


    def convert_board_index_to_list(self, col, row):
        y = 27 - row
        if y in range(0, 14):
            x = -13 + col + y
        else:
            x = -13 + col + row
        return [y, x]

    #def evaluate(self):
        #evaluate self defence
        #evaluate enemy defence
    #def evaluate_self_defence(self):


if __name__ == "__main__":
    algo = TestAlgo()
    


