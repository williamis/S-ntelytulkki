import streamlit as st
import anthropic
from saadokset import SAADOKSET

# Sivun asetukset
st.set_page_config(
    page_title="Sääntelytulkki – Energia-alan säädökset",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Sääntelytulkki")
st.markdown("**Energia-alan säädökset selkokielellä** – työkalu energia-alan ammattilaisille")
st.divider()

# Sidebar – lähdetiedot
with st.sidebar:
    st.header("📚 Lähteet")
    st.markdown("Tietokanta sisältää säädöksiä seuraavista lähteistä:")
    
    kategoriat = list(set(s["kategoria"] for s in SAADOKSET))
    for kat in kategoriat:
        saadokset_kategoriassa = [s for s in SAADOKSET if s["kategoria"] == kat]
        with st.expander(f"📁 {kat} ({len(saadokset_kategoriassa)} säädöstä)"):
            for s in saadokset_kategoriassa:
                st.markdown(f"- [{s['nimi']}]({s['url']})")
    
    st.divider()
    st.caption("Säädöstiedot perustuvat julkisiin lähteisiin: Finlex, Energiavirasto ja EUR-Lex")

# Pääsisältö
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Kysy energia-alan sääntelystä")
    
    # Esimerkkikysymykset
    st.markdown("**Esimerkkikysymyksiä:**")
    esimerkit = [
        "Kuinka paljon sähkönsiirtohintoja saa korottaa vuodessa?",
        "Mitä toimitusvarmuusvaatimuksia jakeluverkonhaltijalle on asetettu?",
        "Mitä tietoja sähkölaskussa pitää olla?",
        "Mitä kulutusjousto tarkoittaa?",
        "Mitkä ovat EU:n uusiutuvan energian tavoitteet?",
    ]
    
    cols = st.columns(2)
    for i, esimerkki in enumerate(esimerkit):
        if cols[i % 2].button(esimerkki, key=f"esimerkki_{i}", use_container_width=True):
            st.session_state["kysymys"] = esimerkki

    kysymys = st.text_area(
        "Kirjoita kysymyksesi:",
        value=st.session_state.get("kysymys", ""),
        height=100,
        placeholder="Esim. Mitä sähkömarkkinalaki sanoo toimitusvarmuudesta?"
    )

    if st.button("🔍 Hae vastaus", type="primary", use_container_width=True):
        if not kysymys.strip():
            st.warning("Kirjoita kysymys ensin.")
        else:
            # Rakennetaan konteksti säädöksistä
            konteksti = "\n\n".join([
                f"[{s['nimi']}]\nLähde: {s['url']}\n{s['sisalto']}"
                for s in SAADOKSET
            ])

            prompt = f"""Olet energia-alan sääntelyasiantuntija. Sinulle on annettu kokoelma energia-alan säädöksiä ja viranomaisohjeita.

Tehtäväsi on vastata ammattilaisille suunnatusti, selkeästi ja tarkasti. 

TÄRKEÄÄ:
- Viittaa aina konkreettisiin säädöksiin ja lakipykäliin
- Käytä selkeää kieltä mutta säilytä juridinen tarkkuus
- Jos et löydä vastausta tietokannasta, sano se selvästi
- Mainitse aina minkä lain tai direktiivin perusteella vastaat

SÄÄDÖSTIETOKANTA:
{konteksti}

KYSYMYS: {kysymys}

Vastaa suomeksi. Rakenna vastauksesi selkeästi:
1. Suora vastaus kysymykseen
2. Juridinen perusta (mikä laki/pykälä)
3. Käytännön vaikutukset ammattilaiselle"""

            with st.spinner("Haetaan vastausta..."):
                try:
                    client = anthropic.Anthropic()
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1000,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    vastaus = response.content[0].text

                    st.success("✅ Vastaus löydetty")
                    st.markdown("### Vastaus")
                    st.markdown(vastaus)

                    # Lähdeviittaukset
                    st.divider()
                    st.markdown("### 📎 Lähdeviittaukset")
                    st.markdown("Tarkista alkuperäiset säädökset:")
                    
                    for s in SAADOKSET:
                        if any(keyword in kysymys.lower() or keyword in vastaus.lower() 
                               for keyword in ["siirto", "korotus", "hinta"]) and "siirtohinnat" in s["id"]:
                            st.markdown(f"- 📄 [{s['nimi']}]({s['url']})")
                        elif any(keyword in kysymys.lower() or keyword in vastaus.lower() 
                                 for keyword in ["toimitus", "varmuus", "keskeytys"]) and "toimitusvarmuus" in s["id"]:
                            st.markdown(f"- 📄 [{s['nimi']}]({s['url']})")
                        elif any(keyword in kysymys.lower() or keyword in vastaus.lower() 
                                 for keyword in ["lasku", "laskutus"]) and "laskutus" in s["id"]:
                            st.markdown(f"- 📄 [{s['nimi']}]({s['url']})")
                        elif any(keyword in kysymys.lower() or keyword in vastaus.lower() 
                                 for keyword in ["uusiutuva", "red", "direktiivi"]) and "uusiutuva" in s["id"]:
                            st.markdown(f"- 📄 [{s['nimi']}]({s['url']})")
                        elif any(keyword in kysymys.lower() or keyword in vastaus.lower() 
                                 for keyword in ["jousto", "kulutus"]) and "kulutusjousto" in s["id"]:
                            st.markdown(f"- 📄 [{s['nimi']}]({s['url']})")
                    
                    st.markdown("**Kaikki lähteet:**")
                    for s in set(s["url"] for s in SAADOKSET):
                        st.markdown(f"- {s}")

                except Exception as e:
                    st.error(f"Virhe API-kutsussa: {e}")
                    st.info("Varmista että ANTHROPIC_API_KEY on asetettu ympäristömuuttujiin.")

with col2:
    st.subheader("ℹ️ Ohjeet")
    st.info("""
**Miten käyttää:**
1. Kirjoita kysymys tekstikenttään tai valitse esimerkkikysymys
2. Paina "Hae vastaus"
3. Lue vastaus ja tarkista lähdeviittaukset

**Työkalu sopii:**
- Säädösten nopeaan tulkintaan
- Lakipykälien selventämiseen
- Käytännön vaikutusten arviointiin
""")
    
    st.subheader("⚠️ Huomio")
    st.warning("""
Tämä työkalu on tarkoitettu tiedon hakemisen apuvälineeksi. 
Se ei korvaa juridista neuvontaa. 
Tarkista aina alkuperäinen säädösteksti ennen päätöksentekoa.
""")

st.divider()
st.caption("Sääntelytulkki v1.0 | Lähteet: Finlex, Energiavirasto, EUR-Lex | Rakennettu Claude API:lla")
