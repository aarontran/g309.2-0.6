evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0) &&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7)) &&(PI in [300:8000])' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=mos1S001-obj-im.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='X' ximagesize=900 ximagemax=48400 ximagemin=3401 ycolumn='Y' yimagesize=900 yimagemax=48400 yimagemin=3401 updateexposure=yes filterexposure=yes
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152))) &&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=mos1S001-obj-im-sp-det.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=780 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=780 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
atthkgen atthkset=atthk.fits timestep=1 
   
eexpmap attitudeset=atthk.fits eventset=mos1S001-clean.fits:EVENTS expimageset=mos1S001-exp-im.fits imageset=mos1S001-obj-im.fits pimax=8000 pimin=300 withdetcoords=no
   
emask detmaskset=mos1S001-mask-im.fits expimageset=mos1S001-exp-im.fits threshold1=0.01 threshold2=0.5
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2)) &&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152))) ' imagebinning='imageSize' imagedatatype='Int32' imageset=detmap.ds squarepixels=yes ignorelegallimits=no withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=120 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=120 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
rmfgen format=var rmfset=mos1S001.rmf spectrumset=mos1S001-obj.pi threshold=1.0e-6 detmaptype=dataset detmaparray=detmap.ds
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152))) ' imagebinning='imageSize' imagedatatype='Int32' imageset=detmap.ds squarepixels=yes ignorelegallimits=no withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=120 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=120 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
arfgen arfset=mos1S001.arf spectrumset=mos1S001-obj.pi withrmfset=yes rmfset=mos1S001.rmf extendedsource=yes modelee=no withbadpixcorr=no detmaptype=dataset detmaparray=detmap.ds  badpixlocation=mos1S001-clean.fits modelootcorr=no
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) in BOX(20,-60,6610,6570,0)) &&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))' withspectrumset=yes spectrumset=mos1S001-1ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-1ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) in BOX(20,-60,6610,6570,0))&&(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152))) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-1obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-1obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) in BOX(6550,-13572,6590,6599,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-2oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-2oc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(6550,-13572,6590,6599,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-2obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-2obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6550,-13572,6590,6599,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6550,-13572,6590,6599,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6550,-13572,6590,6599,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6550,-13572,6590,6599,0))&&!(((DETX,DETY) in CIRCLE(100,-200,17700))||((DETX,DETY) in CIRCLE(834,135,17100))||((DETX,DETY) in CIRCLE(770,-803,17100))||((DETX,DETY) in BOX(-20,-17000,6500,500,0))||((DETX,DETY) in BOX(5880,-20500,7500,1500,10))||((DETX,DETY) in BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) in BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-2fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-2fc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(6550,-13572,6590,6599,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-2ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-2ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) in BOX(13280,-306,6610,6599,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-3oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-3oc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(13280,-306,6610,6599,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-3obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-3obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(13280,-306,6610,6599,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(13280,-306,6610,6599,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(13280,-306,6610,6599,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(13280,-306,6610,6599,0))&&!(((DETX,DETY) in CIRCLE(100,-200,17700))||((DETX,DETY) in CIRCLE(834,135,17100))||((DETX,DETY) in CIRCLE(770,-803,17100))||((DETX,DETY) in BOX(-20,-17000,6500,500,0))||((DETX,DETY) in BOX(5880,-20500,7500,1500,10))||((DETX,DETY) in BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) in BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-3fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-3fc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(13280,-306,6610,6599,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-3ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-3ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) in BOX(6700,13070,6530,6560,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-4oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-4oc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(6700,13070,6530,6560,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-4obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-4obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6700,13070,6530,6560,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6700,13070,6530,6560,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6700,13070,6530,6560,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6700,13070,6530,6560,0))&&!(((DETX,DETY) in CIRCLE(100,-200,17700))||((DETX,DETY) in CIRCLE(834,135,17100))||((DETX,DETY) in CIRCLE(770,-803,17100))||((DETX,DETY) in BOX(-20,-17000,6500,500,0))||((DETX,DETY) in BOX(5880,-20500,7500,1500,10))||((DETX,DETY) in BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) in BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-4fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-4fc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(6700,13070,6530,6560,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-4ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-4ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) in BOX(-6410,13130,6570,6560,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-5oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-5oc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-6410,13130,6570,6560,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-5obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-5obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6410,13130,6570,6560,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6410,13130,6570,6560,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6410,13130,6570,6560,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6410,13130,6570,6560,0))&&!(((DETX,DETY) in CIRCLE(100,-200,17700))||((DETX,DETY) in CIRCLE(834,135,17100))||((DETX,DETY) in CIRCLE(770,-803,17100))||((DETX,DETY) in BOX(-20,-17000,6500,500,0))||((DETX,DETY) in BOX(5880,-20500,7500,1500,10))||((DETX,DETY) in BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) in BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-5fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-5fc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-6410,13130,6570,6560,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-5ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-5ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) in BOX(-13169,-105,6599,6599,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-6oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-6oc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-13169,-105,6599,6599,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-6obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-6obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-13169,-105,6599,6599,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-13169,-105,6599,6599,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-13169,-105,6599,6599,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-13169,-105,6599,6599,0))&&!(((DETX,DETY) in CIRCLE(100,-200,17700))||((DETX,DETY) in CIRCLE(834,135,17100))||((DETX,DETY) in CIRCLE(770,-803,17100))||((DETX,DETY) in BOX(-20,-17000,6500,500,0))||((DETX,DETY) in BOX(5880,-20500,7500,1500,10))||((DETX,DETY) in BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) in BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-6fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-6fc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-13169,-105,6599,6599,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-6ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-6ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) in BOX(-6540,-13438,6570,6599,0))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-7oc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-7oc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-6540,-13438,6570,6599,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-7obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-7obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6540,-13438,6570,6599,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6540,-13438,6570,6599,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6540,-13438,6570,6599,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6540,-13438,6570,6599,0))&&!(((DETX,DETY) in CIRCLE(100,-200,17700))||((DETX,DETY) in CIRCLE(834,135,17100))||((DETX,DETY) in CIRCLE(770,-803,17100))||((DETX,DETY) in BOX(-20,-17000,6500,500,0))||((DETX,DETY) in BOX(5880,-20500,7500,1500,10))||((DETX,DETY) in BOX(-5920,-20500,7500,1500,350))||((DETX,DETY) in BOX(-20,-20000,5500,500,0)))' filtertype=expression keepfilteroutput=no withspectrumset=yes spectrumset=mos1S001-7fc.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-7fc.pi useodfatt=no badpixlocation=mos1S001-clean.fits withbadpixcorr=yes ignoreoutoffov=no 
   
evselect table=/data/mpofls/atran/research/g309/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-6540,-13438,6570,6599,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-7ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-7ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
backscale spectrumset=mos1S001-7ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
