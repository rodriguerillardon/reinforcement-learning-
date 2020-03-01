from neural_net import ConnectNet, AlphaLoss, board_data
import os
import pickle
import datetime
import numpy as np
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.nn.utils import clip_grad_norm_
import matplotlib.pyplot as plt
import logging

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', \
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logger = logging.getLogger(__file__)

def save_as_pickel(filename, data):
    complete_name = os.path.join("./model_data/", filename)
    with open(complete_name, 'wb') as output:
        pickle.dump(data, output)

def load_pickle(filename):
    complete_name = os.path.join("./model_data/", filename)
    with open(complete_name, 'rb') as pkl_file:
        data = pickle.load(pkl_file)
    return data

def load_state(net, optimizer, scheduler, args, iteration, new_optim_state=True):
    base_path = "./model-data/"
    checkpoint_path = os.path.join(base_path, "%s_iter%d.pth.tar" % (args.neural_net_name, iteration))
    start_epoch, checkpoint = 0, None
    if os.path.isfile(checkpoint_path):
        checkpoint = torch.load(checkpoint_path)
    if checkpoint != None:
        if (len(checkpoint) == 1) or (new_optim_state == True):
            net.load_state_dict(checkpoint['state_dict'])
            logger.info("Loaded checkpoint model %s." % checkpoint_path)
        else:
            start_epoch = checkpoint['epoch']
            net.load_state_dict(checkpoint['state_dict'])
            optimizer.load_state_dict(checkpoint['optimizer'])
            scheduler.load_state_dict(checkpoint['scheduler'])
            logger.info('Loaded checkpoint model %s, and optimizer, scheduler.' % checkpoint_path)
    return start_epoch

def load_results(iteration):
    losses_path = "./model_data/losses_per_epoch_iter%d.pkl" % iteration
    if os.path_isfile(losses_path):
        losses_per_epoch = load_pickle("losses_per_epoch_iter%d.pkl" % iteration)
        logger.info("Loaded results buffer")
    else:
        losses_per_epoch = []
    return losses_per_epoch

def train(net, dataset, optimizer, scheduler, start_epoch, cpu, args, iteration):
    torch.manual_seed(cpu)
    cuda = torch.cuda.is_available()
    net.train()
    criterion = AlphaLoss()

    train_set = board_data(dataset)
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True, num_workers=0, pin_memory=False)
    losses_per_epoch = load_results(iteration + 1)

    logger.info("Starting training process...")
    update_size = len(train_loader)//10
    print("Update step size: %d" % update_size)
    for epoch in range(start_epoch, args.num_epochs):
        total_loss = 0.0
        losses_per_batch = []
        for i, data in enumerate(train_loader, 0):
            state, policy, value = data
            state = state.float()
            policy = policy.float()
            value = value.float()
            if cuda:
                state = state.cuda()
                policy = policy.cuda()
                value = value.cuda()
            policy_pred, value_pred = net(state)
            loss = criterion(value_pred[:,0], value, policy_pred, policy)
            loss = loss/args.gradient_acc_steps
            loss.backward()
            clip_grad_norm_(net.parameters(), args.max_norm)
            if (epoch % args.gradient_acc_steps) == 0:
                optimizer.step()
                optimizer.zero_grad()

            total_loss += loss.item()
            if i % update_size == (update_size - 1):
                losses_per_batch.append(args.gradient_acc_steps*total_loss/update_size)
                print('[Iteration %d] Process ID: %d [Epoch: %d, %5d/ %d points] total loss per batch: %.3f' %
                      (iteration, os.getpid(), epoch + 1, (i + 1) * args.batch_size, len(train_set),
                       losses_per_batch[-1]))
                print("Policy (actual, predicted):", policy[0].argmax().item(), policy_pred[0].argmax().item())
                print("Policy data:", policy[0]);
                print("Policy pred:", policy_pred[0])
                print("Value (actual, predicted):", value[0].item(), value_pred[0, 0].item())
                print(" ")
                total_loss = 0.0

        scheduler.step()
        if len(losses_per_batch) >=1:
            losses_per_epoch.append(sum(losses_per_batch)/len(losses_per_batch))
        if (epoch % 2) == 0:
            save_as_pickel("losses_per_epoch_iter%d.pkl" % (iteration + 1), losses_per_epoch)
            torch.save({
                'epoch' : epoch +1,
                'state_dict': net.state_dict(),
                'optimizer' : optimizer.state_dict(),
                'scheduler' : scheduler.state_dict()
            }, os.path.join('./model_data/', "s_iter%d.pth.tar" % (args.neural_net_name, (iteration+1))))

    logger.info('Finished Training!')
    fig = plt.figure()
    ax = fig.add_subplot(222)
    ax.scatter([e for e in range(start_epoch, (len(losses_per_epoch) + start_epoch))], loss)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss per batch')
    ax.set_title('loss vs Epoch')
    plt.savefig(os.path.join("./model_data", 'Loss_vs_Epoch_iter%d_%s.png' % ((iteration + 1), datetime.datetime.today().strftime("%Y-%m-%d"))))
    plt.show()

def train_connectnet(args, iteration, new_optim_state):
    logger.info("Loading training data...")
    data_path = "./datasets/iter_%d/" % iteration
    datasets = []
    for idx, file in enumerate(os.listdir(data_path)):
        filename = os.path.join(data_path, file)
        with open(filename, 'rb') as fo:
            datasets.extend(pickle.load(fo, encoding='bytes'))
    datasets = np.array(datasets)
    logger.info("Loaded data from %s." % data_path)

    net = ConnectNet()
    cuda = torch.cuda.is_available()
    if cuda:
        net.cuda()
    optimizer = optim.Adam(net.parameters(), lr=args.lr, betas=(0.8, 0.999))
    scheduler = optim.lr_scheduler.MultiStepLR(optimizer, milestones=[50,100,150, 200, 250, 300, 400], gamma=0.77)
    start_epoch = load_state(net, optimizer, scheduler, args, iteration, new_optim_state)

    train(net, datasets, optimizer, scheduler, start_epoch, 0, args, iteration)




