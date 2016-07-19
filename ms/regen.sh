#!/bin/sh

fname="text"

# Run bibtex if any command line arg given (gibberish OK)
if [[ "$#" -eq 1 ]]; then
  pdflatex "${fname}.tex" 
  bibtex $fname
fi
pdflatex "${fname}.tex"
pdflatex "${fname}.tex"

# Only "deploy" on HEAD computer
if [[ $HOSTNAME == 'treble' ]]; then
  cp "${arg}.pdf" /data/wdocs/atran/g309/.
fi


