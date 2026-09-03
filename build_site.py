#!/usr/bin/env python3
"""Generate the Teinar.is static site (Icelandic + English) from structured content."""
import os, shutil, json, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
ASSETS = os.path.join(ROOT, "assets")
SITE_URL = "https://www.teinar.is"

CONTACT = {
    "is": {
        "org": "Tannlæknastofa Gísla Vilhjálmssonar",
        "tagline": "Sérfræðistofa í tannréttingum",
        "addr": "Laugavegi 163, 105 Reykjavík",
        "phone": "562 9944",
        "phone_href": "tel:+3545629944",
        "emergency": "893 5181",
        "emergency_href": "tel:+3548935181",
        "email": "teinar@teinar.is",
    },
    "en": {
        "org": "Gísli Vilhjálmsson Orthodontics",
        "tagline": "Orthodontic specialist practice",
        "addr": "Laugavegur 163, 105 Reykjavík, Iceland",
        "phone": "+354 562 9944",
        "phone_href": "tel:+3545629944",
        "emergency": "+354 893 5181",
        "emergency_href": "tel:+3548935181",
        "email": "teinar@teinar.is",
    },
}

def tel(cd):
    """Clickable main phone link built from CONTACT."""
    return f'<a href="{cd["phone_href"]}">{cd["phone"]}</a>'

def tel_emergency(cd):
    return f'<a href="{cd["emergency_href"]}">{cd["emergency"]}</a>'

HOURS = {
    "is": [
        ("Mánudaga til föstudaga", ""),
        ("Vetrartími (september–maí)", "8:15–16:00"),
        ("Sumartími (júní–ágúst)", "8:15–16:00 (föstudaga til 12:00)"),
    ],
    "en": [
        ("Monday to Friday", ""),
        ("Winter (Sep–May)", "8:15–16:00"),
        ("Summer (Jun–Aug)", "8:15–16:00 (Fridays until 12:00)"),
    ],
}

NAV = {
    "is": [
        ("Heim", "index.html", "index"),
        ("Tannréttingar", "tannrettingar.html", "tannrettingar"),
        ("Um fyrirtækið", "um-fyrirtaekid.html", "um"),
        ("Starfsfólk", "starfsfolk.html", "starfsfolk"),
        ("Staðsetning", "stadhsetning.html", "stadhsetning"),
        ("Hafa samband", "hafdu-samband.html", "samband"),
    ],
    "en": [
        ("Home", "index.html", "index"),
        ("Orthodontics", "orthodontics.html", "orthodontics"),
        ("About", "about.html", "about"),
        ("Staff", "staff.html", "staff"),
        ("Location", "location.html", "location"),
        ("Contact", "contact.html", "contact"),
    ],
}

# is/en page pairs — used for hreflang alternates and the language switcher
PAIRS = [
    ("is/index.html", "en/index.html"),
    ("is/tannrettingar.html", "en/orthodontics.html"),
    ("is/um-fyrirtaekid.html", "en/about.html"),
    ("is/starfsfolk.html", "en/staff.html"),
    ("is/stadhsetning.html", "en/location.html"),
    ("is/hafdu-samband.html", "en/contact.html"),
    ("is/gisli-vilhjalmsson.html", "en/gisli-vilhjalmsson.html"),
    ("is/fyrsta-skodun.html", "en/first-visit.html"),
    ("is/skard-i-vor-og-gom.html", "en/cleft-lip-and-palate.html"),
    ("is/tannrettingar-fyrir-alla.html", "en/orthodontics-for-all.html"),
    ("is/stodtaeki.html", "en/appliances.html"),
    ("is/fyrsta-hjalp.html", "en/first-aid.html"),
    ("is/faeda-sem-skal-fordast.html", "en/food-to-avoid.html"),
    ("is/sarsauki.html", "en/pain.html"),
    ("is/sjukratryggingar.html", "en/insurance.html"),
    ("is/timapantanir.html", "en/booking.html"),
    ("is/tenglar.html", "en/links.html"),
]
PAIR_MAP = {}
for _is, _en in PAIRS:
    PAIR_MAP[_is] = (_is, _en)
    PAIR_MAP[_en] = (_is, _en)

# per-page meta descriptions (fall back to org — tagline)
META_DESC = {
    "is/index.html": "Sérfræðistofa í tannréttingum á Laugavegi 163 í Reykjavík. Tannréttingar barna og fullorðinna, með sérstaka áherslu á skarð í vör og góm.",
    "is/tannrettingar.html": "Yfirlit yfir tannréttingameðferðina hjá Tannlæknastofu Gísla Vilhjálmssonar — fyrsta skoðun, stoðtæki, verkir, fæða, sjúkratryggingar og fleira.",
    "is/um-fyrirtaekid.html": "Um Tannlæknastofu Gísla Vilhjálmssonar á Laugavegi 163. Stofan hefur eingöngu sinnt tannréttingum frá árinu 1986.",
    "is/starfsfolk.html": "Starfsfólk Tannlæknastofu Gísla Vilhjálmssonar — tannréttingasérfræðingur, tanntæknar og tannsmiður.",
    "is/stadhsetning.html": "Tannlæknastofan er á Laugavegi 163, 105 Reykjavík. Sérinngangur Katrínartúnsmegin, upp á 2. hæð.",
    "is/hafdu-samband.html": "Hafðu samband við Tannlæknastofu Gísla Vilhjálmssonar — sími 562 9944, teinar@teinar.is, Laugavegi 163 í Reykjavík.",
    "is/gisli-vilhjalmsson.html": "Gísli Vilhjálmsson, tannlæknir og sérfræðingur í tannréttingum. Nám, ferill og sérfræðiréttindi.",
    "is/fyrsta-skodun.html": "Hvenær á að koma með barnið í fyrstu skoðun hjá tannréttingasérfræðingi og hvernig meðferð hefst.",
    "is/skard-i-vor-og-gom.html": "Tannréttingar barna með skarð í vör og góm — meðferðarferli frá unga aldri þar til tannskiptum og vexti er lokið.",
    "is/tannrettingar-fyrir-alla.html": "Bæklingurinn „Leiðin að fallegra brosi“ um undirbúning tannréttinga, meðferðina sjálfa og tækjakostinn.",
    "is/stodtaeki.html": "Stoðtæki að lokinni tannréttingu — stoðtæki í efri góm og stoðbogi í neðri góm til að halda árangrinum stöðugum.",
    "is/fyrsta-hjalp.html": "Fyrsta hjálp og neyðaraðstoð vegna tannréttingatækja utan opnunartíma.",
    "is/faeda-sem-skal-fordast.html": "Hvaða fæðu skal forðast með fastri tannréttingu — allt sem er hart og seigt getur skemmt tækin.",
    "is/sarsauki.html": "Sársauki og verkjalyf við tannréttingu — ráðleggingar um íbúprófen og parasetamól og dæmi um skammta fyrir börn.",
    "is/sjukratryggingar.html": "Þátttaka Sjúkratrygginga Íslands í tannréttingameðferðum og aðstoð við umsóknir.",
    "is/timapantanir.html": "Tímabókanir hjá Tannlæknastofu Gísla Vilhjálmssonar — sími 562 9944 og teinar@teinar.is. Opnunartími.",
    "is/tenglar.html": "Gagnlegir tenglar — Breið bros, samtök aðstandenda barna með skarð í vör og góm, og Sjúkratryggingar Íslands.",
    "en/index.html": "Orthodontic specialist practice at Laugavegur 163, Reykjavík. Orthodontics for children and adults, with special expertise in cleft lip and palate.",
    "en/orthodontics.html": "An overview of orthodontic treatment at Gísli Vilhjálmsson Orthodontics — first visit, retainers, pain relief, food, insurance and more.",
    "en/about.html": "About Gísli Vilhjálmsson Orthodontics at Laugavegur 163. The practice has focused exclusively on orthodontics since 1986.",
    "en/staff.html": "The team at Gísli Vilhjálmsson Orthodontics — orthodontic specialist, dental assistants and a dental technician.",
    "en/location.html": "The practice is at Laugavegur 163, 105 Reykjavík. Separate entrance on the Katrínartún side, up to the 2nd floor.",
    "en/contact.html": "Contact Gísli Vilhjálmsson Orthodontics — phone +354 562 9944, teinar@teinar.is, Laugavegur 163, Reykjavík.",
    "en/gisli-vilhjalmsson.html": "Gísli Vilhjálmsson, dentist and orthodontic specialist. Education, career and specialist licence.",
    "en/first-visit.html": "When to bring your child for a first visit with an orthodontic specialist and how treatment begins.",
    "en/cleft-lip-and-palate.html": "Orthodontics for children with cleft lip and palate — a treatment pathway from an early age until the permanent teeth and growth are complete.",
    "en/orthodontics-for-all.html": "The brochure ‘The road to a beautiful smile’ on preparation for orthodontic treatment, the treatment itself and the appliances used.",
    "en/appliances.html": "Retainers after orthodontic treatment — an upper retainer and a lower retaining wire to keep the result stable.",
    "en/first-aid.html": "First aid and emergency assistance for orthodontic appliances outside opening hours.",
    "en/food-to-avoid.html": "Which foods to avoid with fixed braces — anything hard or chewy can damage the appliances.",
    "en/pain.html": "Pain relief during orthodontic treatment — advice on ibuprofen and paracetamol and example doses for children.",
    "en/insurance.html": "Icelandic Health Insurance participation in orthodontic treatment and help with applications.",
    "en/booking.html": "Booking appointments at Gísli Vilhjálmsson Orthodontics — phone +354 562 9944 and teinar@teinar.is. Opening hours.",
    "en/links.html": "Useful links — Breið bros, the association for families of children with cleft lip and palate, and Icelandic Health Insurance.",
}


