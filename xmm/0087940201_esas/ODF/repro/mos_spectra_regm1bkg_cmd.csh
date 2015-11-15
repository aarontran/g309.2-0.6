evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152))) &&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=mos1S001-obj-im-sp-det.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=780 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=780 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2))) &&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152))) ' imagebinning='imageSize' imagedatatype='Int32' imageset=detmap.ds squarepixels=yes ignorelegallimits=no withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=120 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=120 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
rmfgen format=var rmfset=mos1S001.rmf spectrumset=mos1S001-obj.pi threshold=1.0e-6 detmaptype=dataset detmaparray=detmap.ds
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152))) ' imagebinning='imageSize' imagedatatype='Int32' imageset=detmap.ds squarepixels=yes ignorelegallimits=no withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=120 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=120 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
arfgen arfset=mos1S001.arf spectrumset=mos1S001-obj.pi withrmfset=yes rmfset=mos1S001.rmf extendedsource=yes modelee=no withbadpixcorr=no detmaptype=dataset detmaparray=detmap.ds  badpixlocation=mos1S001-clean.fits modelootcorr=no
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) in BOX(20,-60,6610,6570,0)) &&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))' withspectrumset=yes spectrumset=mos1S001-1ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-1ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) in BOX(20,-60,6610,6570,0))&&(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152))) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-1obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-1obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(6550,-13572,6590,6599,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-2obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-2obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6550,-13572,6590,6599,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6550,-13572,6590,6599,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6550,-13572,6590,6599,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(6550,-13572,6590,6599,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-2ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-2ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(13280,-306,6610,6599,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-3obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-3obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(13280,-306,6610,6599,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(13280,-306,6610,6599,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(13280,-306,6610,6599,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(13280,-306,6610,6599,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-3ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-3ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(6700,13070,6530,6560,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-4obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-4obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6700,13070,6530,6560,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6700,13070,6530,6560,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(6700,13070,6530,6560,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(6700,13070,6530,6560,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-4ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-4ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-6410,13130,6570,6560,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-5obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-5obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6410,13130,6570,6560,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6410,13130,6570,6560,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6410,13130,6570,6560,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-6410,13130,6570,6560,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-5ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-5ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-13169,-105,6599,6599,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-6obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-6obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-13169,-105,6599,6599,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-13169,-105,6599,6599,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-13169,-105,6599,6599,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-13169,-105,6599,6599,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-6ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-6ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-6540,-13438,6570,6599,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos1S001-7obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos1S001-7obj.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6540,-13438,6570,6599,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6540,-13438,6570,6599,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) in BOX(-6540,-13438,6570,6599,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos1-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) in BOX(-6540,-13438,6570,6599,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos1S001-7ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos1S001-7ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
backscale spectrumset=mos1S001-7ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes 
   
