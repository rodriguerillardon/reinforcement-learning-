#!/usr/bin/env python

import ast
import copy
import os.path

import encode_board as ed
import numpy as np
import torch
from monte_Carlo_Tree import UCT_search, do_decode_n_move_pieces, get_policy
from neural_net import ConnectNet

from morpion import Morpion_board as cboard


def play_game(net):
    # Asks human what he/she wanna play as
    white = None;
    black = None
    while (True):
        play_as = input("What do you wanna play as? (\"O\"/\"X\")? Note: \"O\" starts first, \"X\" starts second\n")
        if play_as == "O":
            black = net;
            break
        elif play_as == "X":
            white = net;
            break
        else:
            print("I didn't get that.")
    current_board = cboard()
    checkmate = False
    dataset = []
    value = 0;
    t = 0.1;
    moves_count = 0
    while checkmate == False and current_board.actions() != []:
        if moves_count <= 5:
            t = 1
        else:
            t = 0.1
        moves_count += 1
        dataset.append(copy.deepcopy(ed.encode_board(current_board)))
        print(current_board.board);
        print(" ")
        if current_board.player == 0:
            if white != None:
                print("AI is thinking........")
                root = UCT_search(current_board, 777, white, t)
                policy = get_policy(root, t)
                current_board = do_decode_n_move_pieces(current_board, \
                                                        int(np.random.choice(np.array(range(9)), \
                                                                             p=policy)))
            else:
                while (True):
                    row, col = ast.literal_eval(
                        input("Which tuple do you wanna drop your piece? (Enter row, column as [(1,3),(1,3)])\n"))
                    current_board.draw_sign([int(row) - 1, int(col) - 1])
                    break
        elif current_board.player == 1:
            if black != None:
                print("AI is thinking.............")
                root = UCT_search(current_board, 333, black, t)
                policy = get_policy(root, t)
                current_board = do_decode_n_move_pieces(current_board, \
                                                        int(np.random.choice(np.array(range(9)), \
                                                                             p=policy)))
            else:
                while (True):
                    row, col = ast.literal_eval(
                        input("Which tuple do you wanna drop your piece? (Enter row, column as [(1,3),(1,3)])\n"))
                    current_board.draw_sign([int(row) - 1, int(col) - 1])
                    break
        # decode move and move piece(s)
        if current_board.check_winner() == True:  # someone wins
            if current_board.player == 0:  # black wins
                value = -1
            elif current_board.player == 1:  # white wins
                value = 1
            checkmate = True
    dataset.append(ed.encode_board(current_board))
    print(current_board.current_board);
    print(" ")
    if value == -1:
        if play_as == "O":
            dataset.append(f"AI as black wins");
            print("YOU LOSE!!!!!!!")
        else:
            dataset.append(f"Human as black wins");
            print("YOU WIN!!!!!!!")
        return "black", dataset
    elif value == 1:
        if play_as == "O":
            dataset.append(f"Human as white wins");
            print("YOU WIN!!!!!!!!!!!")
        else:
            dataset.append(f"AI as white wins");
            print("YOU LOSE!!!!!!!")
        return "white", dataset
    else:
        dataset.append("Nobody wins");
        print("DRAW!!!!!")
        return None, dataset


if __name__ == "__main__":
    best_net = "tictactoe_iter1.pth.tar"
    best_net_filename = os.path.join("./model_data/", \
                                     best_net)
    best_cnet = ConnectNet()
    # cuda = torch.cuda.is_available()
    # if cuda:
    #     best_cnet.cuda()
    best_cnet.eval()
    checkpoint = torch.load(best_net_filename)
    best_cnet.load_state_dict(checkpoint['state_dict'])
    play_again = True
    while (play_again == True):
        play_game(best_cnet)
        while (True):
            again = input("Do you wanna play again? (Y/N)\n")
            if again.lower() in ["y", "n"]:
                if again.lower() == "n":
                    play_again = False;
                    break
                else:
                    break