def rel_to(from_lang, target_path):
    """Relative href from a page in site/<from_lang>/ to target_path like 'is/foo.html'."""
    tlang, tfile = target_path.split("/", 1)
    return tfile if tlang == from_lang else f"../{target_path}"


def json_ld(lang, url):
    c = CONTACT[lang]
    data = {
        "@context": "https://schema.org",
        "@type": "Dentist",
        "name": c["org"],
        "description": c["tagline"],
        "url": url,
        "telephone": "+354 562 9944",
        "email": c["email"],
        "medicalSpecialty": "Orthodontic",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Laugavegur 163",
            "postalCode": "105",
            "addressLocality": "Reykjavík",
            "addressCountry": "IS",
        },
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "08:15",
            "closes": "16:00",
        }],
        "hasMap": "https://ja.is/kort/?q=G%C3%ADsli+Vilhj%C3%A1lmsson%2C+Laugavegi+163",
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_header(lang, active, asset, path):
    c = CONTACT[lang]
    nav = NAV[lang]
    items = []
    for label, href, key in nav:
        cls = ' class="active"' if key == active else ""
        items.append(f'<a href="{href}"{cls}>{label}</a>')
    nav_html = "\n      ".join(items)
    # language switcher points at the equivalent page in the other language
    is_path, en_path = PAIR_MAP.get(path, ("is/index.html", "en/index.html"))
    is_href = rel_to(lang, is_path)
    en_href = rel_to(lang, en_path)
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html">
      <img src="{asset}/images/logo.png" alt="{c['org']}">
      <span class="brand-text">
        <span class="name">{c['org']}</span><br>
        <span class="tagline">{c['tagline']}</span>
      </span>
    </a>
    <nav class="nav" aria-label="{'Aðalvalmynd' if lang == 'is' else 'Main menu'}">
      {nav_html}
    </nav>
    <div class="lang">
      <a href="{is_href}" hreflang="is" aria-label="Íslenska"{' aria-current="true"' if lang == 'is' else ''} class="{'active' if lang=='is' else ''}">IS</a>
      <a href="{en_href}" hreflang="en" aria-label="English"{' aria-current="true"' if lang == 'en' else ''} class="{'active' if lang=='en' else ''}">EN</a>
    </div>
  </div>
</header>"""

def render_footer(lang, asset):
    c = CONTACT[lang]
    h = HOURS[lang]
    hours_rows = "".join(
        f'<p><strong>{a}</strong>{(" — " + b) if b else ""}</p>' for a, b in h
    )
    if lang == "is":
        quick = [("Tannréttingar", "tannrettingar.html"),
                 ("Skarð í vör og góm", "skard-i-vor-og-gom.html"),
                 ("Tímabókanir", "timapantanir.html"),
                 ("Sjúkratryggingar", "sjukratryggingar.html"),
                 ("Tenglar", "tenglar.html")]
        col_h = "Flýtileiðir"; col_c = "Hafa samband"; col_o = "Opnunartími"
        fine = f"© 2026 {c['org']}. Öll réttindi áskilin."
    else:
        quick = [("Orthodontics", "orthodontics.html"),
                 ("Cleft lip and palate", "cleft-lip-and-palate.html"),
                 ("Appointments", "booking.html"),
                 ("Insurance", "insurance.html"),
                 ("Links", "links.html")]
        col_h = "Quick links"; col_c = "Contact"; col_o = "Opening hours"
        fine = f"© 2026 {c['org']}. All rights reserved."
    quick_rows = "".join(f'<p><a href="{h}">{l}</a></p>' for l, h in quick)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="cols">
      <div>
        <a class="brand" href="index.html"><img src="{asset}/images/logo.png" alt="{c['org']}"></a>
        <p style="margin-top:12px">{c['org']}<br>{c['tagline']}</p>
      </div>
      <div>
        <h4>{col_c}</h4>
        <p>{c['addr']}</p>
        <p>Sími / Phone: {tel(c)}</p>
        <p><a href="mailto:{c['email']}">{c['email']}</a></p>
      </div>
      <div>
        <h4>{col_o}</h4>
        {hours_rows}
      </div>
      <div>
        <h4>{col_h}</h4>
        {quick_rows}
      </div>
    </div>
    <div class="fine">{fine}</div>
  </div>
</footer>"""

def page(lang, path, title, body, active="", prehead=True):
    c = CONTACT[lang]
    # both is/ and en/ pages live one directory deep (site/is/, site/en/),
    # so both reference assets via ../assets
    asset = "../assets"
    # normalize any ../assets/ back to assets/, then prefix with the correct asset dir
    body = body.replace("../assets/", "assets/").replace("assets/", f"{asset}/")
    # decorative emoji icons must not be announced by screen readers
    body = body.replace('<div class="icon">', '<div class="icon" aria-hidden="true">')

    # page title (h1) shares the same .wrap gutter as the rest of the page
    head_txt = f'<div class="wrap page-head"><h1>{title}</h1></div>' if prehead else ""

    desc = META_DESC.get(path, f"{c['org']} — {c['tagline']}")
    is_path, en_path = PAIR_MAP.get(path, ("is/index.html", "en/index.html"))
    canonical = f"{SITE_URL}/{path}"
    skip_txt = "Beint í meginmál" if lang == "is" else "Skip to content"

    html_doc = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — {c['org']}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="is" href="{SITE_URL}/{is_path}">
