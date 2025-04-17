import streamlit as st
import math
import pandas as pd
import io

# === Funções ===

def calcular_blocos(area_parede):
    return math.ceil(area_parede * 20)

def calcular_ferro_pilares(pilares_alturas, bitola):
    total_metros = sum([altura * 4 for altura in pilares_alturas])
    barras = math.ceil(total_metros / 12)
    return barras, total_metros, bitola

def calcular_estribos_pilares(pilares_alturas):
    total_estribos = sum([math.ceil(altura / 0.20) for altura in pilares_alturas])
    ferro_total = total_estribos * 0.60
    barras = math.ceil(ferro_total / 12)
    return barras, ferro_total

def calcular_ferro_baldrame(perimetro):
    ferro_10mm_total = perimetro * 4
    barras_10mm = math.ceil(ferro_10mm_total / 12)

    num_estribos = math.ceil(perimetro / 0.20)
    ferro_estribo_total = num_estribos * 0.60
    barras = math.ceil(ferro_estribo_total / 12)

    return barras_10mm, barras, ferro_10mm_total, ferro_estribo_total

def calcular_volume_concreto_baldrame(perimetro):
    return perimetro * 0.20 * 0.30

def calcular_volume_concreto_pilares(pilares_alturas):
    return sum([0.15 * 0.15 * altura for altura in pilares_alturas])

def calcular_materiais_concreto(volume, fck):
    if fck == 20:
        traço = (1, 2, 3)
        cimento_m3 = 7.5
        areia_m3 = 0.45
        brita_m3 = 0.90
        agua_m3 = 0.18
    elif fck == 25:
        traço = (1, 1.5, 3)
        cimento_m3 = 8.5
        areia_m3 = 0.40
        brita_m3 = 0.90
        agua_m3 = 0.18
    else:
        raise ValueError("MPA inválido. Use apenas 20 ou 25 MPa.")

    cimento_sacos = math.ceil(volume * cimento_m3)
    areia = round(volume * areia_m3, 2)
    brita = round(volume * brita_m3, 2)
    agua = math.ceil(volume * agua_m3 * 1000)  # litros

    return cimento_sacos, areia, brita, agua, traço

def calcular_assentamento(area_parede):
    cimento_sacos = math.ceil(area_parede / 1.5)
    areia_m3 = round(cimento_sacos * 0.035, 2)
    return cimento_sacos, areia_m3

def calcular_reboco(area_parede):
    cimento_sacos = math.ceil(area_parede / 4)
    areia_m3 = round(cimento_sacos * 0.045, 2)
    cal_kg = math.ceil(cimento_sacos * 10)
    return cimento_sacos, areia_m3, cal_kg

def calcular_contrapiso(area_contrapiso):
    cimento_sacos = math.ceil(area_contrapiso / 3)
    areia_m3 = round(cimento_sacos * 0.05, 2)
    return cimento_sacos, areia_m3

# === Streamlit Interface ===

st.title("Calculadora de Materiais para Construção")

area_parede = st.number_input("Quantos metros quadrados de parede?", min_value=1, step=1)
num_pilares = st.number_input("Quantos pilares você vai fazer?", min_value=1, step=1)

pilares_alturas = []
for i in range(num_pilares):
    altura = st.number_input(f"Altura do pilar {i+1} (em metros):", min_value=1.0, step=0.1)
    pilares_alturas.append(altura)

bitola = st.selectbox("Qual bitola do ferro para os pilares?", options=[8, 10])

perimetro = st.number_input("Qual o perímetro da viga baldrame (em metros)?", min_value=1.0, step=0.1)

fck = st.selectbox("Qual a resistência do concreto desejada (MPa)?", options=[20, 25])

area_contrapiso = st.number_input("Quantos metros quadrados de contrapiso serão feitos?", min_value=1, step=1)

# Blocos e ferro
blocos = calcular_blocos(area_parede)
barras_pilar, ferro_pilar_metros, bitola_pilar = calcular_ferro_pilares(pilares_alturas, bitola)
barras_5mm_pilares, ferro_5mm_pilares = calcular_estribos_pilares(pilares_alturas)

barras_10mm, barras_5mm_baldrame, ferro_10mm_metros, ferro_5mm_baldrame = calcular_ferro_baldrame(perimetro)
total_barras_5mm = barras_5mm_pilares + barras_5mm_baldrame

