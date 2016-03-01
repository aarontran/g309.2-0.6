FFLAGS = -e -O -C
# -e : accept extended (132 character) source lines
# -O : optimize
# -C : check array references for out of range subscripts
# -o : target output file

rot_inv : rot_inv.o findends.o
	f77 $(FFLAGS)  -o rot_inv rot_inv.o findends.o `mirlibs` 
