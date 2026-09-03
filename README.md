# Teinar.is — endurhönnun

Nýr static vefur fyrir [www.teinar.is](https://www.teinar.is).

Núverandi síða er WordPress. Þessi útgáfa er hraður, öruggur static vefur
(enginn gagnagrunnur, bara HTML/CSS), tvítyngdur (íslenska + enska).

## Uppbygging

```
content/        skrapað innihald úr gamla vefnum (ís + en, markdown)
assets/         css, myndir og PDF-bæklingur
build_site.py   skriftan sem byggir síðuna
site/           útbúna síðan (það sem fer á netið)
```

## Byggja / endurbyggja

    python3 build_site.py

Það endurræstir `site/` með öllum síðum (íslensku og ensku).

## Forskoða staðbundið

    cd site && python3 -m http.server 8899
    # opna http://localhost:8899/is/index.html

## Módel / virkni

- 17 íslenskar síður + 17 enskar + redirect
- Forsíða, tannréttingar (miðstöð), skarð í vör og góm, fyrsta skoðun,
  stoðtæki, fyrsta hjálp, fæða sem skal forðast, sársauki, starfsfólk,
  staðsetning, tímabókanir, hafa samband, sjúkratryggingar, tenglar.
- Responsive, hrein nútímaleg hönnun (teal + hvítur).

## Staða

- [x] Skrapa innihald úr gamla síðu
- [x] Byggja nýja útlit + allar síður (ís + en)
- [ ] Birta (GitHub Pages / Netlify) og færa teinar.is