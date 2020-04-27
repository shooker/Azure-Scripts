param (
    
    # Key Vault Information:
    [string]       $KeyVaultName = "#",
    [string]       $SecretName = "#",

    # Event Hub Information:
    [string]       $EventHubNamespace = "#",
    [string]       $EventHubName = "#",
    [string]       $ResourceGroupName = "#",
    [string]       $AccessPolicyName = "#",
    [int]          $Expiration = 2592000 # Token expires in 2,592,000 seconds, or 30 days.
   
)

# Create Shared Access Policy
New-AzEventHubAuthorizationRule -ResourceGroupName $ResourceGroupName -NamespaceName $EventHubNamespace -AuthorizationRuleName $AccessPolicyName -EventHub $EventHubName -Rights @("Send")

# Retreive primary key for Event Hub
$primaryKey = (Get-AzEventHubKey -ResourceGroupName $ResourceGroupName -Namespace $EventHubNamespace -Name $AccessPolicyName -EventHub $EventHubName).PrimaryKey

# Generate Event Hub SAS URL
[Reflection.Assembly]::LoadWithPartialName("System.Web")| out-null
$URI= $EventHubNamespace + ".servicebus.windows.net/" + $EventHubName
$Access_Policy_Name = $AccessPolicyName
$Access_Policy_Key = $primaryKey
$Expires=([DateTimeOffset]::Now.ToUnixTimeSeconds())+$Expiration
$SignatureString=[System.Web.HttpUtility]::UrlEncode($URI)+ "`n" + [string]$Expires
$HMAC = New-Object System.Security.Cryptography.HMACSHA256
$HMAC.key = [Text.Encoding]::ASCII.GetBytes($Access_Policy_Key)
$Signature = $HMAC.ComputeHash([Text.Encoding]::ASCII.GetBytes($SignatureString))
$Signature = [Convert]::ToBase64String($Signature)
$SASToken = "sr=" + [System.Web.HttpUtility]::UrlEncode($URI) + "&sig=" + [System.Web.HttpUtility]::UrlEncode($Signature) + "&se=" + $Expires + "&skn=" + $Access_Policy_Name
$SasURL = "https://" + $URI + '?' + $SASToken

# Convert Expiration DateTime for Key Vault
$keyexp = ([datetime]'1/1/1970').AddSeconds($Expires)

# Store SasURL in Key Vault:
$secretvalue = ConvertTo-SecureString $SasURL -AsPlainText -Force
Set-AzKeyVaultSecret -VaultName $KeyVaultName -Name $SecretName -SecretValue $secretvalue -Expires $keyexp -Confirm