const chatbot = document.getElementById("chatbot");
const chatbotIcon = document.getElementById("chatbot-icon");
const closeBtn = document.getElementById("close-btn");
const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");
const chatbotBody = document.getElementById("chatbot-body");
chatbotIcon.addEventListener("click", () => {
  chatbot.style.display = "flex";
  chatbot.classList.add("expanded");
  chatbotIcon.style.display = "none";
});

closeBtn.addEventListener("click", () => {
  chatbot.style.display = "none";
  chatbotIcon.style.display = "block";
});

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

function sendMessage() {
  let message = userInput.value.trim();
  if (message === "") return;

  chatbotBody.innerHTML += `<div class="user-msg">You: ${message}</div>`;
  userInput.value = "";

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: message })
  })
  .then(res => res.json())
  .then(data => {
    chatbotBody.innerHTML += `<div class="bot-msg">Bot: ${data.response}</div>`;
    chatbotBody.scrollTop = chatbotBody.scrollHeight;
  })
  .catch(err => {
    chatbotBody.innerHTML += `<div class="bot-msg">⚠️ Error: ${err}</div>`;
  });
}
