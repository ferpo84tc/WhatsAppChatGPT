from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET
from io import StringIO
from openai import OpenAI
import os

app = Flask(__name__)

# Configurar o cliente da OpenAI com a chave da variável de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# URL do XML
XML_URL = "https://xpicer.nyc3.cdn.digitaloceanspaces.com/socd_shippingdiscount.xml"

# Carregar o XML e armazenar os produtos em memória
products = []
try:
    response = requests.get(XML_URL)
    if response.status_code == 200:
        xml_content = response.text
        root = ET.fromstring(xml_content)
        products = root.findall(".//item")
    else:
        print(f"Erro ao carregar o XML: Status {response.status_code}")
except Exception as e:
    print(f"Erro ao processar o XML: {e}")

# Função para buscar informações de produtos no XML
def search_product_in_xml(user_message):
    user_message_lower = user_message.lower()
    for item in products:
        title = item.find("title").text.lower()
        synonyms = [synonym.text.lower() for synonym in item.findall("synonyms/synonym")]
        if title in user_message_lower or any(synonym in user_message_lower for synonym in synonyms):
            price = item.find("g:price", namespaces={'g': 'http://base.google.com/ns/1.0'}).text
            link = item.find("link").text
            return f"Encontrei um produto para você: **{item.find('title').text}** - Preço: R${price} - Link: {link}"
    return None

# Função para obter resposta do GPT da OpenAI
def get_gpt_response(user_message):
    try:
        # Primeiro, verificar se a mensagem corresponde a um produto no XML
        product_response = search_product_in_xml(user_message)
        if product_response:
            return product_response

        # Se não houver correspondência no XML, usar a API da OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Você pode usar "gpt-4" se tiver acesso
            messages=[
                {"role": "system", "content": "Você é um assistente útil que ajuda os usuários a encontrar produtos e responder perguntas gerais."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro ao chamar a API da OpenAI: {e}")
        return "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente!"

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'response': 'Por favor, envie uma mensagem.'}), 400

    # Obter a resposta do GPT (usando XML ou OpenAI)
    response = get_gpt_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)