#! /usr/local/dist/bin/python
# -*- coding: utf8 -*-

import DBtransactions


def wrapInPanel(heading, content, numberOfColumns, panelType="primary"):
	if numberOfColumns == 1:
		x = 12
	elif numberOfColumns == 2:
		x = 6
	elif numberOfColumns == 3:
		x = 4
	else:
		x = 3
	panelString = "<div class=\"col-xs-8 col-sm-6 col-md-"+str(x)+"\"><div class=\"panel panel-"+panelType+"\"><div class=\"panel-heading\"><h3 class=\"panel-title\">"+heading+"</h3></div><div class=\"panel-body\">"+content+"</div></div></div>"
	return panelString


def propertyToString(property, value):
	if value:
		labeltype = "success"
		icon = "ok"
	else:
		labeltype = "danger"
		icon = "flash"
	#return """<h1><span class="label label-"""+labeltype+"""">"""+property+""" <span class="glyphicon glyphicon-"""+icon+"""" aria-hidden=""""+icon+""""></span></span></h1>"""
	return """<h1><div class="alert alert-"""+labeltype+"""">"""+property+""" <span class="glyphicon glyphicon-"""+icon+"""" aria-hidden=""""+icon+""""></span></div></h1>"""


def htmlGraph():
	graphstring =  """<div id="graph" style="height: 400px; width: 100%; left: 0; background-color: #EDF1FA; border-top: 1px solid #ccc;"></div><br/>"""
	return wrapInPanel("Serialisierbarkeitsgraph SG(H)",  graphstring, 1)


def historyToString(history, html=True):
        historyString = ""
        for i,e in enumerate(history):
                historyString = historyString + e.toString(html)
		if i < len(history)-1:
			historyString = historyString + ","
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
	return wrapInPanel("Historie H", table, 1)

def conflictOperationsToString(conflictOperations):
	if not conflictOperations:
		return "-"
	else:
		operationsString = ""
		for o in conflictOperations:
			operationsString = operationsString + o[0].toString() + " &lt; " + o[1].toString() + "<br/>"
		return operationsString
