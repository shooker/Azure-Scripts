# Azure Public IP Address List in CSV Format
Azure is a massive public cloud and maintains an ongoing list of IP addresses. If you are building a secure cloud environment and monitoring every request that enters your network perimter, it's particularly useful to suppress false alarms using a list of known IP addresses.

Microsoft provides a list of all of the Azure Public Cloud IP addresses and related service tags. However, it comes in a JSON file and many network monitoring tools and SIEMs, including Azure Sentinel, prefer a Start IP and End IP address range or CIDR block.

This simple Python script takes the Microsoft JSON file as an input, removes duplicate entries, and exports 3 CSV files:
- The Public IP ranges in CIDR notation
- The Start and End IP address of each range in IPv4 format
- The Start and End IP address of each range in "long" 64-bit format

## To Use This Script
1. Ensure that you have Python 3.6 and Pandas installed
2. Download the latest list of IP addresses from Microsoft [here](https://www.microsoft.com/en-us/download/details.aspx?id=56519)
3. Update the file name on **Line 7** with the newest file name from Step 2
4. Run it!

## Notes
- As of April 2020 there is an [API in Preview](https://azure.microsoft.com/en-us/updates/service-tag-discovery-api-in-preview/) to download these IP addresses. The output from this API call is provided in the same format as the input file used in this code. This will help users obtain more granular ranges.
- Upload the output CSV to a blob storage container to use with Azure Sentinel
- You can automate this entire process using the new API and Azure Functions