document.getElementById('sendButton').addEventListener('click', sendMessage);
document.getElementById('uploadButton').addEventListener('click', uploadPDF);
document.getElementById('userInput').addEventListener('keypress', function(event) {
  if (event.key === 'Enter') {
    sendMessage();
  }
});

function addMessage(text, sender) {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message', sender);
  messageDiv.innerText = text;
  document.getElementById('chatbox').appendChild(messageDiv);
  document.getElementById('chatbox').scrollTop = document.getElementById('chatbox').scrollHeight;
}

function sendMessage() {
  const userInput = document.getElementById('userInput');
  const text = userInput.value.trim();
  if (text === '') return;

  addMessage(text, 'user');
  userInput.value = '';

  fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ question: text })
  })
  .then(response => response.json())
  .then(data => {
    typingEffect(data.answer, 'bot');
  })
  .catch(error => {
    addMessage('Error: Could not reach the server.', 'bot');
    console.error('Error:', error);
  });
}

function uploadPDF() {
  const fileInput = document.getElementById('pdfInput');
  const file = fileInput.files[0];
  if (!file) {
    alert('Please select a PDF file first.');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  fetch('http://localhost:8000/upload-pdf', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    alert('PDF uploaded successfully!');
  })
  .catch(error => {
    alert('Error uploading PDF.');
    console.error('Error:', error);
  });
}

function typingEffect(text, sender) {
  let i = 0;
  const typingSpeed = 30;
  const chatbox = document.getElementById('chatbox');

  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message', sender);
  chatbox.appendChild(messageDiv);

  function typeChar() {
    if (i < text.length) {
      messageDiv.innerText += text.charAt(i);
      i++;
      setTimeout(typeChar, typingSpeed);
      chatbox.scrollTop = chatbox.scrollHeight;
    }
  }
  typeChar();
}
