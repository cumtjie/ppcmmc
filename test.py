import codecs
import sys
from msvcrt import *

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
			for _input in range(len(candidatesWeights)):
				if candidatesWeights[_input] > maxWeight:
					chosen = _input
					maxWeight = candidatesWeights[_input]
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
	text = None
	mem = ''
	candidates = None
	valid_chars = 'qwertyiuopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
	options = '12345'
	
	def __init__(self):
		self.mWord = Markov()
		self.mContext = Markov()
		self.text = ''
		self.candidates = []
		
	def logic(self, _input):
		if self.lastWord is not None:
			if self.mContext.hasState(self.lastWord):
				result = self.processInputForContext(_input, self.lastWord)
			else:
				result = self.processInput(_input)
		else:
			result = self.processInput(_input)
		return result
		
	def processInputForContext(self, _input, _context):
		contexts = [context for context in self.mContext.nextStates(_context) if context.startswith(_input) and not context == _input ]
		if len(contexts) > 0:
			return contexts[:5]
		return self.processInput(_input)
		
	def processInput(self, _input):
		nextWords = self.mWord.nextStates(_input)
		if nextWords is not None:
			if len(nextWords) > 0:
				return nextWords[:5]
		return [_input]
	
	def run(self):
		while True:
			_input = getch()
			if _input == '!': #quit
				break
			elif _input == '#': #clean
				self.text = ''
				self.lastWord = None
				self.mem = ''
				print 
			elif _input == '@': #status
				print 'context: ', self.mContext.table
				print 'word: ', self.mWord.table
				print 'lastWord: ', self.lastWord
			elif _input == ' ': #new word
				self.text += ' ' + self.mem
				if self.lastWord is not None:
					self.mContext.increaseRelation(self.lastWord, self.mem)
				self.mWord.train(TextHandler.getPairsCompletions(self.mem))
				self.lastWord = self.mem
				self.mem = ''
				print '\n' + self.text
			else: #new char
				if _input in self.options:
					if int(_input) <= len(self.candidates):
						w = self.candidates[int(_input)-1]
						self.mem = ''
						self.text += ' ' + w
						print '\n' + self.text
						if self.lastWord is not None:
							self.mContext.increaseRelation(self.lastWord, w)
						self.mWord.train(TextHandler.getPairsCompletions(w))
						self.lastWord = w
				elif _input in self.valid_chars:
					self.mem += _input
					self.candidates = self.logic(self.mem)
					print '\ncandidates:' , self.candidates
					print self.text + ' ' + self.mem
	
	def train(self, text):
		pairs = TextHandler.getPairsCompletions(text)
		self.mWord.train(pairs)

		pairsContext = TextHandler.getPairsContext(text)
		self.mContext.train(pairsContext)

class TextHandler(object):
	
	@staticmethod
	def getPairsCompletions(text, separator=' '):
		pairList = []
		for word in text.split(separator):
			for _input in range(len(word)-1):
				pairList.append((word[:_input+1], word))
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

ppm = PPM()
ppm.train(TextHandler.treatText(TextHandler.getText("war&peace2.txt")))

ppm.run()