<link rel="alternate" hreflang="en" href="{SITE_URL}/{en_path}">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{is_path}">
<link rel="icon" type="image/png" href="{asset}/images/logo.png">
<link rel="apple-touch-icon" href="{asset}/images/logo.png">
<meta property="og:type" content="website">
<meta property="og:title" content="{title} — {c['org']}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="{'is_IS' if lang == 'is' else 'en_GB'}">
<meta property="og:image" content="{SITE_URL}/assets/images/hero-office.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset}/css/style.css">
<script type="application/ld+json">
{json_ld(lang, canonical)}
</script>
</head>
<body>
<a class="skip-link" href="#main">{skip_txt}</a>
{render_header(lang, active, asset, path)}
<main id="main">
{head_txt}
{body}
</main>
{render_footer(lang, asset)}
</body>
</html>"""
    return html_doc

# ──────────────────────────────────────────────────────
# CONTENT
# ──────────────────────────────────────────────────────

def build():
    os.makedirs(os.path.join(SITE, "is"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "en"), exist_ok=True)

    ci, ce = CONTACT["is"], CONTACT["en"]

    # ============ ICELANDIC ============
    P = {}  # path -> (title, active, body)

    hero_is = f"""<section class="hero">
  <div class="wrap">
    <div class="hero-text">
      <h1>Fallegt bros — alla ævi.</h1>
      <p class="lead">Sérfræðistofa í tannréttingum á Laugavegi 163 í Reykjavík. Við sinnum eingöngu tannréttingum barna og fullorðinna, með sérstaka áherslu á skarð í vör og góm.</p>
      <a class="btn primary" href="hafdu-samband.html">Bóka tíma</a>
    </div>
    <div class="hero-img">
      <img src="assets/images/hero-office.jpg" alt="Stofan">
    </div>
  </div>
</section>"""

    P["is/index.html"] = ("Forsíða", "index",
        f"""{hero_is}
<section class="section">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Verkefni okkar</div>
      <h2>Vandaðar tannréttingar fyrir alla aldurshópa</h2>
    </div>
    <div class="cards">
      <div class="card"><div class="icon">🦷</div><h3>Tannréttingar barna og unglinga</h3><p>Frá fyrstu skoðun um 4–6 ára aldri og í gegnum allt tannskiptaferlið.</p></div>
      <div class="card"><div class="icon">💛</div><h3>Skarð í vör og góm</h3><p>Margra ára reynsla af tannréttingu barna með skarð í vör og góm, í samvinnu við sérfræðiteymi.</p></div>
      <div class="card"><div class="icon">✨</div><h3>Tannréttingar fullorðinna</h3><p>Mögulegt er að rétta tennur á öllum aldri. Við metum hvert tilvik sérstaklega.</p></div>
      <div class="card"><div class="icon">🛡️</div><h3>Eftirfylgd og stoðtæki</h3><p>Við fylgjum meðferð eftir með stoðtækjum til að tryggja varanlegan árangur.</p></div>
    </div>
  </div>
</section>
<section class="section alt">
  <div class="wrap">
    <div class="section-head"><div class="kicker">Opnunartími</div><h2>Stofan er opin mánudaga til föstudaga</h2></div>
    <div class="info-grid">
      <div class="info-item"><div class="icon">📅</div><div><div class="label">Vetrartími (september–maí)</div><div class="value">8:15–16:00</div></div></div>
      <div class="info-item"><div class="icon">☀️</div><div><div class="label">Sumartími (júní–ágúst)</div><div class="value">8:15–16:00, föstudaga til 12:00</div></div></div>
      <div class="info-item"><div class="icon">📞</div><div><div class="label">Sími</div><div class="value">{tel(ci)}</div></div></div>
      <div class="info-item"><div class="icon">📍</div><div><div class="label">Staðsetning</div><div class="value">Laugavegur 163, 105 Reykjavík</div></div></div>
    </div>
  </div>
</section>""")

    P["is/tannrettingar.html"] = ("Tannréttingar", "tannrettingar",
        """<div class="wrap section">
  <div class="prose" style="max-width:none">
    <p class="lead" style="font-size:1.15rem">Við sinnum eingöngu tannréttingum og höfum gert frá árinu 1986. Hér að neðan má finna upplýsingar um helstu þætti meðferðarinnar.</p>
    <div class="cards" style="margin-top:24px">
      <a class="card" href="fyrsta-skodun.html"><h3>Fyrsta skoðun</h3><p>Hvenær og hvernig meðferð hefst.</p></a>
      <a class="card" href="skard-i-vor-og-gom.html"><h3>Skarð í vör og góm</h3><p>Sérhæft meðferðarferli fyrir börn.</p></a>
      <a class="card" href="tannrettingar-fyrir-alla.html"><h3>Tannréttingar fyrir alla</h3><p>Bæklingur og almennar upplýsingar.</p></a>
      <a class="card" href="stodtaeki.html"><h3>Stoðtæki</h3><p>Eftirfylgd að lokinni meðferð.</p></a>
      <a class="card" href="fyrsta-hjalp.html"><h3>Fyrsta hjálp</h3><p>Neyðartilfelli og aðstoð.</p></a>
      <a class="card" href="faeda-sem-skal-fordast.html"><h3>Fæða sem skal forðast</h3><p>Hvað má og hvað má ekki með tækjum.</p></a>
      <a class="card" href="sarsauki.html"><h3>Sársauki og verkjalyf</h3><p>Ráðleggingar um verkjastillingu.</p></a>
      <a class="card" href="sjukratryggingar.html"><h3>Sjúkratryggingar</h3><p>Þátttaka Sjúkratrygginga Íslands.</p></a>
    </div>
  </div>
</div>""")

    P["is/fyrsta-skodun.html"] = ("Fyrsta skoðun", "tannrettingar",
        f"""<div class="wrap section"><div class="prose">
  <p>Mælt er með að koma með barnið snemma í fyrstu skoðun hjá tannréttingasérfræðingi — helst um 4–6 ára aldur. Þannig er hægt að meta hvort og hvenær tannrétting eigi við og skipuleggja meðferðina á réttum tíma.</p>
  <p>Yfirleitt er hafist handa við tannréttingu á tannskiptaaldri, um 7–8 ára aldri. Ekki er greitt fyrir fyrstu skoðunina.</p>
  <div class="callout">Til að bóka fyrstu skoðun hafið samband í síma <strong>{tel(ci)}</strong> eða sendið tölvupóst á <a href="mailto:teinar@teinar.is">teinar@teinar.is</a>.</div>
