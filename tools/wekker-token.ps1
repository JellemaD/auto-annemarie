# Eenmalig (en opnieuw als het token verloopt): zet het GitHub-token als geheim in de wekker.
# Wrangler vraagt om het token; plak het en druk op Enter. Het token komt alleen bij Cloudflare.
Remove-Item Env:CLOUDFLARE_API_TOKEN -ErrorAction SilentlyContinue
Set-Location (Join-Path (Split-Path $PSScriptRoot -Parent) 'wekker')
npx -y wrangler@4 secret put GITHUB_TOKEN
