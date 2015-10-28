# Broccoli

<img src="https://github.com/mcmartins/parallel-jobs/blob/master/docs/broccoli.png" alt="logo" width="200px" height="200px">

# README

The tool should be able to start a Job. The Job is constituted by a set of Tasks.
These Tasks can have Guidance Tasks and so on, forming a kind of Tree.
Each Task at the same Level in the Tree will run in parallel.
The processing finishes when one top level Task finishes executing (including, if any, all its guidance).

# API

The tool should accept as input a JSON String/File, parse it and start the processing.

The input JSON includes the following information:

* For each Job to execute:
 1. Name
 2. Working directory;
 3. Timeout;
 4. Tasks

* For each Task
 1. Name
 2. Command
 3. Wait
 4. Sub Tasks (Guidance)

## Integration with WebGAP

A node.js module should be produced in order to wrap the python tool. This tool will be used as an asynchronous job executor.
The tool will be invoked over the WebGAP API and will run inside a docker container.

# Diagrams

Application Flow Diagram:

![alt text](https://github.com/mcmartins/parallel-jobs/blob/master/docs/flow.png)

# LICENSE

Apache License, Version 2.0
