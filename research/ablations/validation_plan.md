# Frosset plan — kø 12, valideringshygiene

Planen er frosset før noen arkivkjøring. Den registrerer hvilke events,
hvilke features og hvilken metrikk som er lov. Den inneholder ingen resultater.

## Events

Hele sammenligningsutvalget, samme event-id-er i hver arm. Ingen
etter-seleksjon når et tall er sett.

## Features

De tre trialene fra kø 10, og ingen andre:

| Trial | Arm |
| --- | --- |
| `10A` | `A_full` |
| `10B` | `B_ticker_date` |
| `10C` | `C_materials_only` |

Et nytt prompt-utkast eller en ny arm er et nytt trial. Tallet rapporteres
uansett utfall. Gjentatte seeds er ikke nye trials.

## Metrikk

Paret ΔΔR² på samme events.

ΔR² er R²(y ~ 1 + surprise + predicted_percentile) minus R²(y ~ 1 + surprise).
ΔΔR² er differansen mellom to armer. Bootstrap trekker ett felles
event-utvalg med tilbakelegging og regner begge armer på det utvalget.
Intervall er percentil 2,5 og 97,5.

En konstant prediksjon har ΔR² = 0. En prediksjon som er en affin funksjon
av surprise øker ikke ΔR².

## Cutoff

Cutoff-antagelsen for Astra er **ukjent**. Arm B skal ikke tolkes før
antagelsen er skrevet som noe annet enn `unknown`, inkludert om arkivet
ligger før eller etter kuttet.

## Kjøringsforbud

`validation_hygiene.py` kan regne metrikken på arrays som allerede er gitt
inn. `--run` avslås. Denne leveransen har ingen arkivprediksjoner og ingen
resultatfil.