</div></div>""")

    P["is/skard-i-vor-og-gom.html"] = ("Skarð í vör og góm", "tannrettingar",
        """<div class="wrap section"><div class="prose">
  <p>Við höfum sinnt mörgum börnum með skarð í vör og góm. Hér að neðan eru almennar upplýsingar um tannréttingar barnanna. Neðst á síðunni er tengill á heimasíðu félags aðstandenda barna með skarð í vör og góm, <em>Breið bros</em>.</p>

  <h2>Tannréttingar barna með skarð í vör og góm</h2>
  <p>Foreldrum sem eignast börn með klofinn góm eða skarð í tanngarð eða vör verður brátt ljóst að þau þurfa að njóta umönnunar stórs hóps fagmanna öll uppvaxtarárin. Tannréttingasérfræðingar eru tannlæknar sem hafa sérmenntað sig í meðferð á tann- og bitskekkjum og gegna veigamiklu hlutverki innan þessa hóps.</p>
  <p>Skarði í tanngarð eða góm fylgja að jafnaði tann- og bitskekkjur sem eru bein afleiðing þessa meðfædda galla. Dæmi um slíkar skekkjur eru undirbit sem stafar af því að framvöxtur efri kjálkans er ekki nægilegur, og krossbit sem rekja má til þess að jaxlasvæði falla saman inn að skarðinu. Einnig verður oft truflun á vexti tannkíma næst skarðinu.</p>
  <p>Börn sem fæðast með klofinn góm eða skarð í tanngarð og vör hafa því mikla þörf fyrir tannréttingar. Meðferð og eftirlit hefst yfirleitt á unga aldri og lýkur ekki fyrr en tannskiptum og vexti er lokið.</p>

  <h2>Tannréttingar á tannskiptaaldri</h2>
  <p>Yfirleitt er hafist handa við lagfæringu á tannskekkju um 7–8 ára aldur, en æskilegt er þó að koma með barnið fyrr til skoðunar, t.d. 4–6 ára. Þegar barnið er 6–8 ára fara fyrstu fullorðinsframtennurnar að koma í ljós; þær eru yfirleitt snúnar og í rangstöðu og nauðsynlegt að stýra þeim á réttan stað. Þetta er ýmist gert með gómplötum eða föstum, álímdum tannréttingatækjum (teinum). Jafnframt er oft hafist handa við að víkka út hliðartannbogana og laga krossbitið.</p>

  <h2>Tannréttingar að loknum tannskiptum</h2>
  <p>Hafi hlé verið gert eftir fyrsta áfangann hefst yfirleitt ný meðferðarlota við 12–14 ára aldur þegar allar fullorðinstennur eru komnar. Þessi tannrétting er gerð með föstum tækjum og markmiðið er að rétta tennur og bit til fullnustu. Ef mikið misræmi er í framvexti kjálka getur þurft að breyta afstöðu þeirra með skurðaðgerð, en slíkar kjálkatilfærslur eru í höndum lýtalækna og munnskurðlækna.</p>

  <h2>Samvinna</h2>
  <p>Tannréttingin einkennist af því að meðferðartíminn getur orðið langur. Þess vegna er mikilvægt að börn og foreldrar taki á þolinmæðinni og vinni samviskusamlega að settu marki — árangurinn verður oft undraverður ef góð samvinna næst.</p>

  <h2>Tenglar</h2>
  <p>Breið bros — Samtök aðstandenda barna með skarð í vör og góm: <a href="https://www.facebook.com/groups/breidbros/">www.facebook.com/groups/breidbros</a></p>
</div></div>""")

    P["is/tannrettingar-fyrir-alla.html"] = ("Tannréttingar fyrir alla", "tannrettingar",
        """<div class="wrap section"><div class="prose">
  <p>Tannréttingar geta nýst fólki á öllum aldri. Hér má nálgast bækling sem lýsir meðferðinni og þeim tækjakosti sem notaður er.</p>
  <h2>Leiðin að fallegra brosi</h2>
  <p>Bæklingur sem fjallar um undirbúning tannréttingameðferðar, tannréttinguna sjálfa og þann tækjakost sem notaður er, auk þess sem skýrt er hvað lagt er til grundvallar þegar ákveðið er að hefja meðferð.</p>
  <div class="callout"><a href="assets/docs/tannrettingar-fyrir-alla.pdf">Hlaða niður bæklingnum (PDF, 10,8 MB)</a></div>
</div></div>""")

    P["is/fyrsta-hjalp.html"] = ("Fyrsta hjálp", "tannrettingar",
        f"""<div class="wrap section"><div class="prose">
  <p>Í neyðartilfellum er hægt að hafa samband við Gísla í síma <strong>{tel_emergency(ci)}</strong>.</p>
  <p>Þegar Gísli er í fríi reynum við að hafa annan tannréttingasérfræðing til taks. Upplýsingar um það er hægt að nálgast hjá okkur.</p>
</div></div>""")

    P["is/stodtaeki.html"] = ("Stoðtæki", "tannrettingar",
        """<div class="wrap section"><div class="prose">
  <p>Í lok meðferðar eru sett upp stoðtæki í báða góma til að halda niðurstöðunni stöðugri.</p>
  <ul>
    <li><strong>Stoðtæki í efri góm</strong> — límt á bakhlið tanna, frá augntönn til augntannar. Mælum með að það sé haft í u.þ.b. 15 ár.</li>
    <li><strong>Stoðbogi í neðri góm</strong> — límdur á augntennur. Mælum með að hann sé aldrei fjarlægður.</li>
  </ul>
</div></div>""")

    foods = [
        ("🍎", "Epli", "borgar sig að skera niður í bita"),
        ("🥕", "Gulrætur", "tæta niður eða skera mjög smátt"),
        ("🌽", "Maískorn", "skafa af stönglinum, ekki naga af"),
        ("🧊", "Ísmolar", "bannað að bryðja"),
        ("🍬", "Kúlur, karamellur, sleikjó", "á bannlistanum"),
        ("🍿", "Poppkorn", "hýðið festist undir tannholdi"),
        ("🍬", "Sykrað tyggjó", "klessist út um tækin"),
        ("🐟", "Harðfiskur", "brýtur tækin"),
    ]
    food_cards = "\n".join(f'<div class="card"><div class="icon">{i}</div><h3>{n}</h3><p>{d}</p></div>' for i, n, d in foods)
    P["is/faeda-sem-skal-fordast.html"] = ("Fæða sem skal forðast", "tannrettingar",
        f"""<div class="wrap section"><div class="prose" style="max-width:none">
  <p>Í flestum tilfellum áttar þú þig á því hvað ber að forðast. Það ber að forðast allt sem er hart og seigt þar sem það getur skemmt tækin.</p>
  <div class="cards" style="margin:20px 0">{food_cards}</div>
  <p>Einnig skal forðast að naga neglur, blýanta og penna.</p>
