document.addEventListener('DOMContentLoaded', function () {
    const sendButton = document.getElementById('send-btn');
    const chatInput = document.getElementById('chat-input');
    const chatLog = document.getElementById('chat-log');
    const spinner = document.getElementById('chatbot-spinner');


    sendButton.addEventListener('click', function () {
        const query = chatInput.value;
        addMessage('You', query);
        spinner.style.display = 'inline'; // Afficher le spinner
        fetch('/chatbotRag/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // 'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({
                    query: query
                })
            })
            .then(response => response.json())
            .then(data => {
                spinner.style.display = 'none'; // Cacher le spinner

                if (data.response) {
                    addMessage('Bot', data.response);
                } else {
                    addMessage('Bot', "Une erreur s'est produite.");
                }
                chatInput.value = '';
            })
            .catch(() => {
                spinner.style.display = 'none'; // Cacher le spinner
                addMessage('Bot', "Une erreur s'est produite.");
            });
    });

    function addMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = "p-3"
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatLog.appendChild(messageDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function getCsrfToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        return csrfToken;
    }
});