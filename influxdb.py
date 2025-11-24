# import influxdb_client, os, time
# from influxdb_client import InfluxDBClient, Point, WritePrecision
# from influxdb_client.client.write_api import SYNCHRONOUS

# token = "2odr9RGi2iozvfhhGG5e7HgMvtaImx_3CdcD3Zog5cVP5utTbhao5ht8G6B8DgIaKpsJyAC5bm_86XE0OdRkQg=="
# org = "Landho Dev"
# url = "http://localhost:8086"

# write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

# bucket="stocks"

# write_api = write_client.write_api(write_options=SYNCHRONOUS)
   
# for value in range(5):
#   point = (
#     Point("measurement1")
#     .tag("tagname1", "tagvalue1")
#     .field("field1", value)
#   )
#   write_api.write(bucket=bucket, org="Landho Dev", record=point)
#   time.sleep(1)