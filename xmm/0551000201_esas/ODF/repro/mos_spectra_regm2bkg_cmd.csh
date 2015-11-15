evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0))) &&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )' filtertype=expression imagebinning='imageSize' imagedatatype='Int32' imageset=mos2S002-obj-im-sp-det.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=780 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=780 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) ) &&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0))) ' imagebinning='imageSize' imagedatatype='Int32' imageset=detmap.ds squarepixels=yes ignorelegallimits=no withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=120 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=120 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
rmfgen format=var rmfset=mos2S002.rmf spectrumset=mos2S002-obj.pi threshold=1.0e-6 detmaptype=dataset detmaparray=detmap.ds
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0))) ' imagebinning='imageSize' imagedatatype='Int32' imageset=detmap.ds squarepixels=yes ignorelegallimits=no withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=120 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=120 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes
   
arfgen arfset=mos2S002.arf spectrumset=mos2S002-obj.pi withrmfset=yes rmfset=mos2S002.rmf extendedsource=yes modelee=no withbadpixcorr=no detmaptype=dataset detmaparray=detmap.ds  badpixlocation=mos2S002-clean.fits modelootcorr=no
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&((DETX,DETY) IN BOX(20,-60,6610,6590,0)) &&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )' withspectrumset=yes spectrumset=mos2S002-1ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-1ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='((DETX,DETY) IN BOX(20,-60,6610,6590,0))&&(PATTERN<=12)&&(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0))) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-1obj.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-1obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(6580,-13530,6620,6640,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-2obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-2obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6580,-13530,6620,6640,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6580,-13530,6620,6640,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6580,-13530,6620,6640,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(6580,-13530,6620,6640,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-2ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-2ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(13320,-295,6620,6590,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-3obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-3obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(13320,-295,6620,6590,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(13320,-295,6620,6590,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(13320,-295,6620,6590,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(13320,-295,6620,6590,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-3ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-3ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(6610,13110,6590,6550,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-4obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-4obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6610,13110,6590,6550,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6610,13110,6590,6550,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(6610,13110,6590,6550,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(6610,13110,6590,6550,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-4ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-4ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-6560,13180,6590,6600,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-5obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-5obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6560,13180,6590,6600,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6560,13180,6590,6600,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6560,13180,6590,6600,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-6560,13180,6590,6600,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-5ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-5ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-13190,-90,6600,6630,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-6obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-6obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-13190,-90,6600,6630,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-13190,-90,6600,6630,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-13190,-90,6600,6630,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-13190,-90,6600,6630,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-6ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-6ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-clean.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0)) ' filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes withspectrumset=yes spectrumset=mos2S002-7obj.pi energycolumn=PI  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999
   
backscale spectrumset=mos2S002-7obj.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0))&&(PI in [300:10000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0))&&(PI in [500:800])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=mos2S002-corn.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0))&&(PI in [2500:5000])' filtertype=expression filteredset=temp_events.fits keepfilteroutput=yes updateexposure=yes filterexposure=yes 
   
evselect table=/data/mpofls/atran/research/xmm/caldb/mos2-fwc.fits.gz:EVENTS withfilteredset=yes expression='(FLAG == 0)&&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )&&(((DETX,DETY) IN circle(-61,-228,17085))||((DETX,DETY) IN box(14.375,-16567.6,5552.62,795.625,0)))&&((DETX,DETY) IN BOX(-6620,-13438,6620,6599,0)) ' withspectrumset=yes keepfilteroutput=no updateexposure=yes filterexposure=yes spectrumset=mos2S002-7ff.pi energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 
   
backscale spectrumset=mos2S002-7ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
backscale spectrumset=mos2S002-7ff.pi badpixlocation=mos2S002-clean.fits withbadpixcorr=yes 
   
