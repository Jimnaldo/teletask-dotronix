# Dotronix-fork van teletask-hacs

Deze fork volgt [claesmathias/teletask-hacs](https://github.com/claesmathias/teletask-hacs)
en voegt een paar fixes toe die we op installaties in het veld nodig hadden.
Versies heten `<upstream>-dtx.<n>`, bv. `1.8.1-dtx.1` = upstream 1.8.1 + Dotronix-fixes.

## Fixes

| Bestand | Wat |
|---|---|
| `cover.py` | **Rolluikpositie omgekeerd.** Teletask meldt de positie als % *dicht* (0 = open), Home Assistant verwacht % *open*. Positie, `is_closed`, `requested_position` en `set_cover_position` worden nu omgezet (`100 - p`). |
| `client.py` | **Motor stop-melding.** Een stilstaande motor stuurt maar 4 statusbytes; de positie uit die melding wordt nu ook gelezen. |
| `hub.py` | **Motorstatus samenvoegen.** Start- en stopmeldingen bevatten verschillende velden; ze worden samengevoegd zodat de positie niet verloren gaat. `seconds_to_finish` wordt gewist zodra de motor stilstaat. |
| `client.py` | **PROSOFT 5 sensoren (32-bit float).** PROSOFT 5 stuurt sensorwaarden als IEEE754 float (big-endian); temperaturen in Kelvin (−273). Alleen actief met de optie hieronder. |
| `client.py` | **Centrale 0 voor globale functies.** Op PROSOFT 5 worden FLAG, LOCMOOD, GENMOOD en TIMEDMOOD naar centrale 0 gestuurd (DoIP API: "If you don't know the central unit id, like for a flag, you must use number 0"). Alleen actief met de optie hieronder. |

## Optie: `protocol`

Voor centrales op **PROSOFT 5** zet je bovenaan in `config.json`:

```json
{
  "type": "PALAS",
  "protocol": "prosoft5",
  ...
}
```

Zonder deze optie (PROSOFT 4) gedraagt de integratie zich voor sensoren en globale
functies exact zoals upstream. De rolluikfixes gelden altijd.

## Installeren via de Marketplace (HACS)

Voeg `https://github.com/Jimnaldo/teletask-dotronix` toe als custom repository
(type *Integration*) en kies release `v1.8.1-dtx.1`. Maak eerst een backup van
`custom_components/teletask` en van `config.json`.

## Upstream bijhouden

```bash
git remote add upstream https://github.com/claesmathias/teletask-hacs
git fetch upstream --tags
git checkout dotronix && git rebase vX.Y.Z   # nieuwe upstream-tag
```

Daarna versie in `manifest.json` op `X.Y.Z-dtx.1` zetten en een release maken.
