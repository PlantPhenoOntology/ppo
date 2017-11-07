# Test framework for PPO

In order to run the tests in this directory, simply install the python pytest module
ane type "pytest" in this directory.  Pytest will run test_reasoner.py which in turn
calls the ontopilot inferencing pipeline to reason on the the file test_data.ttl.
The output of this command will be compared to the expected results in test_expected_output.csv
file.  Any inconsitencies will be reported as errors.

NOTE:  The following line in test_reasoner.py will need to be adjusted for your environment before running:

```
self.ontopilot_jar = '/Users/jdeck/IdeaProjects/ppo-data-pipeline/process/../lib/ontopilot-2017-08-04.jar' 
```

For now, talk to John if you want this JAR file, i have an issue to put in place a more robust
method for handling this dependency
