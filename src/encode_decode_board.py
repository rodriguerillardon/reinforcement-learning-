#!/usr/bin/env python

import numpy as np
from connect4 import Board

COLORS = [WHITE, BLACK] = [True, False]

def encode_board(board):
    board_state = board.squares
    encoded = np.zeros([6,6,3]).astype(int)
    encoder_dict = {1:0, 2:1}
    for row in range(6):
        for col in range(6):
            if board_state[row,col] != 0:
                encoded[row, col, encoder_dict[board_state[row,col]]] = 1
    if board.turn:
        encoded[:,:,2] = 0 # player to move
    else:
        encoded[:, :, 2] = 1
    return encoded

def decode_board(encoded):
    decoded = np.zeros([6,6])
    decoder_dict = {0:1, 1:2}
    for row in range(6):
        for col in range(6):
            for k in range(2):
                if encoded[row, col, k] == 1:
                    decoded[row, col] = decoder_dict[k]
    cboard = Board()
    cboard.squares = decoded
    cboard.turn = (encoded[0,0,2]==0)
    return cboard

if __name__ == "__main__":
    b = Board()
    b.play(1)
    l = encode_board(b)
    # print(l[:,:,0])
    # print(l[:, :, 1])
    # print(l[:, :, 2])
    m = decode_board(l)
    print(m.turn)
    print(decode_board(l))