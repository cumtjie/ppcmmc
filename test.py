import codecs
import sys

class Markov(object):

	table = None

	def __init__(self):
		self.table = {}

	def addState(self, state):
		if not state in self.table:
			self.table[state] = {}

	def setRelation(self, start, end, weight = 1):
		if self.hasState(start) and self.hasState(end):
			self.table[start][end] = weight

	def hasState(self, state):
		return state in self.table

	def getRelationWeigth(self, start, end):
		if self.hasState(start) and self.hasState(end):
			if end in self.table[start]:
				return self.table[start][end]
			else:
				return 0

	def increaseRelation(self, start, end, weigth = 1):
		if self.hasState(start) and self.hasState(end):
			self.setRelation(start, end, self.getRelationWeigth(start, end) + weigth)
		else:
			self.addState(start)
			self.addState(end)
			self.increaseRelation(start, end, weigth)

	def next(self, state):
		maxWeight = 0.0
		chosen = -1
		if state in self.table:
			candidatesWeights = list(self.table[state].values())
			for i in range(len(candidatesWeights)):
				if candidatesWeights[i] > maxWeight:
					chosen = i
					maxWeight = candidatesWeights[i]
		if chosen == -1:
			return None
		return list(self.table[state].keys())[chosen]

	def nextStates(self, state):
		if self.hasState(state):
			states = sorted(self.table[state].keys(), key=lambda key:self.table[state][key])
			states.reverse()
			return states
		else:
			return None
	
	def train(self, pairList):
		for pair in pairList:
			self.increaseRelation(pair[0], pair[1])


class PPM(object):

	mWord = None
	mContext = None
	lastWord = None
	
	def __init__(self):
		self.mWord = Markov()
		self.mContext = Markov()
		
	def logic(self, i, mContext, m):
		if self.lastWord is not None:
			if mContext.hasState(self.lastWord):
				result = processInputForContext(i, self.lastWord)
				mContext.increaseRelation(self.lastWord, result)
				self.lastWord = result
			else:
				result = processInput(i)
				mContext.train([(self.lastWord, result)])
				m.train(TextHandler.getPairsCompletions(result))
				self.lastWord = result
		else:
			self.lastWord = processInput(i)
			if False in [m.hasState(pair[0]) for pair in TextHandler.getPairsCompletions(self.lastWord)]:
				m.train(TextHandler.getPairsCompletions(self.lastWord))
#		text += ' ' + lastWord
		return self.lastWord

class TextHandler(object):
	
	@staticmethod
	def getPairsCompletions(text, separator=' '):
		pairList = []
		for word in text.split(separator):
			for i in range(len(word)-1):
				pairList.append((word[:i+1], word))
		return pairList

	@staticmethod
	def getPairsContext(text, separator=' '):
		pairList = []
		lastWord = None
		for word in text.split(separator):
			if lastWord is not None:
				pairList.append((lastWord, word))
			lastWord = word
		return pairList

	@staticmethod
	def getText(file):
		text = None
		f = codecs.open(file, 'r')
		text = f.read()
		f.close()
		return text

	@staticmethod
	def treatText(text, ignore='.,[]()!?/\\:;@#$%\"\'*&^~{}<>\n', separator=' '):
		treatedText = text
		for symbol in ignore:
			treatedText = treatedText.replace(symbol, separator)
		tempList = treatedText.split(separator)
		if '' in tempList:
			tempList.remove('')
		return separator.join(tempList)

text = TextHandler.getText("war&peace2.txt")
treatedText = TextHandler.treatText(text)

m = Markov()
pairs = TextHandler.getPairsCompletions(treatedText)
m.train(pairs)

mContext = Markov()
pairsContext = TextHandler.getPairsContext(treatedText)
mContext.train(pairsContext)

ppm = PPM()

lastWord = None
text = ''

def select(list, max = 5):
	print("\nPossible values: ")
	limit = min(len(list), max)
	for count in range(limit):
		print(count, list[count])
	print("any other number cancels selection")
	selected = input((" value? "))
	if selected in range(limit):
		return list[selected]
	return None

def processInput(i):
	nextWords = m.nextStates(i)
	if nextWords is not None:
		if len(nextWords) > 0:
			selected = select(nextWords)
			if selected is not None:
				return selected
	return i

def processInputForContext(i, c):
	contexts = [context for context in mContext.nextStates(c) if context.startswith(i) and not context == i ]
	if len(contexts) > 0:
		print("*")
		selected = select(contexts)
		if selected is not None:
			return selected
	else:
		return processInput(i)
	return i

while True:
	i = raw_input('\n' + text + "\n(# = clean, @ = status) > ")
	if i == '#':
		text = ''
		ppm.lastWord = None
	elif i == '@':
		print 'context: ', mContext.table
		print 'word: ', m.table
		print 'lastWord: ', ppm.lastWord
	else:
		for word in i.split(' '):
			result = ppm.logic(word, mContext, m)
			text += ' ' + result
