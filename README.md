# inreach2arps

I don't like that there is not an opensoure Delorme/Garmin inReach to APRS bridge. So naturally now there are 15 obscure versions. This 16th version is probably vapourware.

For reference - The Delorme API is documented at https://files.delorme.com/support/inreachwebdocs/KML%20Feeds.pdf

## Goal

Send inReach positions to APRSIS

## Nice to haves

* Support public MapShare links
* Support authenticated MapShare links
* Handle deduplicating rather than relying on APRSIS to handle dupes

## Theory

Take KML payload for past 60 minutes https://share.delorme.com/feed/share/JoeTester?d1=2018-08-21T10:00Z&d2=2018-08-21T11:00Z

Load KML items into cache

Publish positions to APRSIS, mark in cache. Use SSID-6 for APRS via Sat (fight me, what else is iridium).

Receiver marks APRSIS repeated packets for delete

GC deletes positions from cache beyond KML payload window with recieved by APRSIS marks
