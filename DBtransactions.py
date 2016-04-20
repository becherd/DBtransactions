#! /usr/local/dist/bin/python
# -*- coding: utf8 -*-


import string
import re
import random
import views

READ="r"
WRITE="w"
COMMIT="c"
ABORT="a"

class HistoryItem:
	def __init__(self, transaction, operation, data="", index=-1):
		self.transaction = transaction
		self.operation = operation
		self.data=data
		self.index=index
	def toString(self, html=True):
		if self.data != "":
			data = "["+self.data+"]"
		else:
			data = ""
		if html:
			transaction = "<sub>"+self.transaction+"</sub>"
		else:
			transaction = self.transaction
		return self.operation+transaction+data


def generateHistory():
	numberOfTransactions = random.randint(2,4)
	numberOfDataItems = random.randint(2,4) - random.randint(0,1)
	numberOfOperations = numberOfTransactions*random.randint(0,2)+random.randint(2,3)
	history = []
	usedTransactions = set()
	for i in range(numberOfOperations):
		item = generateRandomHistoryItem(numberOfTransactions, numberOfDataItems)
		history.append(item)
		usedTransactions.add(item.transaction)
	#make sure all transactions make at least one operation
	while len(usedTransactions) != numberOfTransactions:
		item = generateRandomHistoryItem(numberOfTransactions, numberOfDataItems)
		if item.transaction not in usedTransactions:
			history.append(item)
			usedTransactions.add(item.transaction)
	#add commits/aborts
	for t in usedTransactions:
		for i, e in enumerate(reversed(history)):
			if e.transaction == t:
				indexForCommit = random.randint(len(history)-i, len(history))
				commitOrAbort = random.randint(0,100)
				if commitOrAbort > 90:
					operation = ABORT
				else:
					operation = COMMIT
				item = HistoryItem(t,operation,"")
				history.insert(indexForCommit, item)
				break
	#sgenerate new history in some cases to balance it out a bit
	if isST(operationsNotST(history)) or not isRC(operationsNotRC(history)):
		if random.randint(0,100) > 50:
			return generateHistory()
	if random.randint(0,100) < 15:
		while isSR(generateGraph(history)) and isACA(operationsNotACA(history)):
			history = generateHistory()
	elif random.randint(0,100) < 15:
		while isSR(generateGraph(history)):
			history = generateHistory()
		while not isST(operationsNotST(history)):
			history = generateHistory()
	return history

def generateRandomHistoryItem(numberOfTransactions, numberOfDataItems):
	operations = [READ,WRITE]
	dataItems = ["x", "y","z","w"]
	transaction = str(random.randint(1,numberOfTransactions))
	dataItem = dataItems[random.randint(0,numberOfDataItems-1)]
	operation = operations[random.randint(0,1)]
	item = HistoryItem(transaction, operation, dataItem)
	return item


def parseInput(string):
	string = string.replace(" ", "")
	elements = string.split(",")
	history = []
	for i, e in enumerate(elements):
		if len(e) == 2:
			#c or a
			if re.match("^[ac]\d$",e):
				history.append(HistoryItem(e[1],e[0], "", i))
			else:
				return views.getMessageBox("Verstehe deine Eingabe "+e+" nicht!", "exclamation-sign")
		elif len(e) == 5:
			#w or r
			if re.match("^[wr]\d[\[\(][a-zA-Z][\]\)]$",e):
				history.append(HistoryItem(e[1],e[0],e[3], i))
			else:
				return views.getMessageBox("Verstehe deine Eingabe "+e+" nicht!", "exclamation-sign")
		elif re.match("[ac]\d+$",e) or re.match("[wr]\d+[\[\(][a-zA-Z][\]\)]",e):
			return views.getMessageBox("Bitte nur TA-IDs zwischen 0 und 9 verwenden!", "exclamation-sign")
		else:
			return views.getMessageBox("Kein gültiges Format: "+e+"", "exclamation-sign")
	validation = validateInput(history)
	if validation[0]:
		return history
	else:
		return validation[1]


def involvedTransactions(history, operation=READ+WRITE+COMMIT+ABORT):
	transactions = set("")
	for e in history:
		if e.operation in operation:
			transactions.add(e.transaction)
	return transactions


def committedTransactions(history):
        return involvedTransactions(history, COMMIT)


def abortedTransactions(history):
        return involvedTransactions(history, ABORT)


def getEndOperationOfTA(history, transactionId):
	for e in history:
		if e.transaction == transactionId and e.operation in COMMIT+ABORT:
			return e
	return history[-1]

def validateInput(history):
	for i,e in enumerate(history):
		if (e.operation == COMMIT or e.operation == ABORT) and i<len(history)-1:
			for e2 in history[i+1:]:
				if e.transaction == e2.transaction:
					#the transaction does something after abort/commit, which is invalid
					return (False, views.getMessageBox("Operationen nach Commit/Abort!", "exclamation-sign"))
	if committedTransactions(history) | abortedTransactions(history) < involvedTransactions(history):
		#there are transactions which do not commit/abort
		return (False, views.getMessageBox("Es gibt TAs, die weder committen noch aborten!", "exclamation-sign"))
	else:
		return (True, "Alles ok") 





def iReadsFromj(history):
	readTAs = []
	for i,e in enumerate(history):
		if e.operation == READ:
			aborted = set()
			for e2 in reversed(history[:i]):
				if e.transaction != e2.transaction:
					if e2.operation==ABORT:
						aborted.add(e2.transaction)
					elif e2.operation==WRITE and e.data==e2.data and e2.transaction not in aborted:
						readTAs.append((e,e2))
						break
	return readTAs

	

