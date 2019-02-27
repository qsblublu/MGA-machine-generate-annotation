import torch
import torch.nn as nn
import torch.nn.functional as F


class EncoderRNN(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(EncoderRNN, self).__init__()
        
        self.hidden_size = hidden_size

        # The nn.Embedding is a lookup table (actually a matrix[input_size][hidden_size])
        self.embedding = nn.Embedding(input_size, hidden_size)
        '''
        nn.GRU is a type of RNN
        Args:
            input_size
            hidden_size
            num_layers(default: 1)
        Inputs:
            input: the size of input is (seq_len, batch, input_size)
            h0: the size of h0 is (num_layers * num_directions, batch, hidden_size)
        Outputs:
            output: the size of output is (seq_len, batch, num_directions * hidden_size)
            hn: the size of hn is the same as h0
        '''
        self.gru = nn.GRU(hidden_size, hidden_size)

    def forward(self, input, hidden):
        # The size of sembedded is (1, 1, self.hidden_size)
        embedded = self.embedding(input).view(1, 1, -1)
        output, hidden = self.gru(embedded, hidden)

        # The size of output and hidden is (1, 1, self.hidden_size)
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size)


class AttnDecoderRNN(nn.Module):
    def __init__(self, hidden_size, output_size, max_length, dropout_p=0.1):
        super(AttnDecoderRNN, self).__init__()

        self.hidden_size = hidden_size
        self.max_length = max_length

        self.embedding = nn.Embedding(output_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size)
        self.attn = nn.Linear(hidden_size * 2, max_length)
        self.attn_combine = nn.Linear(hidden_size * 2, hidden_size)
        self.dropout = nn.Dropout(p=dropout_p)
        self.out = nn.Linear(hidden_size, output_size)

    def forward(self, input, hidden, encoder_outputs):
        # The size of embedded is (1, 1, self.hidden_size)
        embedded = self.embedding(input).view(1, 1, -1)
        embedded = self.dropout(embedded)

        # The size of attn_weights is (1, self.max_length)
        attn_weights = F.softmax(self.attn(torch.cat((embedded[0], hidden[0]), dim=1)), dim=1)
        '''
        torch.bmm
            input1, input2 must be a 3-D tensor
            input1 is b * n * m, input2 is b * m * p
            output is b * n * p
        So, in follow case, the size of attn_weights.unsqueeze(0) is (1, 1, self.max_length)
            the size of encoder_outputs.unsqueeze(0) is (1, self.max_length, self.hidden_size)
        '''
        # The size of attn_applied is (1, 1, self.hidden_size)
        attn_applied = torch.bmm(attn_weights.unsqueeze(0), encoder_outputs.unsqueeze(0))

        # The size of follow output is (1, self.hidden_size * 2)
        output = torch.cat((embedded[0], attn_applied[0]), dim=1)
        # The size of follow output is (1, 1, self.hidden_size)
        output = self.attn_combine(output).unsqueeze(0)
        output = F.relu(output)
        output, hidden = self.gru(output, hidden)
        output = F.log_softmax(self.out(output[0]), dim=1)

        # The size of output is (1, 1, self.output_size)
        # The size of hidden is (1, 1, self.hidden_size)
        return output, hidden, attn_weights

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size)