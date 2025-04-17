import streamlit as st
import pandas as pd
import os






# Configuração de caminhos SEGUROS
BASE_DIR = os.path.dirname(os.path.abspath("produtos.csv"))  # Pega o diretório do app.py
CSV_DIR = os.path.join(BASE_DIR, "datasets")          # Caminho absoluto para datasets
IMG_DIR = os.path.join(BASE_DIR, "imagens_produtos")  # Caminho absoluto para imagens
CSV_PATH = os.path.join(CSV_DIR, "produtos.csv")      # Caminho completo do CSV

# Garante que as pastas existam
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)




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
    try:
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(
                CSV_PATH,
                delimiter=",",
                encoding="utf-8",
                on_bad_lines="skip",
                quotechar='"',
                dtype={"Rua": str, "Código": str, "Descrição": str, "Imagem do produto": str}
            )

            # Garante que as colunas obrigatórias existam
            for col in ["Rua", "Código", "Descrição", "Imagem do produto"]:
                if col not in df.columns:
                    df[col] = None

            return df

        # Se o arquivo não existir, cria um DataFrame vazio
        return pd.DataFrame(columns=["Rua", "Código", "Descrição", "Imagem do produto"])

    except Exception as e:
        st.error(f"🚨 Erro ao carregar dados: {str(e)}")
        return pd.DataFrame(columns=["Rua", "Código", "Descrição", "Imagem do produto"])

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

            for i, file in enumerate(uploaded_files[:3]):  # Limita a 3 imagens
                # Remove caracteres perigosos do nome do arquivo
                nome_seguro = "".join([c for c in file.name if c.isalnum() or c in ('.', '_')]).rstrip()
                nome_arquivo = f"{produto_selecionado}{i + 1}{nome_seguro}"
                caminho_imagem = os.path.join(IMG_DIR, nome_arquivo)

                # Salva o arquivo
                with open(caminho_imagem, "wb") as f:
                    f.write(file.getbuffer())

                # Verifica se o arquivo foi salvo
                if os.path.exists(caminho_imagem):
                    img_paths.append(caminho_imagem)
                else:
                    st.warning(f"Arquivo não pôde ser salvo: {nome_arquivo}")

            # Atualiza o DataFrame
            if img_paths:
                mask = df_produto["Código"].astype(str) == produto_selecionado
                imagens_existentes = df_produto.loc[mask, "Imagem do produto"].iloc[0]

              
                

                df_produto.loc[mask, "Imagem do produto"] = ";".join(img_paths)
                st.session_state.df_produto = df_produto
                st.success(f"✅ {len(img_paths)} imagem(ns) salvas com sucesso!")

        except Exception as e:
            st.error(f"❌ Falha no upload: {str(e)}")

# Botão de salvamento
if st.button("💾 Salvar Alterações", type="primary"):
    try:
        # Cria o diretório se não existir (redundante, mas seguro)
        os.makedirs(CSV_DIR, exist_ok=True)

        # Salva o CSV
        st.session_state.df_produto.to_csv(CSV_PATH, index=False)
        st.toast("Dados salvos com sucesso!", icon="✅")

    except Exception as e:
        st.error(f"❌ Falha ao salvar: {str(e)}")
        st.error(f"Verifique permissões em: {CSV_DIR}")
# Barra lateral

logo_html = """
<style>
.mobit-logo {
    font-family: 'Arial', sans-serif;
    font-weight: bold;
    font-size: 48px;
    color: #002f6c; /* azul escuro */
}
.mobit-logo .circle {
    background-color: #002f6c;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    display: inline-block;
    position: relative;
    margin: 0 4px;
}
.mobit-logo .circle::before {
    content: '';
    position: absolute;
    top: 6px;
    left: 6px;
    width: 18px;
    height: 18px;
    background-color: #f5a623; /* laranja */
    border-radius: 50%;
}
</style>

<div class="mobit-logo">
    m<span class="circle"></span>bit
</div>
"""

# Exibe no Streamlit
st.sidebar.markdown(logo_html, unsafe_allow_html=True, width=400)




df_pesquisa = st.sidebar.text_input("🔍 Digite o código do produto:")

# Resultado da pesquisa
if df_pesquisa:
    filtro = df_produto[df_produto["Código"].astype(str).str.contains(df_pesquisa, case=False, na=False)]
    
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
