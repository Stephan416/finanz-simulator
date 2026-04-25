# ------------------------------------------------------------
# FINANZ-SIMULATOR BASISMODELL
# ------------------------------------------------------------
# Dieses Programm ist eine erste kleine Streamlit-App.
# Es simuliert mögliche Vermögensverläufe mit einem
# GBM-ähnlichen Modell und t-verteilten Zufallsschocks.
#
# Ziel:
# - einfach verständlich
# - später gut erweiterbar
# - geeignet als Grundlage für Entnahme, Premium-Features,
#   Interpretationstexte und weitere Modelle
# ------------------------------------------------------------


# Streamlit ist das Framework, mit dem aus Python eine Web-App wird.
import streamlit as st

# NumPy brauchen wir für schnelle mathematische Berechnungen.
import numpy as np

# Pandas brauchen wir für tabellarische Daten.
import pandas as pd

# Plotly nutzen wir für schöne interaktive Diagramme.
import plotly.graph_objects as go

# Aus scipy.stats importieren wir die t-Verteilung.
from scipy.stats import t


# ------------------------------------------------------------
# 1. GRUNDEINSTELLUNG DER WEB-APP
# ------------------------------------------------------------

# Hier legen wir den Titel, das Icon und das Layout der App fest.
st.set_page_config(
    page_title="Finanz-Simulator",
    page_icon="📈",
    layout="wide"
)


# ------------------------------------------------------------
# 2. HILFSFUNKTION: T-VERTEILTE SIMULATION
# ------------------------------------------------------------

def simulate_t_gbm(
    startwert,
    rendite,
    volatilitaet,
    jahre,
    schritte_pro_jahr,
    simulationen,
    freiheitsgrade
):
    """
    Diese Funktion simuliert viele mögliche Vermögenspfade.

    startwert:
        Anfangsvermögen, z. B. 100.000 €

    rendite:
        erwartete Jahresrendite, z. B. 0.07 für 7 %

    volatilitaet:
        erwartete Jahresschwankung, z. B. 0.15 für 15 %

    jahre:
        Simulationsdauer in Jahren

    schritte_pro_jahr:
        Anzahl der Rechenschritte pro Jahr.
        12 = monatlich, 252 = börsentäglich

    simulationen:
        Anzahl der simulierten Pfade

    freiheitsgrade:
        Parameter der t-Verteilung.
        Kleinere Werte erzeugen extremere Ausschläge.
    """

    # Die Gesamtzahl aller Zeitschritte ergibt sich aus Jahren mal Schritten pro Jahr.
    anzahl_schritte = jahre * schritte_pro_jahr

    # dt ist die Länge eines einzelnen Zeitschritts in Jahren.
    # Bei monatlicher Simulation wäre dt = 1 / 12.
    dt = 1 / schritte_pro_jahr

    # Wir erstellen eine Matrix für alle simulierten Vermögenswerte.
    # Jede Zeile ist ein Zeitpunkt.
    # Jede Spalte ist eine einzelne Simulation.
    werte = np.zeros((anzahl_schritte + 1, simulationen))

    # Zum Zeitpunkt 0 starten alle Simulationen mit dem gleichen Startwert.
    werte[0, :] = startwert

    # Jetzt simulieren wir Schritt für Schritt die Zukunft.
    for zeitpunkt in range(1, anzahl_schritte + 1):

        # Wir ziehen Zufallszahlen aus einer t-Verteilung.
        # Diese Verteilung erzeugt häufiger extreme Werte als die Normalverteilung.
        zufall = t.rvs(df=freiheitsgrade, size=simulationen)

        # Die t-Verteilung hat nicht automatisch Standardabweichung 1.
        # Damit unsere Volatilität später ungefähr stimmt, skalieren wir sie.
        zufall = zufall / np.sqrt(freiheitsgrade / (freiheitsgrade - 2))

        # Das ist die Renditeformel.
        # Sie ähnelt der geometrischen Brownschen Bewegung.
        #
        # Der erste Teil ist der Drift:
        # (rendite - 0.5 * volatilitaet^2) * dt
        #
        # Der zweite Teil ist der Zufallsteil:
        # volatilitaet * sqrt(dt) * zufall
        #
        # Anders als beim klassischen GBM ist "zufall" hier nicht normalverteilt,
        # sondern t-verteilt.
        schritt_rendite = (
            (rendite - 0.5 * volatilitaet ** 2) * dt
            + volatilitaet * np.sqrt(dt) * zufall
        )

        # Der neue Vermögenswert ergibt sich aus:
        # alter Wert mal exponentielle Rendite.
        #
        # np.exp(...) sorgt dafür, dass der Wert nicht negativ werden kann.
        werte[zeitpunkt, :] = werte[zeitpunkt - 1, :] * np.exp(schritt_rendite)

    # Wir geben die gesamte Matrix zurück.
    return werte


