# Zet de wekker (map wekker/) online als Cloudflare Worker. Draai in je eigen terminal.
# Het token van aanhangerinsoest heeft geen Workers-rechten, dus leegmaken zodat de OAuth-login telt.
Remove-Item Env:CLOUDFLARE_API_TOKEN -ErrorAction SilentlyContinue
Set-Location (Join-Path (Split-Path $PSScriptRoot -Parent) 'wekker')
npx -y wrangler@4 deploy
