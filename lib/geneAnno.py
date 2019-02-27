import torch
import sys
import re
from config import config
from dataset import DataSet
from model import EncoderRNN, AttnDecoderRNN


def evaluate(encoder, decoder, input_tensor, output_lang, hidden_size=config.hidden_size):
    with torch.no_grad():
        encoder_hidden = encoder.initHidden()

        input_length = input_tensor.size(0)

        encoder_outputs = torch.zeros(config.MAX_LENGTH, hidden_size)
        
        for ei in range(input_length):
            encoder_output, encoder_hidden = encoder(input_tensor[ei], encoder_hidden)
            encoder_outputs[ei] = encoder_output[0, 0]

        decoder_hidden = encoder_hidden
        decoder_input = torch.tensor([[config.SOS_token]])
        output_sentence = []
        
        for di in range(config.MAX_LENGTH):
            decoder_output, decoder_hidden, decoder_attention = decoder(decoder_input, decoder_hidden, encoder_outputs)
            topv, topi = decoder_output.data.topk(1)
            if topi.item() == config.EOS_token:
                break
            else:
                output_sentence.append(output_lang.index2word[topi.item()])
            decoder_input = topi.squeeze().detach()

    return ' '.join(output_sentence)



dataset = DataSet(config.input_lang, config.target_lang, config.path)
dataset.prepareData()
encoder = EncoderRNN(dataset.input_lang.n_words, config.hidden_size)
decoder = AttnDecoderRNN(config.hidden_size, dataset.target_lang.n_words, config.MAX_LENGTH)
encoder.load_state_dict(torch.load(config.curPath + 'annotation_encoder.pth', map_location=config.eval_device))
decoder.load_state_dict(torch.load(config.curPath + 'annotation_decoder.pth', map_location=config.eval_device))

code = sys.argv[1]
#code = input()

input_tensor = dataset.tensorFromSentence(code, dataset.input_lang)
output_annotation = evaluate(encoder, decoder, input_tensor, dataset.target_lang)
print(output_annotation)
    