import json
import logging
from random import shuffle
logger = logging.getLogger(__name__)


class CardStack(object):
    def __init__(self):
        self.stack = []
        self.availableCards = []

    def _decode(self, filename):
        logger.info('decoding file : ' + filename)
        with open(filename, 'r') as fd:
            data = json.load(fd)
            logger.info('nb entry : ' + str(len(data)))
            return data

    def _shuffle(self):
        self.availableCards = range(0, len(self.stack))
        shuffle(self.availableCards)

    def pick(self):
        if len(self.availableCards) == 0:
            self._shuffle()
        return self.stack[self.availableCards.pop()]

    def __len__(self):
        return len(self.stack)

class MultiStack(CardStack):
    def __init__(self):
        super(MultiStack, self).__init__()

    def _shuffle(self):
        self.availableCards = []
        index = 0
        for i in self.stack:
            self.availableCards.extend([index] * len(i))
        shuffle(self.availableCards)

    def addFiles(self, files, DeckClass):
        ''' add multiple files to a MultiStack
        :param files list of filename to add
        :param DeckClass base clase used to parse file

        DeckClass should have a pick method that return a card
        DeckClass should take the filename under the construtor
        '''
        for i in files:
            self.stack.append(DeckClass(i))

    def pick(self):
        return super(MultiStack, self).pick().pick()

class BlackCard(object):
    def __init__(self, value, pick):
        self.value = value
        self.pick = pick

    def printSentance(self, value):
        '''
        return card filled with white proposition
        '''
        if len(value) != self.pick:
            raise ValueError('bad number of white card, need ' + str(self.pick))
        #cards can have pick-1 filling token, we should manage this case
        sentanceNormalized = self.value + ' {}'
        valueNormalized = list(value)
        valueNormalized.append('')
        return sentanceNormalized.format(*valueNormalized)

    def printEmpty(self):
        param = ['____']*self.pick
        return self.printSentance(param)

class WhiteCard(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class BlackCardStack(CardStack):
    def __init__(self, filename):
        super(BlackCardStack, self).__init__()
        data = self._decode(filename)
        entryCount = -1
        for i in data:
            entryCount += 1
            #check entry
            if not i.has_key('type') or i['type'] != 'Question':
                logger.error('bad kind of question, skip entry {0}', entryCount)
                continue
            if not i.has_key('value'):
                logger.error('no value, skip entry {0}', entryCount)
                continue
            if not i.has_key('pick') or not isinstance(i['pick'], (int, long)):
                logger.debug('pick type ' + repr(type(i['pick'])))
                logger.error('bad pick value, skip')
                continue
            self.stack.append(BlackCard(i['value'], i['pick']))

class WhiteCardStack(CardStack):
    def __init__(self, filename):
        super(WhiteCardStack, self).__init__()
        data = self._decode(filename)
        entryCount = -1
        for i in data:
            entryCount += 1
            if not i.has_key('type') or i['type'] != 'Answer':
                logger.error('bad kind of responde, skip entry {0}', entryCount)
                continue
            if not i.has_key('value'):
                logger.error('no value, skip entry {0}'.entryCount)
                continue
            self.stack.append(WhiteCard(i['value']))
