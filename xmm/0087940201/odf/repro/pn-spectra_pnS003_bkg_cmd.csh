evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)||(CCDNR == 8)||(CCDNR == 9)||(CCDNR == 10)||(CCDNR == 11)||(CCDNR == 12))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) )&&((DETX,DETY) IN circle(-2200,-1110,17980)) ' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=pnS003-obj-im-sp-det.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=780 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=780 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)||(CCDNR == 8)||(CCDNR == 9)||(CCDNR == 10)||(CCDNR == 11)||(CCDNR == 12))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) )&&((DETX,DETY) IN circle(-2200,-1110,17980)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-obj.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes 
rmfgen format=var rmfset=pnS003.rmf spectrumset=pnS003-obj.pi threshold=1.0e-6 
   
evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)||(CCDNR == 8)||(CCDNR == 9)||(CCDNR == 10)||(CCDNR == 11)||(CCDNR == 12))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) )&&((DETX,DETY) IN circle(-2200,-1110,17980)) ' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=detmap.ds squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=60 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=60 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes 
   
arfgen arfset=pnS003.arf spectrumset=pnS003-obj.pi withrmfset=yes rmfset=pnS003.rmf extendedsource=yes modelee=no withbadpixcorr=no detmaptype=dataset detmaparray=detmap.ds  badpixlocation=pnS003-clean.fits modelootcorr=no 
   
evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes  expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) ) &&((DETX,DETY) IN circle(-2200,-1110,17980))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-1obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479
   
backscale spectrumset=pnS003-1obj.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes 
   
evselect table=pnS003-clean-oot.fits:EVENTS withfilteredset=yes  expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) ) &&((DETX,DETY) IN circle(-2200,-1110,17980))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-1obj-oot.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479
   
backscale spectrumset=pnS003-1obj-oot.pi badpixlocation=pnS003-clean-oot.fits withbadpixcorr=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='((PI in [600:1300])||(PI in [1650:7200]))&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='((PI in [600:1300])||(PI in [1650:7200]))&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='(PI in [600:1300])&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='(PI in [1650:7200])&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='(PI in [600:1300])&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='(PI in [1650:7200])&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/pn-fwc-filt.fits.gz withfilteredset=yes withspectrumset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2200,-1110,17980))&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) )&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0)) ' spectrumset=pnS003-1ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-1ff.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/pn-fwc-oot-filt.fits.gz withfilteredset=yes withspectrumset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2200,-1110,17980))&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) )&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0)) ' spectrumset=pnS003-1ff-oot.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-1ff-oot.pi badpixlocation=pnS003-clean-oot.fits withbadpixcorr=yes 
   
evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes  expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) in BOX(5840.0,7115.0,8040.0,8210.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) ) &&((DETX,DETY) IN circle(-2200,-1110,17980))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-2obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479
   
backscale spectrumset=pnS003-2obj.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes 
   
evselect table=pnS003-clean-oot.fits:EVENTS withfilteredset=yes  expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) in BOX(5840.0,7115.0,8040.0,8210.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) ) &&((DETX,DETY) IN circle(-2200,-1110,17980))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-2obj-oot.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479
   
backscale spectrumset=pnS003-2obj-oot.pi badpixlocation=pnS003-clean-oot.fits withbadpixcorr=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='((PI in [600:1300])||(PI in [1650:7200]))&&((DETX,DETY) in BOX(5840.0,7115.0,8040.0,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='((PI in [600:1300])||(PI in [1650:7200]))&&((DETX,DETY) in BOX(5840.0,7115.0,8040.0,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='(PI in [600:1300])&&((DETX,DETY) in BOX(5840.0,7115.0,8040.0,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='(PI in [1650:7200])&&((DETX,DETY) in BOX(5840.0,7115.0,8040.0,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='(PI in [600:1300])&&((DETX,DETY) in BOX(5840.0,7115.0,8040.0,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='(PI in [1650:7200])&&((DETX,DETY) in BOX(5840.0,7115.0,8040.0,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/pn-fwc-filt.fits.gz withfilteredset=yes withspectrumset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2200,-1110,17980))&&((DETX,DETY) in BOX(5840.0,7115.0,8040.0,8210.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) )&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0)) ' spectrumset=pnS003-2ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-2ff.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/pn-fwc-oot-filt.fits.gz withfilteredset=yes withspectrumset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2200,-1110,17980))&&((DETX,DETY) in BOX(5840.0,7115.0,8040.0,8210.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) )&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0)) ' spectrumset=pnS003-2ff-oot.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-2ff-oot.pi badpixlocation=pnS003-clean-oot.fits withbadpixcorr=yes 
   
evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes  expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) in BOX(5840.0,-9311.0,8040.0,8216.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) ) &&((DETX,DETY) IN circle(-2200,-1110,17980))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-3obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479
   
