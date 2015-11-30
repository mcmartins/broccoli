# Broccoli

[![Build Status](https://travis-ci.org/mcmartins/broccoli.svg)](https://travis-ci.org/mcmartins/broccoli)

<img src="https://github.com/mcmartins/parallel-jobs/blob/master/docs/broccoli.png" alt="logo" width="200px" height="200px">

# README

This tool handles Jobs. A Job is constituted by a set of Tasks.
Each Task can have Children Tasks and so on, forming a kind of Tree.
Top Level Tasks will run in parallel and Children Tasks will follow as soon parent Tasks finishes.
The processing finishes when one top level Task finishes executing (including, if any, all its Children Tasks).
Each Task might need preparation, so Tasks are resolved into Sub Tasks before execution. 

# API

This tool accepts as input a JSON String/File, parses it and starts the processing.

The input JSON includes the following information:

* A Job to execute:
 1. Name to identify the Job
 2. Description to best describe the Job
 3. Working directory where the Job will run, and all the output will be stored (if not specified otherwise)
 4. Timeout in seconds to kill the Job if exceeds
 5. List of Tasks that constitute the Job

* For each Task:
 1. Name o identify the Task
 2. Description to best describe the Task
 3. Preparation step where the user can define what to do before running the commands in the form of Sub Tasks
 4. Command the actual command to execute and accomplish the Task
 5. List of Children Tasks circular dependency for other Tasks

## Example Input

The input follows a schema [Schema](https://github.com/mcmartins/broccoli/blob/master/broccoli/schema/broccoli_schema.json).<br/>
An example of an input would be something like:

```json
{
    "jobName": "Job1",
    "jobDescription": "Job1 Description",
    "workingDir": "/tmp",
    "timeout": 100,
    "tasks": [
        {
            "taskName": "T1",
            "taskDescription": "T1 Description",
            "wait": false,
            "timeout": 10,
            "commands": [
                "prover9 -f Axioms.in > Axioms.out"
            ],
            "children": [
                {
                    "taskName": "T1.1",
                    "taskDescription": "T1.1 Description",
                    "wait": false,
                    "timeout": 10,
                    "preparation": {
                        "filterFile": "Axioms.out",
                        "pattern": "^given.*?T.*?:\\s*\\d+([^.\\#]*.)",
                        "writeFile": "New_Axioms.in",
                        "placeholder": "$placeholder",
                        "copy": true
                    },
                    "commands": [
                        "prover9 -f $file > $file_prover.out",
                        "mace4 -f $file > $file_mace.out"
                    ]
                },
                {
                    "taskName": "T1.2",
                    "taskDescription": "T1.2 Description",
                    "wait": false,
                    "timeout": 10,
                    "preparation": {
                        "searchDirectory": "/fancy_dir",
                        "pattern": "*.in"
                    },
                    "commands": [
                        "prover9 -f $file > $file_prover.out",
                        "mace4 -f $file > $file_mace.out"
                    ]
                }
            ]
        },
        {
            "taskName": "T2",
            "taskDescription": "T2 Description",
            "wait": false,
            "timeout": 10,
            "commands": [
                "prover9 -f Axioms.in > Axioms.out"
            ]
        }
    ]
}

```

## Integration with WebGAP

A node.js module should be produced in order to wrap the python tool. This tool will be used as an asynchronous job executor.
The tool will be invoked over the WebGAP API and will run inside docker containers.

# Diagrams - TBU

Application Flow Diagram:

![alt text](https://github.com/mcmartins/broccoli/blob/master/docs/flow.png)

Job Diagram

![alt text](https://github.com/mcmartins/broccoli/blob/master/docs/job.png)

# Tests

There are 3 TestCases:

Run basic example from the course examples;

Run example with guidance:

![alt text](https://github.com/mcmartins/broccoli/blob/master/docs/test_job.png)

Run task with preparation;

## How to setup environment

Using a RHEL based system, CentOS 7, execute the following steps:

```bash
# assuming we're going to use the user home as working directory to download and install everything
# download prover9 software
wget https://www.cs.unm.edu/~mccune/prover9/download/LADR-2009-11A.tar.gz
# unpack
tar -xzf LADR-2009-11A.tar.gz
# remove tar
rm LADR-2009-11A.tar.gz
# go to folder and compile
cd LADR-2009-11A/
make all
# as root add prover9 to path (change path accordingly)
su -
echo 'pathmunge /home/user/LADR-2009-11A/bin' > /etc/profile.d/LADR.sh
chmod +x /etc/profile.d/LADR.sh
# go to home and download broccoli
su - user
git clone https://github.com/mcmartins/broccoli.git
```

## Install & Run

### Install module

```bash
sudo python setup.py build install
```

### Run module

```bash
python -m broccoli -v -i /path/to/<input.json>
# or
python -m broccoli -v -i '<JSON>'
```

# Missing

* Make available a Test Environment Package (it can be a docker image)
* Sanitize all input / Assess Security (Webgap will run in containers but this tool itself allows to execute commands like 'rm -rf /')
* Support piping Tasks by stdout. At the moment only Tasks generating files for Guidance Tasks is implemented.
* ...

# LICENSE

Apache License, Version 2.0
