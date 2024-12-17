import requests
from bs4 import BeautifulSoup
import ollama 


def summarize_with_ollama(text):
    prompt = f"Resuma o seguinte conteúdo HTML em tópicos e um leve resumo do tópico, para depois eu dizer qual tópico quero melhor explicado:\n\n{text}"
    
    try:
        response = ollama.chat(model="llama3.1", stream=True, messages=[{"role": "user", "content": prompt}])
        
        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                content = chunk['message']['content']
                yield content  
        
    except Exception as e:
        print(f"Erro ao processar o resumo: {e}")
        return None


def extract_html_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        html_content = response.content
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator="\n", strip=True)  # Extraímos o texto com quebras de linha
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para o URL {url}: {e}")
        return None
    
url = input('Link: ')
text_content = extract_html_content(url)

if text_content:
    print("Resumo do Conteúdo:")
    
    for chunk in summarize_with_ollama(text_content):
        print(chunk, end='', flush=True)
else:
    print("Erro ao extrair o conteúdo HTML.")
