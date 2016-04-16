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
	def __init__(self, transaction, operation, data=""):
		self.transaction = transaction
		self.operation = operation
		self.data=data
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
	numberOfDataItems = numberOfTransactions - random.randint(0,1)
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
	return views.historyToString(history, False)

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
	for e in elements:
		if len(e) == 2:
			if re.match("[ac]\d",e):
				history.append(HistoryItem(e[1],e[0]))
			else:
				return "verstehe "+e+" nicht"
		elif len(e) == 5:
			#w or r
			if re.match("[wr]\d\[\w\]",e):
				history.append(HistoryItem(e[1],e[0],e[3]))
			else:
				return "verstehe "+e+" nicht"
		else:
			return "Kein gültiges Format"
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



def validateInput(history):
	for i,e in enumerate(history):
		if (e.operation == COMMIT or e.operation == ABORT) and i<len(history)-1:
			for e2 in history[i+1:]:
				if e.transaction == e2.transaction:
					#the transaction does something after abort/commit, which is invalid
					return (False, "Operationen nach Commit/Abort!")
	if committedTransactions(history) | abortedTransactions(history) < involvedTransactions(history):
		#there are transactions which do not commit/abort
		return (False, "Es gibt TAs, die weder committen noch aborten")
	else:
		return (True, "Alles ok") 


def indexOf(history, element):
	for i,e in enumerate(history):
		if e is element:
			return i
	return -1

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

	

def isRC(history):
	readTAs = iReadsFromj(history)
	for t in readTAs:
		for e in history:
			if e.operation == COMMIT and e.transaction == t[0].transaction:
				#reading TA commits
				return False
			elif e.operation == COMMIT and e.transaction == t[1].transaction:
				#writing TA commits
				break
	return True


def isACA(history):
        readTAs = iReadsFromj(history)
        for t in readTAs:
                indexOfRead = indexOf(history, t[0])
                for e in history[indexOfRead:]:
                        if (e.operation == COMMIT or e.operation == ABORT) and e.transaction == t[1].transaction:
                                return False
        return True


def isST(history):
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
						return False
	return True


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
	return {'conflictOperations': findConflictOperations(history), 'committedTAs': committedTransactions(history), 'abortedTAs': abortedTransactions(history), 'readingTAs': iReadsFromj(history), 'graph': graph, 'SR': isSR(graph), 'RC': isRC(history), 'ACA': isACA(history), 'ST': isST(history)}

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
