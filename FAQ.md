
Frequently (at least 1x) asked questions
========================================

Issues that have cropped up and been answered.
Separate specific questions and miscellany from day-to-day notes.


Why neglect grains when modeling X-ray absorption?
==================================================

(May 2016)

OR, why use tbnew_gas instead of tbnew (with grains)?

Grains have little effect on X-ray absorption.  Fig. 2 of Wilms, Allen, McCray
(2000) shows that grains change optical depth mainly at energies < 0.3 keV.
X-rays penetrate, so grain self-shielding results in little change as when
compared to gas-phase absorption.


XSPEC stuff
===========

Q: Why is Spectrum.values in counts/cm^2/sec instead of counts/sec?
Clearly no effective area is divided out from the data (since we fit folded
models to the counts).
Answer: AREASCAL is divided out -- even though that's just unity.

Q: Can we get data directly from PyXSPEC?
A: Sort of.  We can get data and folded models in CHANNEL SPACE
   (which is where XSPEC does all the fitting anyways).
   But, conversion to energy space is not straightforward.
   We'd need a FITS interface to the RMF EBOUNDS table, and then rescale the
   data in each bin correctly.
   XSPEC and PyXSPEC are a bit opaque on the actual conversion.

   We can also access data through the xs.Plot.{x,y,model} interface,
   but there is no way to access individual models (sky background, remnant,
   soft proton); we only get the sum of model contributions.

   Therefore I opted for the somewhat ugly approach
   of dumping all the data using "iplot wdata",
   and letting the end user manually sort out each model's contribution.
   Let XSPEC handle the energy-channel mapping and don't delve further for now
   (it's not hard to do, but not worth building and validating now,
   especially when I have tools to parse wdata output already)

   Below find explanatory code snippets used to deduce the above.

    s = xs.Spectrum("...")  # spectrum 7, plot group 7
    models = xspec_utils.get_models_for_spec(spectrum)

    s.energies  # energy mapping for each channel
    s.values  # counts / cm^2 / sec in each channel
    s.variance  # variance, counts / cm^2 / sec in each channel
    s.background.values  # same deal

    m = m[0]  # Just some arbitrary model
    m.energies(7)  # unfolded model spectrum (bin boundaries, 2401 values)
    m.values(7)  # unfolded model spectrum (2400 values)
    m.folded(7)  # folded model in channel space, counts / cm^2 / sec
        # (I would say that it's not "really" in /cm^2 since
        # we have already folded the model through the ARF)

    xs.Plot.xAxis="channel"
    xs.Plot("ldata")

    # Confirm that spectrum values - background match plot values
    np.array(s.values) - np.array(s.background.values)) - np.array(xs.Plot.y(7))

    # Confirm that sum of folded models is just the plot "model"
    m_tot = sum([np.array(m.folded(7)) for m in models])
    xs.Plot.model(7) - m_tot

    # Confirm that spectrum energies are just bin centers
    xs.Plot.xAxis="keV"
    xs.Plot("ldata")
    np.mean(s.energies, axis=1) - np.array(xs.Plot.x(7))


XMM-Newton SAS stuff
====================

Q: What's the difference between epproc/emproc and epchain/emchain?
A: Same thing, script vs. compiled implementation.  Maybe chains are better?
> There are two types of tool available, the procs (epproc and emproc) and the
> chains (epchain and emchain) which do essentially the same job. However, the
> chains allow more user control, and can also be set to keep intermediate
> files (like the badpixel files) and can be stopped at certain points and
> restarted at others. An example of when this is useful is to stop the chain
> after bad pixel detection, add, or remove some pixels from the badpixel list,
> then complete the chain, if you're not happy with the bad pixels it detects
> by itself. The chains also appear to do a better job of detecting bad pixels
> and events than the procs, so I would recommend using them.
(from: http://www.sr.bham.ac.uk/xmm2/dataprep.html)

Q: What's in an obsid?
A: 10 digits (PPPPPPOOLL), where PPPPPP = proposal ID, OO = observation within proposal ID, and LL = "extended ID" (usually 1)


Flare removal by GTI cuts decreases error compared to blank sky subtraction
===========================================================================

Tuesday Oct 6 2015

What's the better way to remove flares from spectra: cutting time intervals of
significant flaring, or subtracting blank sky background?

Flares are ~10x the source count rate during flaring periods (note that MOS/PN
histogram of FOV count rate are likely dominated by the bright star HD119682,
and SNR is probably 2-10x fainter).

	Counts in filtered image (flares completely removed; original event list cleaned with XMMEA_EM and espfilt):
	- SNR: 0.077 cts/arcsec^2    / 27ks     -->  2.85e-3 ct/ks/arcsec^2
	- blank sky: 0.04 cts/arcsec^2  / 27ks  -->  1.48e-3 ct/ks/arcsec^2

	Counts in unfiltered image (original event list; no filtering for bad events, but there should be very few of those):
	- SNR: 0.217 cts/arcsec^2   / 40ks    	-->  5.43e-3 ct/ks/arcsec^2
	- blank sky: 0.165 cts/arcsec   / 40ks	-->  4.13e-3 ct/ks/arcsec^2

SNR is ~ 1.4e-3 ct/ks/arcsec, without blank sky background (instrumental, sky, etc. all in one)
Flaring is ~2.6e-3 ct/ks/arcsec^2, roughly 2x SNR brightness.  But flaring is concentrated in 13 of 40 ks.

	Estimated SNR counts (40 ks): 0.056 ct/arcsec^2
	Estimated flare counts (40 ks, but concentrated within 13 ks): 0.10 ct/arcsec^2
	Estimated SNR counts (13 ks): 0.018 ct/arcsec^2

Flares thus cause count rates ~10x brighter than actual SNR (after background removal), over the span of 13 ks.
But, what matters is the total error over 40ks.

	SNR alone (40 ks): 0.056*A +/- sqrt(0.056*A) ct

			relative error: sqrt(0.056*A) / (0.056*A) ~ 4.23 / sqrt(A)

	SNR alone (27 ks): 0.038*A +/- sqrt(0.038*A) ct

			relative error: sqrt(0.038*A) / (0.038*A) ~ 5.13 / sqrt(A)

	SNR (40 ks) - flare (13 ks): 0.056*A +/- sqrt(0.056*A) +/- sqrt(2*0.10*A) ct

			relative error: sqrt(0.256*A) / (0.056*A) ~ 9.04 / sqrt(A)

Adding errors in quadrature. flare subtraction using another region introduces sqrt(2 * flare cts) uncertainty.
This is a very rough estimate, but it looks like we almost double the relative error, as opposed to simply cutting out flare times.

Flares in different parts of FOV are definitely correlated.  So subtraction
process may not introduce that much error if the "actual" Poissonian error in
flare counts from one part of the FOV to another is similar (or, it doesn't
make sense to represent the counts as random discrete events).

So the error for blank sky subtraction is likely not as bad as I estimate.
Nevertheless, simply taking GTIs seems to be the safest approach.


