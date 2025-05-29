import os
import shutil
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from docx import Document
from PyPDF2 import PdfReader


#Carregar variáveis de ambiente do arquivo .env
load_dotenv()


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# Cria um prompt template para categorização
prompt = ChatPromptTemplate.from_messages([
    ("system", """Você é um assistente de organização de arquivos extremamente inteligente e autônomo.
     Sua tarefa é analisar o conteúdo de um arquivo e identificar a CATEGORIA MAIS ESPECÍFICA E RELEVANTE para ele.
     A categoria deve ser concisa (1-3 palavras, no máximo) e refletir o tema principal ou propósito do arquivo.
     Pense em como um humano organizaria esses arquivos em pastas lógicas.
     Exemplos de categorias esperadas: "Relatórios Financeiros", "Contratos Legais", "Receitas Culinárias", "Fotos de Viagem", "Material de Estudo", "Projetos Pessoais", "Documentos de Identidade", "Faturas de Contas", "Música Favorita", "Downloads Aleatórios".
     Não inclua aspas, pontuação extra, ou qualquer outra explicação na sua resposta, apenas a categoria.
     Se o conteúdo for ambíguo, genérico ou insuficiente, use uma categoria ampla como "Vários" ou "Geral"."""),
    ("user", "Conteúdo do arquivo:\n---\n{file_content}\n-----")
])

# Cria uma "chain" simples: prompt -> modelo -> parser de saída
# O StrOutputParser apenas garante que a saída seja uma string limpa.

categorization_chain = prompt | llm | StrOutputParser()


# Função para extrair texto de arquivos 
def extrair_texto_do_arquivo(caminho_arquivo):
    _, extensao = os.path.splitext(caminho_arquivo)
    extensao = extensao.lower()
    
    
    # Tratamento para arquivos de imagem comuns (apenas nome/extensão para este exemplo)
    if extensao in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'):
        return f"Arquivo de imagem: {os.path.basename(caminho_arquivo)}" # Gemini pode inferir de "Arquivo de imagem"
    elif extensao in ('.mp3', '.wav', '.ogg', '.flac'):
         return f"Arquivo de áudio: {os.path.basename(caminho_arquivo)}"
    elif extensao in ('.mp4', '.avi', '.mov', '.mkv'):
         return f"Arquivo de vídeo: {os.path.basename(caminho_arquivo)}"

    if extensao == '.txt':
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Erro ao ler TXT {caminho_arquivo}: {e}")
            return None
    elif extensao == '.docx':
        try:
            document = Document(caminho_arquivo)
            return "\n".join([para.text for para in document.paragraphs])
        except Exception as e:
            print(f"Erro ao ler DOCX {caminho_arquivo}: {e}")
            return None
    elif extensao == '.pdf':
        try:
            reader = PdfReader(caminho_arquivo)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() or ""
            return texto
        except Exception as e:
            print(f"Erro ao ler PDF {caminho_arquivo}: {e}")
            return None
    return None

# --- Função para categorizar arquivo usando Gemini via LangChain ---

def categorizar_arquivo_com_gemini_lc(caminho_arquivo):
    texto_para_analise = extrair_texto_do_arquivo(caminho_arquivo)

    if not texto_para_analise:
        print(f"Não foi possível extrair texto do arquivo: {os.path.basename(caminho_arquivo)}. Ignorando...")
        return None

    texto_curto = texto_para_analise[:10000] # Limite para os primeiros 10.000 caracteres

    try:
        # Invoca a chain para obter a categoria
        categoria = categorization_chain.invoke({"file_content": texto_curto})
        
        # Limpa a categoria, removendo caracteres indesejados para nomes de pasta
        categoria_limpa = "".join(c for c in categoria if c.isalnum() or c in [' ', '_', '-']).strip()
        categoria_limpa = categoria_limpa.replace(" ", "_").replace("__", "_")

        return categoria_limpa if categoria_limpa else "Indefinidos"

    except Exception as e:
        print(f"Erro ao categorizar com Gemini via LangChain o arquivo {os.path.basename(caminho_arquivo)}: {e}")
        return "Erro_Categorizacao_IA"
    
    
