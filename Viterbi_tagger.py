#!/usr/bin/env python3

import sys

helpMsg = '''
	usage: $ python3 Viterbi_tagger.py training_file_name input_file_name
'''

class transiProbMtx:
	"""transition probability matrix of Penn Treebank POS tags: P(t_i|t_i-1)"""
	def __init__(self):
		self.__probCalc = False
		self.tagDict = {}

	def feedSentence(self,tokenLs):
		if self.__probCalc:
			return
		else:
			for i in range(1,len(tokenLs)):
				self.__update(tokenLs[i][1],tokenLs[i-1][1])

	def __addTag(self,tagName):
		self.tagDict[tagName] = {'count':0}

	def __update(self,thisTag, prevTag):
		if thisTag not in self.tagDict:
			self.__addTag(thisTag)
		self.tagDict[thisTag]['count'] += 1
		if prevTag not in self.tagDict[thisTag]:
			self.tagDict[thisTag][prevTag] = 1
		else:
			self.tagDict[thisTag][prevTag] += 1

	def calcProb(self):
		if self.__probCalc:
			return
		else:
			for tag in self.tagDict:
				for prevTag in self.tagDict[tag]:
					if prevTag != 'count':
						self.tagDict[tag][prevTag] = self.tagDict[tag][prevTag] / self.tagDict[tag]['count']
			self.__probCalc = True
	# For debugging purpose only
	def __str__(self):
		string = 'Transition Probability Table \n -------------------------------\n'
		for tag in self.tagDict:
			for prevTag in self.tagDict[tag]:
				string = string + prevTag + '->' + tag + ':' + str(self.tagDict[tag][prevTag]) + ' | '
			string += '\n'
		return string

	def lookup(self, thisTag, prevTag):
		if prevTag in self.tagDict[thisTag]:
			return self.tagDict[thisTag][prevTag]
		else:
			return 0

	#def loadFromFile(self, fileObj)

class obsLlhdMtx():
	"""Observation likelihood for words in WSJ corpus: P(w_i|t_i)"""
	def __init__(self):
		self.__probCalc = False
		self.__OOVhandled = False
		self.tagDict = {}
		self.oneTimeW = []
		self.moreTimeW = []
		self.knownW = []
	
	def feedSentence(self,tokenLs):
		if self.__probCalc:
			return
		else:
			for i in range(1,len(tokenLs)):
				self.__update(tokenLs[i][1],tokenLs[i][0])
				if tokenLs[i][0] in self.oneTimeW:
					self.oneTimeW.remove(tokenLs[i][0])
					self.moreTimeW.append(tokenLs[i][0])
				elif tokenLs[i][0] not in self.moreTimeW:
					self.oneTimeW.append(tokenLs[i][0])

	def __addTag(self,tagName):
		self.tagDict[tagName] = {'$COUNT$':0}

	def __update(self, POStag, word):
		if POStag not in self.tagDict:
			self.__addTag(POStag)
		self.tagDict[POStag]['$COUNT$'] += 1
		if word not in self.tagDict[POStag]:
			self.tagDict[POStag][word] = 1
		else:
			self.tagDict[POStag][word] += 1

	def calcProb(self):
		if self.__probCalc or not self.__OOVhandled:
			return
		else:
			for tag in self.tagDict:
				for word in self.tagDict[tag]:
					if word != '$COUNT$':
						self.tagDict[tag][word] = self.tagDict[tag][word] / self.tagDict[tag]['$COUNT$']
			self.__probCalc = True

	def handleOOV(self):
		if self.__OOVhandled:
			return
		else:
			for tag in self.tagDict:
				OOV_cnt = 0
				for word in self.tagDict[tag]:
					if word in self.oneTimeW:
						OOV_cnt += 1
				self.tagDict[tag]['$UNKNOWN$'] = OOV_cnt

			self.knownW = self.oneTimeW + self.moreTimeW
			self.__OOVhandled = True
			
	# For debugging purpose only
	def __str__(self):
		string = 'Observation Likelihood Table \n -------------------------------\n'
		for tag in self.tagDict:
			for word in self.tagDict[tag]:
				string = string + word + '|' + tag + '=' + str(self.tagDict[tag][word]) + ' ; '
			string += '\n'
		return string

	def lookup(self, tag, word):
		if word in self.knownW:
			if word in self.tagDict[tag]:
				return self.tagDict[tag][word]
			else:
				return 0
		else:
			return self.tagDict[tag]['$UNKNOWN$']

	#def loadFromFile(self, fileObj)

