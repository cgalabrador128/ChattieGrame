
document.addEventListener('DOMContentLoaded', () => {
    const messageContainer = document.querySelector('.message-container');

    if (!messageContainer) return;
    
    const currentChatId = messageContainer.dataset.chatId.trim();
    const userId = messageContainer.dataset.userId.trim();
    const chatMateImage = messageContainer.dataset.chatmateImage;

    
    if (!currentChatId || currentChatId === "#" || currentChatId === "None") {
        console.log("No active chat selected. Real-time paused.");
        return; 
    }
    
    const supabaseUrl = 'https://lrzfpjdxxhkxfvtfqwjy.supabase.co';
    const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxyemZwamR4eGhreGZ2dGZxd2p5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5MDA0NzEsImV4cCI6MjA4OTQ3NjQ3MX0.Res2tCSx_TI3Gt5tZx6AoaTSciUGRxM1z6ns6vi8vc0';
    const supabase = window.supabase.createClient(supabaseUrl, supabaseKey);


    supabase
      .channel('chat_room_' + currentChatId)
      .on(
        'postgres_changes',
        { 
            event: 'INSERT', 
            schema: 'public', 
            table: 'chat',
            filter: `chatid=eq.${currentChatId}`
        },
        (payload) => {
          console.log("SUPABASE EVENT RECEIVED!", payload);
          const newMessageText = payload.new.chatcontent;
          const senderid = String(payload.new.userid_sender).trim();

          const chatContainer = document.querySelector('.mc-body');
          if (!chatContainer){
            console.error("Could not find .mc-body!");
            return;
          } 
          
          let newHtml = "";
          
          if (senderid === userId) {
            newHtml = `<div class="receiver"><p>${newMessageText}</p></div>`;
          } else {
            newHtml = `
              <div class="sender">
                  <img src="${chatMateImage}" alt="Profile">
                  <p>${newMessageText}</p>
              </div>`;
          }

          // Inject the new message and scroll to bottom
          chatContainer.insertAdjacentHTML('afterbegin', newHtml);
          chatContainer.scrollTop = 0;

          console.log("SUCCESS! Injected this HTML:", newHtml);
        }
      )
      .subscribe();

    const chatForm = document.getElementById('chat-form');

    if (chatForm) {
        chatForm.addEventListener('submit', function(event) {
            
            event.preventDefault(); 
            
            const messageInput = document.getElementById('message-content');
            const textValue = messageInput.value;
            if (!textValue.trim()) return;

            // Send to Flask
            fetch(`/messages/${currentChatId}`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json' 
                },
                body: JSON.stringify({ 'message-content': textValue }) 
            })
            .then(response => response.json())
            .then(data => {
                if(data.status === 'success') {
                    // Clear 
                    messageInput.value = ''; 
                } else {
                    console.error("Server error:", data.message);
                }
            })
            .catch(error => console.error('Fetch Error:', error));
        });
    }
});