# --- Função principal para organizar ---
def organizar_pasta_com_ia_lc(caminho_pasta_baguncada):
    if not os.path.isdir(caminho_pasta_baguncada):
        print(f"Erro: O caminho '{caminho_pasta_baguncada}' não é um diretório válido.")
        return

    print(f"Iniciando organização da pasta: {caminho_pasta_baguncada}")
    
    arquivos_a_processar = [
        os.path.join(caminho_pasta_baguncada, item)
        for item in os.listdir(caminho_pasta_baguncada)
        if os.path.isfile(os.path.join(caminho_pasta_baguncada, item))
    ]

    for caminho_completo_arquivo in arquivos_a_processar:
        nome_arquivo = os.path.basename(caminho_completo_arquivo)
        print(f"\nProcessando: {nome_arquivo}")

        categoria_sugerida = categorizar_arquivo_com_gemini_lc(caminho_completo_arquivo)
        
        if categoria_sugerida:
            pasta_destino = os.path.join(caminho_pasta_baguncada, categoria_sugerida)
            
            if not os.path.exists(pasta_destino):
                try:
                    os.makedirs(pasta_destino)
                    print(f"Pasta criada: {pasta_destino}")
                except Exception as e:
                    print(f"Erro ao criar pasta {pasta_destino}: {e}. Usando 'Outros_Arquivos'.")
                    pasta_destino = os.path.join(caminho_pasta_baguncada, "Outros_Arquivos")
                    if not os.path.exists(pasta_destino):
                         os.makedirs(pasta_destino)

            try:
                shutil.move(caminho_completo_arquivo, os.path.join(pasta_destino, nome_arquivo))
                print(f"Movido: '{nome_arquivo}' para '{pasta_destino}'")
            except shutil.Error as e:
                print(f"Erro ao mover '{nome_arquivo}': {e}. Pode ser que já exista um arquivo com esse nome no destino.")
            except Exception as e:
                print(f"Erro inesperado ao mover '{nome_arquivo}': {e}")
        else:
            print(f"Arquivo '{nome_arquivo}' não foi categorizado. Deixando na pasta original ou movendo para 'Não_Categorizados'.")


# --- Exemplo de Uso ---
if __name__ == "__main__":
    # Crie uma pasta de teste e coloque alguns arquivos variados dentro dela
    # para ver como o script funciona.
    # Ex: 'minha_bagunca_pessoal_lc'
    
    pasta_principal = 'C:/Users/dccas/Desktop/ESTUDO DE IA/AI AGENT/bagunça' 
    
    if not os.path.exists(pasta_principal):
        os.makedirs(pasta_principal)
        # Crie alguns arquivos de teste para simular a bagunça
        with open(os.path.join(pasta_principal, "documento_relatorio_2024.txt"), "w") as f:
            f.write("Este é um relatório financeiro anual da empresa X para 2024. Inclui balanços e projeções.")
        with open(os.path.join(pasta_principal, "apresentacao_projeto_alpha.txt"), "w") as f:
            f.write("Slides para a apresentação do projeto Alpha. Foco em marcos e próximos passos.")
        doc = Document()
        doc.add_paragraph("Minhas anotações de aula sobre história romana. Detalhes sobre o império e seus líderes.")
        doc.save(os.path.join(pasta_principal, "notas_historia.docx"))
        with open(os.path.join(pasta_principal, "fatura_internet_maio.pdf"), "w") as f:
            f.write("Fatura de serviços de internet referente a maio. Total R$ 120,00.")

    organizar_pasta_com_ia_lc(pasta_principal)
    print("\nOrganização concluída com LangChain!")