evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0) &&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)) &&(PI in [300:8000])' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=mos2S002-obj-im.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='X' ximagesize=900 ximagemax=48400 ximagemin=3401 ycolumn='Y' yimagesize=900 yimagemax=48400 yimagemin=3401 updateexposure=yes filterexposure=yes
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0))) &&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=mos2S002-obj-im-sp-det.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=780 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=780 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
eexpmap attitudeset=atthk.fits eventset=mos2S002-clean.fits:EVENTS expimageset=mos2S002-exp-im.fits imageset=mos2S002-obj-im.fits pimax=8000 pimin=300 withdetcoords=no
   
emask detmaskset=mos2S002-mask-im.fits expimageset=mos2S002-exp-im.fits threshold1=0.01 threshold2=0.5
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2)) &&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0))) ' imagebinning='imageSize' imagedatatype='Int32' imageset=detmap.ds squarepixels=yes ignorelegallimits=no withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=120 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=120 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
rmfgen format=var rmfset=mos2S002.rmf spectrumset=mos2S002-obj.pi threshold=1.0e-6 detmaptype=dataset detmaparray=detmap.ds
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0))) ' imagebinning='imageSize' imagedatatype='Int32' imageset=detmap.ds squarepixels=yes ignorelegallimits=no withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=120 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=120 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
arfgen arfset=mos2S002.arf spectrumset=mos2S002-obj.pi withrmfset=yes rmfset=mos2S002.rmf extendedsource=yes modelee=no withbadpixcorr=no detmaptype=dataset detmaparray=detmap.ds  badpixlocation=mos2S002-clean.fits modelootcorr=no
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN BOX(20,-60,6610,6590,0)) &&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))' withspectrumset=yes spectrumset=mos2S002-1ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-1ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) IN BOX(20,-60,6610,6590,0))&&(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0))) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-1obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-1obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) IN BOX(6580,-13530,6620,6640,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-2oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-2oc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(6580,-13530,6620,6640,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-2obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-2obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6580,-13530,6620,6640,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6580,-13530,6620,6640,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6580,-13530,6620,6640,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6580,-13530,6620,6640,0))&&!(((DETX,DETY) IN CIRCLE(435,1006,17100))||((DETX,DETY) IN CIRCLE(-34,68,17700))||((DETX,DETY) IN BOX(-20,-17000,6500,500,0))||((DETX,DETY) IN BOX(5880,-20500,7500,1500,10))||((DETX,DETY) IN BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) IN BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-2fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-2fc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(6580,-13530,6620,6640,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-2ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-2ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) IN BOX(13320,-295,6620,6590,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-3oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-3oc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(13320,-295,6620,6590,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-3obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-3obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(13320,-295,6620,6590,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(13320,-295,6620,6590,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(13320,-295,6620,6590,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(13320,-295,6620,6590,0))&&!(((DETX,DETY) IN CIRCLE(435,1006,17100))||((DETX,DETY) IN CIRCLE(-34,68,17700))||((DETX,DETY) IN BOX(-20,-17000,6500,500,0))||((DETX,DETY) IN BOX(5880,-20500,7500,1500,10))||((DETX,DETY) IN BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) IN BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-3fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-3fc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(13320,-295,6620,6590,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-3ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-3ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) IN BOX(6610,13110,6590,6550,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-4oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-4oc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(6610,13110,6590,6550,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-4obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-4obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6610,13110,6590,6550,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6610,13110,6590,6550,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6610,13110,6590,6550,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6610,13110,6590,6550,0))&&!(((DETX,DETY) IN CIRCLE(435,1006,17100))||((DETX,DETY) IN CIRCLE(-34,68,17700))||((DETX,DETY) IN BOX(-20,-17000,6500,500,0))||((DETX,DETY) IN BOX(5880,-20500,7500,1500,10))||((DETX,DETY) IN BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) IN BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-4fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-4fc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(6610,13110,6590,6550,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-4ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-4ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) IN BOX(-6560,13180,6590,6600,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-5oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-5oc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-6560,13180,6590,6600,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-5obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-5obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6560,13180,6590,6600,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6560,13180,6590,6600,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6560,13180,6590,6600,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6560,13180,6590,6600,0))&&!(((DETX,DETY) IN CIRCLE(435,1006,17100))||((DETX,DETY) IN CIRCLE(-34,68,17700))||((DETX,DETY) IN BOX(-20,-17000,6500,500,0))||((DETX,DETY) IN BOX(5880,-20500,7500,1500,10))||((DETX,DETY) IN BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) IN BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-5fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-5fc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-6560,13180,6590,6600,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-5ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-5ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) IN BOX(-13190,-90,6600,6630,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-6oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-6oc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-13190,-90,6600,6630,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-6obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-6obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-13190,-90,6600,6630,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-13190,-90,6600,6630,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-13190,-90,6600,6630,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-13190,-90,6600,6630,0))&&!(((DETX,DETY) IN CIRCLE(435,1006,17100))||((DETX,DETY) IN CIRCLE(-34,68,17700))||((DETX,DETY) IN BOX(-20,-17000,6500,500,0))||((DETX,DETY) IN BOX(5880,-20500,7500,1500,10))||((DETX,DETY) IN BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) IN BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-6fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-6fc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-13190,-90,6600,6630,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-6ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-6ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-7oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-7oc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-7obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-7obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0))&&!(((DETX,DETY) IN CIRCLE(435,1006,17100))||((DETX,DETY) IN CIRCLE(-34,68,17700))||((DETX,DETY) IN BOX(-20,-17000,6500,500,0))||((DETX,DETY) IN BOX(5880,-20500,7500,1500,10))||((DETX,DETY) IN BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) IN BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos2S002-7fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-7fc.pi useodfatt=no badpixlocation=mos2S002-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-7ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-7ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
backscale spectrumset=mos2S002-7ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
