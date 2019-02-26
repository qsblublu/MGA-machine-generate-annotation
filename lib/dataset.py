import re
import random
import torch
import os
from io import open
from config import config


class Lang(object):
    def __init__(self, name):
        self.name = name
        self.word2index = {config.UDW_token: 2}
        self.word2count = {config.UDW_token: 1}
        self.index2word = {0: 'SOS', 1: 'EOS', 2: 'UDW'}
        self.n_words = 3

    def addSentence(self, sentence):
        for word in sentence.split(' '):
            self.addWord(word)

    def addWord(self, word):
        if word not in self.word2count:
            '''
                We make the words defined by user to a unified ID
                If self.n_words > config.DICT_SIZE, the word is very possible defined by user
            '''
            
            if self.n_words > config.DICT_SIZE:
                self.word2count[config.UDW_token] += 1
            else:
                self.word2index[word] = self.n_words
                self.index2word[self.n_words] = word
                self.word2count[word] = 1
                self.n_words += 1
            '''
            self.word2index[word] = self.n_words
            self.index2word[self.n_words] = word
            self.word2count[word] = 1
            self.n_words += 1
            '''
        else:
            self.word2count[word] += 1


class DataSet(object):
    def __init__(self, input_lang, target_lang, path):
        self.input_lang = Lang(input_lang)
        self.target_lang = Lang(target_lang)
        self.path = path
        self.pairs = []

    # Filter the pairs to make len(annotation) and len(code) < config.MAX_LENGTH
    def filterPairs(self, pair):
        return len(pair[0].split(' ')) < config.MAX_LENGTH and len(pair[1].split(' ')) < config.MAX_LENGTH

    # Read from the file and change the data into [[code, annotation], [], ...] stored in self.pairs
    def readLang(self):
        lines = open(self.path, 'r', encoding='utf-8').read().strip().split('\n')
        for line in lines:
            pair = re.split(r' \*/ ', line.strip())
            if len(pair) == 2 and self.filterPairs(pair):
                self.pairs.append(list(reversed(pair)))

    # Add data in self.pairs in lang
    def prepareData(self):
        self.readLang()

        for pair in self.pairs:
            self.input_lang.addSentence(pair[0])
            self.target_lang.addSentence(pair[1])

        # Print the information of dataset
        print('Count the amount of training datas is: %d' % (len(self.pairs)))
        print('Count the amount of input_lang.n_words is: %d' % self.input_lang.n_words)
        print('Count the amount of target_lang.n_words is: %d' % self.target_lang.n_words)

    def tensorFromSentence(self, sentence, lang):
        indexes = []
        for word in sentence.split(' '):
            if word in lang.word2count:
                indexes.append(lang.word2index[word])
            else:
                indexes.append(lang.word2index[config.UDW_token])

        indexes.append(config.EOS_token)
        tensor = torch.tensor(indexes, dtype=torch.long).view(-1, 1)

        return tensor

    def randomTrainingData(self):
        pair = random.choice(self.pairs)

        input_tensor = self.tensorFromSentence(pair[0], self.input_lang)
        target_tensor = self.tensorFromSentence(pair[1], self.target_lang)

        return (input_tensor, target_tensor)

    def evaluateData(self):
        pair = random.choice(self.pairs)
        input_tensor = self.tensorFromSentence(pair[0], self.input_lang)

        return (pair[0], pair[1], input_tensor)


if __name__ == '__main__':
    dataset = DataSet(config.input_lang, config.target_lang, config.path)
    dataset.prepareData()
    print('Finished')