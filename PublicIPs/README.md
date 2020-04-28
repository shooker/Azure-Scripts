# Azure Public IP Address List in CSV Format
Azure is a massive public cloud and maintains an ongoing list of IP addresses. If you are building a secure cloud environment and monitoring every request that enters your network perimter, it's particularly useful to suppress false alarms using a list of known IP addresses.

Microsoft provides a list of all of the Azure Public Cloud IP addresses and related service tags. However, it comes in a JSON file and many network monitoring tools and SIEMs, including Azure Sentinel, prefer a Start IP and End IP address range or CIDR block.

## parsejson.py Script:
The simple Python script called **parsejson.py** takes the Microsoft JSON file as an input, removes duplicate entries, and exports 3 CSV files in your working directory:
- The Public IP ranges in CIDR notation
- The Start and End IP address of each range in IPv4 format
- The Start and End IP address of each range in "long" 64-bit format
*Samples of each file are located in SampleOutput folder.*

1. Ensure that you have Python 3.6 and Pandas installed
2. Download the latest JSON list of IP addresses from Microsoft [here](https://www.microsoft.com/en-us/download/details.aspx?id=56519)
3. Update the file name on **Line 7** with the newest file name and location from Step 2
4. Run it!

# But can it be automated?
## Automated/api_to_blob.py Script:
The Python script in the Automation folder called **apy_to_blob.py** calls the Microsoft [Service Tag List API](https://docs.microsoft.com/en-us/rest/api/virtualnetwork/servicetags/list), performs the same transformations in the parsejson.py script, and uploads the file to a Blob Container in Azure Storage. Use it as a baseline to refactor into your existing business processes or build it as an Azure [Function App](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview).

This script leverages the [API in Preview](https://azure.microsoft.com/en-us/updates/service-tag-discovery-api-in-preview/) to obtain this data from Microsoft. The data obtained from this API call is provided in the same format as the file available on Microsoft's website. 
1. Ensure that you have Python 3.6, Pandas, and azure-storage-blob modules installed
2. Create an [App Registration](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app) in Azure Active Directory with Reader permissions on an Azure subscription
3. Create a Client Secret for the App, determine your expiration policy and save the value
4. Create a Storage Account in Azure and save the connection string for the account
5. Update lines 13-16 and line 28 with the information from Steps 3 and 4
6. Update Container and Blob names as needed on lines 24-26 and line 38