
import streamlit as st
import pandas as pd
import os

# Definir caminho do arquivo CSV
csv_path = "datasets/produtos.csv"

# Função para carregar os dados do CSV para a sessão
def carregar_dados():
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame(columns=["Código", "Descrição", "Rua", "Imagem do produto"])  # lista as colunas
    df.columns = df.columns.str.strip()  # Remove espaços extras nos nomes das colunas
    return df

# Inicializar session_state para armazenar os dados
if "df_produto" not in st.session_state:
    st.session_state.df_produto = carregar_dados()

# Criar referência ao DataFrame na sessão
df_produto = st.session_state.df_produto

# Configuração do layout do Streamlit
st.set_page_config(layout="wide")

# Chame a função e passe o caminho da imagem # Substitua pelo caminho correto da imagem

st.title("📋 Lista de Produtos Mobit")

# Criar colunas para dividir a tela
col1, col2 = st.columns([3, 1])

with col1:
    # Criar uma tabela interativa para edição
    edited_df_produto = st.data_editor(df_produto, num_rows="dynamic")

    # Atualizar os dados editados na sessão
    st.session_state.df_produto = edited_df_produto

with col2:
    # Upload de imagem para atualizar na planilha
    st.subheader("📸 Atualizar Imagem do Produto")
    uploaded_file = st.file_uploader("Faça upload da imagem", type=["png", "jpg", "jpeg"])

    # Campo para selecionar qual produto será atualizado
    produto_selecionado = st.selectbox("Selecione o código do produto", df_produto["Código"].astype(str))

    if uploaded_file and produto_selecionado:
        # Criar diretório para salvar imagens (se não existir)
        img_dir = "imagens_produtos"
        os.makedirs(img_dir, exist_ok=True)

        # Criar nome único para evitar sobrescrita
        img_filename = f"{produto_selecionado}_{uploaded_file.name}"
        img_path = os.path.join(img_dir, img_filename)

        # Salvar a imagem no diretório local
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Atualizar a tabela com o novo caminho da imagem
        df_produto.loc[df_produto["Código"].astype(str) == produto_selecionado, "Imagem do produto"] = img_path

        # Atualizar session_state
        st.session_state.df_produto = df_produto

        st.success("✅ Imagem vinculada ao produto com sucesso!")

# 🔹 Botão para salvar as alterações permanentemente no CSV
if st.button("Salvar Alterações na planilha"):
    st.session_state.df_produto.to_csv(csv_path, index=False)
    st.success("✅ Alterações salvas permanentemente!")

# 🔹 Barra lateral para pesquisa de produtos
df_pesquisa = st.sidebar.text_input("🔍 Digite o código do produto:")

st.sidebar.image("imagens_pagina\LOGO_MOBIT.png", use_container_width=True)

if df_pesquisa:
    # Filtrar produtos pelo código digitado
    filtro = df_produto[df_produto["Código"].astype(str).str.contains(df_pesquisa, case=False, na=False)]

    if not filtro.empty:
        st.subheader("📌 Resultado da pesquisa:")
        for _, row in filtro.iterrows():
            st.write(f"**Código:** {row['Código']}")
            st.write(f"**Descrição:** {row['Descrição']}")
            st.write(f"**Rua:** {row['Rua']}")

            # Exibir imagem se existir
            if pd.notna(row["Imagem do produto"]) and os.path.exists(row["Imagem do produto"]):
                st.image(row["Imagem do produto"], width=400)
            else:
                st.warning("⚠ Nenhuma imagem disponível para este produto.")
    else:
        st.warning("🚨 Nenhum produto encontrado com esse código.")
else:
    st.info("🔎 Digite um código de produto na barra lateral para pesquisar.")