</div></div>""")

    P["is/sarsauki.html"] = ("Sársauki og verkjalyf", "tannrettingar",
        """<div class="wrap section"><div class="prose">
  <p>Skynjun sársauka er mjög einstaklingsbundin. Við höfum tekið það ráð að búa alla undir sársauka eftir að föst tæki eru sett upp, en margir sjúklingar okkar segja síðan að þetta hafi ekki verið svo slæmt.</p>
  <p>Í flestum tilvikum er nægjanlegt að nota veik verkjalyf eins og <strong>paracetamol</strong> (Panodil eða Paratabs).</p>
  <h2>Ráðleggingar okkar</h2>
  <p>Rannsóknir hafa sýnt að lyf sem inniheldur <strong>ibuprofen</strong> (Ibufen, Ibumetin, Nurofen) er mun öflugra við tannréttingasársauka og því mælum við nú með því. 20 stk af 200 mg töflum fást í lausasölu án lyfseðils.</p>
  <p>Skammtastærð fyrir börn samkvæmt sérlyfjaskrá er 20 mg/kg líkamsþunga á dag, gefið í 3–4 jöfnum skömmtum. Ef börn vega minna en 30 kg skal ekki gefa meira en 500 mg á dag.</p>
  <p>Á lyfjaglasi stendur að ekki eigi að gefa börnum yngri en 12 ára lyfið. Ef skammtastærðir miðað við þyngd eru virtar er í lagi að gefa börnum það.</p>
  <p>Sjúklingum sem kvíða heimsóknum vegna sársauka ráðleggjum við að taka eina 200 mg töflu einni klukkustund fyrir heimsókn og síðan eftir þörfum eftir hana.</p>
  <h2>Dæmi um dagsskammt</h2>
  <table>
    <tr><th>Þyngd barns</th><th>Hámarksskammtur á sólarhring</th></tr>
    <tr><td>30 kg</td><td>600 mg (3 × 200 mg)</td></tr>
    <tr><td>40 kg</td><td>800 mg (4 × 200 mg)</td></tr>
    <tr><td>50 kg</td><td>1000 mg (5 × 200 mg)</td></tr>
    <tr><td>60 kg</td><td>1200 mg (6 × 200 mg)</td></tr>
  </table>
  <div class="callout warn"><strong>Athugið:</strong> Þetta eru hámarksskammtar og barnið þarf ef til vill ekki svo mikið. Þar sem hætta á aukaverkunum eykst með skammtastærð skuluð þið reyna að komast af með sem minnst. Forðist að taka lyfið á fastandi maga og drekkið glas af vatni með. Ef barnið tekur önnur lyf skal ráðfæra sig við lækni áður en lyfið er tekið.</div>
  <h2>Aukaverkanir og frábendingar</h2>
  <p>Einstaka sjúklingar geta fengið ofnæmisviðbrögð. Þeir sem hafa orðið fyrir slíkum viðbrögðum af Magnyl eða paracetamoli skyldu forðast lyfið. Meltingaróþægindi geta fylgt; astmi getur versnað og dæmi er um svima og höfuðverk. Lyfið er ekki ætlað þunguðum konum nema að ráði læknis, og getur aukið virkni annarra lyfja svo sem blóðþynningarlyfja og flogaveikilyfja.</p>
</div></div>""")

    P["is/um-fyrirtaekid.html"] = ("Um fyrirtækið", "um",
        """<div class="wrap section"><div class="prose">
  <img src="assets/images/team.jpg" alt="Starfsfólk" style="border-radius:14px;margin-bottom:20px">
  <p>Stofan var opnuð hér á Laugaveginum í ágúst 1986. Gísli er eini tannlæknirinn á stofunni en auk hans vinna hjá okkur fjórir tanntæknar, ritari í móttöku og tannsmiður. Við sinnum eingöngu tannréttingum.</p>
  <p>Við leitumst við að veita vandaða og persónulega þjónustu og reynum að hafa heimsóknirnar eins þægilegar og hægt er. Við leggjum mikið upp úr fræðslu og upplýsingum, bæði til sjúklinga og forráðamanna, svo að allir geti fylgst með framvindu meðferðarinnar.</p>
  <p>Vandaðar tannréttingar eru tímafrekar, krefjast nákvæmni í vinnubrögðum og kosta mikið. Við leggjum okkur öll fram við tannréttinguna og leitumst við að ná sem allra bestum árangri. Markmið okkar er að árangur meðferðarinnar sé varanlegur og verði til ánægju alla ævi.</p>
  <p>Foreldrar eru ætíð velkomnir með börnum sínum, hvort heldur þeir kjósa að bíða á biðstofunni eða koma með inn á aðgerðarstofuna. Til að miðla upplýsingum til foreldra sem ekki geta mætt með börnum sínum eru skrifaðar athugasemdir í sjúkraskrá í lok hverrar heimsóknar.</p>
</div></div>""")

    # staff
    staff = [
        ("gisli", "Gísli Vilhjálmsson", "Tannlæknir, sérfræðingur í tannréttingum"),
        ("agnes", "Agnes Hilmarsdóttir", "Tannsmiður"),
        ("katrin", "Katrín Sigurðardóttir", "Tanntæknir"),
        ("ragnheidur", "Ragnheiður Valdimarsdóttir", "Tanntæknir"),
        ("thora", "Þóra Jóhannesdóttir", "Tanntæknir"),
        ("ingibjorg", "Ingibjörg Jóna Hallgrímsdóttir", "Tanntæknir"),
    ]
    # NOTE: engin raunveruleg portrettmynd er til af Gísla — skrifstofumyndin
    # (hero-office.jpg) er EKKI notuð sem andlitsmynd. Þar til mynd berst
    # (assets/images/staff-gisli.jpg) birtist stafmerktur staðgengill.
    img_map = {"agnes": "staff-agnes.jpg", "katrin": "staff-katrin.jpg",
               "ragnheidur": "staff-ragnheidur.jpg", "thora": "staff-thora.jpg",
               "ingibjorg": "staff-ingibjorg.jpg"}

    def staff_media(k, n):
        img = img_map.get(k)
        if img:
            return f'<img src="assets/images/{img}" alt="{n}">'
        initials = "".join(w[0] for w in n.split()[:2]).upper()
        return (f'<!-- TODO: vantar raunverulega portrettmynd af {n} '
                f'(assets/images/staff-{k}.jpg) --><div class="staff-photo-placeholder" '
                f'aria-hidden="true">{initials}</div>')

    staff_cards = "\n".join(
        f'<div class="staff-card">{staff_media(k, n)}<div class="pname">{n}</div><div class="ptitle">{t}</div></div>'
        for k, n, t in staff
    )
    P["is/starfsfolk.html"] = ("Starfsfólk", "starfsfolk",
        f"""<div class="wrap section">
  <div class="section-head"><div class="kicker">Starfsfólk</div><h2>Fólkið okkar</h2></div>
  <div class="staff-grid">{staff_cards}</div>
  <p style="margin-top:28px;color:var(--muted)">Auk þess starfar ritari í móttöku á stofunni. <a href="gisli-vilhjalmsson.html">Lesið nánar um Gísla</a>.</p>
</div>""")

    P["is/gisli-vilhjalmsson.html"] = ("Gísli Vilhjálmsson", "starfsfolk",
        """<div class="wrap section"><div class="prose">
  <p>Gísli Vilhjálmsson er fæddur 13. maí 1954 í Reykjavík. Hann lauk stúdentsprófi frá M.H. 1974 og prófi (Cand.odont.) frá Tannlæknadeild Háskóla Íslands 1980.</p>
  <p>Gísli fór beina leið í framhaldsnám til Bandaríkjanna og lærði tannréttingar við St. Louis University, Department of Orthodontics. Hann lauk M.Sc. prófi í tannréttingum þaðan 1982 og hlaut Marshalls-viðurkenningu frá St. Louis University Orthodontic Alumni Association fyrir bestan árangur í tveggja ára framhaldsnámi í tannréttingum.</p>
  <p>Gísli fékk tannlæknaleyfi 27. ágúst 1980 og sérfræðiréttindi í tannréttingum 16. júní 1988. Hann stundar virka endurmenntun og sækir reglulega tannréttingaþing erlendis.</p>
  <p>Gísli er giftur Kristínu Jónsdóttur og eiga þau þrjú börn. Kristín sér um bókhald stofunnar og sinnir einnig afleysingum í móttöku.</p>
