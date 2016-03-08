#Some examples that query a sample graph

The graph data we're looking at is at:
http://data.biscicol.org/ds/data?graph=urn:uuid:ca2ad527-1946-4242-9968-4c4f076eedbf


Give me  Identifiers and the plant phenological stage
http://www.sparql.org/sparql?query=SELECT+%3Fs+%3Fo+where+%7B%3Fs+%3Curn%3APPO_plant_phenological_stage%3E+%3Fo%7D%0D%0A&default-graph-uri=http%3A%2F%2Fdata.biscicol.org%2Fds%2Fdata%3Fgraph%3Durn%3Auuid%3Aca2ad527-1946-4242-9968-4c4f076eedbf&output=text&stylesheet=%2Fxml-to-html.xsl

List phenological stage by day of year
http://www.sparql.org/sparql?query=SELECT+distinct+%3Fplant+%3Fstage+%3Fdayofyear%0D%0Awhere+%7B%0D%0A%3Fobsevent+%3Cobi%3Ahas_specified_input%3E+%3Fplant+.%0D%0A%3Fplant+%3Cbco%3Aparticipates_in%3E+++%3Fprocess+.%0D%0A%3Fprocess++%3Curn%3APPO_plant_phenological_stage%3E+%3Fstage+.%0D%0A%3Fobsevent+%3Curn%3Adayofyear%3E+%3Fdayofyear+%0D%0A%7D%0D%0A&default-graph-uri=http%3A%2F%2Fdata.biscicol.org%2Fds%2Fdata%3Fgraph%3Durn%3Auuid%3Aca2ad527-1946-4242-9968-4c4f076eedbf&output=text&stylesheet=%2Fxml-to-html.xsl

