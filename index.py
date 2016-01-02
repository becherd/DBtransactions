#!/usr/bin/env python
import cgi
import cgitb; cgitb.enable()
import views
import DBtransactions
form = cgi.FieldStorage()


def printjquery(graph):
	graphJson = DBtransactions.graphToJson(graph)
	jq = """<script src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script>
		<script src="http://cytoscape.github.io/cytoscape.js/api/cytoscape.js-latest/cytoscape.min.js"></script>
		 <script>
		$(function(){
		"""
	jq = jq + graphJson+jsonend
	return jq

	
print """
	<html>
		<head>
			<meta charset="utf-8">
			<title>DBtransactions</title>
			<link rel="stylesheet" type="text/css" href="http://home.in.tum.de/~becher/static/css/bootstrapcosmo.min.css" />
			<script src="http://home.in.tum.de/~becher/static/js/jquery-1.11.3.min.js"></script>
			<script src="http://home.in.tum.de/~becher/static/js/bootstrap.min.js"></script>
		</head>"""

def html(history):
	return """<body>
	<div class="panel panel-default">
  	<div class="panel-body">
		<div class="row">
			<div class="col-md-6">
				<h1><big>DB[transactions]</big><sub><small>beta</small></sub></h1>
			</div>
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
						<button id="submitbutton" type="submit" class="btn btn-primary" value="send">Absenden</button>
				</div>			
		</form>
		</div>
		</div>
		<br/>
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





jsonend="""
$('#graph').cytoscape({
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
});
}); 
</script>
"""






def printResults(string):
                history = DBtransactions.parseInput(string)
                if not isinstance(history, basestring):
                        historyString = views.historyToString(history)
			historyTable = views.historyToTable(history)
                        result = DBtransactions.computeEverything(history)
                        graph = result[0]
                        isSR = result[1]
                        isRC = result[2]
                        isACA = result[3]
                        isST = result[4]
			returnString =  historyTable+views.htmlGraph()+"<div>"+views.wrapInPanel("Eigenschaften von H:="+historyString, views.propertyToString("serialisierbar", isSR)+views.propertyToString("rücksetzbar", isRC)+views.propertyToString("vermeidet kaskadierendes Rücksetzen", isACA)+views.propertyToString("strikt", isST), 1)+"</div>"+printjquery(graph)
                else:
			returnString = history
		return returnString







try:
	history = str(form['history'].value)
	print html(history) + printResults(history) + htmlend
except KeyError:
	history = DBtransactions.generateHistory()
    	print html(history)+htmlend
