import streamlit as st
import pandas as pd
import os

# Definir caminho do arquivo CSV
csv_path = "datasets/produtos.csv.csv"

# Carregar CSV e remover espaços extras nas colunas
if os.path.exists(csv_path):
    df_produto = pd.read_csv(csv_path)
else:
    df_produto = pd.read_csv("datasets/produtos.csv")

df_produto.columns = df_produto.columns.str.strip() # remove espaços extras

#configura layout da pagina
st.set_page_config(layout="wide")
st.subheader("📋 Lista de Produtos")

#cria uma tabela interativa para edição
edited_df_produto = st.data_editor(df_produto, num_rows="dynamic", use_container_width=True)

#upload da imagem para atualizar planilha


# Botão para salvar as alterações no CSV
if st.button("Salvar Alterações"):
    df_produto.to_csv("datasets/produtos_atualizados.csv", index=False)
    st.success("✅ Dados salvos com sucesso!")

#barra lateral para pesquisa
df_pesquisa = st.sidebar.text_input("Digite o código do produto")

#filtrar produtos pelo codigo digitado
if df_pesquisa:
    filtro = df_produto[df_produto["Código"].str.contains(df_pesquisa, case=False, na=False)]

    if not filtro.empty:
        st.write("Resultado da pesquisa:")

    else:
      st.warning("Nenhum produto encontrado com esse código.")

    for _, row in filtro.iterrows():
        st.write(f"**Código:** {row["Código"]}")
        st.write(f"**Descrição:** {row["Descrição"]}")
        st.write(f"**Rua:** {row["Rua"]}")
        if pd.notna(row["Imagem do produto"]):  # Verifica se o caminho do arquivo válido na coluna de imagem
            st.image(row["Imagem do produto"], width=400)
        else:
            st.warning("Nenhuma imagem disponível para este produto.")
else:
    st.info("Digite um código de produto na barra lateral para pesquisar.")













