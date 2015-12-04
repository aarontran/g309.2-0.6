evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN <= 4)&&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)||(CCDNR == 8)||(CCDNR == 9)||(CCDNR == 10)||(CCDNR == 11)||(CCDNR == 12))&&((FLAG & 0x762a097c) == 0)&&!((DETX,DETY) IN circle(-2200,-1110,18200))' filtertype=expression keepfilteroutput=yes updateexposure=yes  filterexposure=yes filteredset=pnS003-corn.fits
   
evselect table=pnS003-clean-oot.fits:EVENTS withfilteredset=yes expression='(PATTERN <= 4)&&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)||(CCDNR == 8)||(CCDNR == 9)||(CCDNR == 10)||(CCDNR == 11)||(CCDNR == 12))&&((FLAG & 0x762a097c) == 0)&&!((DETX,DETY) IN circle(-2200,-1110,18200))' filtertype=expression keepfilteroutput=yes updateexposure=yes  filterexposure=yes filteredset=pnS003-corn-oot.fits
   
evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&(PI in [400:7200])&&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)||(CCDNR == 8)||(CCDNR == 9)||(CCDNR == 10)||(CCDNR == 11)||(CCDNR == 12))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) IN circle(-2200,-1110,17980)) ' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=pnS003-obj-im.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='X' ximagesize=900 ximagemax=48400 ximagemin=3401 ycolumn='Y' yimagesize=900 yimagemax=48400 yimagemin=3401 updateexposure=yes filterexposure=yes 
   
eexpmap attitudeset=atthk.fits eventset=pnS003-clean.fits:EVENTS expimageset=pnS003-exp-im.fits imageset=pnS003-obj-im.fits pimax=10000 pimin=300 withdetcoords=no 
   
emask detmaskset=pnS003-mask-im.fits expimageset=pnS003-exp-im.fits threshold1=0.01 threshold2=5.0 
   
evselect table=pnS003-clean-oot.fits:EVENTS withfilteredset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&(PI in [400:7200])&&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)||(CCDNR == 8)||(CCDNR == 9)||(CCDNR == 10)||(CCDNR == 11)||(CCDNR == 12))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) IN circle(-2200,-1110,17980)) ' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=pnS003-obj-im-oot.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='X' ximagesize=900 ximagemax=48400 ximagemin=3401 ycolumn='Y' yimagesize=900 yimagemax=48400 yimagemin=3401 updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)||(CCDNR == 8)||(CCDNR == 9)||(CCDNR == 10)||(CCDNR == 11)||(CCDNR == 12))&&((DETX,DETY) IN circle(-2489.4, 4712.3, 4795.2))&&((DETX,DETY) IN circle(-2200,-1110,17980)) ' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=pnS003-obj-im-sp-det.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=780 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=780 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)||(CCDNR == 8)||(CCDNR == 9)||(CCDNR == 10)||(CCDNR == 11)||(CCDNR == 12))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) IN circle(-2489.4, 4712.3, 4795.2))&&((DETX,DETY) IN circle(-2200,-1110,17980)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-obj.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes 
evselect table=pnS003-clean-oot.fits:EVENTS withfilteredset=yes  expression='(PATTERN <= 4)&&(FLAG == 0)&&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)||(CCDNR == 8)||(CCDNR == 9)||(CCDNR == 10)||(CCDNR == 11)||(CCDNR == 12))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) IN circle(-2489.4, 4712.3, 4795.2))&&((DETX,DETY) IN circle(-2200,-1110,17980)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-obj-oot.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479
   
backscale spectrumset=pnS003-obj-oot.pi badpixlocation=pnS003-clean-oot.fits withbadpixcorr=yes 
rmfgen format=var rmfset=pnS003.rmf spectrumset=pnS003-obj.pi threshold=1.0e-6 
   
evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN <= 4)&&(FLAG == 0)&&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)||(CCDNR == 8)||(CCDNR == 9)||(CCDNR == 10)||(CCDNR == 11)||(CCDNR == 12))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) IN circle(-2489.4, 4712.3, 4795.2))&&((DETX,DETY) IN circle(-2200,-1110,17980)) ' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=detmap.ds squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=60 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=60 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes 
   
arfgen arfset=pnS003.arf spectrumset=pnS003-obj.pi withrmfset=yes rmfset=pnS003.rmf extendedsource=yes modelee=no withbadpixcorr=no detmaptype=dataset detmaparray=detmap.ds  badpixlocation=pnS003-clean.fits modelootcorr=no 
   
evselect table=pnS003-clean.fits:EVENTS withfilteredset=yes  expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) IN circle(-2489.4, 4712.3, 4795.2)) &&((DETX,DETY) IN circle(-2200,-1110,17980))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-1obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479
   
backscale spectrumset=pnS003-1obj.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes 
   
evselect table=pnS003-clean-oot.fits:EVENTS withfilteredset=yes  expression='(PATTERN <= 4)&&(FLAG == 0)&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) IN circle(-2489.4, 4712.3, 4795.2)) &&((DETX,DETY) IN circle(-2200,-1110,17980))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=pnS003-1obj-oot.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479
   
backscale spectrumset=pnS003-1obj-oot.pi badpixlocation=pnS003-clean-oot.fits withbadpixcorr=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN <= 4)&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&!((DETX,DETY) IN circle(-2200,-1110,18200))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=pnS003-1oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-1oc.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=pnS003-corn-oot.fits:EVENTS expression='(PATTERN <= 4)&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))&&!((DETX,DETY) IN circle(-2200,-1110,18200))' filtertype=expression withfilteredset=yes keepfilteroutput=no withspectrumset=yes spectrumset=pnS003-1oc-oot.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 
   
backscale spectrumset=pnS003-1oc-oot.pi badpixlocation=pnS003-clean.fits withbadpixcorr=yes  ignoreoutoffov=no
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='((PI in [600:1300])||(PI in [1650:7200]))&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='((PI in [600:1300])||(PI in [1650:7200]))&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='(PI in [600:1300])&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn.fits:EVENTS withfilteredset=yes expression='(PI in [1650:7200])&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='(PI in [600:1300])&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=pnS003-corn-oot.fits:EVENTS withfilteredset=yes expression='(PI in [1650:7200])&&((DETX,DETY) in BOX(-10241.5,7115.0,8041.5,8210.0,0))&&((DETX,DETY) in BOX(-2196,-1110,16060,15510,0))' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
