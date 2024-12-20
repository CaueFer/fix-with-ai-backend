import requests
from bs4 import BeautifulSoup
import ollama 
from flask import Flask, Response, abort, request, jsonify


# HISTORICO DE MASSAGEM DO CHAT
chat_history = []
max_chat_history_size = 5

def addToHistory(newMessageObject):
    if len(chat_history) >= max_chat_history_size: 
        chat_history.pop(1)
        chat_history.append(newMessageObject)
    else:   chat_history.append(newMessageObject)

def summarizeWithLllama(text):
    chat_history = []
    
    prompt = f"Resuma em pt-br o seguinte conteúdo HTML em tópicos e conteudo, para depois eu dizer qual tópico quero melhor explicado:\n\n{text}"
    
    try:
        # Adiciona a mensagem do usuário ao histórico
        chat_history.append({"role": "user", "content": prompt})
        
        response = ollama.chat(model="llama3.1", stream=True, messages=[{"role": "user", "content": prompt}])
        
        finalResponse = ""
        
        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                content = chunk['message']['content']
                finalResponse += content
                yield content  
        
        # ADD MESSAGE TO CHAT HISTORY
        addToHistory({"role": "assistant", "content": finalResponse})
        
        
    except Exception as e:
        error_message = f"Erro ao resumir a url: {e}"
        print(error_message) 
        return jsonify({"error": f"Erro no processamento do resumo: {e}"}), 500

def extractHtmlContent(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        html_content = response.content
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator="\n", strip=True)  # Extraímos o texto com quebras de linha
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para o URL {url}: {e}")
        return None
   
def resume(): 
    urlToResume = request.json.get('url');
    
    if not urlToResume:
        return jsonify({"error": "URL VAZIA"}), 400
    
    text_content = extractHtmlContent(urlToResume)
    
    if text_content:
        print("Iniciando o resumo do conteúdo...")
        
        def generate():
            try:
                result = summarizeWithLllama(text_content)
                if isinstance(result, str): 
                    return jsonify({"error": result}), 500
                else:
                    for chunk in result:
                        yield chunk
                        
            except Exception as e:
                return jsonify({"error": f"Erro no processamento do resumo: {e}"}), 500
        
        return Response(generate(), content_type='text/plain; charset=utf-8')
    
    else:
        return jsonify({"error": "Erro ao extrair o conteúdo HTML."}), 400
  
   
def questionToAI():
    try:
        print('IA Pensando...')
        response = ollama.chat(model="llama3.1", messages=chat_history, stream=True)
        
        finalResponse = ''
        
        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                content = chunk['message']['content']
                finalResponse += content
                yield content 
        
        
        if(len(finalResponse) > 1 ):
            print('Formatando resposta...')
            
            # ADD RESPONSE TO CHAT HISTORY
            addToHistory({"role": "assistant", "content": finalResponse})
        
    except Exception as e:
        error_message = f"Erro ao processar a resposta: {e}"
        print(error_message) 
        yield error_message 
        return None  

def chat(): 
    userMessage = request.json.get('message');
    
    if not userMessage:
        return jsonify({"error": "Mensagem invalida ou vazia"}), 400
    
    # ADD MESSAGE TO CHAT HISTORY
    addToHistory({"role": "user", "content": 'Responder essa pergunta '+ userMessage})
    
    print("Gerando resposta...")
    
    def generateResponse():    
        for chunk in questionToAI():
            yield chunk 
        
    return Response(generateResponse(), content_type='text/plain; charset=utf-8')
