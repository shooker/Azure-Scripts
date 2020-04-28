from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from datetime import datetime
import os
import json
import pandas as pd
import ipaddress
import logging
import requests
import msal

# Create an App Registration in Azure Active Directory and put details here:
# Do not store secrets in code!
tenant_id = "#"
subscription_id = "#"
app_id = "#" # aka Client ID
app_secret = "#" # Use Key Vault or equivalent
location = "eastus"
# The location that will be used as a reference for version
# not as a filter based on location, you will get the list
# of service tags with prefix details across all regions
# but limited to the cloud that your subscription belongs to.

# File names in Azure blob containers
public_ip_file_name = 'PublicIPs.CSV'
ipv4_ip_file_name = 'start_end_ips.csv'
long_ip_file_name = 'start_end_ips_64.csv'

os.environ["AZURE_STORAGE_CONNECTION_STRING"] = "#"

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

# Create the BlobServiceClient object which will be used to create and list containers
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Create a unique name for the container based on today's date
dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%d-%b-%Y").lower()
container_name = ("csvs" + '-' + str(timestampStr))

# Check to see if container from today already exists, if not, create the container
containerlist = []

containers = blob_service_client.list_containers() 
for c in containers:
    containerlist.append(c.name)

if container_name not in containerlist:
    container_client = blob_service_client.create_container(container_name)

# Build URLs for Service Tag API Call
ipendpoint = "https://management.azure.com/subscriptions/" + subscription_id + "/providers/Microsoft.Network/locations/" + location + "/serviceTags?api-version=2020-03-01"
authority = "https://login.microsoftonline.com/" + tenant_id

config = {
    "authority": authority,
    "client_id": app_id,
    "scope": ["https://management.azure.com/.default"],
    "secret": app_secret,
    "endpoint": ipendpoint
}

# Create a preferably long-lived app instance which maintains a token cache.
app = msal.ConfidentialClientApplication(
    config["client_id"], authority=config["authority"],
    client_credential=config["secret"]
    )

result = None

result = app.acquire_token_silent(config["scope"], account=None)

if not result:
    logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
    result = app.acquire_token_for_client(scopes=config["scope"])

if "access_token" in result:
    # Calling graph using the access token
    graph_data = requests.get(  # Use token to call downstream service
        config["endpoint"],
        headers={'Authorization': 'Bearer ' + result['access_token']},).json()
    with open('rawoutput.json', 'w') as outfile:
        json.dump(graph_data, outfile)

else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug

# Update this with file downloaded from Microsoft here:
# https://www.microsoft.com/en-us/download/details.aspx?id=56519
with open('rawoutput.json') as file:
    json = json.load(file)
    
iplist = []

for each in json['values']:
    iplist.extend((each['properties']['addressPrefixes']))

pd.DataFrame(iplist).drop_duplicates().to_csv(public_ip_file_name, index = False, header = False)

# Save Public IP CSV file to Blob Storage
upload_file_path = os.path.abspath(public_ip_file_name)
blob_client = blob_service_client.get_blob_client(container=container_name, blob=public_ip_file_name)
with open(public_ip_file_name, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
print("Public IP ranges in CIDR notation saved to Azure Blob as: " + public_ip_file_name)

# Put data into a DataFrame and separate CIDR notation
df = pd.DataFrame(iplist, columns=['StartIPv4']).drop_duplicates()
df[['StartIPv4','CIDR']] = df['StartIPv4'].str.split("/", expand = True)
df['CIDR'] = pd.to_numeric(df['CIDR'])

# Create new column and calculate number of IPs from CIDR notation
df['IPs'] = '2'
df['IPs'] = pd.to_numeric(df['IPs'])
df['IPs'] = (df['IPs']).pow(32 - (df['CIDR']))

# Python ipaddress module cannot recognize IP addresses directly inside of DataFrame
# Put IPs into a list and add back into DataFrame

rawstartips = df['StartIPv4'].tolist()

startips = []

for ip in rawstartips:
    startips.append(int(ipaddress.ip_address(ip)))

df['StartIP64'] = startips

# Calculate end IP address
df['EndIP64'] = df['StartIP64'] + df['IPs']

# Export start and end 64-bit IPs to a CSV
header = ['StartIP64','EndIP64']
df.to_csv(long_ip_file_name, columns = header, index = False)

# Save 64-bit IP CSV file to Blob Storage
upload_file_path = os.path.abspath(long_ip_file_name)
blob_client = blob_service_client.get_blob_client(container=container_name, blob=long_ip_file_name)
with open(long_ip_file_name, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
print("Start and end IPs in 64-bit format saved to Azure Blob as: " + long_ip_file_name)

endipslong = df['EndIP64'].tolist()

endipsshort = []

for ip in endipslong:
    endipsshort.append(str(ipaddress.ip_address(ip)))

df['EndIPv4'] = endipsshort

# Export IPv4 start and end IP addresses to a CSV
header = ['StartIPv4','EndIPv4']
df.to_csv(ipv4_ip_file_name, columns = header, index = False)

# Save IPv4 CSV file to Blob Storage
upload_file_path = os.path.abspath(ipv4_ip_file_name)
blob_client = blob_service_client.get_blob_client(container=container_name, blob=ipv4_ip_file_name)
with open(ipv4_ip_file_name, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
print("Start and end IPs in IPv4 format saved to Azure Blob as: " + ipv4_ip_file_name)

# Clean up JSON and CSV files
os.remove('rawoutput.json')
os.remove(public_ip_file_name)
os.remove(ipv4_ip_file_name)
os.remove(long_ip_file_name)