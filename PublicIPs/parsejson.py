import json
import pandas as pd
import ipaddress

# Update this with file downloaded from Microsoft here:
# https://www.microsoft.com/en-us/download/details.aspx?id=56519
with open('ServiceTags_Public_20200420.json') as file:
    json = json.load(file)
    
iplist = []

for each in json['values']:
    iplist.extend((each['properties']['addressPrefixes']))
    
pd.DataFrame(iplist).drop_duplicates().to_csv(r'publicips.csv', index = False, header = False)
print("Public IP ranges extracted from JSON and saved as publicips.csv")

# Put data into a DataFrame and separate CIDR notation
df = pd.DataFrame(iplist, columns=['StartIPv4']).drop_duplicates()
df[['StartIPv4','CIDR']] = df['StartIPv4'].str.split("/", expand = True)
df['CIDR'] = pd.to_numeric(df['CIDR'])

# Create new column and calculate number of IPs from CIDR notation
df['IPs'] = "2"
df['IPs'] = pd.to_numeric(df['IPs'])
df['IPs'] = (df['IPs']).pow(32 - (df['CIDR']))

# Python ipaddress module cannot recognize IP addresses directly inside of DataFrame
# Put IPs into a list and add back into DataFrame

rawstartips = df['StartIPv4'].tolist()

startips = []

for ip in rawstartips:
    startips.append(int(ipaddress.ip_address(ip)))

df['StartIP-64'] = startips

# Calculate end IP address
df['EndIP-64'] = df['StartIP-64'] + df['IPs']

# Export start and end 64-bit IPs to a CSV
header = ['StartIP-64','EndIP-64']
df.to_csv('start_end_ips_64.csv', columns = header, index = False)
print("Start and end IPs in 64-bit format saved as start_end_ips_64.csv")

endipslong = df['EndIP-64'].tolist()

endipsshort = []

for ip in endipslong:
    endipsshort.append(str(ipaddress.ip_address(ip)))

df['EndIPv4'] = endipsshort

# Re-Arrange DataFrame columns (useful in a Jupyter Notebook)
# df = df[['StartIPv4', 'EndIPv4', 'CIDR', 'IPs', 'StartIP-64', 'EndIP-64']]

# Export start and end to a CSV
header = ['StartIPv4','EndIPv4']
df.to_csv('start_end_ips.csv', columns = header, index = False)
print("Start and end IPs in IPv4 format saved as start_end_ips.csv")