# ------------------------------------------------------------
# 3. HILFSFUNKTION: INTERPRETATION DES ERGEBNISSES
# ------------------------------------------------------------

def interpretation_text(startwert, median, p5, p95):
    """
    Diese Funktion erzeugt später den verständlichen Erklärungstext.
    Aktuell ist sie bewusst einfach gehalten.
    Später kannst du hier sehr viel Intelligenz einbauen.
    """

    # Wenn das schlechte 5%-Szenario über dem Startwert liegt,
    # klingt das Ergebnis sehr stabil.
    if p5 > startwert:
        return "Dein Vermögen entwickelt sich in den meisten Szenarien sehr stabil."

    # Wenn der Median über dem Startwert liegt, aber das 5%-Szenario darunter,
    # ist das Ergebnis grundsätzlich gut, aber mit Risiko.
    elif median > startwert:
        return "Dein Vermögen wächst im mittleren Szenario, kann in schwachen Marktphasen aber deutlich zurückfallen."

    # Wenn sogar der Median unter dem Startwert liegt,
    # ist das Szenario eher kritisch.
    else:
        return "Dein Vermögen steht unter Druck. Die gewählten Annahmen wirken eher riskant."


# ------------------------------------------------------------
# 4. APP-ÜBERSCHRIFT
# ------------------------------------------------------------

st.title("Finanz-Simulator")
st.subheader("Basismodell: stochastische Simulation mit Drift und t-verteilten Marktschocks")

st.write(
    "Dieses Modell simuliert viele mögliche Zukunftsverläufe deines Vermögens. "
    "Es nutzt eine erwartete Rendite, eine erwartete Schwankung und eine t-Verteilung, "
    "damit extreme Marktbewegungen realistischer abgebildet werden als bei einer reinen Normalverteilung."
)


# ------------------------------------------------------------
# 5. EINGABEBEREICH
# ------------------------------------------------------------

# Wir teilen die Seite in zwei Spalten.
# Links kommen die Eingaben, rechts später die wichtigsten Ergebnisse.
eingabe_spalte, ergebnis_spalte = st.columns([1, 1])


