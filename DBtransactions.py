#! /usr/local/dist/bin/python
# -*- coding: utf8 -*-


import string
import re


READ="r"
WRITE="w"
COMMIT="c"
ABORT="a"

class HistoryItem:
	def __init__(self, transaction, operation, data=""):
		self.transaction = transaction
		self.operation = operation
		self.data=data
	def toString(self):
		if self.data != "":
			data = "["+self.data+"]"
		else:
			data = ""
		return self.operation+"<sub>"+self.transaction+"</sub>"+data


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
					for c in history[i:j]:
						if (c.operation==COMMIT or c.operation == ABORT) and c.transaction == e.transaction:
							#commit/abort before operation -> ok
							commitAbortFound=True
							break
					if not commitAbortFound:
						return False
	return True


def findConflictOperations(history, transactions):
	conflictTAs = set()
	for i,e in enumerate(history):
		for j,e2 in enumerate(history):
			if e.transaction != e2.transaction and e.transaction in transactions and e2.transaction in transactions and i<j and not (e.operation == READ and e2.operation==READ) and e.data==e2.data and not e.data == "":
				conflictTAs.add((e.transaction, e2.transaction))
	return conflictTAs

def generateGraph(history):
	transactions = committedTransactions(history)
	graph = {}
	conflictTransactions =  findConflictOperations(history, transactions)
	for t in transactions:
		dest = []
		for c in conflictTransactions:
			if c[0] == t:
				dest.append(c[1])
		graph[t] = dest
	return graph

def computeEverything(history):
	graph = generateGraph(history)
	return (graph, isSR(graph), isRC(history), isACA(history), isST(history))

def nodesToJson(graph):
	json = "nodes: ["
	for i,t in enumerate(graph):
		json=json+""" { data: { id: 'T""" + t + """' } }"""
		if i < len(graph)-1:
			json=json+","
	json=json+"]"
	return json


def edgesToJson(graph):
        json = "edges: ["
        for source in graph:
		targets = graph[source]
		for i, target in enumerate(targets):
                	json=json+""" { data: { id: 'T"""+ source +"T"+target+"""', source: 'T"""+source+"""', target: 'T"""+target+"""' } }"""
                	if i < len(graph)-1:
                        	json=json+","
        json=json+"]"
        return json

def graphToJson(graph):
	json = "var elesJson = {" + nodesToJson(graph) + ", " + edgesToJson(graph) + "};"
	return json



def isSR(graph):
	return not cycle_exists(graph)


####via https://algocoding.wordpress.com/2015/04/02/detecting-cycles-in-a-directed-graph-with-dfs-python/
def cycle_exists(G):                     # - G is a directed graph
    color = {}
    for u in G:
	color[u] = "white"
    #color = { u : "white" for u in G  }  # - All nodes are initially white
    found_cycle = [False]                # - Define found_cycle as a list so we can change
                                         # its value per reference, see:
                                         # http://stackoverflow.com/questions/11222440/python-variable-reference-assignment
    for u in G:                          # - Visit all nodes.
        if color[u] == "white":
            dfs_visit(G, u, color, found_cycle)
        if found_cycle[0]:
            break
    return found_cycle[0]
 
#-------
 
def dfs_visit(G, u, color, found_cycle):
    if found_cycle[0]:                          # - Stop dfs if cycle is found.
        return
    color[u] = "gray"                           # - Gray nodes are in the current path
    for v in G[u]:                              # - Check neighbors, where G[u] is the adjacency list of u.
        if color[v] == "gray":                  # - Case where a loop in the current path is present.  
            found_cycle[0] = True       
            return
        if color[v] == "white":                 # - Call dfs_visit recursively.   
            dfs_visit(G, v, color, found_cycle)
    color[u] = "black"                          # - Mark node as done.
