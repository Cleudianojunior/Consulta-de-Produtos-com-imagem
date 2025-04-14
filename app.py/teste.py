import streamlit as st
import pandas as pd
import os

# Configurações iniciais
st.set_page_config(layout="wide")
st.title("📋 Lista de Produtos Mobit")

# Definir caminhos
csv_path = os.path.abspath("datasets/produtos.csv")
img_dir = os.path.abspath("imagens_produtos")
os.makedirs(os.path.dirname(csv_path), exist_ok=True)
os.makedirs(img_dir, exist_ok=True)

# Função para carregar os dados
def carregar_dados():
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, delimiter=",", encoding="utf-8", 
                           on_bad_lines='skip', quotechar='"',
                           dtype={"Código": str, "Descrição": str, "Rua": str, "Imagem do produto": str})
            
            required_cols = ["Código", "Descrição", "Rua", "Imagem do produto"]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = None
            
            return df
        except Exception as e:
            st.error(f"Erro ao carregar CSV: {str(e)}")
            return pd.DataFrame(columns=required_cols)
    else:
        return pd.DataFrame(columns=["Código", "Descrição", "Rua", "Imagem do produto"])

# Inicializar session_state
if "df_produto" not in st.session_state:
    st.session_state.df_produto = carregar_dados()

df_produto = st.session_state.df_produto

# Layout principal
col1, col2 = st.columns([3, 1])

# Coluna 1 - Editor de dados
with col1:
    edited_df_produto = st.data_editor(
        df_produto, 
        num_rows="dynamic",
        column_config={
            "Imagem do produto": st.column_config.TextColumn(
                "Caminho das Imagens",
                help="Caminhos das imagens separados por ponto-e-vírgula"
            )
        }
    )
    st.session_state.df_produto = edited_df_produto

# Coluna 2 - Upload de imagens
with col2:
    st.subheader("📸 Atualizar Imagens do Produto")
    uploaded_files = st.file_uploader(
        "Faça upload de até 3 imagens", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True, 
        key="multi_upload"
    )
    
    produto_selecionado = st.selectbox(
        "Selecione o código do produto", 
        df_produto["Código"].astype(str).unique()
    )
    
    if uploaded_files and produto_selecionado:
        try:
            img_paths = []
            for i, file in enumerate(uploaded_files[:3]):
                safe_name = "".join(c for c in file.name if c.isalnum() or c in ('_', '.')).rstrip()
                img_filename = f"{produto_selecionado}_{i+1}_{safe_name}"
                img_path = os.path.join(img_dir, img_filename)
                
                with open(img_path, "wb") as f:
                    f.write(file.getbuffer())
                
                if os.path.exists(img_path):
                    img_paths.append(img_path)
                else:
                    st.error(f"Falha ao salvar: {img_filename}")
            
            if img_paths:
                mask = df_produto["Código"].astype(str) == produto_selecionado
                current_images = df_produto.loc[mask, "Imagem do produto"].iloc[0]
                if pd.notna(current_images):
                    img_paths = current_images.split(";") + img_paths
                
                df_produto.loc[mask, "Imagem do produto"] = ";".join(img_paths)
                st.session_state.df_produto = df_produto
                st.success(f"{len(img_paths)} imagem(ns) salva(s) com sucesso!")
        except Exception as e:
            st.error(f"Erro ao processar imagens: {str(e)}")

# Botão de salvamento
if st.button("💾 Salvar Alterações na planilha"):
    try:
        st.session_state.df_produto.to_csv(csv_path, index=False)
        st.success("✅ Alterações salvas permanentemente!")
    except Exception as e:
        st.error(f"Erro ao salvar CSV: {str(e)}")

# Barra lateral
st.sidebar.image("imagens_pagina/LOGO_MOBIT.png", use_container_width=True)
df_pesquisa = st.sidebar.text_input("🔍 Digite o código do produto:")

# Resultado da pesquisa
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
                for col, img_path in zip(cols, img_list):
                    try:
                        if os.path.exists(img_path):
                            col.image(img_path, width=300)
                        else:
                            col.error(f"Imagem não encontrada: {os.path.basename(img_path)}")
                    except Exception as e:
                        col.error(f"Erro ao carregar imagem: {str(e)}")
    else:
        st.warning("🚨 Nenhum produto encontrado com esse código.")
else:
    st.info("🔎 Digite um código de produto na barra lateral para pesquisar.")