# Concreto
volume_baldrame = calcular_volume_concreto_baldrame(perimetro)
volume_pilares = calcular_volume_concreto_pilares(pilares_alturas)
volume_total = volume_baldrame + volume_pilares

cimento_concreto, areia_concreto, brita, agua, traco = calcular_materiais_concreto(volume_total, fck)

# Reboco, assentamento, contrapiso
cimento_assentamento, areia_assentamento = calcular_assentamento(area_parede)
cimento_reboco, areia_reboco, cal_reboco = calcular_reboco(area_parede)
cimento_contrapiso, areia_contrapiso = calcular_contrapiso(area_contrapiso)

total_cimento = (
    cimento_concreto +
    cimento_assentamento +
    cimento_reboco +
    cimento_contrapiso
)

total_areia = round(
    areia_concreto + areia_assentamento + areia_reboco + areia_contrapiso, 2
)

total_brita = brita

# Caçambas de areia e brita
cacamba_m3 = 5
cacambas_areia = math.ceil(total_areia / cacamba_m3)
cacambas_brita = math.ceil(total_brita / cacamba_m3)

# Exibindo resultados no Streamlit
st.subheader("RESULTADOS")

st.write(f"🧱 Blocos de 6 furos: {blocos} unidades")
st.write(f"🔩 Barras de {bitola_pilar} mm para pilares: {barras_pilar} unidades ({ferro_pilar_metros:.2f} m)")
st.write(f"🔩 Barras de 10 mm para baldrame: {barras_10mm} unidades ({ferro_10mm_metros:.2f} m)")
st.write(f"🔩 Barras de 5 mm para estribos (pilares + baldrame): {total_barras_5mm} unidades")

st.write(f"\n🧱 Concreto (total {volume_total:.2f} m³) | Traço fck {fck} MPa = {traco[0]}:{traco[1]}:{traco[2]}")
st.write(f"🪨 Cimento: {cimento_concreto} sacos")
st.write(f"🏖️ Areia: {areia_concreto} m³")
st.write(f"🪨 Brita: {brita} m³")
st.write(f"💧 Água: {agua} litros")

st.write(f"\n🧱 Assentamento: {cimento_assentamento} sacos | Areia: {areia_assentamento} m³")
st.write(f"🧱 Reboco: {cimento_reboco} sacos | Areia: {areia_reboco} m³ | Cal: {cal_reboco} kg")
st.write(f"🧱 Contrapiso: {cimento_contrapiso} sacos | Areia: {areia_contrapiso} m³")

st.write(f"\n📦 TOTAL GERAL DE CIMENTO: {total_cimento} sacos")
st.write(f"🏖️ TOTAL GERAL DE AREIA: {total_areia} m³ (~ {cacambas_areia} caçambas de 5 m³)")
st.write(f"🪨 TOTAL DE BRITA: {total_brita} m³ (~ {cacambas_brita} caçambas de 5 m³)")


# Criando os dados para a tabela
dados_tabela = {
    'Material': ['Blocos', 'Ferro Pilar', 'Ferro Baldrame (10mm)', 'Ferro Baldrame (5mm)', 'Concreto (Cimento)', 
                 'Concreto (Areia)', 'Concreto (Brita)', 'Concreto (Água)', 'Assentamento (Cimento)', 
                 'Assentamento (Areia)', 'Reboco (Cimento)', 'Reboco (Areia)', 'Reboco (Cal)', 
                 'Contrapiso (Cimento)', 'Contrapiso (Areia)', 'Total de Cimento', 'Total de Areia', 
                 'Total de Brita', 'Caçambas de Areia', 'Caçambas de Brita'],
    'Quantidade': [blocos, f"{barras_pilar} unidades ({ferro_pilar_metros:.2f} m)", barras_10mm, total_barras_5mm,
                   cimento_concreto, areia_concreto, brita, agua, cimento_assentamento, areia_assentamento, 
                   cimento_reboco, areia_reboco, cal_reboco, cimento_contrapiso, areia_contrapiso, total_cimento, 
                   total_areia, total_brita, cacambas_areia, cacambas_brita]
}

# Criando um DataFrame
df = pd.DataFrame(dados_tabela)

# Exibindo a tabela no Streamlit
st.subheader("Tabela de Materiais")
st.dataframe(df)

# Função para exportar para Excel
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Materiais")
    return output.getvalue()

# Botão de download
st.download_button(
    label="Download da Tabela de Materiais em Excel",
    data=to_excel(df),
    file_name="materiais_construcao.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
