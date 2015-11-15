For a description of the FLAG column, see the documentation of the SAS package evatt.
http://xmm.esac.esa.int/sas/current/doc/evatt/node3.html
almost the same as: http://xmm.esac.esa.int/sas/5.4.1/doc/saslib/gvxmm199901.txt

So we have nice keyword-encoded flag selectors...

Finally, the #XMMEA_EM (#XMMEA_EP for the PN) filter provides a
canned screening set of FLAG values for the event.
(The FLAG value provides a bit encoding of various event
conditions, e.g., near hot pixels or outside of the field of
view.) Setting FLAG == 0 in the selection expression provides
the most conservative screening criteria and should always be
used when serious spectral analysis is to be done on the PN. It
typically is not necessary for the MOS.	


OK, I have spent ~1 hour on this flag business and can't find jack shit on this.
I can surmise that each of the 32 bits encodes one attribute, which is described in GV/XMM/1999-01 or in XMM SAS package evatt.


https://heasarc.gsfc.nasa.gov/docs/xmm/sas/USG/MOSmetatask.html

    Then evselect is called on the resulting event list(s) applying (by
    default) the destructive filter selection (#XMMEA_EM) && (FLAG &
    0x762a0000) == 0. Note that in case of emchain, (#XMMEA_EM) is not applied:
    here events flagged as OUT_OF_FOV and REJECTED_BY_GATTI are kept in the
    list (as they are useful for background assessments and flare screening,
    respectively). For a description of the event attribute based selection,
    refer to the documentation of the SAS package evatt.
