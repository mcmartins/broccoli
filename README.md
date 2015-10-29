# Broccoli

<img src="https://github.com/mcmartins/parallel-jobs/blob/master/docs/broccoli.png" alt="logo" width="200px" height="200px">

# README

The tool should be able to start a Job. The Job is constituted by a set of Tasks.
These Tasks can have Guidance Tasks (Sub Tasks) and so on, forming a kind of Tree.
Top Level Tasks will run in parallel and Guidance Tasks will follow as soon parent Tasks finishes.
The processing finishes when one top level Task finishes executing (including, if any, all its Guidance Tasks).

# API

The tool should accept as input a JSON String/File, parse it and start the processing.

The input JSON includes the following information:

* A Job to execute:
 1. Name
 2. Working directory
 3. Timeout to kill the Job
 4. List of Tasks

* For each Task:
 1. Name
 2. Command to Execute
 3. Wait if the Task should wait for the output of another (at the moment is not possible to use stdout from a Task to it Sub Tasks)
 4. List of Sub Tasks (Guidance)

## Example Input

The input will be something like:

```json
{
  "jobName": "Boolean Algebra 2-Basis",
  "workingDir": "/tmp/",
  "timeout": 60,
  "tasks": [
    {
      "taskName": "Get guiding interpretation",
      "wait": false,
      "command": "mace4 -n6 -m -1 -f BA2-interp.in | get_interps | isofilter ignore_constants wrap > BA2-interp.out",
      "guidance": [
        {
          "taskName": "Job with guidance (20 seconds)",
          "wait": false,
          "command": "prover9 -f BA2.in BA2-interp.out > BA2.out"
        }
      ]
    },
    {
      "taskName": "Job without guidance (46 seconds)",
      "wait": false,
      "command": "prover9 -f BA2.in > BA2-base.out"
    }
  ]
}
```

## Integration with WebGAP

A node.js module should be produced in order to wrap the python tool. This tool will be used as an asynchronous job executor.
The tool will be invoked over the WebGAP API and will run inside docker containers.

# Diagrams

Application Flow Diagram:

![alt text](https://github.com/mcmartins/parallel-jobs/blob/master/docs/flow.png)

Job Diagram

![alt text](https://github.com/mcmartins/parallel-jobs/blob/master/docs/job.png)

# Test

The following Job is being used as TestCase:

![alt text](https://github.com/mcmartins/parallel-jobs/blob/master/docs/test_job.png)

# Missing

* Make available a Test Environment Package (it can e a docker image)
* Tests implementation
* Sanitize all input / Assess Security (Webgap will run in containers but this tool itself allows to execute commands like 'rm -rf /')
* Support piping Tasks by stdout. At the moment only Tasks generating files for Guidance Tasks is implemented.
* Multi-thread implementation
* ...

# LICENSE

Apache License, Version 2.0
