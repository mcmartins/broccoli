# Broccoli

<img src="https://github.com/mcmartins/parallel-jobs/blob/master/docs/broccoli.png" alt="logo" width="200px" height="200px">

# README

This tool handles Jobs. A Job is constituted by a set of Tasks.
Each Task can have Guidance Tasks (Sub Tasks) and so on, forming a kind of Tree.
Top Level Tasks will run in parallel and Guidance Tasks will follow as soon parent Tasks finishes.
The processing finishes when one top level Task finishes executing (including, if any, all its Guidance Tasks).

# API

This tool accepts as input a JSON String/File, parses it and starts the processing.

The input JSON includes the following information:

* A Job to execute:
 1. Name to identify the Job
 2. Working directory where the Job will run, and all the output will be stored (if not specified otherwise)
 3. Timeout in seconds to kill the Job if exceeds
 4. List of Tasks that constitute the Job

* For each Task:
 1. Name o identify the Task
 2. Command the actual command to execute and accomplish the Task
 3. Wait if the Task should wait for the output of another (at the moment is not possible to use stdout from a Task to it Sub Tasks and thus making this obsolete)
 4. List of Sub Tasks (Guidance) circular dependency for other Tasks

## Example Input

The input can be something like:

```json
{
  "jobName": "Boolean Algebra 2-Basis",
  "workingDir": "/tmp/",
  "timeout": 60,
  "tasks": [
    {
      "taskName": "T1 - Get guiding interpretation",
      "wait": false,
      "command": "mace4 -n6 -m -1 -f BA2-interp.in | get_interps | isofilter ignore_constants wrap > BA2-interp.out",
      "guidance": [
        {
          "taskName": "T1.1 - Task with guidance (20 seconds)",
          "command": "prover9 -f BA2.in BA2-interp.out > BA2.out",
          "wait": false
        }
      ]
    },
    {
      "taskName": "T2 - Task without guidance (46 seconds)",
      "command": "prover9 -f BA2.in > BA2-base.out",
      "wait": false
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

# Install & Run

## Install module

```bash
sudo python setup.py build install
```

## Run module

```bash
python -m broccoli -v -i /path/to/input.json
# or
python -m broccoli -v -i '<JSON>'
```

# Missing

* Make available a Test Environment Package (it can be a docker image)
* Tests implementation
* Sanitize all input / Assess Security (Webgap will run in containers but this tool itself allows to execute commands like 'rm -rf /')
* Support piping Tasks by stdout. At the moment only Tasks generating files for Guidance Tasks is implemented.
* Multiprocessing  implementation
* ...

# LICENSE

Apache License, Version 2.0
