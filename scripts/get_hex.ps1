param([string]$filePath) $bytes = [System.IO.File]::ReadAllBytes($filePath); for ($i = 0; $i -lt [Math]::Min(100, $bytes.Length); $i++) { Write-Host -NoNewline ("{0:X2} " -f $bytes[$i]) }
