import streamlit as st
import pandas as pd
import os

# Configuração de pastas
IMG_DIR = os.path.abspath("imagens_produtos")
os.makedirs(IMG_DIR, exist_ok=True)

# Configurações iniciais
dados_iniciais = [
    {"Rua": "Rua A", "Código": "1001", "Descrição": "Cabo USB-C 1m", "Imagem do produto": ""},
    {"Rua": "Rua B", "Código": "1002", "Descrição": "Carregador 20W", "Imagem do produto": ""},
    {"Rua": "Rua C", "Código": "1003", "Descrição": "Suporte de Celular para carro", "Imagem do produto": ""},
]

# Função de carregamento de dados estáticos
def carregar_dados():
    return pd.DataFrame(dados_iniciais)

st.set_page_config(layout="wide")
st.title("📋 Lista de Produtos Mobit")

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

    if not df_produto.empty:
        produto_selecionado = st.selectbox(
            "Selecione o código do produto", 
            df_produto["Código"].astype(str).unique()
        )

        if uploaded_files and produto_selecionado:
            try:
                img_paths = []

                for i, file in enumerate(uploaded_files[:3]):
                    nome_seguro = "".join([c for c in file.name if c.isalnum() or c in ('.', '_')]).rstrip()
                    nome_arquivo = f"{produto_selecionado}_{i + 1}_{nome_seguro}"
                    caminho_imagem = os.path.join(IMG_DIR, nome_arquivo)

                    with open(caminho_imagem, "wb") as f:
                        f.write(file.getbuffer())

                    if os.path.exists(caminho_imagem):
                        img_paths.append(caminho_imagem)
                    else:
                        st.warning(f"Arquivo não pôde ser salvo: {nome_arquivo}")

                if img_paths:
                    mask = df_produto["Código"].astype(str) == produto_selecionado
                    df_produto.loc[mask, "Imagem do produto"] = ";".join(img_paths)
                    st.session_state.df_produto = df_produto
                    st.success(f"✅ {len(img_paths)} imagem(ns) salvas com sucesso!")

            except Exception as e:
                st.error(f"❌ Falha no upload: {str(e)}")

# Barra lateral - Logo + busca
logo_html = """
<style>
.mobit-logo {
    font-family: 'Arial', sans-serif;
    font-weight: bold;
    font-size: 100px;
    color: #002f6c;
    width: 100%;
    display: block;
}
.mobit-logo .circle {
    background-color: #002f6c;
    border-radius: 50%;
    width: 56px;
    height: 56px;
    display: inline-block;
    position: relative;
    margin: 0 4px;
}
.mobit-logo .circle::before {
    content: '';
    position: absolute;
    top: 8px;
    left: 8px;
    width: 30px;
    height: 30px;
    background-color: #f5a623;
    border-radius: 50%;
}
</style>
<div class="mobit-logo">
    m<span class="circle"></span>bit
</div>
"""
st.sidebar.markdown(logo_html, unsafe_allow_html=True)

# Campo de busca
codigo_busca = st.sidebar.text_input("🔍 Digite o código do produto:")

if codigo_busca:
    filtro = df_produto[df_produto["Código"].astype(str).str.contains(codigo_busca, case=False, na=False)]

    if not filtro.empty:
        st.subheader("📌 Resultado da pesquisa:")
        for _, row in filtro.iterrows():
            st.write(f"**Rua:** {row['Rua']}")
            st.write(f"**Codigo:** {row['Código']}")
            st.write(f"**Descrição:** {row['Descrição']}")

            if pd.notna(row["Imagem do produto"]):
                img_list = [img for img in row["Imagem do produto"].split(";") if img.strip()]

                if img_list:
                    cols = st.columns(len(img_list))
                    for col, img_path in zip(cols, img_list):
                        try:
                            if os.path.exists(img_path):
                                col.image(img_path, width=400)
                            else:
                                col.warning(f"Imagem ausente: {os.path.basename(img_path)}")
                        except Exception as e:
                            col.error(f"Erro ao carregar: {str(e)}")
    else:
        st.warning("🚨 Nenhum produto encontrado com esse código.")
else:
    st.info("🔎 Digite um código de produto na barra lateral para pesquisar.")
