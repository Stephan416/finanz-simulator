# ------------------------------------------------------------
# FINANZ-SIMULATOR BASISMODELL
# ------------------------------------------------------------
# Dieses Programm simuliert mögliche Vermögensverläufe.
# Neu: Das Portfolio besteht aus zwei Anlageklassen:
# 1. Aktien
# 2. Anleihen
#
# Die erwartete Rendite und Volatilität des Portfolios ergeben sich
# aus Aktienrendite, Anleihenrendite, Aktienvolatilität,
# Anleihenvolatilität, Aktienquote und Korrelation.
# ------------------------------------------------------------

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import t


# ------------------------------------------------------------
# 1. GRUNDEINSTELLUNG DER WEB-APP
# ------------------------------------------------------------

st.set_page_config(
    page_title="Finanz-Simulator",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
div[data-testid="stNumberInput"],
div[data-testid="stSlider"],
div[data-testid="stSelectbox"] {
    margin-bottom: 14px;
}

/* ✅ NUR Icons bekommen Hover */
.icon-box {
    transition: 0.2s ease;
}

.icon-box:hover {
    transform: scale(1.15);
    filter: drop-shadow(0px 4px 10px rgba(123, 97, 255, 0.35));
}


</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# 2. HILFSFUNKTION: PORTFOLIO-SIMULATION MIT T-VERTEILUNG
# ------------------------------------------------------------

def simulate_t_gbm_portfolio(
    startwert,
    aktienrendite,
    anleihenrendite,
    aktienvolatilitaet,
    anleihenvolatilitaet,
    aktienquote,
    korrelation,
    jahre,
    schritte_pro_jahr,
    simulationen,
    freiheitsgrade
):
    """
    Diese Funktion simuliert ein Portfolio aus Aktien und Anleihen.

    startwert:
        Anfangsvermögen

    aktienrendite:
        Erwartete Jahresrendite der Aktien, z. B. 0.07 für 7 %

    anleihenrendite:
        Erwartete Jahresrendite der Anleihen, z. B. 0.03 für 3 %

    aktienvolatilitaet:
        Erwartete Jahresschwankung der Aktien

    anleihenvolatilitaet:
        Erwartete Jahresschwankung der Anleihen

    aktienquote:
        Anteil des Vermögens in Aktien, z. B. 0.70 für 70 %

    korrelation:
        Zusammenhang zwischen Aktien und Anleihen.
        -1 = bewegen sich gegensätzlich
         0 = unabhängig
         1 = bewegen sich gleich

    freiheitsgrade:
        Parameter der t-Verteilung.
        Kleinere Werte bedeuten häufigere Extremereignisse.
    """

    # Anleihenquote ist der Rest des Portfolios.
    anleihenquote = 1 - aktienquote

    # Die Portfolio-Rendite ist der gewichtete Durchschnitt
    # aus Aktienrendite und Anleihenrendite.
    portfolio_rendite = (
        aktienquote * aktienrendite
        + anleihenquote * anleihenrendite
    )

    # Die Portfolio-Volatilität berücksichtigt:
    # - Aktienvolatilität
    # - Anleihenvolatilität
    # - Gewichtung beider Anlageklassen
    # - Korrelation zwischen Aktien und Anleihen
    portfolio_volatilitaet = np.sqrt(
        aktienquote ** 2 * aktienvolatilitaet ** 2
        + anleihenquote ** 2 * anleihenvolatilitaet ** 2
        + 2
        * aktienquote
        * anleihenquote
        * korrelation
        * aktienvolatilitaet
        * anleihenvolatilitaet
    )

    # Gesamtzahl der Simulationsschritte.
    anzahl_schritte = jahre * schritte_pro_jahr

    # Länge eines Zeitschritts in Jahren.
    dt = 1 / schritte_pro_jahr

    # Matrix für alle simulierten Vermögenswerte.
    # Zeilen = Zeitpunkte
    # Spalten = Simulationen
    werte = np.zeros((anzahl_schritte + 1, simulationen))

    # Alle Simulationen starten mit dem gleichen Startwert.
    werte[0, :] = startwert

    # Schrittweise Simulation.
    for zeitpunkt in range(1, anzahl_schritte + 1):

        # Zufallswerte aus t-Verteilung ziehen.
        zufall = t.rvs(df=freiheitsgrade, size=simulationen)

        # t-Verteilung auf ungefähr Standardabweichung 1 skalieren.
        zufall = zufall / np.sqrt(freiheitsgrade / (freiheitsgrade - 2))

        # Rendite des aktuellen Simulationsschritts.
        schritt_rendite = (
            (portfolio_rendite - 0.5 * portfolio_volatilitaet ** 2) * dt
            + portfolio_volatilitaet * np.sqrt(dt) * zufall
        )

        # Neuer Wert = alter Wert * exponentielle Rendite.
        werte[zeitpunkt, :] = werte[zeitpunkt - 1, :] * np.exp(schritt_rendite)

    return werte, portfolio_rendite, portfolio_volatilitaet


# ------------------------------------------------------------
# 3. HILFSFUNKTION: INTERPRETATION
# ------------------------------------------------------------

def interpretation_text(startwert, median, p5, p95):
    if p5 > startwert:
        return "Dein Vermögen entwickelt sich in den meisten Szenarien sehr stabil."
    elif median > startwert:
        return "Dein Vermögen wächst im mittleren Szenario, kann in schwachen Marktphasen aber deutlich zurückfallen."
    else:
        return "Dein Vermögen steht unter Druck. Die gewählten Annahmen wirken eher riskant."


# ------------------------------------------------------------
# 4. APP-ÜBERSCHRIFT
# ------------------------------------------------------------

<div style="font-size: 36px; font-weight: 700;">
    ⚡ Finanz-Simulator
</div>

st.markdown(
"""
<div style="padding: 10px 0 25px 0;">

<div style="
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #7c3aed, #3b82f6);
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
    -webkit-text-fill-color: transparent;
">
Finanz-Simulator
</div>

<div style="
    font-size: 17px;
    color: #6b7280;
    margin-top: 6px;
    max-width: 900px;
">
Simuliere dein Vermögen mit Aktien, Anleihen und realistischen Marktschocks – verständlich, visuell und in heutiger Kaufkraft.
</div>

</div>
""",
unsafe_allow_html=True
)

# ------------------------------------------------------------
# 5. EINGABEBEREICH
# ------------------------------------------------------------

eingabe_spalte, ergebnis_spalte = st.columns([0.7, 1.3], gap="large")


with eingabe_spalte:

    st.markdown("### Eingaben")
    def icon_input(icon, color, widget_func):
        icon_col, input_col = st.columns([0.12, 0.88])
        with icon_col:
            st.markdown(
                f"""
                <div class="icon-box" style="
                    width:42px;
                    height:42px;
                    border-radius:12px;
                    background:{color}18;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:22px;
                    margin-top:22px;
                ">
                    {icon}
                </div>
                """,
                unsafe_allow_html=True
            )
        with input_col:
            return widget_func()

    startwert = icon_input(
        "💼",
        "#7c3aed",
        lambda: st.number_input(
            "Startvermögen (€)",
            min_value=0,
            value=100_000,
            step=10_000
        )
    )

    aktienquote_prozent = icon_input(
        "📊",
        "#7c3aed",
        lambda: st.slider(
            "Aktienquote (%)",
            min_value=0,
            max_value=100,
            value=60
        )
    )

    aktienrendite_prozent = icon_input(
        "📈",
        "#22c55e",
        lambda: st.number_input(
            "Erwartete reale Aktienrendite (%)",
            min_value=-20.0,
            max_value=30.0,
            value=7.0,
            step=0.5
        )
    )


    anleihenrendite_prozent = icon_input(
        "🛡️",
        "#10b981",
        lambda: st.number_input(
            "Erwartete reale Anleihenrendite (%)",
            min_value=-20.0,
            max_value=30.0,
            value=3.0,
            step=0.5
        )
    )

   


    

    jahre = icon_input(
        "📅",
        "#ef4444",
        lambda: st.slider(
            "Zeitraum in Jahren",
            min_value=1,
            max_value=60,
            value=30
        )
    )

    

   

    marktrisiko = st.selectbox(
        "Marktrisiko",
        options=[
            "Normale Märkte",
            "Leicht erhöhte Extremereignisse",
            "Starke Extremereignisse"
        ],
        index=1
    )

    if marktrisiko == "Normale Märkte":
        freiheitsgrade = 30
    elif marktrisiko == "Leicht erhöhte Extremereignisse":
        freiheitsgrade = 10
    else:
        freiheitsgrade = 5

    st.caption(
        "Der Marktrisiko-Modus bestimmt, wie häufig außergewöhnlich starke Marktbewegungen auftreten."
    )

    simulationen = icon_input(
        "👥",
        "#ef4444",
        lambda: st.slider(
            "Anzahl Simulationen",
            min_value=100,
            max_value=20000,
            value=2000,
            step=100
        )
    )

    st.caption("Für fortgeschrittene Annahmen wie Volatilität und Korrelation:")
    with st.expander("👑 Erweiterte Einstellungen (optional)"):
        aktienvolatilitaet_prozent = st.number_input(
            "Aktienvolatilität (%)",
            min_value=0.0,
            max_value=80.0,
            value=15.0,
            step=0.5
        )

        anleihenvolatilitaet_prozent = st.number_input(
            "Anleihenvolatilität (%)",
            min_value=0.0,
            max_value=80.0,
            value=6.0,
            step=0.5
        )

        korrelation = st.slider(
            "Korrelation Aktien / Anleihen",
            min_value=-1.0,
            max_value=1.0,
            value=0.2,
            step=0.1
        )

        schritte_pro_jahr = st.selectbox(
            "Zeitschritte",
            options=[12, 52],
            index=0,
            format_func=lambda x: {
                12: "monatlich",
                52: "wöchentlich"
            }[x]
        )

    st.caption(
    "Alle Renditen sind real (nach Inflation). "
    "Die Ergebnisse zeigen Kaufkraft in heutigen Euro. "
    "Das Portfolio besteht aus Aktien und Anleihen. "
    "Eine Aktienquote von 60% impliziert einen Anleihenanteil von 40%."
    )  
    simulation_starten = st.button("🚀 Simulation starten", use_container_width=True)


# ------------------------------------------------------------
# 6. PROZENTWERTE UMWANDELN
# ------------------------------------------------------------

aktienquote = aktienquote_prozent / 100
aktienrendite = aktienrendite_prozent / 100
anleihenrendite = anleihenrendite_prozent / 100
aktienvolatilitaet = aktienvolatilitaet_prozent / 100
anleihenvolatilitaet = anleihenvolatilitaet_prozent / 100


# ------------------------------------------------------------
# 7. SIMULATION AUSFÜHREN
# ------------------------------------------------------------

if simulation_starten:

    with st.spinner("Simulation läuft..."):

        werte, portfolio_rendite, portfolio_volatilitaet = simulate_t_gbm_portfolio(
            startwert=startwert,
            aktienrendite=aktienrendite,
            anleihenrendite=anleihenrendite,
            aktienvolatilitaet=aktienvolatilitaet,
            anleihenvolatilitaet=anleihenvolatilitaet,
            aktienquote=aktienquote,
            korrelation=korrelation,
            jahre=jahre,
            schritte_pro_jahr=schritte_pro_jahr,
            simulationen=simulationen,
            freiheitsgrade=freiheitsgrade
        )

    endwerte = werte[-1, :]

    median = np.median(endwerte)
    p5 = np.percentile(endwerte, 5)
    p95 = np.percentile(endwerte, 95)
    durchschnitt = np.mean(endwerte)
    minimum = np.min(endwerte)
    maximum = np.max(endwerte)

    with ergebnis_spalte:

        st.markdown("### Ergebnis")

        text = interpretation_text(startwert, median, p5, p95)
        st.success(text)

        k1, k2, k3 = st.columns(3)

        k1.metric(
            label="Median",
            value=f"{median:,.0f} €".replace(",", ".")
        )

        k2.metric(
            label="Schlechtes 5%-Szenario",
            value=f"{p5:,.0f} €".replace(",", ".")
        )

        k3.metric(
            label="Gutes 95%-Szenario",
            value=f"{p95:,.0f} €".replace(",", ".")
        )

        with st.expander("Weitere Kennzahlen anzeigen"):
            st.write(f"Durchschnitt: {durchschnitt:,.0f} €".replace(",", "."))
            st.write(f"Minimum: {minimum:,.0f} €".replace(",", "."))
            st.write(f"Maximum: {maximum:,.0f} €".replace(",", "."))
            st.write(f"Portfolio-Rendite: {portfolio_rendite * 100:.2f} % p.a.")
            st.write(f"Portfolio-Volatilität: {portfolio_volatilitaet * 100:.2f} % p.a.")
            st.write(f"Aktienquote: {aktienquote_prozent:.0f} %")
            st.write(f"Anleihenquote: {100 - aktienquote_prozent:.0f} %")


    # ------------------------------------------------------------
    # 8. ZEITACHSE
    # ------------------------------------------------------------

    zeitachse = np.linspace(0, jahre, werte.shape[0])


    # ------------------------------------------------------------
    # 9. DIAGRAMM: BEISPIELPFADE
    # ------------------------------------------------------------

    st.markdown("### Beispielhafte Zukunftspfade")

    fig_pfade = go.Figure()

    anzahl_anzeigen = min(30, simulationen)

    for i in range(anzahl_anzeigen):
        fig_pfade.add_trace(
            go.Scatter(
                x=zeitachse,
                y=werte[:, i],
                mode="lines",
                line=dict(width=1),
                opacity=0.25,
                showlegend=False
            )
        )

    median_pfad = np.median(werte, axis=1)

    fig_pfade.add_trace(
        go.Scatter(
            x=zeitachse,
            y=median_pfad,
            mode="lines",
            name="Medianpfad",
            line=dict(width=4)
        )
    )

    fig_pfade.update_layout(
        height=450,
        xaxis_title="Jahre",
        yaxis_title="Vermögen (€)",
        template="plotly_white"
    )

    st.plotly_chart(fig_pfade, use_container_width=True)


    # ------------------------------------------------------------
    # 10. DIAGRAMM: ENDWERT-VERTEILUNG
    # ------------------------------------------------------------

    st.markdown("### Verteilung der Endwerte")

    fig_hist = go.Figure()

    fig_hist.add_trace(
        go.Histogram(
            x=endwerte,
            nbinsx=60,
            name="Endwerte"
        )
    )

    fig_hist.add_vline(
        x=p5,
        line_width=2,
        line_dash="dash",
        annotation_text="5%-Szenario",
        annotation_position="top left"
    )

    fig_hist.add_vline(
        x=median,
        line_width=3,
        annotation_text="Median",
        annotation_position="top"
    )

    fig_hist.add_vline(
        x=p95,
        line_width=2,
        line_dash="dash",
        annotation_text="95%-Szenario",
        annotation_position="top right"
    )

    fig_hist.update_layout(
        height=450,
        xaxis_title="Endvermögen (€)",
        yaxis_title="Anzahl Simulationen",
        template="plotly_white"
    )

    st.plotly_chart(fig_hist, use_container_width=True)


    # ------------------------------------------------------------
    # 11. MODELL-HINWEIS
    # ------------------------------------------------------------

    st.info(
        "Hinweis: Dieses Basismodell ist bewusst vereinfacht. "
        "Es berücksichtigt Aktien, Anleihen, deren Gewichtung, Volatilität und Korrelation. "
        "Noch nicht enthalten sind Entnahmen, Inflation, Gebühren, Rebalancing, "
        "Volatility Clustering oder wechselnde Marktphasen."
    )

else:
    with ergebnis_spalte:
        st.markdown("### Ergebnis")
        st.write("Starte die Simulation, um mögliche Zukunftsverläufe zu sehen.")