# Frosset plan — kø 13, surprise-konveksitet

Ett trial, registrert før noen arkivkjøring. Ingen resultater. System-prompten
er ikke endret.

## Trial

`13A`. Prediksjonen i armen er en monoton transform av surprise-persentilen,
betinget på verdsettelsesusikkerhet u fra opsjonsstats. Identitets-trialene
`10A`–`10C` er et annet forsøk og teller ikke med her.

## u

Bare `implied_earnings_volatility` og `implied_absolute_earnings_move`.

u = clip(vol / abs_move − 1, 0, 1).

Mangler ett av tallene, eller er et av dem ikke positivt, er u = 0 og
transformen er identiteten. Preview-felt er ikke med. Kø 5 har ikke et
deterministisk uttrekk ennå.

## Formen

s er surprise-persentilen. t = 2s − 1. Med frosset k = 2:

blandet = (1 − u) · t + u · tanh(k t) / tanh(k)

Resultatet er 0,5 + 0,5 · blandet. Endepunktene 0 og 1 og medianen 0,5 ligger
fast. Høy u er brattere ved medianen og slakere mot halene. Lav u er lineær.
k er ikke estimert på arkivet.

## Sammenligning

Mot lineær surprise på samme events, paret ΔΔR² fra kø 12. Tallet rapporteres
uansett fortegn. Cutoff-antagelsen for Astra er **ukjent**.

## Det som ikke gjøres her

Prompt-instruks i 3c bare hvis den parede kjøringen er positiv. Denne
leveransen kjører ikke arkivet, og `--run` avslås.
