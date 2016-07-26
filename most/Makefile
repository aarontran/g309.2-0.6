
# Simple downloader for MOST radio data
# may eventually extend to simple analysis (contour extraction)
# Aaron Tran, 2015 Nov 13

SNR = G309.2-0.6
DLOBJS = $(SNR).fits $(SNR).jpg $(SNR).ps

OBJS = $(SNR)_linear.con $(SNR)_log_sparse.con

.PHONY : all
all : $(DLOBJS) $(OBJS)

.PHONY : clean
clean :
	rm -f $(DLOBJS) $(OBJS)

# Using makefile as dependency in this case is not great, but it'll do...
$(SNR)_linear.con : $(SNR).fits linear.lev
	ds9 $< \
	    -contour yes \
	    -contour smooth 1 \
	    -contour loadlevels linear.lev \
	    -contour save $@ wcs fk5 -exit

$(SNR)_log_sparse.con : $(SNR).fits log_sparse.lev
	ds9 $< \
	    -contour yes \
	    -contour smooth 1 \
	    -contour loadlevels log_sparse.lev \
	    -contour save $@ wcs fk5 -exit

%.ps :
	curl -o $@.gz http://www.physics.usyd.edu.au/astrop/wg96cat/ps/$@.gz
	gunzip $@.gz

%.jpg :
	curl -o $@ http://www.physics.usyd.edu.au/astrop/wg96cat/jpeg/$@

%.fits :
	curl -o $@.gz http://www.physics.usyd.edu.au/astrop/wg96cat/fits/$@.gz
	gunzip $@.gz