</div></div>""")

    P["is/stadhsetning.html"] = ("Staðsetning", "stadhsetning",
        """<div class="wrap section"><div class="prose">
  <p>Tannlæknastofan er staðsett á <strong>Laugavegi 163, 105 Reykjavík</strong>. Gengið er inn á 1. hæð í gegnum sérinngang Katrínartúnsmegin og upp stiga á 2. hæð til hægri.</p>
  <img src="assets/images/husid.jpg" alt="Húsið á Laugavegi 163" style="border-radius:14px;margin:20px 0">
  <p><a class="btn primary" href="https://ja.is/kort/?q=G%C3%ADsli+Vilhj%C3%A1lmsson%2C+Laugavegi+163" target="_blank" rel="noopener noreferrer">Skoða á korti (Já.is)</a></p>
</div></div>""")

    P["is/timapantanir.html"] = ("Tímabókanir", "samband",
        f"""<div class="wrap section"><div class="prose">
  <p>Hægt er að panta tíma og breyta í síma <strong>{tel(ci)}</strong>.</p>
  <p>Einnig er hægt að senda tölvupóst á netfangið <a href="mailto:teinar@teinar.is">teinar@teinar.is</a>.</p>
  <h2>Opnunartími</h2>
  <table>
    <tr><th>Vetrartími (september–maí)</th><td>8:15–16:00</td></tr>
    <tr><th>Sumartími (júní–ágúst)</th><td>8:15–16:00 (föstudaga til 12:00)</td></tr>
  </table>
</div></div>""")

    P["is/hafdu-samband.html"] = ("Hafa samband", "samband",
        f"""<div class="wrap section"><div class="prose">
  <p>Endilega hafið samband ef þið hafið spurningar um tannréttingar eða viljið bóka tíma.</p>
  <div class="info-grid" style="margin-top:20px">
    <div class="info-item"><div class="icon">📞</div><div><div class="label">Sími</div><div class="value">{tel(ci)}</div></div></div>
    <div class="info-item"><div class="icon">✉️</div><div><div class="label">Netfang</div><div class="value"><a href="mailto:teinar@teinar.is">teinar@teinar.is</a></div></div></div>
    <div class="info-item"><div class="icon">📍</div><div><div class="label">Heimilisfang</div><div class="value">Laugavegur 163, 105 Reykjavík</div></div></div>
    <div class="info-item"><div class="icon">🚨</div><div><div class="label">Neyðarsími</div><div class="value">{tel_emergency(ci)} (Gísli)</div></div></div>
  </div>
</div></div>""")

    P["is/sjukratryggingar.html"] = ("Sjúkratryggingar", "tannrettingar",
        """<div class="wrap section"><div class="prose">
  <p>Við aðstoðum viðskiptavini okkar við umsóknir til Sjúkratrygginga Íslands.</p>
  <p>Nánari upplýsingar um þátttöku Sjúkratrygginga Íslands í tannréttingameðferðum má finna á heimasíðu þeirra:</p>
  <p><a href="https://island.is/tannlaekningar/tannrettingar">island.is/tannlaekningar/tannrettingar</a></p>
  <p><a href="https://www.sjukra.is/">www.sjukra.is</a></p>
</div></div>""")

    P["is/tenglar.html"] = ("Tenglar", "tannrettingar",
        """<div class="wrap section"><div class="prose">
  <ul>
    <li><strong>Breið bros</strong> — Samtök aðstandenda barna með skarð í vör og góm: <a href="https://www.facebook.com/groups/breidbros/">www.facebook.com/groups/breidbros</a></li>
    <li><strong>Sjúkratryggingar Íslands</strong>: <a href="https://www.sjukra.is/">www.sjukra.is</a></li>
  </ul>
</div></div>""")

    # ============ ENGLISH ============
    E = {}

    hero_en = f"""<section class="hero">
  <div class="wrap">
    <div class="hero-text">
      <h1>A beautiful smile — for life.</h1>
      <p class="lead">An orthodontic specialist practice at Laugavegur 163, Reykjavík. We focus exclusively on orthodontics for children and adults, with special expertise in cleft lip and palate.</p>
      <a class="btn primary" href="contact.html">Book an appointment</a>
    </div>
    <div class="hero-img">
      <img src="../assets/images/hero-office.jpg" alt="The practice">
    </div>
  </div>
</section>"""

    E["en/index.html"] = ("Home", "index",
        f"""{hero_en}
<section class="section">
  <div class="wrap">
    <div class="section-head"><div class="kicker">What we do</div><h2>Quality orthodontics for all ages</h2></div>
    <div class="cards">
      <div class="card"><div class="icon">🦷</div><h3>Children &amp; teens</h3><p>From the first visit at age 4–6 through the full eruption of adult teeth.</p></div>
      <div class="card"><div class="icon">💛</div><h3>Cleft lip and palate</h3><p>Years of experience treating children with cleft lip and palate, together with a specialist team.</p></div>
      <div class="card"><div class="icon">✨</div><h3>Adult orthodontics</h3><p>It is possible to straighten teeth at any age. Every case is assessed individually.</p></div>
      <div class="card"><div class="icon">🛡️</div><h3>Retainers &amp; follow-up</h3><p>We complete treatment with retainers to ensure long-lasting results.</p></div>
    </div>
  </div>
</section>
<section class="section alt">
  <div class="wrap">
    <div class="section-head"><div class="kicker">Opening hours</div><h2>Open Monday to Friday</h2></div>
    <div class="info-grid">
      <div class="info-item"><div class="icon">📅</div><div><div class="label">Winter (Sep–May)</div><div class="value">8:15–16:00</div></div></div>
      <div class="info-item"><div class="icon">☀️</div><div><div class="label">Summer (Jun–Aug)</div><div class="value">8:15–16:00, Fridays until 12:00</div></div></div>
      <div class="info-item"><div class="icon">📞</div><div><div class="label">Phone</div><div class="value">{tel(ce)}</div></div></div>
      <div class="info-item"><div class="icon">📍</div><div><div class="label">Location</div><div class="value">Laugavegur 163, Reykjavík</div></div></div>
    </div>
  </div>
</section>""")

    E["en/orthodontics.html"] = ("Orthodontics", "orthodontics",
        """<div class="wrap section"><div class="prose" style="max-width:none">
  <p class="lead" style="font-size:1.15rem">We focus exclusively on orthodontics and have done so since 1986. Below you will find information on the main aspects of treatment.</p>
  <div class="cards" style="margin-top:24px">
    <a class="card" href="first-visit.html"><h3>First visit</h3><p>When and how treatment begins.</p></a>
    <a class="card" href="cleft-lip-and-palate.html"><h3>Cleft lip and palate</h3><p>A specialised treatment pathway for children.</p></a>
    <a class="card" href="orthodontics-for-all.html"><h3>Orthodontics for all</h3><p>Brochure and general information.</p></a>
    <a class="card" href="appliances.html"><h3>Appliances &amp; retainers</h3><p>Follow-up after treatment.</p></a>
    <a class="card" href="first-aid.html"><h3>First aid</h3><p>Emergencies and assistance.</p></a>
    <a class="card" href="food-to-avoid.html"><h3>Food to avoid</h3><p>What is safe with braces.</p></a>
    <a class="card" href="pain.html"><h3>Pain relief</h3><p>Advice on managing discomfort.</p></a>
    <a class="card" href="insurance.html"><h3>Insurance</h3><p>Icelandic Health Insurance participation.</p></a>
  </div>
