import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Form, Button, Card } from 'react-bootstrap';
import AdvancedBiomedAnimation from './AdvancedBiomedAnimation';
import BiomedIcon from './BiomedIcon';
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
    <Container fluid className="chat-container">
      {messages.length === 0 ? (
        <div className="landing-container">
          <div className="animation-wrapper fade-in">
            <AdvancedBiomedAnimation />
          </div>
          <div className="input-section">
            <div className="welcome-text text-center mb-4">
              <h1 className="text-gradient mb-2">Welcome to Biomed Chat</h1>
              <p className="text-muted">Start a conversation with our AI assistant</p>
            </div>
            <Form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="input-form">
              <Row className="g-2">
                <Col xs={10}>
                  <div className="input-wrapper">
                    <Form.Control
                      as="textarea"
                      rows={1}
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
                      className="modern-input"
                    />
                    <div className="input-actions">
                      <small className="text-muted">Press Enter to send</small>
                    </div>
                  </div>
                </Col>
                <Col xs={2} className="d-grid">
                  <Button
                    variant="primary"
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className="send-button"
                  >
                    {isLoading ? (
                      <div className="loading-spinner"></div>
                    ) : (
                      <>
                        <i className="fas fa-paper-plane me-1"></i>
                        Send
                      </>
                    )}
                  </Button>
                </Col>
              </Row>
            </Form>
          </div>
        </div>
      ) : (
        <div className="chat-active">
          <div className="chat-header">
            <div className="d-flex align-items-center">
              <BiomedIcon />
              <div className="ms-3">
                <h5 className="mb-0 text-gradient">Biomed Chat</h5>
                <small className="text-muted">AI Assistant</small>
              </div>
            </div>
            <div className="chat-stats">
              <small className="text-muted">{messages.length} messages</small>
            </div>
          </div>

          <div className="messages-container">
            {messages.map((msg, index) => (
              <div key={index} className={`message-wrapper ${msg.role} slide-in-${msg.role === 'user' ? 'right' : 'left'}`}>
                <div className={`message-avatar ${msg.role}`}>
                  {msg.role === 'user' ? (
                    <i className="fas fa-user"></i>
                  ) : (
                    <BiomedIcon />
                  )}
                </div>
                <div className={`message-content ${msg.role}`}>
                  <div className="message-text">{msg.content}</div>
                  <div className="message-time">
                    <small className="text-muted">
                      {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </small>
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message-wrapper assistant slide-in-left">
                <div className="message-avatar assistant">
                  <BiomedIcon />
                </div>
                <div className="message-content assistant loading">
                  <div className="typing-indicator">
                    <div className="dot-flashing"></div>
                    <div className="typing-text">AI is typing...</div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-container">
            <Form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="input-form">
              <Row className="g-2">
                <Col xs={10}>
                  <div className="input-wrapper">
                    <Form.Control
                      as="textarea"
                      rows={1}
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
                      className="modern-input"
                    />
                    <div className="input-actions">
                      <small className="text-muted">Press Enter to send</small>
                    </div>
                  </div>
                </Col>
                <Col xs={2} className="d-grid">
                  <Button
                    variant="primary"
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className="send-button"
                  >
                    {isLoading ? (
                      <div className="loading-spinner"></div>
                    ) : (
                      <>
                        <i className="fas fa-paper-plane me-1"></i>
                        Send
                      </>
                    )}
                  </Button>
                </Col>
              </Row>
            </Form>
          </div>
        </div>
      )}
    </Container>
  );
};

export default Chat;
