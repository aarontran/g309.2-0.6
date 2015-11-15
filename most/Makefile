
# Simple downloader for MOST radio data
# may eventually extend to simple analysis (contour extraction)
# Aaron Tran, 2015 Nov 13

SNR = G309.2-0.6

.PHONY : all
all : $(SNR).fits $(SNR).jpg $(SNR).ps

.PHONY : clean
clean :
	rm -f $(SNR).fits $(SNR).jpg $(SNR).ps

%.ps :
	curl -o $@.gz http://www.physics.usyd.edu.au/astrop/wg96cat/ps/$@.gz
	gunzip $@.gz

%.jpg :
	curl -o $@ http://www.physics.usyd.edu.au/astrop/wg96cat/jpeg/$@

%.fits :
	curl -o $@.gz http://www.physics.usyd.edu.au/astrop/wg96cat/fits/$@.gz
	gunzip $@.gz
