import streamlit as st

st.set_page_config(page_title="Finanz-Simulator", page_icon="💶")

st.title("Finanz-Simulator")
st.write("Meine erste online veröffentlichte Streamlit-App")

betrag = st.number_input("Startkapital", min_value=0.0, value=10000.0, step=1000.0)
zins = st.slider("Zinssatz p.a. (%)", 0.0, 15.0, 5.0)
jahre = st.slider("Jahre", 1, 40, 10)

endwert = betrag * ((1 + zins / 100) ** jahre)

st.subheader("Ergebnis")
st.write(f"Endwert: {endwert:,.2f} €")