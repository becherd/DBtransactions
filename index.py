#!/usr/bin/python
# -*- coding: utf8 -*-
import cgi
import cgitb; cgitb.enable()
import views
import DBtransactions
form = cgi.FieldStorage()


def printjquery(graph, history):
	graphJson = DBtransactions.graphToJson(graph)
	jq = """<script src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script>
		<script src="/becher/static/js/cytoscape.min.js"></script>
		<script src="http://cdnjs.cloudflare.com/ajax/libs/qtip2/2.2.0/jquery.qtip.min.js"></script>
		<link href="http://cdnjs.cloudflare.com/ajax/libs/qtip2/2.2.0/jquery.qtip.min.css" rel="stylesheet" type="text/css" />
		<script src="https://cdn.rawgit.com/cytoscape/cytoscape.js-qtip/2.2.5/cytoscape-qtip.js"></script>
		
		 <script>
		$(function(){
		"""
	jq = jq + graphJson+graphStyle(history)
	return jq


print "Content-Type: text/html"
print """
	<html>
		<head>
			<meta charset="utf-8">
			<title>DB[transactions]</title>
			<link rel="stylesheet" type="text/css" href="/becher/static/css/bootstrapcosmo.min.css" />
			<script src="/becher/static/js/jquery-1.11.3.min.js"></script>
			<script src="/becher/static/js/bootstrap.min.js"></script>
		</head>"""

def html(history):
	return """<body>
	<div class="panel panel-default">
  	<div class="panel-body">
		<div class="row">
			<div class="col-md-6">
"""+views.getHeading()+"""</div>
			<div class="col-md-6">
				<p class="text-right"><button type="button" class="btn btn-primary btn-xs" data-toggle="modal" data-target="#helpModal">
		 			<span class="glyphicon glyphicon-question-sign" aria-hidden="true"></span> Hilfe</button>
				</p>
			</div>
		</div>
		<br/>
		<div class="panel panel-default">
			<div class="panel-body">
			<span class="label label-success">DB-Fragen? DB fragen:</span> <a href="mailto:david.becher@mytum.de">david.becher@mytum.de</a>
			</div>
		</div>
		<br/>
		<form class="form" action="index.py" method="POST"> 
				<div class="form-group">
					<h4>Historie eingeben</h4>
					<input type="text" class="form-control" name="history" value="
""" + history+ """ 
"></input>
				</div>
				<div class="form-group">
						<a href="index.py" class="btn btn-default">Neue Historie generieren</a>
				</div>
		"""


htmlend="""
		<!-- Modal: help -->
		<div id="helpModal" class="modal fade" role="dialog">
			<div class="modal-dialog">
			<!-- Modal content-->
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal">&times;</button>
					<h3 class="modal-title">Hilfe</h3>
				</div>
				<div class="modal-body">
					<p>
						<h4>Historie eingeben</h4>
						<p>Historien in folgender Form eingeben: <code>w1[x],r2[y],r2[x],c1,a2</code></p>
					</p>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-default" data-dismiss="modal">OK</button>
				</div>
			</div>
			</div>
		</div>
	</body>
</html>
"""





def graphStyle(history):
	edgeTooltips = views.conflictOperationsTooltip(history)
	return """
	var graph = cytoscape({
	  container: document.getElementById('graph'),

	  style: cytoscape.stylesheet()
	    .selector('node')
	      .css({
		'background-color': '#2780E3',
		'color': '#ffffff',
		'text-outline-width': 2,
		'text-outline-color': '#2780E3',
		'shape': 'rectangle',
		'width': 'mapData(0, 0, 30, 30, 0)',
		'height': 'mapData(0, 0, 20, 20, 50)',
		'content': 'data(id)',
		'text-valign': 'center',
		'text-halign': 'center'
	      })
	    .selector('edge')
	      .css({
		'width': 'mapData(0, 0, 10, 5, 9)',
		'line-color': 'data(color)',
		'target-arrow-color': 'data(color)',
		'target-arrow-shape': 'triangle',
		'opacity': 0.5
	      }),
	  
	  elements: elesJson,
	  
	  layout: {
	    name: 'circle',
	    directed: true,
	    padding: 10
	  },
	  minZoom: 0.5,
	  maxZoom: 2,
	  autoungrabify: false,
	  userPanningEnabled: false,
	  zoomingEnabled: true,
	  userZoomingEnabled: false,
	}); """ + edgeTooltips + """
	}); 
	</script>
	"""






