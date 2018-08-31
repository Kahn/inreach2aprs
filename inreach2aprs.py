#!/usr/bin/env python3

# It's super dodgy but this will give you something to run via cron at least with a zero return for success ...

import os, sys
import aprslib
import datetime
import LatLon23
import pprint
import argparse
import requests
# Requires hacks from http://installfights.blogspot.com/2018/04/how-to-run-pykml-in-python3.html
from pykml import parser as kmlparser
from urllib.parse import urlparse
from io import BytesIO
import sqlite3

parser = argparse.ArgumentParser(description='inreach2aprs')
# default=os.environ.get('I2A', None)
parser.add_argument('aprs_callsign', help='Your callsign; VK2GPL')
parser.add_argument('aprs_ssid', help='ARPS SSID or none; eg "-6"; see http://www.aprs.net.au/general/standard-ssids/')
parser.add_argument('aprs_password', help='APRS Passcode')
parser.add_argument('--mapshare_url', help='inReach MapShare URL; see https://support.garmin.com/en-AU/?faq=p2lncMOzqh71P06VifrQE7')
parser.add_argument('--mapshare_password', help='OPTIONAL - inReach MapShare password')

args = parser.parse_args()
if not args.aprs_callsign:
    exit(parser.print_usage())


pp = pprint.PrettyPrinter()
o = urlparse(args.mapshare_url)
# print(o.path.strip("/"), args.mapshare_password)

try:
    conn = sqlite3.connect('inreach2aprs.db')
    c = conn.cursor()
    c.execute("CREATE TABLE positions (callsign text, ts text, lat text, long text)")
    conn.commit()
except sqlite3.OperationalError:
    print("INFO: Database already exists and is initialised")
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


try:
    r = requests.get(args.mapshare_url, auth=(o.path.strip("/"), args.mapshare_password))
    r.raise_for_status()
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

kml = kmlparser.parse(BytesIO(r.content)).getroot()

# Maps as per https://files.delorme.com/support/inreachwebdocs/KML%20Feeds.pdf and with inreach.kml example
#0 - Id int
#1 - Time UTC str
#2 - Time str
#3 - Name str
#4 - Map Display Name str
#5 - Device Type str
#6 - IMEI str
#7 - Incident Id str
#8 - Latitude float
#9 - Longitude float
#10 - Elevation str
#11 - Velocity str
#12 - Course str
#13 - Valid GPS Fix bool
#14 - In Emergency bool
#15 - Text str
#16 - Event str

d = datetime.datetime.strptime(str(kml.Document.Folder.Placemark[0].TimeStamp.when),'%Y-%m-%dT%H:%M:%SZ')
aprs_timestamp = d.strftime("%d%H%Mz")

inreach_lat = round(float(kml.Document.Folder.Placemark[0].ExtendedData.Data[8].value),2)
# print(inreach_lat)
inreach_lon = round(float(kml.Document.Folder.Placemark[0].ExtendedData.Data[9].value),2)
# print(inreach_lon)

aprs_pos = LatLon23.LatLon( LatLon23.Latitude(inreach_lat), LatLon23.Longitude(inreach_lon))

lat_deg, lon_deg = aprs_pos.to_string('d%')
lat_mins, lon_mins = aprs_pos.to_string('M%')
lat_hem, lon_hem = aprs_pos.to_string('H%')
aprs_lat_mins = format(float(lat_mins),'.2f')
aprs_lon_mins = format(float(lon_mins),'.2f')

try:
    aprs_lat = lat_deg.replace("-","") + aprs_lat_mins + lat_hem
    # print(aprs_lat, len(aprs_lat))
    aprs_lon = lon_deg.replace("-","") + aprs_lon_mins + lon_hem
    # print(aprs_lon, len(aprs_lon))
    assert len(aprs_lat)<=8
    assert len(aprs_lat)<=9
except AssertionError:
    print("Position report values exceed specification length")

position_report = args.aprs_callsign + args.aprs_ssid + ">"+ "APZ001,TCPIP*:/" + aprs_timestamp + aprs_lat + "/" + aprs_lon + "Sinreach2aprs-0.0.2"

params = (args.aprs_callsign + args.aprs_ssid,aprs_timestamp,aprs_lat,aprs_lon)
c.execute(
    "SELECT * FROM positions WHERE callsign=? AND ts=? AND lat=? AND long=?", params
)

if c.fetchone() == None:
    # (?, ?)", (who, age)
    params = (args.aprs_callsign + args.aprs_ssid, aprs_timestamp, aprs_lat, aprs_lon)
    pp.pprint(params)
    c.execute(
        """insert into positions values (?,?,?,?)""", params
    )
    try:
        AIS = aprslib.IS(args.aprs_callsign, passwd=args.aprs_password, port=14580)
        AIS.connect()
        AIS.sendall(position_report)
        sent = True
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    if sent:
        conn.commit()
        print("INFO: Sent packet \n")
        pp.pprint(aprslib.parse(position_report))
        conn.close()
        sys.exit(0)
    else:
        print("ERROR: Sending packet failed")
        sys.exit(1)

else:
    print("WARN: Not sending duplicate report")
    pp.pprint(aprslib.parse(position_report))
    sys.exit(1)
