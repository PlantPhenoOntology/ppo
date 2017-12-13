import pytest
import subprocess
import os
import rdflib

class Reason:
    # Initialize environment, set variables
    def __init__(self):
        self.base = os.path.dirname(__file__)
        self.ontopilot_jar = '/Users/jdeck/IdeaProjects/ppo-data-pipeline/process/../lib/ontopilot-2017-08-04.jar' 
        self.test_input_file = os.path.join(self.base,'test_data.ttl')
        self.test_output_file = os.path.join(self.base,'test_output.ttl')
        self.test_humanoutput_file = os.path.join(self.base,'test_output.csv')
        self.test_expected_output = os.path.join(self.base,'test_expected_output.csv')
        self.test_reasoner_conf = os.path.join(self.base,'reasoner.conf')
        self.reasoner_output_file = 'output_file.txt'
        self.graph = rdflib.Graph()
        self.ontology = "https://raw.githubusercontent.com/PlantPhenoOntology/ppo/master/releases/2017-10-20/ppo.owl"

        test_expected_output_file = open (self.test_expected_output, "r")
        self.expected_results = test_expected_output_file.read().splitlines()
        test_expected_output_file.close()
        
    # Run reaoner on input file data and write to temporary output file
    def reason(self):
        cmd = ['java','-jar',self.ontopilot_jar,'-i',self.test_input_file,'-o',self.test_output_file,'-c',self.test_reasoner_conf, 'inference_pipeline']

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("")
        print("the commandline is")
        print(subprocess.list2cmdline(cmd))

        stdout, stderr = proc.communicate()
        out = open(self.reasoner_output_file,'wb')
        out.write(stdout)
        out.close() 
        err = open(self.reasoner_output_file+ '.err','wb')
        err.write(stderr)
        err.close() 
    
        # wait for process to complete before continuing
        p_status = proc.wait()

        # Simple test to make sure the program exited with a good status
        assert p_status==0


    # parse the graph using the output file and specifying the released ontology
    def parse(self):
        self.graph.parse(self.test_output_file,format="turtle")
        self.graph.parse(self.ontology,format="xml")

    # Parse the reasoned output file with instanceIDs
    def query(self,instanceID,output_file):
        actual_results = []

	# grab description of instance ID from input file and write to output file
        with open(self.test_input_file) as f:
            for line in f:
                if "("+instanceID+")" in line:
                     output_file.write(line)

        # query for a particular instance in the reasoned output along with rdfs:label
        qres = self.graph.query('SELECT ?o ?l WHERE { :' + instanceID + ' a ?o . ?o rdfs:label ?l } ORDER BY ?o')

        # loop results of query
        for row in qres:
            row_result = ("%s,%s" % row)
            # Write first part of reasoned data query results to an array 
            actual_results.append(instanceID+","+ row_result.split(",")[0])
            # Write reasoned data query results to output file so humans can more easily verify results
            output_file.write(instanceID+","+row_result+"\n")


        # compare results
        count = 0
        for e in self.expected_results:
            # checck for in instanceID in expected and that the line matches 
            if (instanceID in e and e not in actual_results):
                assert False, "did not find an expected result: " + e
            # count the # of times this instance is in expected results
            if (instanceID in e):
                count = count + 1

        # test length of actual vs. expected output
        if (count != len(actual_results)):
            print (".")
            assert False, "Unexpected number of output lines"

def test_reasoner():
    runner = Reason()
    runner.reason()
    runner.parse()     
    output_file = open(runner.test_humanoutput_file,"w") 
    instanceIDs = ["mtlp_01","mtlp_02", "utlp_01", "utlp_02", "ppcp_01", "ppcp_02", "rfp_01", "rfp_02", "pfsp_01", "pfsp_02"]
    for instanceID in instanceIDs:
        runner.query(instanceID,output_file)
    output_file.close()
