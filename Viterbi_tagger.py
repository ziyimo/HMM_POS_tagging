import sys

helpMsg = '''
	usage: $ python3 Viterbi_tagger.py training_file_name
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
		string = ''
		for tag in self.tagDict:
			for prevTag in self.tagDict[tag]:
				string = string + prevTag + '->' + tag + ':' + str(self.tagDict[tag][prevTag]) + ' | '
			string += '\n'
		return string

	#def lookup(thisTag, prevTag):


class obsLlhdMtx():
	"""Observation likelihood for words in WSJ corpus: P(w_i|t_i)"""
	def __init__(self):
		self.__probCalc = False
		self.__OOVhandled = False
		self.tagDict = {}
		self.oneTimeW = []
		self.moreTimeW = []
	
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
				if OOV_cnt != 0:
					self.tagDict[tag]['$UNKNOWN$'] = OOV_cnt

			self.__OOVhandled = True
			
	# For debugging purpose only
	def __str__(self):
		string = ''
		for tag in self.tagDict:
			for word in self.tagDict[tag]:
				string = string + word + '|' + tag + '=' + str(self.tagDict[tag][word]) + ' ; '
			string += '\n'
		return string

	#def lookup(tag, word):

def main(args):
	if len(args) != 2:    #one argument for now
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
	obsLikelihood.calcProb()
	obsLikelihood.handleOOV()
	print(priorP)
	print(obsLikelihood)
	return 0

sys.exit(main(sys.argv))