def printResults(string, answers={}):
                history = DBtransactions.parseInput(string)
                if not isinstance(history, basestring):
                        historyString = views.historyToString(history)
			historyTable = views.historyToTable(history)
                        result = DBtransactions.computeEverything(history)
			conflictOperations = views.conflictOperationsToString(result['conflictOperations'])
			readingTAs = views.readingTAsToString(result['readingTAs'])
			committedTransactions = views.transactionListToString(result['committedTAs'])
			abortedTransactions = views.transactionListToString(result['abortedTAs'])
                        graph = result['graph']
                        isSR = result['SR']
                        operationsNotRC = result['operationsNotRC']
			isRC = result['RC']
                        operationsNotACA = result['operationsNotACA']
			isACA = result['ACA']
                        operationsNotST = result['operationsNotST']
			isST = result['ST']
			
			resultString =  historyTable+views.wrapInPanel("Konfliktoperationen", conflictOperations,3)+views.wrapInPanel("Lesende Transaktionen", readingTAs, 3)+views.wrapInPanel("Committete Transaktionen", committedTransactions, 3)+views.wrapInPanel("Abortete Transaktionen", abortedTransactions, 3)+views.htmlGraph()+"<div>"+views.wrapInPanel("Eigenschaften von H := "+historyString, views.booleanPropertyToString("serialisierbar", isSR)+views.propertyToString("rücksetzbar", history, operationsNotRC)+views.propertyToString("vermeidet kaskadierendes Rücksetzen", history, operationsNotACA)+views.propertyToString("strikt", history, operationsNotST), 12)+"</div>"+printjquery(graph, history)
                	if answers:
				if answers['SR'] == isSR and  answers['RC'] == isRC and  answers['ACA'] == isACA and  answers['ST'] == isST:
					returnString = printCheckboxes(answers) + views.getMessageBox("Richtig!","thumbs-up") + resultString
				else:
					returnString = printCheckboxes(answers) + views.getMessageBox("Leider falsch!","thumbs-down")
			else:
				returnString = printCheckboxes(result) + resultString
		else:
			returnString = printCheckboxes(answers) + history
		return returnString


def getUserAnswers(form):
	formKeys = form.keys();
	input = {"SR": "SR" in formKeys, "RC": "RC" in formKeys, "ACA": "ACA" in formKeys, "ST": "ST" in formKeys}
	return input	


def printCheckboxes(checked={}):
	returnString = ""
	checkedStrings = {"SR": "", "RC": "", "ACA": "", "ST": ""}

	for k,v in checked.iteritems():
		if v:
			checkedStrings[k] = " checked"
		else:
			checkedStrings[k] = ""
	
	returnString = """ <br/><h4>Welche Eigenschaften erfüllt diese Historie?</h4>
			 <div class="form-group">
				<div id="toggleButtons" class="btn-group" data-toggle="buttons">
			                <label id="SR" type="toggleButton">
                                                <input type="checkbox" name="SR" autocomplete="off" 
"""+checkedStrings['SR'] +"""/>
                                                 <span></span>
                                        </label>
                                        <label id="RC" type="toggleButton">
			                        <input type="checkbox" name="RC" autocomplete="off"
"""+checkedStrings['RC'] +"""/>
                                                 <span></span>
                                        </label>
                                        <label id="ACA" type="toggleButton">
                                                <input type="checkbox" name="ACA" autocomplete="off"
"""+checkedStrings['ACA'] +"""/>
                                                <span></span>
                                        </label>
                                        <label id="ST" type="toggleButton">
                                                <input type="checkbox" name="ST" autocomplete="off"
"""+checkedStrings['ST'] +"""/>
                                                <span></span>
                                        </label>
                        	</div>
			 	<button id="quizbutton" name="quizbutton" type="submit" class="btn btn-primary" value="true">Überprüfen</button>
                        </div>  
			<div class="form-group">
				<button id="submitbutton" type="submit" class="btn btn-default btn-sm" value="send">Ergebnis anzeigen</button>
			  </div>
			</div>
			</form>
		
		<script>
			$('label[type="toggleButton"]').on("change click", function () {
        		var checked = $('input', this).is(':checked');
       			if (checked){ 
				$(this).removeClass().addClass("btn btn-success active");
				$('span', this).html('<span class="glyphicon glyphicon-ok" aria-hidden="true" onclick="return iconclicked('+this.id+');"></span>'+this.id);
			}
			else{
				$(this).removeClass().addClass("btn btn-danger");
				$('span', this).html('<span class="glyphicon glyphicon-flash" aria-hidden="true" onclick="return iconclicked('+this.id+');"></span>'+this.id);
			}
			}).change();
		</script>

		<script>
			function iconclicked(label){
				$("#"+label.id).click();
			};
		</script>
                </div>
                </div>
		"""
	return returnString

try:
	history = str(form['history'].value)
	try:
		quizButton = form['quizbutton'].value
		#quiz has been sent
		print html(history) +  printResults(history, getUserAnswers(form)) + htmlend
	except KeyError:
		#just show the results
		print html(history) + printResults(history) + htmlend
except KeyError:
	history = views.historyToString(DBtransactions.generateHistory(), False)
    	print html(history)+printCheckboxes()+htmlend
