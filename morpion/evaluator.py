import os.path
import torch
import numpy as np
from neural_net import ConnectNet
from morpion import Morpion_board as cboard
import encode_board as ed
import copy
from monte_Carlo_Tree import UCT_search, do_decode_n_move_pieces, get_policy
import pickle
import torch.multiprocessing as mp
import datetime
import logging

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', \
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logger = logging.getLogger(__file__)

def save_as_pickle(filename, data):
    complete_name = os.path.join("./evaluator_data/", filename)
    with open(complete_name, 'wb') as output:
        pickle.dump(data, output)

def load_pickle(filename):
    complete_name = os.path.join("./evaluator_data/", filename)
    with open(complete_name, 'rb') as pkl_file:
        data = pickle.load(pkl_file)
    return data

class arena():
    def __init__(self, current_cnet, best_cnet):
        self.current = current_cnet
        self.best = best_cnet


    def play_round(self):
        logger.info("starting game round...")
        if np.random.uniform(0,1) <= 0.5:
            white = self.current
            black = self.best
            w = "current"
            b = "best"
        else:
            white = self.best
            black = self.current
            w = 'best'
            b= 'current'
        current_board = cboard()
        checkmate = False
        dataset = []
        value = 0
        t = 0.1
        while checkmate == False and current_board.actions() != []:
            dataset.append(copy.deepcopy(ed.encode_board(current_board)))
            print("")
            print(current_board.current_board)
            if current_board.player == 0:
                root = UCT_search(current_board, 50, white, t)
                policy = get_policy(root, t)
                print("Policy : ", policy, "white = %s" %(str(w)))
            elif current_board.player == 1:
                root = UCT_search(current_board, 50, black, t)
                policy = get_policy(root, t)
                print("Policy : ", policy, "black = %s" % (str(b)))
            current_board = do_decode_n_move_pieces(current_board, np.random.choice(np.array([0,1,2,3,4,5,6]), p = policy))
            if current_board.check_winner() == True:
                if current_board.player == 0:
                    value = -1
                elif current_board.player == 1:
                    value = 1
                checkmate = True
        dataset.append(ed.encode_board(current_board))
        if value == -1:
            dataset.append(f"{b} as circle wins")
            return b, dataset
        elif value == 1:
            dataset.append(f"{w} as cross wins")
            return w, dataset
        else:
            dataset.append('Nobody wins')
            return None, dataset
    def evaluate(self, num_games, cpu):
        current_wins = 0
        logger.info("[CPU %d]: Starting games..." % cpu)
        for i in range(num_games):
            with torch.no_grad():
                winner, dataset = self.play_round()
                print("%s wins!" % winner)
            if winner == 'current':
                current_wins += 1
            save_as_pickle("evaluate_net_dataset_cpu%i_%i_%s_%s" % (cpu,i,datetime.datetime.today().strftime("%Y-%m-%d"),\
                                                                     str(winner)),dataset)
        print("Current_net wins ratio %.5f" % (current_wins/num_games))
        save_as_pickle("wins_cpu_%i"  % (cpu),\
                                             {"best_win_ratio": current_wins/num_games, "num_games":num_games})
        logger.info("[CPU %d]: Finished arena games!" % cpu)

def fork_process(arena_obj, num_games, cpu):
    arena_obj.evaluate(num_games, cpu)

def evaluate_nets(args, iteration_1, iteration_2):
    logger.info('Loading nets...')
    current_net = "%s_iter%d.pth.tar" % (args.neural_net_name, iteration_2)
    best_net = "%s_iter%d.pth.tar" % (args.neural_net_name, iteration_1)
    current_net_filename = os.path.join("./model_data/", current_net)
    best_net_filename = os.path.join("./model_data/", best_net)

    logger.info('Current net: %s' % current_net)
    logger.info("Previous (Best net: %s" %best_net)

    current_cnet = ConnectNet()
    best_cnet = ConnectNet()
    cuda = torch.cuda.is_available()
    if cuda:
        current_cnet.cuda()
        best_cnet.cuda()

    if not os.path.isir("./evaluator_data/"):
        os.mkdir("evaluator_data")

    if args.MCTS_num_processes > 1:
        mp.set_start_method("spawn", force=True)

        current_cnet.share_memory()
        best_cnet.share_memory()
        current_cnet.eval()
        best_cnet.eval()

        checkpoint = torch.load(current_net_filename)
        current_cnet.load_state_dict(checkpoint['state_dict'])
        checkpoint = torch.load(best_net_filename)
        best_cnet.load_state_dict(checkpoint['state_dict'])

        processes = []
        if args.MCTS_nim_processes > mp.cpu_count():
            num_processes = mp.cpu_count()
            logger.info("Required number of processes exceed number of CPUs! Setting MCTS_num_processes to %d" % num_processes)
        else:
            num_processes = args.MCTS_num_processes
        logger.info("Spawning %d processes..." % num_processes)
        with torch.no_grad():
            for i in range(num_processes):
                p = mp.Process(target=fork_process,args=(arena(current_cnet,best_cnet), args.num_evaluator_games, i))
                p.start()
                processes.append(p)
            for p in processes:
                p.join()

        wins_ratio = 0.0
        for i in range(num_processes):
            stats = load_pickle("wins_cpu_%i" % (i))
            wins_ratio += stats['best_win_ratio']
        wins_ratio = wins_ratio/num_processes
        if wins_ratio >= 0.55:
            return iteration_2
        else :
            return iteration_1

    elif args.MCTS_num_processes == 1:
        current_cnet.eval()
        best_cnet.eval()
        checkpoint = torch.load(current_net_filename)
        current_cnet.load_state_dict(checkpoint['state_dict'])
        checkpoint = torch.load(best_net_filename)
        best_cnet.load_state_dict(checkpoint['state_dict'])
        arena1 = arena(current_cnet=current_cnet, best_cnet=best_cnet)
        arena1.evaluate(num_games=args.num_evaluator_games, cpu=0)

        stats = load_pickle('wins_cpu_%i' % (0))
        if stats.best_win_ratio >= 0.55:
            return iteration_2
        else:
            return iteration_1

