import numpy as np
from morpion import Morpion_board

def encode_board(board):
    board_sate = board.current_board
    encoded = np.zeros([3,3,3]).astype(int)
    encoder_dict = {'O':0, 'X':1}
    for row in range(3):
        for col in range(3):
            if board_sate[row,col] != ' ':
                encoded[row, col, encoder_dict[board_sate[row, col]]] = 1
    if board.player == 1:
        encoded[:,:,2] = 1
    return encoded

def decode_board(encoded):
    decoded = np.zeros([3,3]).astype(str)
    decoded[decoded == '0.0'] = ' '
    decoder_dict = {0:'O', 1:'X'}
    for row in range(3):
        for col in range(3):
            for k in range(2):
                if encoded[row,col,k] == 1:
                    decoded[row,col] = decoder_dict[k]
    cboard = Morpion_board()
    cboard.current_board = decoded
    cboard.player = encoded[0,0,2]
    return cboard


if __name__ == '__main__':
    M = Morpion_board()
    M.draw_sign(1,1)
    M.draw_sign(2,2)
    M.draw_sign(0,1)

    l = encode_board(M)
    m = decode_board(l)
    print(M)
    #print(m.player)
    print(m)
    print(l[:,:,0])
