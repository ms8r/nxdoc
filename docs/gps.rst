GPS and Navigatrix
==================

You should just be able to just plug in your GPS and have it work.
There's a little thing in Navigatrix called a daemon. This GPS daemon,
gpsd, runs in the background. It looks at every external port. When
anything is plugged in to one of these ports it runs over there and asks
“Are you a GPS?” The GPS will say, “Why, Yes. I am.” The gpsd will ask
your gps to prove it; provide gps data. The daemon and your GPS then get
acquainted; speed; protocol...stuff  like that.

| The gpsd works with many many many GPS units. Chances are very good
that your gps will function without any other intervention. Once your
gps is connected the gpsd will provide gps data to any other software on
the system that can listen. The gpsd will also help keep your clock on
time and setups for other location based functions in synch with your
whereabouts.

Try it. Open the GPS Monitor Manta Menu -> Navigation -> GPS Satellites
and it should show something. If that fails: ask in the `Navigatrix
Support Forum <http://navigatrix.net/support.php>`__ to find some who
knows how to fix it. A good thread to start with in the Support Forum is `this
one <http://navigatrix.net/viewtopic.php?f=4&t=366>`__.
