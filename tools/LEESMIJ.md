# Tools — Auto voor Annemarie

Alle commando's beginnen met `cd` naar de projectmap, zodat ze vanuit elke map werken.

## Wekker (Cloudflare Worker `auto-annemarie-wekker`)

Start elke dag om 08:00 Nederlandse tijd de GitHub-workflow "Dagelijkse update". Code in `wekker/`.
Nodig omdat GitHub geplande runs op het gratis plan uren te laat start.

**Online zetten (na een wijziging in `wekker/`):**

```powershell
cd "G:\Mijn Drive\DATA70 - Programming en Bots\20 - Claude Code\Projecten\05 - Premium auto zoeken\auto-annemarie"; .\tools\wekker-deploy.ps1
```

**GitHub-token zetten of vernieuwen** (verloopt na de looptijd die je bij het maken kiest):

1. Maak op https://github.com/settings/personal-access-tokens/new een *fine-grained* token:
   naam `auto-annemarie-wekker`, repository `JellemaD/auto-annemarie`, permissie **Actions: Read and write**.
2. Draai en plak het token als wrangler erom vraagt:

```powershell
cd "G:\Mijn Drive\DATA70 - Programming en Bots\20 - Claude Code\Projecten\05 - Premium auto zoeken\auto-annemarie"; .\tools\wekker-token.ps1
```

**Controleren of hij liep:** GitHub → Actions → "Dagelijkse update": een run met event `workflow_dispatch` rond 08:00.
Logboek van de Worker live meekijken: `cd wekker; npx -y wrangler@4 tail`.

## sync_sheet.py

Zet `docs/BACKLOG.md` en `docs/VERSIES.md` in de Google Sheet. Draait vanzelf bij elke push (Action `sync-sheet.yml`).
