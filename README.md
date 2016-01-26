# Broccoli

[![Build Status](https://travis-ci.org/mcmartins/broccoli.svg)](https://travis-ci.org/mcmartins/broccoli)
[![Code Climate](https://codeclimate.com/github/mcmartins/broccoli/badges/gpa.svg)](https://codeclimate.com/github/mcmartins/broccoli)
[![Issue Count](https://codeclimate.com/github/mcmartins/broccoli/badges/issue_count.svg)](https://codeclimate.com/github/mcmartins/broccoli)

<img src="https://github.com/mcmartins/parallel-jobs/blob/master/docs/broccoli.png" alt="logo" width="200px" height="200px">

# README

Broccoli is a concurrent Job executor. It allows an user to save time and money when running concurrent software on HPC.

## Assumpptions

1. A user has a long process to run</br>
1a. A user has a sequence of processes to run</br>
2. A user runs it on a rented platform</br>
2a. Costs are based on a per resources usage

## Use Cases

A user is writing a new paper on a new theory. He needs to test his theory by finding a proof or counter proof. The user can simply run prover9 and mace4 for this. He can execute his theory within the prover9 and try to find a counter proof on mace4 at the same time, in parallel, by executing the two proceses. The processing may take days running and uses a fair amount of resources, so he is using a rented cloud HPC infrastructure. By taking an uncertain amount of time, these processes, and in order to save resources (and thus money), the user can simply configure *broccoli* for running these tasks in parallel. *Broccoli* will ensure that when a proof or counter proof is found, e.g. the first Task that finishes with success, all tasks started for the study are cancelled/killed/stoped in order to save computing resources.

```json
{
  "jobName": "MyFirstBroccoli",
  "jobDescription": "Search for a proof or counter proof for my new theory.",
  "workingDir": "/tmp/",
  "timeout": 259200,
  "tasks": [
    {
      "taskName": "T1",
      "taskDescription": "Generate Consequences from a predefined Theory.",
      "wait": false,
      "failTolerant": false,
      "commands": [
        "prover9 -f Input.p9 > Prover.out",
        "mace4 -f Input.m4 > Mace.out"
      ],
      "children": [
        {
          "taskName": "T1.1.1",
          "taskDescription": "For each Prover9/Mace4 output check for proofs found and notify PI.",
          "wait": false,
          "commands": [
            "for file in `grep -rl PROVED --exclude='*.json' --exclude='*.log' .`; do sendmail user@example.com  < $file; done"
          ]
        }
      ]
    }
  ]
}
```

# API

## Description

This tool handles Jobs. A Job is constituted by a set of Tasks.
Each Task has Children Tasks and so on.
Top Level Tasks will run in parallel and Children Tasks will follow as soon parent Tasks finishes.
The processing finishes when one top level Task finishes executing (including, if any, all its Children Tasks).
Each Task might need preparation, so Tasks are resolved into Sub Tasks before execution. 

This tool accepts as input a JSON String/File, parses it and starts the processing.

The input JSON includes the following information:

* A Job to execute:
 1. Name to identify the Job
 2. Description to best describe the Job
 3. Working directory where the Job will run, and all the output will be stored (if not specified otherwise)
 4. Timeout in seconds to kill the Job if exceeds
 5. List of Tasks that constitute the Job

* For each Task:
 1. Name to identify the Task
 2. Description to best describe the Task
 3. Preparation step where the user can define what to do before running the commands in the form of Sub Tasks
 4. Command the actual command to execute and accomplish the Task
 5. List of Children Tasks circular dependency for other Tasks

## Example Input

The input follows the following JSON [Schema](https://github.com/mcmartins/broccoli/blob/master/broccoli/schema/broccoli_schema.json).<br/>
An example of an input would be something like:

```json
{
  "jobName": "Consequences",
  "jobDescription": "Search for new Theories.",
  "workingDir": "/tmp/autonomous",
  "timeout": 10000,
  "tasks": [
    {
      "taskName": "T1",
      "taskDescription": "Generate Consequences from a predefined Theory.",
      "wait": false,
      "failTolerant": true,
      "commands": [
        "../LADR-2009-11A/bin/prover9 -f Theory.in > Consequences.out"
      ],
      "children": [
        {
          "taskName": "T1.1",
          "taskDescription": "For each consequence found, replace in original Theory and Run prover/mace to find new Theories.",
          "wait": false,
          "failTolerant": true,
          "preparation": {
            "filterFile": "Consequences.out",
            "pattern": "^given.*?T.*?:\\s*\\d+([^.\\#]*.)",
            "writeFile": "New-Theory-*.in",
            "placeholder": "$placeholder",
            "copy": true
          },
          "commands": [
            "../LADR-2009-11A/bin/prover9 -f $file > $file_prover.out",
            "../LADR-2009-11A/bin/mace4 -f $file > $file_mace.out"
          ],
          "children": [
            {
              "taskName": "T1.1.1",
              "taskDescription": "For each Prover9/Mace4 output check for proofs found.",
              "wait": false,
              "commands": [
                "grep -rl PROVED --exclude='*.json' --exclude='*.log' . && echo 'New Theories Found.' || echo 'No new Theories Found.'"
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

This input will look for equivalent theories by replacing Concequences in the original Theory. It will run 2 commands in parallel and if a proof or counterproof is found, the other command will be killed. It will do this for each Consequence.

## Integration with WebGAP

A node.js module should be produced in order to wrap the python tool. This tool will be used as an asynchronous job executor.
The tool will be invoked over the WebGAP API and will run inside docker containers.

# Diagrams

Application Flow Diagram:

![alt text](https://github.com/mcmartins/broccoli/blob/master/docs/flow.png)

Job Diagram

![alt text](https://github.com/mcmartins/broccoli/blob/master/docs/job.png)

# Tests

These Test Cases can be viewed on [Tests Source](https://github.com/mcmartins/broccoli/tree/master/broccoli/test) / [Travis CI](https://travis-ci.org/mcmartins/broccoli)

# Online Input Editor

WebGAP will have his own input editor. While is not available, the input for broccoli can be generated here: [Input Form](http://jeremydorn.com/json-editor/?schema=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&value=N4IgVg9gRgcghgWwKYgFwgMIQHYGckCOArktgMZK4gA040AIpWQE4CWADgC6s5ogDKSOMzIALAAQAzCM3HYkAd3EAVUUhmtKAOhogFMgNatsAc3qtmfAPScE7K3CKccEBBCJVa3ZO85oAjAAMwYFecLgGVKgA2qCc4QbwyHzK/rrxEYy4LBzcvOgA4qRIzHCcSOJYeIQk5JRSzK7icOLszEgAJkiSxp0qajIAnjq0CnCsfqiScAA2+LTTrDPKEDMlcNiTnMwktGSuCBsdUdEgWlpWADIAgvQASgC0AEzBAJwP/v7XVlDGVm0QABuJVe4gekn66mYw2M4gAfJUcPhiKQKLgtL4QABdPaiJYddrYNCxEAZRKIFDoVJaNJhTJMNhcHhE9AAMRk4iEYnE+2qKLqUnc2A61HE7XYMzgFHEsI0JmMs0hQ2awvEdyI2FajWBzCsh2lzikxg6ckUSrY2l0YwmaGmcyQC3Gy1W602aG2uxAbSQ7GEZWZaFAPRm5WYrKWlMwSJqqO0mNovs4oZZIAAevLgdgtAAqAD8yhzudQAB1i7hs6WOgBqAAU0VTWlLAGIsdmtABKK1scrhtZ8GCKB6qKGDB5t4y6CVSpCiVZdSzoAAkU4os5m890+3Yg3dOyQAF89gcjiczhcbvdnm8Pl8fn8ATrQeDxIvgxUEa+IwB9B8lDFOXRziuW5HheQJ3k+b5fmwPVpwAFjBCFPzWeEXzfL99SQf8/BxEAxHxQliTiBIkkjal/BpdIEiyHImXyEB2VkLkJAABW1EErAAWXg8RfHYJweTUMgDEFWQAQgSRcEFDUOhGPRxkmO15jw49hVPExxTBZgZnEFi7gAeQANQAUXoMEHiQAAPMgZiILoAF4AHI2zAXAcEc8yrJsuykCctsZggEwPK0cQADJQs5MQIHERyByUYcNHqdkZK0DyAB80si2cYpgaL5HigYLSk5LhVS7F9yxCqqqAAAA=&theme=foundation5&iconlib=fontawesome4&object_layout=normal&show_errors=interaction&disable_edit_json&disable_properties&disable_array_reorder)

# How to setup environment

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

# Future Tasks

* Make available a Test Environment Package (it can be a docker image)
* Support piping Tasks by stdout. At the moment only Tasks generating files for Guidance Tasks is implemented.

# LICENSE

Apache License, Version 2.0
