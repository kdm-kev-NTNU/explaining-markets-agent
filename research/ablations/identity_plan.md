# Frosset plan — kø 10, identitets-ablation

Planen er frosset før noen arkivkjøring. Dette dokumentet registrerer armene.
Det inneholder ingen resultater.

## Spørsmål

Hvor mye av ΔR² som kommer fra materials, og hvor mye som er identitets-prior
fra ticker alene.

## Armer

Samme arkiv-events i alle armer. Ingen maskering. Maskering er ikke en arm:
den måler lekkasje, ikke identitets-prioren.

| Arm | Id | Input |
| --- | --- | --- |
| A | `A_full` | Hele materials-bundlen |
| B | `B_ticker_date` | Ticker, kalenderkvartal og event-dato. Ingen facts, preview eller opsjonsstats |
| C | `C_materials_only` | Hele bundlen, pluss en instruks om å begrunne bare fra leverte felt |

ΔR²(A) − ΔR²(B) er materials-gevinsten. ΔR²(B) er identitets-prioren.
Sammenligningen er paret på samme events (kø 12).

## Trials

Tre trials, ett per arm: `10A`, `10B`, `10C`. En senere variant er et nytt
trial og skal telles med, også når utfallet er null.

## Cutoff

Cutoff-antagelsen for Astra er **ukjent**. Arm B skal ikke tolkes før det er
skrevet om arkivet ligger før eller etter treningskuttet.

## Kjøringsforbud

`identity_arms.py` bygger inputene og nekter `--run`. Ingen modellkall og
ingen arkivprediksjoner i denne leveransen.
