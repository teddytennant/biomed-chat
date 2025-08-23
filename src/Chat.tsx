import React, { useState, useEffect, useRef } from 'react';
import './Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (input.trim() && !isLoading) {
      const newMessages = [...messages, { role: 'user', content: input }];
      setMessages(newMessages);
      setInput('');
      setIsLoading(true);

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ messages: newMessages }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = '';

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          const jsonMatch = chunk.match(/data: (.*)\n\n/);
          if (jsonMatch && jsonMatch[1] !== '[DONE]') {
            try {
              const data = JSON.parse(jsonMatch[1]);
              if (data.choices && data.choices[0].delta.content) {
                fullResponse += data.choices[0].delta.content;
              }
            } catch (e) {
              console.error("Error parsing SSE chunk", e);
            }
          }
        }

        setMessages(prevMessages => [...prevMessages, { role: 'assistant', content: fullResponse }]);
      } catch (error) {
        console.error("Failed to send message:", error);
        setMessages(prevMessages => [...prevMessages, { role: 'assistant', content: "Sorry, I'm having trouble connecting to the server. Please try again later." }]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="chat-container">
      {messages.length === 0 ? (
        <div className="landing-container">
          <div className="welcome-section">
            <h1>Welcome to Biomed Chat</h1>
            <p>Start a conversation with our AI assistant</p>
          </div>
          <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="input-form">
            <div className="input-row">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Ask me anything about biomedical topics..."
                disabled={isLoading}
                className="chat-input"
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="send-button"
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="chat-active">
          <div className="chat-header">
            <div>
              <h5>Biomed Chat</h5>
              <small>AI Assistant</small>
            </div>
            <div className="chat-stats">
              <small>{messages.length} messages</small>
            </div>
          </div>

          <div className="messages-container">
            {messages.map((msg, index) => (
              <div key={index} className={`message-wrapper ${msg.role}`}>
                <div className={`message-avatar ${msg.role}`}>
                  {msg.role === 'user' ? 'U' : 'AI'}
                </div>
                <div className={`message-content ${msg.role}`}>
                  <div className="message-text">{msg.content}</div>
                  <div className="message-time">
                    <small>
                      {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </small>
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message-wrapper assistant">
                <div className="message-avatar assistant">AI</div>
                <div className="message-content assistant">
                  <div className="typing-indicator">
                    <div>AI is typing...</div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-container">
            <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="input-form">
              <div className="input-row">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder="Continue the conversation..."
                  disabled={isLoading}
                  className="chat-input"
                />
                <button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="send-button"
                >
                  {isLoading ? 'Sending...' : 'Send'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;
