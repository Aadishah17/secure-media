param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [string]$Region = "us-central1",
    [string]$Service = "securemedia-ai",
    [string]$SimilarityProvider = "google",
    [string]$GoogleCloudLocation = "us-central1",
    [string]$BackendEnvPath = "backend/.env",
    [switch]$IncludeBlockchainConfig,
    [string]$GeminiApiSecretName,
    [string]$BlockchainPrivateKeySecretName,
    [switch]$DryRun
)

function Get-GcloudPath {
    $command = Get-Command gcloud -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $localPath = Join-Path $env:LOCALAPPDATA "Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    if (Test-Path $localPath) {
        return $localPath
    }

    throw "gcloud CLI not found. Install Google Cloud SDK first."
}

function Read-EnvFile {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return @{}
    }

    $values = @{}
    foreach ($line in Get-Content $Path) {
        if ([string]::IsNullOrWhiteSpace($line) -or $line.Trim().StartsWith("#")) {
            continue
        }

        $parts = $line -split "=", 2
        if ($parts.Count -ne 2) {
            continue
        }

        $values[$parts[0].Trim()] = $parts[1].Trim().Trim("'`"")
    }

    return $values
}

function Get-ActiveGcloudAccount {
    param([string]$GcloudPath)

    $account = & $GcloudPath auth list --filter=status:ACTIVE --format="value(account)"
    return ($account | Select-Object -First 1).Trim()
}

$gcloud = Get-GcloudPath
$envFile = Read-EnvFile -Path $BackendEnvPath

$envVars = @(
    "SIMILARITY_PROVIDER=$SimilarityProvider",
    "GOOGLE_CLOUD_PROJECT=$ProjectId",
    "GOOGLE_CLOUD_LOCATION=$GoogleCloudLocation"
)

if ($IncludeBlockchainConfig) {
    foreach ($key in @("WEB3_PROVIDER_URI", "CONTRACT_ADDRESS", "OWNER_ADDRESS", "CHAIN_ID")) {
        $value = $envFile[$key]
        if ($value) {
            $envVars += "$key=$value"
        }
    }
}

$deployArgs = @(
    "run", "deploy", $Service,
    "--source", ".",
    "--region", $Region,
    "--allow-unauthenticated",
    "--set-env-vars", ($envVars -join ",")
)

$secrets = @()
if ($GeminiApiSecretName) {
    $secrets += "GEMINI_API_KEY=$GeminiApiSecretName:latest"
}
if ($BlockchainPrivateKeySecretName) {
    $secrets += "PRIVATE_KEY=$BlockchainPrivateKeySecretName:latest"
}
if ($secrets.Count -gt 0) {
    $deployArgs += @("--set-secrets", ($secrets -join ","))
}

if ($DryRun) {
    Write-Host "Resolved gcloud:" $gcloud
    Write-Host "Deploy command:"
    Write-Host "& `"$gcloud`" $($deployArgs -join ' ')"
    exit 0
}

$activeAccount = Get-ActiveGcloudAccount -GcloudPath $gcloud
if (-not $activeAccount) {
    throw "No active gcloud account. Run 'gcloud auth login' first."
}

& $gcloud config set project $ProjectId
if ($LASTEXITCODE -ne 0) {
    throw "Failed to set gcloud project to '$ProjectId'."
}

& $gcloud services enable `
    run.googleapis.com `
    cloudbuild.googleapis.com `
    artifactregistry.googleapis.com `
    aiplatform.googleapis.com
if ($LASTEXITCODE -ne 0) {
    throw "Failed to enable required Google Cloud APIs."
}

& $gcloud @deployArgs
if ($LASTEXITCODE -ne 0) {
    throw "Cloud Run deployment failed."
}
