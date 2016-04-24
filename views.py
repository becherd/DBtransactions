#! /usr/local/dist/bin/python
# -*- coding: utf8 -*-

import DBtransactions


def wrapInPanel(heading, content, gridClass, panelType="primary"):
	panelString = "<div class=\"col-xs-12 col-sm-12 col-md-"+str(gridClass)+"\"><div class=\"panel panel-"+panelType+"\"><div class=\"panel-heading\"><h3 class=\"panel-title\">"+heading+"</h3></div><div class=\"panel-body\">"+content+"</div></div></div>"
	return panelString


def getMessageBox(message, icon="exclamation-sign"):
		if icon=="thumbs-up":
			style="success"
		else:
			style="danger"
		return """<div class="panel-body"><div class="row"><div class="col-md-12"><div class="alert alert-"""+style+"""" role="alert"><span class="glyphicon glyphicon-"""+icon+"""" aria-hidden=""""+icon+""""></span><span class="sr-only">"""+style+"""</span> """+message+"""</div></div></div></div>"""



def booleanPropertyToString(property, isFilfilled, valueString=""):
	if isFilfilled:
		labeltype = "success"
		icon = "ok"
	else:
		labeltype = "danger"
		icon = "flash"
	if valueString:
		panelBody = """<div class="panel-body">"""+valueString+"""</div>"""
	else:
		panelBody=""
	return """<div class="panel panel-"""+labeltype+""""><div class="panel-heading">"""+property+""" <span class="glyphicon glyphicon-"""+icon+"""" aria-hidden=""""+icon+""""></span></div>""" + panelBody + """</div>"""


def propertyToString(property, history=[], operationsNotFulfillProperty=[]):
	infoString=""
	if not operationsNotFulfillProperty:
		propertyFulfilled=True
	else:
		propertyFulfilled=False
		infoString = """<div class="list-group">"""
		for v in operationsNotFulfillProperty:
			conflictOperations = v[0]
			endOperations = v[1]
			markElements = {}
			for c in conflictOperations:
				markElements[c.index] = "danger"
			for e in endOperations:
				markElements[e.index] = "warning"
			infoString = infoString+ """<div class="list-group-item"> """ + historyToString(history, True, markElements) + "</div>"
		infoString = infoString + "</div>"
	returnString = booleanPropertyToString(property, propertyFulfilled, infoString)
	
	return returnString


def htmlGraph():
	graphstring =  """<div id="graph" style="height: 400px; width: 100%; left: 0; background-color: #EDF1FA; border-top: 1px solid #ccc;"></div><br/>"""
	return wrapInPanel("Serialisierbarkeitsgraph SG(H)",  graphstring, 12)


def historyToString(history, html=True, markElements={}):
        historyString = ""
        for i,e in enumerate(history):
		if e.index in markElements:
			elementString = """<b><span class="text-"""+markElements[e.index]+"""">"""+e.toString(html)+"</span></b>"
		else:
			elementString = e.toString(html)

                historyString = historyString + elementString
		if i < len(history)-1:
			historyString = historyString + ", "
        return historyString


def transactionToString(transaction):
	return  "T<sub>"+transaction+"</sub>"

def transactionListToString(transactions):
	if not transactions:
		return "-"
	else:
		transactionString = ""
		for t in sorted(list(transactions)):
			transactionString = transactionString + transactionToString(t) + "<br/>"
		return transactionString

def historyToTable(history):
	transactions = sorted(list(DBtransactions.involvedTransactions(history)))
	table = """<table class="table table-bordered table-striped table-hover " style="width: 100%;">
  		<thead>
    			<tr><th>#</th>"""
	for t in transactions:
		table = table + "<th>"+transactionToString(t)+"</th>"
	table = table + "</thead><tbody>"
	for step, e in enumerate(history):
		table = table + "<tr><td>"+str(step)+"</td>"
		index = transactions.index(e.transaction)
		for i in range(len(transactions)):
			table = table + "<td>"
			if i == index:
				table = table + e.toString()
			table = table + "</td>"
		table = table + "</tr>"
	table = table + "</tbody></table>"
	return wrapInPanel("Historie H", table, 12)

def conflictOperationsToString(conflictOperations):
	if not conflictOperations:
		return "-"
	else:
		operationsString = ""
		for o in conflictOperations:
			addString = o[0].toString() + " &lt; " + o[1].toString() + "<br/>"
			if addString not in operationsString:
				operationsString = operationsString + addString
		return operationsString

def readingTAsToString(readingTAs):
	if not readingTAs:
		return "-"
	else:
		readingTAstring = ""
		for ta in readingTAs:
			addString = transactionToString(ta[0].transaction) + " liest von " + transactionToString(ta[1].transaction) + "<br/>"
			if addString not in readingTAstring:
				readingTAstring = readingTAstring + addString
		return readingTAstring
