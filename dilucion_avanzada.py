# app.py  – dilución con contracción + pesos en gramos
import streamlit as st

# ─────────────────────────────────────────────────────────
# ► Densidades g/mL (20 °C)  – tabla OIML resumida
DENS_TABLE = {
     0: 0.99823, 10: 0.98471, 20: 0.97038, 30: 0.95690,
    40: 0.94348, 50: 0.93005, 60: 0.91655, 70: 0.90297,
    80: 0.88923, 90: 0.87529, 96: 0.80500, 100: 0.78924,
}
RHO_ETHANOL = 0.78924  # g/mL  (etanol puro, 20 °C)
RHO_WATER   = 0.99823  # g/mL  (agua pura, 20 °C)

def rho(abv: float) -> float:
    """Interpola densidad a 20 °C para ABV (%)"""
    keys = sorted(DENS_TABLE)
    if abv <= keys[0]:
        return DENS_TABLE[keys[0]]
    if abv >= keys[-1]:
        return DENS_TABLE[keys[-1]]
    for k2 in keys:
        if abv < k2:
            k1 = keys[keys.index(k2) - 1]
            return DENS_TABLE[k1] + (DENS_TABLE[k2] - DENS_TABLE[k1]) * (abv - k1) / (k2 - k1)

def w_ethanol(abv: float) -> float:
    """Fracción másica de etanol a partir de ABV (%)"""
    return (RHO_ETHANOL / rho(abv)) * (abv / 100)

# ─────────────────────────────────────────────────────────
st.set_page_config(page_title="Dilución con contracción exacta", page_icon="🧪")

# Banner superior (se mantiene)
st.markdown(
    """
    <div style="background-color:#f5f5f5;padding:0.6rem 1rem;border-radius:6px;">
        <a href="https://www.nosoynormalcerveceria.com" target="_blank"
           style="text-decoration:none;color:#0066cc;font-weight:600;">
           Mirá más calculadoras para productores de bebidas en www.nosoynormalcerveceria.com
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("🧪 Calculadora de Dilución (con contracción + pesos)")

st.markdown(
    "Ingresá los datos y presioná **Calcular alcohol base**. "
    "El cálculo tiene en cuenta la contracción de volumen que se produce al mezclar agua y alcohol, además, te indica "
    "el peso en gramos de alcohol y agua si trabajás con balanza."
)

# ---- Entradas de usuario --------------------------------
unidad = st.radio("¿En qué unidades deseás hacer los cálculos?",
                  ("Litros", "Mililitros"), horizontal=True)

grad_base = st.number_input("¿Qué graduación tiene tu alcohol base? (normalmente 96 %)",
                            1.0, 100.0, 96.0, 0.1, format="%.1f")
grad_final = st.number_input("¿Qué graduación final deseás obtener? (p. ej. 40 %)",
                             1.0, 99.9, 40.0, 0.1, format="%.1f")

vol_label = ("¿Cuántos litros finales deseás obtener?"
             if unidad == "Litros"
             else "¿Cuántos mililitros finales deseás obtener?")
V2_in = st.number_input(vol_label,
                        0.1 if unidad == "Litros" else 1.0,
                        value=1.0,
                        step=0.1 if unidad == "Litros" else 10.0,
                        format="%.2f")

# ---- Cálculo --------------------------------------------
if st.button("Calcular alcohol base"):
    if grad_final >= grad_base:
        st.error("La graduación inicial debe ser mayor a la final en una dilución.")
    else:
        # Volumen final (litros) para el cálculo interno
        V2_L = V2_in if unidad == "Litros" else V2_in / 1000

        ρ1, ρ2 = rho(grad_base), rho(grad_final)
        w1, w2 = w_ethanol(grad_base), w_ethanol(grad_final)

        # Volumen de alcohol base (L) y de agua (L)
        V1_L  = (w2 * ρ2 * V2_L) / (w1 * ρ1)
        Vw_L  = (ρ2 * V2_L - ρ1 * V1_L) / RHO_WATER

        # Conversión a unidades elegidas
        factor_vol = 1 if unidad == "Litros" else 1000
        sufijo_vol = "L" if unidad == "Litros" else "ml"

        # ---- Resultados en volumen -----------------------
        st.subheader("Resultado exacto (volumen)")
        st.write(f"**Alcohol base necesario:** `{V1_L*factor_vol:.3f} {sufijo_vol}`")
        st.write(f"**Agua a agregar:** `{Vw_L*factor_vol:.3f} {sufijo_vol}`")

        # ---- Resultados en masa --------------------------
        masa_alcohol_g = V1_L * 1000 * ρ1        # L → mL → g
        masa_agua_g    = Vw_L * 1000 * RHO_WATER

        st.markdown("---")
        st.markdown(
            "**Si tenés una balanza de precisión quizás quieras pesar el alcohol "
            "base y el agua:**"
        )
        st.write(f"- Alcohol base: `{masa_alcohol_g:.1f} g`")
        st.write(f"- Agua: `{masa_agua_g:.1f} g`")

        st.caption(
            "Datos de densidad tomados de las Tablas Internacionales OIML a 20 °C; "
            "el cálculo respeta la contracción real al mezclar agua y alcohol."
        )
