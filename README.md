# Broccoli

<img src="https://github.com/mcmartins/parallel-jobs/blob/master/docs/broccoli.png" alt="logo" width="200px" height="200px">

# README

The tool should be able to start a set of processes in parallel and stop when one of these processes finishes.
Multiple processes can generate multiple processes and so on.

# API

The tool should accept as input a JSON or XML String/File, parse it and start the processing.

The input JSON/XML should include information such as:

* For each process to execute:
 1. Which command to execute;
 2. What are the inputs;
 3. Path to output;
 4. Timeout;
 5. ...

## Integration with WebGAP

A node.js module should be produced in order to wrap the python tool. This tool will be used as an asynchronous job executor.

# Diagrams

Application Flow Diagram:

![alt text](https://github.com/mcmartins/parallel-jobs/blob/master/docs/flow.png)

# LICENSE

Apache License, Version 2.0
