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

	def nextLeaf(self, state):
		tempState = state
		result = self.next(state)
		while result:
			tempState += result
			result = m.next(tempState)
		return tempState

	def nextLeafs(self, state):
		if self.hasState(state):
#			return [self.nextLeaf(state+leaf) for leaf in list(self.table[state].keys())]
			leafs = sorted(self.table[state], key=lambda key:self.table[state])
			leafs.reverse()
			return leafs
		else:
			return None

	def nextStates(self, state):
		if self.hasState(state):
#			return list(self.table[state].keys())
			states = sorted(self.table[state], key=lambda key:self.table[state])
			states.reverse()
			return states
		else:
			return None

def train(markov, pairList):
	for pair in pairList:
		markov.increaseRelation(pair[0], pair[1])

def getPairs(text, separator=' '):
	pairList = []
	symbol = ''
	for i in range(len(text)):
		if i+1 < len(text):
			if text[i+1] != separator and text[i] != separator:
				if symbol == '':
					symbol = text[i]
					pairList.append((symbol, text[i+1]))
					symbol += text[i+1]
				else:
					pairList.append((symbol, text[i+1]))
					symbol += text[i+1]
			else:
				symbol = ''
	return pairList

def getPairsCompletions(text, separator=' '):
	pairList = []
	for word in text.split(separator):
		for i in range(len(word)-1):
			pairList.append((word[:i+1], word[i+1:]))
	return pairList

def getPairsCompletions2(text, separator=' '):
	pairList = []
	for word in text.split(separator):
		for i in range(len(word)-1):
			pairList.append((word[:i+1], word))
	return pairList

def getPairsContext(text, separator=' '):
	pairList = []
	lastWord = None
	for word in text.split(separator):
		if lastWord is not None:
			pairList.append((lastWord, word))
		lastWord = word
	return pairList

def getText(file):
	text = None
	f = codecs.open(file, 'r')
	text = f.read()
	f.close()
	return text

def treatText(text, ignore='.,[]()!?/\\:;@#$%\"\'*&^~{}<>\n', separator=' '):
	treatedText = text
	for symbol in ignore:
		treatedText = treatedText.replace(symbol, separator)
	tempList = treatedText.split(separator)
	if '' in tempList:
		tempList.remove('')
	return separator.join(tempList)

#text = getText("war&peace2.txt")
#treatedText = treatText(text)

m = Markov()
#pairs = getPairsCompletions2(treatedText)
#train(m, pairs)

mContext = Markov()
#pairsContext = getPairsContext(treatedText)
#train(mContext, pairsContext)

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
	contexts = [context for context in mContext.nextStates(c) if context.startswith(i) ]
	if len(contexts) > 0:
		print("*")
		selected = select(contexts)
		if selected is not None:
			return selected
	else:
		return processInput(i)
	return i

while True:
	i = raw_input(text + " > ")
	if lastWord is not None:
		if mContext.hasState(lastWord):
			result = processInputForContext(i, lastWord)
			mContext.increaseRelation(lastWord, result)
			lastWord = result
		else:
			result = processInput(i)
			train(mContext,[(lastWord, result)])
			train(m, getPairsCompletions2(result))
			lastWord = result
	else:
		lastWord = processInput(i)
		if False in [m.hasState(pair[0]) for pair in getPairsCompletions2(lastWord)]:
			train(m, getPairsCompletions2(lastWord))
	text += ' ' + lastWord