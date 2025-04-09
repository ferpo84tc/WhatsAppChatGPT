function sendMessage() {
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');
    
    const messageText = userInput.value.trim();
    if (!messageText) return;

    // Adicionar mensagem do usuário
    const userMessage = document.createElement('div');
    userMessage.className = 'message user';
    userMessage.innerHTML = `<div class="message-content">${messageText}</div>`;
    chatMessages.appendChild(userMessage);

    // Limpar o campo de entrada
    userInput.value = '';

    // Enviar mensagem para o servidor
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageText }),
    })
    .then(response => response.json())
    .then(data => {
        // Adicionar resposta do bot
        const botMessage = document.createElement('div');
        botMessage.className = 'message bot';
        botMessage.innerHTML = `<div class="message-content">${data.response}</div>`;
        chatMessages.appendChild(botMessage);

        // Rolar para a última mensagem
        chatMessages.scrollTop = chatMessages.scrollHeight;
    })
    .catch(error => {
        console.error('Erro:', error);
        const botMessage = document.createElement('div');
        botMessage.className = 'message bot';
        botMessage.innerHTML = `<div class="message-content">Desculpe, ocorreu um erro.</div>`;
        chatMessages.appendChild(botMessage);
    });
}