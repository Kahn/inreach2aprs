# inreach2arps

I don't like that there is not an opensoure Delorme/Garmin inReach to APRS bridge. So naturally now there are 15 obscure versions. This 16th version is probably vapourware.

For reference - The Delorme API is documented at https://files.delorme.com/support/inreachwebdocs/KML%20Feeds.pdf

## Goal

Send inReach positions to APRSIS ✅

      usage: inreach2aprs.py [-h] [--mapshare_url MAPSHARE_URL]
                             [--mapshare_password MAPSHARE_PASSWORD]
                             aprs_callsign aprs_ssid aprs_password

      inreach2aprs

      positional arguments:
        aprs_callsign         Your callsign; VK2GPL
        aprs_ssid             ARPS SSID or none; eg "-6"; see
                              http://www.aprs.net.au/general/standard-ssids/
        aprs_password         APRS Passcode

      optional arguments:
        -h, --help            show this help message and exit
        --mapshare_url MAPSHARE_URL
                              inReach MapShare URL; see
                              https://support.garmin.com/en-
                              AU/?faq=p2lncMOzqh71P06VifrQE7
        --mapshare_password MAPSHARE_PASSWORD
                              OPTIONAL - inReach MapShare password

## Nice to haves

* Support public MapShare links
* Support authenticated MapShare links ✅
* Handle deduplicating rather than relying on APRSIS to handle dupes

## Theory

Take KML payload for past 60 minutes https://share.delorme.com/feed/share/JoeTester?d1=2018-08-21T10:00Z&d2=2018-08-21T11:00Z

Load KML items into cache

Publish positions to APRSIS, mark in cache. Use SSID-6 for APRS via Sat (fight me, what else is iridium).

Receiver marks APRSIS repeated packets for delete

GC deletes positions from cache beyond KML payload window with recieved by APRSIS marks