class ViterbiParser():
	"""as its name suggests"""
	def __init__(self, transMtx, obsMtx):
		self.A_trans = transMtx
		self.B_obs = obsMtx
		self.tagKey = list(self.A_trans.tagDict.keys())
		self.rowN = len(self.tagKey)
		self.tokenKey = []
		self.colN = len(self.tokenKey)
		self.DPcell = []
		self.backPtr = []
		self.__purgeCells()

	def __purgeCells(self):
		self.tokenKey = []
		self.colN = len(self.tokenKey)
		self.DPcell = []
		self.backPtr =[]
		for POStag in self.tagKey:
			self.DPcell.append([])
			self.backPtr.append([])

	def tagTokens(self, tokenLs):
		self.__purgeCells()
		self.tokenKey = tokenLs
		self.colN = len(self.tokenKey)

		#Initialization step
		for i in range(self.rowN):
			currTag = self.tagKey[i]
			self.DPcell[i].append(self.A_trans.lookup(currTag,'<s>')*self.B_obs.lookup(currTag, self.tokenKey[0]))
			self.backPtr[i].append(-1)

		#Recursion Step
		for w in range(1, self.colN):
			for t in range(self.rowN):
				maxArg = -1
				maxProb = -1
				thisObsProb = self.B_obs.lookup(self.tagKey[t], self.tokenKey[w])

				for pt in range(self.rowN):
					pathProb = self.DPcell[pt][w-1]*self.A_trans.lookup(self.tagKey[t], self.tagKey[pt])
					if pathProb > maxProb:
						maxProb = pathProb
						maxArg = pt
				self.DPcell[t].append(maxProb*thisObsProb)
				self.backPtr[t].append(maxArg)

		#Termination Step
		endPt = -1
		endProb = -1
		for lt in range(self.rowN):
			if self.DPcell[lt][self.colN-1] > endProb:
				endProb = self.DPcell[lt][self.colN-1]
				endPt = lt

		taggedPairs=[]
		mlTag = endPt
		for i in range(self.colN-1, -1, -1):
			taggedPairs.insert(0,[self.tokenKey[i], self.tagKey[mlTag]])
			mlTag = self.backPtr[mlTag][i]

		return taggedPairs

def main(args):
	if len(args) != 3:    #2 arguments for now
		return helpMsg

	priorP = transiProbMtx()
	obsLikelihood = obsLlhdMtx()
	trainingF = open(args[1], 'r')
	tokenLs = [['<s>','<s>']]
	for line in trainingF:
		if line != '\n':
			tokenLs.append(line.strip().split('\t'))
		else:
			priorP.feedSentence(tokenLs)
			obsLikelihood.feedSentence(tokenLs)
			#print(tokenLs)
			tokenLs = [['<s>','<s>']]

	trainingF.close()
	priorP.calcProb()
	obsLikelihood.handleOOV()
	obsLikelihood.calcProb()

	viterbi_HMM_tagger = ViterbiParser(priorP, obsLikelihood)

	inputF = open(args[2], 'r')
	tokenLs = []
	for line in inputF:
		if line != '\n':
			tokenLs.append(line.strip())
		else:
			print(viterbi_HMM_tagger.tagTokens(tokenLs))
			#print(tokenLs)
			tokenLs = []

	#print(priorP.lookup('VBG','JJ'))
	#print('\n')
	#print(obsLikelihood.lookup('VB','output'))
	#print(priorP)
	#print(obsLikelihood)



	return 0

sys.exit(main(sys.argv))