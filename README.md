# 📁 AI File Organizer

Um organizador de arquivos inteligente desenvolvido em Python, utilizando o poder da Inteligência Artificial do Google Gemini e a flexibilidade do LangChain. Este programa é projetado para te ajudar a categorizar e organizar arquivos em sua máquina local de forma autônoma, criando pastas baseadas no conteúdo e tipo de cada arquivo.

## ✨ Funcionalidades

- **Organização Inteligente:** Utiliza o modelo Gemini para analisar o conteúdo de arquivos (textos, documentos, planilhas) e categorizá-los em pastas relevantes.
- **Suporte a Múltiplos Formatos:** Processa `.txt`, `.docx`, `.pdf`, `.xlsx`, `.csv`, e pode inferir categorias para arquivos de imagem, áudio e vídeo baseando-se em seus nomes e extensões.
- **Interface Gráfica (GUI):** Fácil de usar, permitindo selecionar a pasta a ser organizada e acompanhar o progresso em tempo real.
- **Automatização:** Reduz a necessidade de organizar arquivos manualmente, ideal para pastas de downloads ou documentos bagunçados.

### Visualização

Aqui está uma prévia da interface do programa em funcionamento:

![Captura de tela da interface do AI File Organizer](assets/gui_screenshot.png)

## 🚀 Como Fazer Funcionar

Siga os passos abaixo para configurar e executar o AI File Organizer em sua máquina.

### Pré-requisitos

- **Python 3.11.4+**: Certifique-se de ter uma versão compatível do Python instalada.
- **Chave de API do Google Gemini**: Você precisará de uma chave de API para acessar o modelo Gemini. Obtenha a sua em [Google AI Studio](https://aistudio.google.com/).

### Configuração do Ambiente

Este projeto utiliza `pipenv` para gerenciar as dependências.

1.  **Clone o Repositório:**

    ```bash
    git clone [https://github.com/](https://github.com/)[lilkirito22]/[AI-File-Organizer].git
    cd [AI-File-Organizer]
    ```

    _Substitua `[lilkirito22]` e `[AI-File-Organizer]` pelos dados do seu projeto._

2.  **Instale o Pipenv (se ainda não tiver):**

    ```bash
    pip install pipenv
    ```

3.  **Instale as Dependências do Projeto:**
    Com o arquivo `Pipfile` e `Pipfile.lock`, você pode instalar as dependências.

    _Observação: `pipenv install` geralmente já instala as dependências especificadas no Pipfile._

4.  **Ative o Ambiente Virtual:**
    ```bash
    pipenv shell
    ```
    Isso ativará o ambiente virtual do `pipenv`, colocando você dentro de um shell onde todas as dependências do projeto estão disponíveis.

### Configuração da Chave de API

O projeto utiliza um arquivo `.env` (que é ignorado pelo Git para sua segurança) para carregar a chave de API do Gemini.

1.  Crie um arquivo chamado `.env` na raiz do seu projeto (no mesmo diretório onde está `main.py` e `Pipfile`).
2.  Adicione a seguinte linha a este arquivo, substituindo `SUA_CHAVE_API_GEMINI_AQUI` pela sua chave real:
    ```
    GEMINI_API_KEY=SUA_CHAVE_API_GEMINI_AQUI
    ```

### Executando o Programa

Com o ambiente `pipenv` ativado e a chave de API configurada, você pode iniciar o organizador de arquivos:

```bash
python main.py
```
