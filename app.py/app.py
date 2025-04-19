import streamlit as st
import pandas as pd
import os
from PIL import Image
import io

# Configuração inicial
st.set_page_config(layout="wide")
st.title("📋 Lista de Produtos Mobit")

# Dados iniciais (embutidos no código)
DADOS_INICIAIS = {
    "Código": ["1-A", "2-B", "3-C"1-A],
    "Descrição": ["TV LED 50\" Smart", "Notebook i7", "Smartphone Android"],
    "Rua": ["A1", "B2", "C3"],
    "Imagem do produto": [None, None, None]
}

# Função para inicializar os dados
def carregar_dados():
    if "df_produto" not in st.session_state:
        df = pd.DataFrame(DADOS_INICIAIS)
        st.session_state.df_produto = df
    return st.session_state.df_produto

# Carregar dados
df_produto = carregar_dados()

# Layout principal
col1, col2 = st.columns([3, 1])

# Coluna 1 - Editor de dados
with col1:
    st.subheader("📝 Editor de Produtos")
    edited_df = st.data_editor(
        df_produto,
        num_rows="dynamic",
        column_config={
            "Imagem do produto": st.column_config.TextColumn(
                "Caminho das Imagens",
                help="Caminhos das imagens separados por ponto-e-vírgula"
            )
        }
    )
    st.session_state.df_produto = edited_df

# Coluna 2 - Upload de imagens
with col2:
    st.subheader("📸 Atualizar Imagens do Produto")
    
    # Armazenar imagens em bytes na sessão
    if "imagens_produtos" not in st.session_state:
        st.session_state.imagens_produtos = {}
    
    produto_selecionado = st.selectbox(
        "Selecione o código do produto", 
        df_produto["Código"].unique()
    )
    
    uploaded_files = st.file_uploader(
        "Faça upload de até 3 imagens", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True,
        key="uploader_imagens"
    )
    
    if uploaded_files and produto_selecionado:
        try:
            # Armazenar imagens na sessão
            imagens = []
            for i, file in enumerate(uploaded_files[:3]):
                img_bytes = file.getvalue()
                imagens.append(img_bytes)
            
            # Atualizar referências no DataFrame
            mask = df_produto["Código"] == produto_selecionado
            df_produto.loc[mask, "Imagem do produto"] = f"img_{produto_selecionado}"
            st.session_state.df_produto = df_produto
            
            # Armazenar imagens na sessão
            st.session_state.imagens_produtos[f"img_{produto_selecionado}"] = imagens
            st.success(f"✅ {len(imagens)} imagem(ns) vinculadas ao produto!")
            
        except Exception as e:
            st.error(f"Erro ao processar imagens: {e}")

# Função para exibir imagens
def exibir_imagens(referencia):
    if referencia in st.session_state.imagens_produtos:
        imagens = st.session_state.imagens_produtos[referencia]
        cols = st.columns(len(imagens))
        for col, img_bytes in zip(cols, imagens):
            try:
                img = Image.open(io.BytesIO(img_bytes))
                col.image(img, width=200)
            except Exception as e:
                col.error(f"Erro ao carregar imagem: {e}")

# Barra lateral - Pesquisa
st.sidebar.title("🔍 Pesquisa")
codigo_pesquisa = st.sidebar.text_input("Digite o código do produto:")

# Resultado da pesquisa
if codigo_pesquisa:
    filtro = df_produto[df_produto["Código"].astype(str).str.contains(
        codigo_pesquisa, case=False, na=False
    )]
    
    if not filtro.empty:
        st.subheader("🔍 Resultado da Pesquisa")
        for _, row in filtro.iterrows():
            st.write(f"**Código:** {row['Código']}")
            st.write(f"**Descrição:** {row['Descrição']}")
            st.write(f"**Rua:** {row['Rua']}")
            
            if pd.notna(row["Imagem do produto"]):
                exibir_imagens(row["Imagem do produto"])
    else:
        st.warning("Nenhum produto encontrado com esse código.")
else:
    st.info("Digite um código de produto na barra lateral para pesquisar.")

# Botão para resetar dados
if st.sidebar.button("🔄 Resetar para Dados Iniciais"):
    st.session_state.df_produto = pd.DataFrame(DADOS_INICIAIS)
    st.session_state.imagens_produtos = {}
    st.rerun()

# Botão para exportar dados (opcional)
if st.sidebar.button("💾 Exportar Dados"):
    # Cria um arquivo CSV em memória
    csv = df_produto.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Baixar CSV",
        data=csv,
        file_name="produtos_mobit.csv",
        mime="text/csv"
    )