</div></div>""")

    E["en/first-visit.html"] = ("First visit", "orthodontics",
        f"""<div class="wrap section"><div class="prose">
  <p>We recommend bringing your child for an early first visit with an orthodontic specialist — ideally around age 4–6. This allows us to assess whether and when orthodontic treatment is needed and to plan it at the right time.</p>
  <p>Treatment usually begins during the mixed-dentition years, around age 7–8. The first examination is free of charge.</p>
  <div class="callout">To book a first visit, call <strong>{tel(ce)}</strong> or email <a href="mailto:teinar@teinar.is">teinar@teinar.is</a>.</div>
</div></div>""")

    E["en/cleft-lip-and-palate.html"] = ("Cleft lip and palate", "orthodontics",
        """<div class="wrap section"><div class="prose">
  <p>We have treated many children with cleft lip and palate. Below is general information about their orthodontic treatment. At the bottom of the page there is a link to <em>Breið bros</em>, the association for families of children with cleft lip and palate in Iceland.</p>

  <h2>Orthodontics for children with cleft lip and palate</h2>
  <p>Parents of children born with cleft palate or cleft lip and palate soon learn that their child needs care from a large team of specialists throughout childhood. Orthodontic specialists are dentists with advanced training in the treatment of tooth and bite irregularities, and they play an important role within this team.</p>
  <p>A cleft in the gum or palate is usually accompanied by tooth and bite irregularities that are a direct consequence of this congenital condition — for example an underbite due to insufficient forward growth of the upper jaw, or a crossbite. Tooth development near the cleft is often disturbed as well.</p>
  <p>Children born with cleft palate or cleft lip and palate therefore have a great need for orthodontics. Treatment and follow-up usually begin at an early age and do not end until the permanent teeth and growth are complete.</p>

  <h2>Treatment during the mixed dentition</h2>
  <p>Correction of tooth irregularities usually begins around age 7–8, but it is preferable to bring the child for an examination earlier, e.g. at age 4–6. When the child is 6–8 years old the first adult incisors emerge; they are usually rotated and misaligned and must be guided into place. This is done with removable plates or fixed (bonded) appliances. At the same time we often begin widening the side arches to correct crossbite.</p>

  <h2>Treatment after the permanent teeth erupt</h2>
  <p>If there has been a break after the first phase, a new phase usually begins at age 12–14 when all adult teeth have erupted. This treatment uses fixed appliances and aims to fully correct the teeth and bite. If there is a large discrepancy in jaw growth, the jaws may need to be repositioned surgically — such procedures are performed by plastic and oral surgeons.</p>

  <h2>Working together</h2>
  <p>Orthodontic treatment can take a long time. It is therefore important that children and parents be patient and work conscientiously toward the goal — the result is often remarkable when there is good cooperation.</p>
</div></div>""")

    E["en/orthodontics-for-all.html"] = ("Orthodontics for all", "orthodontics",
        """<div class="wrap section"><div class="prose">
  <p>Orthodontics can benefit people of all ages. The brochure below describes the treatment and the appliances used.</p>
  <h2>The road to a beautiful smile</h2>
  <p>A brochure covering the preparation for orthodontic treatment, the treatment itself, and the appliances used, as well as the criteria for deciding to begin treatment.</p>
  <div class="callout"><a href="../assets/docs/tannrettingar-fyrir-alla.pdf">Download the brochure (PDF, 10.8&nbsp;MB, in Icelandic)</a></div>
</div></div>""")

    E["en/first-aid.html"] = ("First aid", "orthodontics",
        f"""<div class="wrap section"><div class="prose">
  <p>In emergencies, you can contact Gísli by phone at <strong>{tel_emergency(ce)}</strong>.</p>
  <p>When Gísli is on holiday we try to arrange for another orthodontic specialist to be available. You can obtain information about this from us.</p>
</div></div>""")

    E["en/appliances.html"] = ("Appliances &amp; retainers", "orthodontics",
        """<div class="wrap section"><div class="prose">
  <p>At the end of treatment, retainers (appliances) are fitted in both arches to keep the result stable.</p>
  <ul>
    <li><strong>Upper retainer</strong> — bonded to the back of the teeth, from canine to canine. We recommend keeping it for about 15 years.</li>
    <li><strong>Lower retaining wire</strong> — bonded to the canines. We recommend that it never be removed.</li>
  </ul>
</div></div>""")

    foods_en = [
        ("🍎", "Apples", "better cut into pieces"),
        ("🥕", "Carrots", "shred or cut very small"),
        ("🌽", "Corn on the cob", "scrape off the cob, don't bite it"),
        ("🧊", "Ice cubes", "do not crunch"),
        ("🍬", "Hard sweets &amp; lollipops", "on the banned list"),
        ("🍿", "Popcorn", "husks get stuck under the gums"),
        ("🍬", "Sugary chewing gum", "stuck around appliances"),
        ("🐟", "Dried fish", "can break appliances"),
    ]
    food_cards_en = "\n".join(f'<div class="card"><div class="icon">{i}</div><h3>{n}</h3><p>{d}</p></div>' for i, n, d in foods_en)
    E["en/food-to-avoid.html"] = ("Food to avoid", "orthodontics",
        f"""<div class="wrap section"><div class="prose" style="max-width:none">
  <p>In most cases you will know what to avoid: anything hard or chewy that can damage the appliances.</p>
  <div class="cards" style="margin:20px 0">{food_cards_en}</div>
  <p>Also avoid biting nails, pencils and pens.</p>
</div></div>""")

    E["en/pain.html"] = ("Pain relief", "orthodontics",
        """<div class="wrap section"><div class="prose">
  <p>The perception of pain is very individual. We advise everyone to expect some discomfort after fixed appliances are fitted, but many of our patients later say it was not as bad as expected.</p>
  <p>In most cases a mild painkiller such as <strong>paracetamol</strong> is sufficient.</p>
  <h2>Our recommendation</h2>
  <p>Research shows that medication containing <strong>ibuprofen</strong> is much more effective for orthodontic discomfort, and we now recommend it. Packs of 20 × 200 mg tablets are available over the counter.</p>
  <p>The dosage for children is 20 mg/kg body weight per day, given in 3–4 equal doses. If a child weighs less than 30 kg, do not give more than 500 mg per day.</p>
  <div class="callout warn"><strong>Note:</strong> these are maximum doses. Because the risk of side effects increases with dose, use as little as possible. Avoid taking on an empty stomach and drink a glass of water with it. If the child takes other medication, consult a doctor first.</div>
  <h2>Side effects and contraindications</h2>
  <p>Some patients may have allergic reactions; those who have reacted to aspirin or paracetamol should avoid it. Stomach discomfort may occur, asthma may worsen, and dizziness and headache have been reported. The medication is not intended for pregnant women except on medical advice, and may increase the effect of other drugs such as blood thinners.</p>
</div></div>""")

    E["en/about.html"] = ("About", "about",
        """<div class="wrap section"><div class="prose">
  <img src="../assets/images/team.jpg" alt="The team" style="border-radius:14px;margin-bottom:20px">
  <p>The practice opened on Laugavegur in August 1986. Gísli is the only dentist, but alongside him work four dental technicians, a receptionist and a dental technician. We focus exclusively on orthodontics.</p>
  <p>We strive to provide careful, personal service and to make visits as comfortable as possible. We place great emphasis on education and information for both patients and parents, so that everyone can follow the progress of treatment.</p>
  <p>Quality orthodontics takes time, requires precision and is a significant investment. We all put great effort into treatment and aim for the best possible outcome. Our goal is that the result of treatment is lasting and brings satisfaction for life.</p>
  <p>Parents are always welcome with their children, whether they prefer to wait in the waiting room or come into the treatment room. Notes are written in the patient file at the end of each visit for parents unable to attend.</p>
