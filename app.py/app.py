import streamlit as st
import pandas as pd
import os

# Definir caminho do arquivo CSV
csv_path = "datasets/produtos.csv"

# Função para carregar os dados do CSV para a sessão
def carregar_dados():
    if os.path.exists(csv_path):
        try: 
            df = pd.read_csv(csv_path, delimiter=",", encoding="utf-8", on_bad_lines='skip', quotechar='"' )
        except pd.errors.ParserError as e:
            st.error(f"Erro de carregar CSV: {e}")
            df = pd.DataFrame(columns=["Código", "Descrição", "Rua", "Imagem do produto"])
    else:
        df = pd.DataFrame(columns=["Código", "Descrição", "Rua", "Imagem do produto"])
    df.columns = df.columns.str.strip()
    return df

# Inicializar session_state para armazenar os dados
if "df_produto" not in st.session_state:
    st.session_state.df_produto = carregar_dados()

df_produto = st.session_state.df_produto

st.set_page_config(layout="wide")
st.title("📋 Lista de Produtos Mobit")

# criar colunas
col1, col2 = st.columns([3, 1])

# coluna com o arquivo CSV interativo
with col1:
    edited_df_produto = st.data_editor(df_produto, num_rows="dynamic")
    st.session_state.df_produto = edited_df_produto

# coluna de carregamento e atualização da foto por código
with col2:
    st.subheader("📸 Atualizar Imagens do Produto")
    uploaded_files = st.file_uploader("Faça upload de até 3 imagens", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="multi_upload")
    
    produto_selecionado = st.selectbox("Selecione o código do produto", df_produto["Código"].astype(str))
    
    if uploaded_files and produto_selecionado:
        img_dir = "imagens_produtos"
        os.makedirs(img_dir, exist_ok=True)
        
        img_paths = []
        for i, file in enumerate(uploaded_files[:3]):  # Limite de 3 imagens
            img_filename = f"{produto_selecionado}_{i+1}_{file.name}"
            img_path = os.path.join(img_dir, img_filename)
            with open(img_path, "wb") as f:
                f.write(file.getbuffer())
            img_paths.append(img_path)
        
        df_produto.loc[df_produto["Código"].astype(str) == produto_selecionado, "Imagem do produto"] = ";".join(img_paths)
        st.session_state.df_produto = df_produto
        st.success("✅ Imagens vinculadas ao produto com sucesso!")

# botão para salvar imagem e alterações no arquivo CSV
if st.button("Salvar Alterações na planilha"):
    st.session_state.df_produto.to_csv(csv_path, index=True)
    st.success("✅ Alterações salvas permanentemente!")

# 🔹 Barra lateral para pesquisa
df_pesquisa = st.sidebar.text_input("🔍 Digite o código do produto:")



# resultado da pesquisa
if df_pesquisa:
    filtro = df_produto[df_produto["Código"].astype(str).str.contains(df_pesquisa, case=False, na=False)]
    
    if not filtro.empty:
        st.subheader("📌 Resultado da pesquisa:")
        for _, row in filtro.iterrows():
            st.write(f"**Código:** {row['Código']}")
            st.write(f"**Descrição:** {row['Descrição']}")
            st.write(f"**Rua:** {row['Rua']}")
            
            if pd.notna(row["Imagem do produto"]):
                img_list = row["Imagem do produto"].split(";")
                cols = st.columns(len(img_list))
                for col, img_path in zip (cols, img_list):
                    if os.path.exists(img_path):
                        col.image(img_path, width=300)
                    else:
                        col.warning(f"⚠ Imagem não encontrada: {img_path}")
    else:
        st.warning("🚨 Nenhum produto encontrado com esse código.")
else:
    st.info("🔎 Digite um código de produto na barra lateral para pesquisar.")














