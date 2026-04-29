$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Speech

$root = "C:\Users\sseja\OneDrive\Documents\New project 2"
$audioDir = Join-Path $root "docs\video\audio"
New-Item -ItemType Directory -Force -Path $audioDir | Out-Null

$segments = @(
    @{
        Name = "scene01_intro.wav"
        Text = "This is SecureMedia AI, a website that checks uploaded images for similarity, duplicate risk, and ownership status."
    },
    @{
        Name = "scene02_home.wav"
        Text = "On the home screen, the user sees a simple upload interface, an image preview area, and result cards for similarity, duplicate status, owner, and blockchain verification."
    },
    @{
        Name = "scene03_selected.wav"
        Text = "After choosing an image, the preview appears immediately, and the file is ready for analysis."
    },
    @{
        Name = "scene04_result.wav"
        Text = "When the user clicks Analyze image, the Flask backend processes the upload, compares it against stored data and optional AI similarity services, and returns the result. Here the image is marked original with zero percent similarity, while ownership remains unverified."
    },
    @{
        Name = "scene05_deploy.wav"
        Text = "The full stack is deployed on Google Cloud Run. React handles the front end, Flask handles the API, and the workflow stays simple enough for a quick live demo."
    }
)

$voice = "Microsoft Zira Desktop"

foreach ($segment in $segments) {
    $outputPath = Join-Path $audioDir $segment.Name
    if (Test-Path $outputPath) {
        Remove-Item -LiteralPath $outputPath -Force
    }

    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.SelectVoice($voice)
    $synth.Rate = 0
    $synth.Volume = 100
    $synth.SetOutputToWaveFile($outputPath)
    $synth.Speak($segment.Text)
    $synth.Dispose()
}

Get-ChildItem -Path $audioDir | Select-Object Name, Length, LastWriteTime
