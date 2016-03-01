        program rot_inv
C       Converts velocity into a distance
C       Written by BMG 21may97
C       Modified AT 24feb2016

        implicit none

        real l, b, v(1000), theta0, r0, r, d(1000), dproj, w
        real xmin, xmax, ymin, ymax
        integer i, numpts

C       224, 7.62 used in code as received (Feb 2016)
C       but 220, 8.5 used to derive fits in Fich/Blitz/Stark
C       Since fit coefficients weren't changed, return to old
C       (possibly less correct) values

C       parameter (theta0 = 224, r0 = 7.62)
        parameter (theta0 = 220, r0 = 8.5)

        print*, ' Enter longitude & latitude of source: '
        read(*,*) l, b

C       Compute velocity to 25 kpc (numpts/10) along line-of-sight
        numpts = 250
        do i = 1, numpts
          d(i) = i*0.1
          dproj = d(i)*cos(b/180.*3.14159)

          r=sqrt(r0**2+dproj**2-2*r0*dproj*cos(l/180.*3.14159))

C         Fit parameters from Fich, Blitz, Stark (1989ApJ...342...272F)
          w=1.00746*theta0/r-0.017112*theta0/r0

          v(i)=(w-theta0/r0)*r0*sin(l/180.*3.14159)*cos(b/180.*3.14159)

c         print*, ' Velocity (in km/s) is ', v
          print*, v(i), d(i)
        enddo

        call pgbegin (0, '?', 1,1)
        call pgslw(2)
        call pgsch(1.5)
        call pgscf(2)
        call findends (v,numpts,xmin,xmax)
        call findends (d,numpts,ymin,ymax)
        xmin = -120.
        xmax = 140.
        ymin = 0.
        ymax = 20.
        call pgenv(xmin,xmax,ymin,ymax,0,0)
        call pglabel('LSR Velocity (km s\\u-1\\d)', 'Distance (kpc)','')
        call pgline(numpts,v,d,1)
        call pgend

        end

