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
    ("system", """Você é um assistente inteligente que categoriza arquivos pessoais.
     Sua tarefa é analisar o conteúdo fornecido e sugerir a categoria mais apropriada em uma única palavra ou frase curta.
     As categorias devem ser úteis para organizar arquivos.
     Exemplos de categorias: "Documentos", "Relatórios", "Faturas", "Fotos", "Vídeos", "Estudos", "Trabalho", "Pessoal", "Recibos", "Contratos", "Música", "Projetos", "Downloads", "Outros".
     Se o conteúdo for muito curto ou genérico, use uma categoria ampla.
     Não inclua aspas, pontuação extra, ou qualquer outra explicação na sua resposta, apenas a categoria."""),
    ("user", "Conteúdo do arquivo:\n---\n{file_content}\n---\nCategoria Sugerida:")
])

# Cria uma "chain" simples: prompt -> modelo -> parser de saída
# O StrOutputParser apenas garante que a saída seja uma string limpa.

categorization_chain = prompt | llm | StrOutputParser()


# Função para extrair texto de arquivos 
def extrair_texto_do_arquivo(caminho_arquivo):
    _, extensao = os.path.splitext(caminho_arquivo)
    extensao = extensao.lower()

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