with eingabe_spalte:

    # Überschrift für Eingaben.
    st.markdown("### Eingaben")

    # Startwert des Vermögens.
    startwert = st.number_input(
        "Startvermögen (€)",
        min_value=0,
        value=100_000,
        step=10_000
    )

    # Erwartete Jahresrendite in Prozent.
    rendite_prozent = st.number_input(
        "Erwartete Jahresrendite (%)",
        min_value=-20.0,
        max_value=30.0,
        value=7.0,
        step=0.5
    )

    # Erwartete Jahresvolatilität in Prozent.
    volatilitaet_prozent = st.number_input(
        "Erwartete Jahresschwankung / Volatilität (%)",
        min_value=0.0,
        max_value=80.0,
        value=15.0,
        step=0.5
    )

    # Simulationsdauer in Jahren.
    jahre = st.slider(
        "Zeitraum in Jahren",
        min_value=1,
        max_value=60,
        value=30
    )

    # Anzahl der Simulationen.
    simulationen = st.slider(
        "Anzahl Simulationen",
        min_value=100,
        max_value=20000,
        value=5000,
        step=100
    )

    # Schritte pro Jahr.
    # Monatlich ist für langfristige Finanzplanung oft ausreichend.
    schritte_pro_jahr = st.selectbox(
        "Zeitschritte",
        options=[12, 52, 252],
        index=0,
        format_func=lambda x: {
            12: "monatlich",
            52: "wöchentlich",
            252: "börsentäglich"
        }[x]
    )

    # Freiheitsgrade der t-Verteilung.
    # Niedriger = mehr extreme Ausschläge.
    marktrisiko = st.selectbox(
        "Marktrisiko",
        options=[
            "Normale Märkte",
            "Leicht erhöhte Extremereignisse",
            "Starke Extremereignisse"
        ],
        index=1
    )

    # Normale Märkte: fast wie Normalverteilung.
    # Leicht erhöhte Extremereignisse: realistischer Standardmodus.
    # Starke Extremereignisse: mehr Crash- und Boomphasen.
    if marktrisiko == "Normale Märkte":
        freiheitsgrade = 30
    elif marktrisiko == "Leicht erhöhte Extremereignisse":
        freiheitsgrade = 10
    else:
        freiheitsgrade = 5

    # Kurze Erklärung für Nutzer.
    st.caption(
        "Der Marktrisiko-Modus bestimmt, wie häufig außergewöhnlich starke Marktbewegungen auftreten."
    )

    # Button zum Starten der Simulation.
    simulation_starten = st.button("Simulation starten", use_container_width=True)


# ------------------------------------------------------------
# 6. SIMULATION AUSFÜHREN
# ------------------------------------------------------------

# Prozentwerte werden in Dezimalzahlen umgerechnet.
# 7 % wird also zu 0.07.
rendite = rendite_prozent / 100

# 15 % wird zu 0.15.
volatilitaet = volatilitaet_prozent / 100


