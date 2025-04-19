import streamlit as st
import pandas as pd
import os

# Definir caminho do arquivo CSV


# Função para carregar os dados do CSV para a sessão
def carregar_dados_para_tabela(df):
    tabela = PrettyTable()
    tabela.field_names = ["Rua", "Código", "Descrição", "Imagem do produto"]
    
    for _, row in df.iterrows():
        tabela.add_row([
            row["Rua"],
            row["Código"],
            row["Descrição"],
            row["Imagem do produto"]
        ])
    
    return tabela

# Na seção onde você exibe os dados, substitua o st.data_editor por:
with col1:
    st.subheader("📋 Tabela de Produtos")
    
    # Converter DataFrame para PrettyTable
    tabela_produtos = carregar_dados_para_tabela(df_produto)
    
    # Exibir a tabela formatada
    st.text(tabela_produtos.get_string())
    
    # Adicionar controles para edição (simplificado)
    with st.expander("✏️ Editar Produto"):
        codigo_editar = st.selectbox(
            "Selecione o código para editar",
            df_produto["Código"].unique()
        )
        
        # Preencher formulário com dados existentes
        produto = df_produto[df_produto["Código"] == codigo_editar].iloc[0]
        
        with st.form(f"form_editar_{codigo_editar}"):
            nova_rua = st.text_input("Rua", produto["Rua"])
            novo_codigo = st.text_input("Código", produto["Código"])
            nova_descricao = st.text_area("Descrição", produto["Descrição"])
            novas_imagens = st.text_input("Imagens (separadas por ;)", produto["Imagem do produto"])
            
            if st.form_submit_button("Salvar Alterações"):
                # Atualizar o DataFrame
                mask = df_produto["Código"] == codigo_editar
                df_produto.loc[mask, "Rua"] = nova_rua
                df_produto.loc[mask, "Código"] = novo_codigo
                df_produto.loc[mask, "Descrição"] = nova_descricao
                df_produto.loc[mask, "Imagem do produto"] = novas_imagens
                
                st.session_state.df_produto = df_produto
                st.success("Alterações salvas!")
                st.experimental_rerun()uto

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
    st.session_state.df_produto.to_csv(csv_path, index=False)
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















