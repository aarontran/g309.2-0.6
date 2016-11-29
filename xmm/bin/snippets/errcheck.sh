#!/bin/bash

# Check for errors in all .log files in current or user-specified directory
# Default to current directory.  Accepts one argument only (ignores others)
if [ "$#" -lt 1 ]
then
    DIR="."
else
    DIR=$1
fi

# Check for presence of log files
FILES=`ls -trx ${DIR}/*.log`
if [ "$FILES" == "" ]
then
    echo "No log files found, exiting"
    exit 1
#else
#    echo "DEBUG"
#    echo $FILES
fi

grep -inTH -a --color=always --max-count=2 "error" ${FILES} | sed '/evselect:- Executing (routine)/d'

