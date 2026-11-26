# Eenmalig (en opnieuw als het token verloopt): zet het GitHub-token als geheim in de wekker.
# Vooraf: token maken op GitHub (zie tools/LEESMIJ.md) en kopiëren (Ctrl+C). Dan dit script starten.
# Het token komt van het klembord, niet in beeld of in een bestand; het klembord wordt daarna leeggemaakt.
# Werkwijze overgenomen van Energielogboek/tool/tools/sleutel-instellen.ps1 (plakken in wrangler lukt niet altijd).
Remove-Item Env:CLOUDFLARE_API_TOKEN -ErrorAction SilentlyContinue
$OutputEncoding = New-Object System.Text.UTF8Encoding $false   # geen BOM vóór geheimen (PowerShell 5.1)
Set-Location (Join-Path (Split-Path $PSScriptRoot -Parent) 'wekker')
$token = ''
try { $token = ([string](Get-Clipboard -Raw)).Trim() } catch {}
if ($token -notmatch '^(github_pat_|ghp_)\S+$') { Write-Host 'Op het klembord staat geen GitHub-token (github_pat_...). Er is niets gewijzigd.' -ForegroundColor Red; exit 1 }
$token | npx -y wrangler@4 secret put GITHUB_TOKEN
Set-Clipboard -Value ' '
Write-Host "Klaar: token ($($token.Length) tekens) staat bij de wekker, en het klembord is leeggemaakt." -ForegroundColor Green
