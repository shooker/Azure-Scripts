param (
    
    # Event Hub Information:
    [string]       $EventHubNamespace = "diagext",
    [string]       $EventHubName = "oslogs",
    [int]          $Expiration = 30000, # Token expires now+30000 seconds
    
    # Shared Access Policy Information:
    [string]       $AccessPolicyKey = "vCBDAR3YD6sqSAI06SOC0/sIsfimug8z5H02B5cy5aI=",
    [string]       $AccessPolicyName = "diagext-Send"
)

# Generate Event Hub SAS URL
[Reflection.Assembly]::LoadWithPartialName("System.Web")| out-null
$URI= $EventHubNamespace + ".servicebus.windows.net/" + $EventHubName
$Access_Policy_Name = $AccessPolicyName
$Access_Policy_Key = $AccessPolicyKey
$Expires=([DateTimeOffset]::Now.ToUnixTimeSeconds())+$Expiration
$SignatureString=[System.Web.HttpUtility]::UrlEncode($URI)+ "`n" + [string]$Expires
$HMAC = New-Object System.Security.Cryptography.HMACSHA256
$HMAC.key = [Text.Encoding]::ASCII.GetBytes($Access_Policy_Key)
$Signature = $HMAC.ComputeHash([Text.Encoding]::ASCII.GetBytes($SignatureString))
$Signature = [Convert]::ToBase64String($Signature)
$SASToken = "sr=" + [System.Web.HttpUtility]::UrlEncode($URI) + "&sig=" + [System.Web.HttpUtility]::UrlEncode($Signature) + "&se=" + $Expires + "&skn=" + $Access_Policy_Name
$SasURL = "https://" + $URI + '?' + $SASToken

$SasURL