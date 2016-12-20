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

grep -inTH -a --color=always "error" ${FILES} | sed '/evselect:- Executing (routine)/d' \
  | sed '/emldetect:- Executing (routine)/d' \
  | sed '/Final parameter values and the formal standard/d' \
  | perl -ne 'print unless /POISSERR\s*-\s*(TRUE|FALSE)\s*Whether Poissonian/;' \
  | perl -ne 'print unless /STAT_ERR\s*-\s*(TRUE|FALSE)\s*Statistical/;' \
  | perl -ne 'print unless /SYS_ERR\s*-\s*(TRUE|FALSE)\s*Fractional Systematic/;' \
  | perl -ne 'print unless /(Rate|Hard):\s*[0-9.Ee-]+\s*/;'