# Wenn der Nutzer den Button klickt, wird gerechnet.
if simulation_starten:

    # Mit Spinner zeigen wir, dass gerade gerechnet wird.
    with st.spinner("Simulation läuft..."):

        # Hier wird unsere Simulationsfunktion aufgerufen.
        werte = simulate_t_gbm(
            startwert=startwert,
            rendite=rendite,
            volatilitaet=volatilitaet,
            jahre=jahre,
            schritte_pro_jahr=schritte_pro_jahr,
            simulationen=simulationen,
            freiheitsgrade=freiheitsgrade
        )

    # Die Endwerte sind die letzte Zeile der Matrix.
    endwerte = werte[-1, :]

    # Median bedeutet:
    # 50 % der Simulationen liegen darunter, 50 % darüber.
    median = np.median(endwerte)

    # 5%-Perzentil:
    # Nur 5 % der Simulationen enden schlechter als dieser Wert.
    p5 = np.percentile(endwerte, 5)

    # 95%-Perzentil:
    # Nur 5 % der Simulationen enden besser als dieser Wert.
    p95 = np.percentile(endwerte, 95)

    # Durchschnitt der Endwerte.
    durchschnitt = np.mean(endwerte)

    # Minimum und Maximum der Simulationen.
    minimum = np.min(endwerte)
    maximum = np.max(endwerte)


    # ------------------------------------------------------------
    # 7. ERGEBNISBOX
    # ------------------------------------------------------------

    with ergebnis_spalte:

        st.markdown("### Ergebnis")

        # Wir erzeugen einen kurzen Interpretationstext.
        text = interpretation_text(startwert, median, p5, p95)

        # Ergebnistext anzeigen.
        st.success(text)

        # Drei Kennzahlen nebeneinander anzeigen.
        k1, k2, k3 = st.columns(3)

        # Median anzeigen.
        k1.metric(
            label="Median",
            value=f"{median:,.0f} €".replace(",", ".")
        )

        # 5%-Szenario anzeigen.
        k2.metric(
            label="Schlechtes 5%-Szenario",
            value=f"{p5:,.0f} €".replace(",", ".")
        )

        # 95%-Szenario anzeigen.
        k3.metric(
            label="Gutes 95%-Szenario",
            value=f"{p95:,.0f} €".replace(",", ".")
        )

        # Weitere Kennzahlen in einem ausklappbaren Bereich.
        with st.expander("Weitere Kennzahlen anzeigen"):
            st.write(f"Durchschnitt: {durchschnitt:,.0f} €".replace(",", "."))
            st.write(f"Minimum: {minimum:,.0f} €".replace(",", "."))
            st.write(f"Maximum: {maximum:,.0f} €".replace(",", "."))


    # ------------------------------------------------------------
    # 8. ZEITACHSE FÜR DIAGRAMME
    # ------------------------------------------------------------

    # Die Zeitachse läuft von 0 bis zur Anzahl Jahre.
    zeitachse = np.linspace(0, jahre, werte.shape[0])


    # ------------------------------------------------------------
    # 9. DIAGRAMM: EINIGE BEISPIELPFADE
    # ------------------------------------------------------------

    st.markdown("### Beispielhafte Zukunftspfade")

    # Wir erstellen ein leeres Plotly-Diagramm.
    fig_pfade = go.Figure()

    # Wir zeigen nicht alle Simulationen, weil das unübersichtlich wäre.
    # Stattdessen zeichnen wir maximal 50 Pfade.
    anzahl_anzeigen = min(50, simulationen)

    # Schleife über die ersten Beispielpfade.
    for i in range(anzahl_anzeigen):

        # Jeder Pfad wird als Linie ins Diagramm eingefügt.
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

    # Zusätzlich zeichnen wir den Medianpfad.
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

    # Layout des Diagramms.
    fig_pfade.update_layout(
        height=450,
        xaxis_title="Jahre",
        yaxis_title="Vermögen (€)",
        template="plotly_white"
    )

    # Diagramm anzeigen.
    st.plotly_chart(fig_pfade, use_container_width=True)


    # ------------------------------------------------------------
    # 10. DIAGRAMM: ENDWERT-VERTEILUNG
    # ------------------------------------------------------------

    st.markdown("### Verteilung der Endwerte")

    # Neues Plotly-Diagramm für Histogramm.
    fig_hist = go.Figure()

    # Histogramm der Endwerte.
    fig_hist.add_trace(
        go.Histogram(
            x=endwerte,
            nbinsx=60,
            name="Endwerte"
        )
    )

    # Senkrechte Linie für 5%-Szenario.
    fig_hist.add_vline(
        x=p5,
        line_width=2,
        line_dash="dash",
        annotation_text="5%-Szenario",
        annotation_position="top left"
    )

    # Senkrechte Linie für Median.
    fig_hist.add_vline(
        x=median,
        line_width=3,
        annotation_text="Median",
        annotation_position="top"
    )

    # Senkrechte Linie für 95%-Szenario.
    fig_hist.add_vline(
        x=p95,
        line_width=2,
        line_dash="dash",
        annotation_text="95%-Szenario",
        annotation_position="top right"
    )

    # Layout des Histogramms.
    fig_hist.update_layout(
        height=450,
        xaxis_title="Endvermögen (€)",
        yaxis_title="Anzahl Simulationen",
        template="plotly_white"
    )

    # Histogramm anzeigen.
    st.plotly_chart(fig_hist, use_container_width=True)


    # ------------------------------------------------------------
    # 11. MODELL-HINWEIS
    # ------------------------------------------------------------

    st.info(
        "Hinweis: Dieses Basismodell ist bewusst vereinfacht. "
        "Es berücksichtigt bereits Extremereignisse über die t-Verteilung, "
        "aber noch keine Entnahmen, Inflation, Gebühren, Korrelationen, " 
        "Volatility Clustering oder Marktphasen."
    )


# Wenn die Simulation noch nicht gestartet wurde,
# zeigen wir rechts einen Platzhaltertext.
else:
    with ergebnis_spalte:
        st.markdown("### Ergebnis")
        st.write("Starte die Simulation, um mögliche Zukunftsverläufe zu sehen.")
