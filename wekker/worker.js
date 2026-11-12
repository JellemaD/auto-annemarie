// Wekker voor Auto voor Annemarie (B18, besluit Durk 12-11-2026).
// GitHub start geplande taken op het gratis plan uren te laat (de "08:00-run" begon 12:54-15:16).
// Cloudflare-crons lopen op de minuut. Deze Worker start daarom om 08:00 Nederlandse tijd de
// workflow "Dagelijkse update" via workflow_dispatch. De cron van GitHub blijft als reserve staan:
// die ziet later "Vandaag al bijgewerkt" en doet dan niets.
//
// Cloudflare rekent in UTC zonder zomertijd: de cron draait om 06:00 en 07:00 UTC en alleen de
// run waarbij het in Amsterdam 8 uur is, start de update.
// Geheim: GITHUB_TOKEN (fine-grained token, alleen repo auto-annemarie, Actions: read and write).

const REPO = 'JellemaD/auto-annemarie';
const WORKFLOW = 'dagelijks.yml';

function uurInAmsterdam(ms) {
  return Number(new Intl.DateTimeFormat('nl-NL', {
    timeZone: 'Europe/Amsterdam', hour: 'numeric', hour12: false,
  }).format(new Date(ms)));
}

async function startUpdate(env) {
  const r = await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: 'application/vnd.github+json',
      'User-Agent': 'auto-annemarie-wekker',
    },
    body: JSON.stringify({ ref: 'main' }),
  });
  if (r.status !== 204) throw new Error(`GitHub gaf ${r.status}: ${await r.text()}`);
}

export default {
  async scheduled(event, env) {
    const uur = uurInAmsterdam(event.scheduledTime);
    if (uur !== 8) {
      console.log(`Het is ${uur} uur in Amsterdam, niet 8: niets te doen.`);
      return;
    }
    await startUpdate(env);
    console.log('Dagelijkse update gestart.');
  },
};
