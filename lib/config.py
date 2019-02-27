import torch
import os


class config(dict):
    # Special identiter
    SOS_token = 0
    EOS_token = 1
    UDW_token = 2

    # Being involved with training
    hidden_size = 256
    input_lang = 'code'
    target_lang = 'annotation'
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    eval_device = 'cpu'
    LR = 0.01
    PRINT_EVERY = 1000
    n_iters = 10000
    dropout_p = 0.5
    teacher_forcing_ratio = 0.5

    # Being involved with dataset
    curPath = os.path.abspath('.')
    path = curPath + 'data.txt'
    MAX_LENGTH = 70
    batch_size = 500
    DICT_SIZE = 7000