backscale spectrumset=pnS003-3obj.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes 
   
evselect table=pnS003-clean-oot.fits:EVENTS withfilteredset=yes  expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) in BOX(5840.0,-9311.0,8040.0,8216.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) ) &&((DETX,DETY) IN circle(-2200,-1110,17980))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-3obj-oot.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479
   
backscale spectrumset=pnS003-3obj-oot.pi badpixlocation=pnS003-clean-oot.fits withbadpixcorr=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='((PI in [600:1300])||(PI in [1650:7200]))&&((DETX,DETY) in BOX(5840.0,-9311.0,8040.0,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='((PI in [600:1300])||(PI in [1650:7200]))&&((DETX,DETY) in BOX(5840.0,-9311.0,8040.0,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='(PI in [600:1300])&&((DETX,DETY) in BOX(5840.0,-9311.0,8040.0,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='(PI in [1650:7200])&&((DETX,DETY) in BOX(5840.0,-9311.0,8040.0,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='(PI in [600:1300])&&((DETX,DETY) in BOX(5840.0,-9311.0,8040.0,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='(PI in [1650:7200])&&((DETX,DETY) in BOX(5840.0,-9311.0,8040.0,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/pn-fwc-filt.fits.gz withfilteredset=yes withspectrumset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2200,-1110,17980))&&((DETX,DETY) in BOX(5840.0,-9311.0,8040.0,8216.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) )&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0)) ' spectrumset=pnS003-3ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-3ff.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/pn-fwc-oot-filt.fits.gz withfilteredset=yes withspectrumset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2200,-1110,17980))&&((DETX,DETY) in BOX(5840.0,-9311.0,8040.0,8216.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) )&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0)) ' spectrumset=pnS003-3ff-oot.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-3ff-oot.pi badpixlocation=pnS003-clean-oot.fits withbadpixcorr=yes 
   
evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes  expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) in BOX(-10241.5,-9311.0,8041.5,8216.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) ) &&((DETX,DETY) IN circle(-2200,-1110,17980))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-4obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479
   
backscale spectrumset=pnS003-4obj.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes 
   
evselect table=pnS003-clean-oot.fits:EVENTS withfilteredset=yes  expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) in BOX(-10241.5,-9311.0,8041.5,8216.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) ) &&((DETX,DETY) IN circle(-2200,-1110,17980))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-4obj-oot.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479
   
backscale spectrumset=pnS003-4obj-oot.pi badpixlocation=pnS003-clean-oot.fits withbadpixcorr=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='((PI in [600:1300])||(PI in [1650:7200]))&&((DETX,DETY) in BOX(-10241.5,-9311.0,8041.5,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='((PI in [600:1300])||(PI in [1650:7200]))&&((DETX,DETY) in BOX(-10241.5,-9311.0,8041.5,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='(PI in [600:1300])&&((DETX,DETY) in BOX(-10241.5,-9311.0,8041.5,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='(PI in [1650:7200])&&((DETX,DETY) in BOX(-10241.5,-9311.0,8041.5,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='(PI in [600:1300])&&((DETX,DETY) in BOX(-10241.5,-9311.0,8041.5,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='(PI in [1650:7200])&&((DETX,DETY) in BOX(-10241.5,-9311.0,8041.5,8216.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/pn-fwc-filt.fits.gz withfilteredset=yes withspectrumset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2200,-1110,17980))&&((DETX,DETY) in BOX(-10241.5,-9311.0,8041.5,8216.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) )&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0)) ' spectrumset=pnS003-4ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-4ff.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/pn-fwc-oot-filt.fits.gz withfilteredset=yes withspectrumset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2200,-1110,17980))&&((DETX,DETY) in BOX(-10241.5,-9311.0,8041.5,8216.0,0))&&( ((DETX,DETY) IN circle(-2537.1, -8487.6, 2400)) || ((DETX,DETY) IN circle(9176.2, -2181.3, 2400)) || ((DETX,DETY) IN circle(-13158.4, 3105.9, 2400)) || ((DETX,DETY) IN circle(8936.3, 6450.1, 2400)) || ((DETX,DETY) IN circle(-8620.6, -4355.9, 2400)) || ((DETX,DETY) IN circle(5031.1, 12283.9, 2400)) )&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0)) ' spectrumset=pnS003-4ff-oot.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-4ff-oot.pi badpixlocation=pnS003-clean-oot.fits withbadpixcorr=yes 
   
rm -f filtered.fits detmap.ds
   