</div></div>""")

    staff_en = [
        ("gisli", "Gísli Vilhjálmsson", "Dentist, orthodontic specialist"),
        ("agnes", "Agnes Hilmarsdóttir", "Dental technician"),
        ("katrin", "Katrín Sigurðardóttir", "Dental technician"),
        ("ragnheidur", "Ragnheiður Valdimarsdóttir", "Dental technician"),
        ("thora", "Þóra Jóhannesdóttir", "Dental technician"),
        ("ingibjorg", "Ingibjörg Jóna Hallgrímsdóttir", "Dental technician"),
    ]
    staff_cards_en = "\n".join(
        f'<div class="staff-card">{staff_media(k, n)}<div class="pname">{n}</div><div class="ptitle">{t}</div></div>'
        for k, n, t in staff_en
    )
    E["en/staff.html"] = ("Staff", "staff",
        f"""<div class="wrap section">
  <div class="section-head"><div class="kicker">Staff</div><h2>Our people</h2></div>
  <div class="staff-grid">{staff_cards_en}</div>
  <p style="margin-top:28px;color:var(--muted)">A receptionist also works at the practice. <a href="gisli-vilhjalmsson.html">Read more about Gísli</a>.</p>
</div>""")

    E["en/gisli-vilhjalmsson.html"] = ("Gísli Vilhjálmsson", "staff",
        """<div class="wrap section"><div class="prose">
  <p>Gísli Vilhjálmsson was born on 13 May 1954 in Reykjavík. He graduated from M.H. (Menntaskólinn í Hamrahlíð) in 1974 and received his dentistry degree (Cand.odont.) from the University of Iceland in 1980.</p>
  <p>Gísli went straight into postgraduate study in the United States, studying orthodontics at St. Louis University. He completed his M.Sc. in orthodontics in 1982 and received the Marshalls Award from the St. Louis University Orthodontic Alumni Association for the best results in the two-year postgraduate programme.</p>
  <p>Gísli received his dental licence on 27 August 1980 and his specialist licence in orthodontics on 16 June 1988. He pursues active continuing education and regularly attends orthodontic congresses abroad.</p>
  <p>Gísli is married to Kristín Jónsdóttir and they have three children. Kristín manages the practice's bookkeeping and also helps in reception.</p>
</div></div>""")

    E["en/location.html"] = ("Location", "location",
        """<div class="wrap section"><div class="prose">
  <p>The practice is located at <strong>Laugavegur 163, 105 Reykjavík</strong>. Enter on the ground floor through a separate entrance on the Katrínartún side and go up the stairs to the 2nd floor, on the right.</p>
  <img src="../assets/images/husid.jpg" alt="The building at Laugavegur 163" style="border-radius:14px;margin:20px 0">
  <p><a class="btn primary" href="https://ja.is/kort/?q=G%C3%ADsli+Vilhj%C3%A1lmsson%2C+Laugavegi+163" target="_blank" rel="noopener noreferrer">View on map (Já.is)</a></p>
</div></div>""")

    E["en/booking.html"] = ("Appointments", "contact",
        f"""<div class="wrap section"><div class="prose">
  <p>Appointments can be booked and changed by phone <strong>{tel(ce)}</strong>.</p>
  <p>You can also email <a href="mailto:teinar@teinar.is">teinar@teinar.is</a>.</p>
  <h2>Opening hours</h2>
  <table>
    <tr><th>Winter (Sep–May)</th><td>8:15–16:00</td></tr>
    <tr><th>Summer (Jun–Aug)</th><td>8:15–16:00 (Fridays until 12:00)</td></tr>
  </table>
</div></div>""")

    E["en/contact.html"] = ("Contact", "contact",
        f"""<div class="wrap section"><div class="prose">
  <p>Please get in touch if you have questions about orthodontics or would like to book an appointment.</p>
  <div class="info-grid" style="margin-top:20px">
    <div class="info-item"><div class="icon">📞</div><div><div class="label">Phone</div><div class="value">{tel(ce)}</div></div></div>
    <div class="info-item"><div class="icon">✉️</div><div><div class="label">Email</div><div class="value"><a href="mailto:teinar@teinar.is">teinar@teinar.is</a></div></div></div>
    <div class="info-item"><div class="icon">📍</div><div><div class="label">Address</div><div class="value">Laugavegur 163, 105 Reykjavík, Iceland</div></div></div>
    <div class="info-item"><div class="icon">🚨</div><div><div class="label">Emergency</div><div class="value">{tel_emergency(ce)} (Gísli)</div></div></div>
  </div>
</div></div>""")

    E["en/insurance.html"] = ("Insurance", "orthodontics",
        """<div class="wrap section"><div class="prose">
  <p>We assist our clients with applications to Icelandic Health Insurance (Sjúkratryggingar Íslands).</p>
  <p>Further information on Icelandic Health Insurance participation in orthodontic treatment can be found on their website:</p>
  <p><a href="https://island.is/en/dentistry/orthodontics">island.is/en/dentistry/orthodontics</a></p>
  <p><a href="https://www.sjukra.is/">www.sjukra.is</a></p>
</div></div>""")

    E["en/links.html"] = ("Links", "orthodontics",
        """<div class="wrap section"><div class="prose">
  <ul>
    <li><strong>Breið bros</strong> — association of families of children with cleft lip and palate: <a href="https://www.facebook.com/groups/breidbros/">www.facebook.com/groups/breidbros</a></li>
    <li><strong>Icelandic Health Insurance</strong>: <a href="https://www.sjukra.is/">www.sjukra.is</a></li>
  </ul>
</div></div>""")

    # copy static assets (css, images, docs) into the deployable site/ folder
    shutil.copytree(ASSETS, os.path.join(SITE, "assets"), dirs_exist_ok=True)

    # write all pages
    count = 0
    all_pages = {**P, **E}
    for path, (title, active, body) in all_pages.items():
        lang = path.split("/")[0]
        # home pages embed their own hero in `body`, so suppress the h1 there
        is_home = path in ("is/index.html", "en/index.html")
        rendered = page(lang, path, title, body, active=active, prehead=not is_home)
        out = os.path.join(SITE, path)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(rendered)
        count += 1

    # root index redirect to Icelandic home
    redirect = """<!DOCTYPE html>
<html lang="is">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url=is/index.html">
<link rel="canonical" href="https://www.teinar.is/is/index.html">
<link rel="alternate" hreflang="is" href="https://www.teinar.is/is/index.html">
<link rel="alternate" hreflang="en" href="https://www.teinar.is/en/index.html">
<link rel="alternate" hreflang="x-default" href="https://www.teinar.is/is/index.html">
<title>Teinar — Tannlæknastofa Gísla Vilhjálmssonar</title>
</head>
<body>
<p><a href="is/index.html">Íslenska →</a> &nbsp; <a href="en/index.html">English →</a></p>
</body>
</html>"""
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(redirect)

    # sitemap.xml
    today = datetime.date.today().isoformat()
    locs = [f"{SITE_URL}/"] + [f"{SITE_URL}/{p}" for p in all_pages]
    urls = "\n".join(
        f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod></url>" for loc in locs
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n"
    )
    with open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(sitemap)

    # robots.txt
    robots = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    with open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(robots)

    print(f"Generated {count} pages + root redirect, sitemap.xml, robots.txt and assets into {SITE}")

if __name__ == "__main__":
    build()