def isRC(operationsNotRC):
	return not operationsNotRC


def operationsNotRC(history):
	notRC = []

	readTAs = iReadsFromj(history)
	for t in readTAs:
		for e in history:
			if e.operation == COMMIT and e.transaction == t[0].transaction:
				#reading TA commits
				notRC.append([(t[1], t[0]), (getEndOperationOfTA(history, t[1].transaction), getEndOperationOfTA(history, t[0].transaction))])
				break
			elif e.operation == COMMIT and e.transaction == t[1].transaction:
				#writing TA commits
				break
	return notRC	


def isACA(operationsNotACA):
        return not operationsNotACA


def operationsNotACA(history):
	notACA = []

        readTAs = iReadsFromj(history)
        for t in readTAs:
                for e in history[t[0].index:]:
                        if (e.operation == COMMIT or e.operation == ABORT) and e.transaction == t[1].transaction:
                                notACA.append([(t[1], t[0]), (getEndOperationOfTA(history, t[1].transaction), getEndOperationOfTA(history, t[0].transaction))])
        return notACA


def isST(operationsNotST):
        return not operationsNotST


def operationsNotST(history):
	notST = []

	for i,e in enumerate(history):
		if e.operation == WRITE:
			for j,e2 in enumerate(history[i:]):
				if (e2.operation == READ or e2.operation == WRITE) and e2.transaction != e.transaction and e2.data==e.data:
					commitAbortFound = False
					for c in history[i:i+j]:
						if (c.operation==COMMIT or c.operation == ABORT) and c.transaction == e.transaction:
							#commit/abort before operation -> ok
							commitAbortFound=True
							break
					if not commitAbortFound:
						notST.append([(e2, e), (getEndOperationOfTA(history, e2.transaction), getEndOperationOfTA(history, e.transaction))])
	return notST


def findConflictOperations(history):
	conflictOperations = set()
	for i,e in enumerate(history):
		for j,e2 in enumerate(history):
			if e.transaction != e2.transaction and i<j and not (e.operation == READ and e2.operation==READ) and e.data==e2.data and not e.data == "":
				conflictOperations.add((e, e2))
	return conflictOperations

def findConflictTransactions(history, transactions):
	conflictOperations = findConflictOperations(history)
	conflictTAs = set()
	for o in conflictOperations:
		t1 = o[0].transaction
		t2 = o[1].transaction
		if t1 in transactions and t2 in transactions:
			conflictTAs.add((t1,t2))
	return conflictTAs

def generateGraph(history):
	transactions = committedTransactions(history)
	graph = {}
	conflictTransactions =  findConflictTransactions(history, transactions)
	for t in transactions:
		dest = []
		for c in conflictTransactions:
			if c[0] == t:
				dest.append(c[1])
		graph[t] = dest
	return graph

def computeEverything(history):
	graph = generateGraph(history)
	opsNotRC = operationsNotRC(history)
	opsNotACA = operationsNotACA(history)
	opsNotST = operationsNotST(history)

	return {'conflictOperations': findConflictOperations(history), 'committedTAs': committedTransactions(history), 'abortedTAs': abortedTransactions(history), 'readingTAs': iReadsFromj(history), 'graph': graph, 'SR': isSR(graph), 'RC': isRC(opsNotRC), 'operationsNotRC': opsNotRC, 'ACA': isACA(opsNotACA), 'operationsNotACA': opsNotACA, 'ST': isST(opsNotST), 'operationsNotST': opsNotST}

def nodesToJson(graph):
	json = "nodes: ["
	for i,t in enumerate(graph):
		json=json+""" { data: { id: 'T""" + t + """' } }"""
		if i < len(graph)-1:
			json=json+","
	json=json+"]"
	return json


def edgesToJson(graph):
	edgesInCycle = getCycleEdges(findCycle(graph))
        json = "edges: ["
        for source in graph:
		targets = graph[source]
		for i, target in enumerate(targets):
			if (source,target) in edgesInCycle:
				color = """#FF0039"""
			else:
				color = """#2780E3"""
                	json=json+""" { data: { id: 'T"""+ source +"T"+target+"""', source: 'T"""+source+"""', target: 'T"""+target+"""', color: '"""+color+"""' } }"""
                	if i < len(graph)-1:
                        	json=json+","
        json=json+"]"
        return json

def graphToJson(graph):
	json = "var elesJson = {" + nodesToJson(graph) + ", " + edgesToJson(graph) + "};"
	return json



def isSR(graph):
	return not cycleExists(graph)

def cycleExists(graph):
	return findCycle(graph) != []


def getCycleEdges(cycle):
	edges = []
	for i in range(len(cycle)-1):
		edges.append((cycle[i],cycle[i+1]))
	return edges



def findCycle(graph):
	for u in graph:
		nodesInCycle = [u]
		found = visitNodes(graph, u, nodesInCycle)
		if found: 
			return nodesInCycle
	return []

def visitNodes(graph, u, nodesInCycle):
	if nodesInCycle.count(u) >1: 
		firstU = nodesInCycle.index(u)
		del nodesInCycle[:firstU]
		return True
	for v in graph[u]:
		nodesInCycle.append(v)
		found = visitNodes(graph, v, nodesInCycle)
		if found:
			return True
		else:
			del nodesInCycle[-1]
	return False
