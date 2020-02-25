import numpy as np

class Morpion_board():
    def __init__(self):
        self.board = np.zeros([3, 3]).astype(str)
        self.board[self.board == "0.0"] = ' '
        self.player = 0
        self.current_board = self.board

    def draw_sign(self, row, column):
        if self.current_board[row, column] != ' ':
            return ('Invalid position')
        else:
            if self.player == 0:
                self.current_board[row, column] = 'O'
                self.player = 1
            elif self.player == 1:
                self.current_board[row, column] = 'X'
                self.player = 0

    def check_winner(self):
        if self.player == 0:
            # on essaye les 6 points qui permettent de gagner (pour le joueur 0)
            if self.current_board[0, 0] == 'O':
                if (self.current_board[0, 0] == 'O' and self.current_board[0, 1] == 'O' and self.current_board[
                    0, 2] == 'O'):
                    return True
                elif (self.current_board[0, 0] == 'O' and self.current_board[1, 0] == 'O' and self.current_board[
                    2, 0] == 'O'):
                    return True
                elif (self.current_board[0, 0] == 'O' and self.current_board[1, 1] == 'O' and self.current_board[
                    2, 2] == 'O'):
                    return True
            if self.current_board[1, 1] == 'O':
                if (self.current_board[0, 1] == 'O' and self.current_board[1, 1] == 'O' and self.current_board[
                    2, 1] == 'O'):
                    return True
                elif (self.current_board[1, 0] == 'O' and self.current_board[1, 1] == 'O' and self.current_board[
                    1, 2] == 'O'):
                    return True
                elif (self.current_board[2, 0] == 'O' and self.current_board[1, 1] == 'O' and self.current_board[
                    0, 2] == 'O'):
                    return True
            if self.current_board[2, 2] == 'O':
                if (self.current_board[0, 2] == 'O' and self.current_board[1, 2] == 'O' and self.current_board[
                    2, 2] == 'O'):
                    return True
                elif (self.current_board[2, 0] == 'O' and self.current_board[2, 1] == 'O' and self.current_board[
                    2, 2] == 'O'):
                    return True

        if self.player == 1:
            # on essaye les 6 points qui permettent de gagner (pour le joueur 1)
            if self.current_board[0, 0] == 'X':
                if (self.current_board[0, 0] == 'X' and self.current_board[0, 1] == 'X' and self.current_board[
                    0, 2] == 'X'):
                    return True
                elif (self.current_board[0, 0] == 'X' and self.current_board[1, 0] == 'X' and self.current_board[
                    2, 0] == 'X'):
                    return True
                elif (self.current_board[0, 0] == 'X' and self.current_board[1, 1] == 'X' and self.current_board[
                    2, 2] == 'X'):
                    return True
            if self.current_board[1, 1] == 'X':
                if (self.current_board[0, 1] == 'X' and self.current_board[1, 1] == 'X' and self.current_board[
                    2, 1] == 'X'):
                    return True
                elif (self.current_board[1, 0] == 'X' and self.current_board[1, 1] == 'X' and self.current_board[
                    1, 2] == 'X'):
                    return True
                elif (self.current_board[2, 0] == 'X' and self.current_board[1, 1] == 'X' and self.current_board[
                    0, 2] == 'X'):
                    return True
            if self.current_board[2, 2] == 'X':
                if (self.current_board[0, 2] == 'X' and self.current_board[1, 2] == 'X' and self.current_board[
                    2, 2] == 'X'):
                    return True
                elif (self.current_board[2, 0] == 'X' and self.current_board[2, 1] == 'X' and self.current_board[
                    2, 2] == 'X'):
                    return True
        return False

    def actions(self):  # returns all possible moves
        acts = []
        for row in range(3):
            for col in range(3):
                if self.current_board[row, col] == ' ':
                    acts.append([row, col])
        return acts

    def __repr__(self):
        return(f"""{self.board}""")

if __name__ == "__main__":
    M = Morpion_board()
    M.draw_sign(1,1)
    M.draw_sign(2,2)
    M.draw_sign(2, 1)
    M.draw_sign(0, 0)
    M.draw_sign(0, 1)
    print(M)
    print(M.actions())
    print(M.check_winner())

