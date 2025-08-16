import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Form, Button, Card } from 'react-bootstrap';
import AdvancedBiomedAnimation from './AdvancedBiomedAnimation';
import BiomedIcon from './BiomedIcon';

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
    <Container fluid className="d-flex flex-column vh-100">
      {messages.length === 0 ? (
        <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center">
          <AdvancedBiomedAnimation />
          <div className="w-100 mt-4">
            <Form onSubmit={(e) => { e.preventDefault(); handleSend(); }}>
              <Row>
                <Col xs={10}>
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
                    placeholder="Type your message..."
                    disabled={isLoading}
                  />
                </Col>
                <Col xs={2} className="d-grid">
                  <Button variant="primary" type="submit" disabled={isLoading}>
                    Send
                  </Button>
                </Col>
              </Row>
            </Form>
          </div>
        </div>
      ) : (
        <Card className="flex-grow-1 d-flex flex-column">
          <Card.Header as="h5" className="d-flex align-items-center">
            <BiomedIcon />
            <span className="ms-2">Biomed Chat</span>
          </Card.Header>
          <Card.Body className="flex-grow-1 overflow-auto">
            {messages.map((msg, index) => (
              <div key={index} className={`d-flex ${msg.role === 'user' ? 'justify-content-end' : 'justify-content-start'} mb-3`}>
                <Card body className={`message-card ${msg.role === 'user' ? 'user' : 'assistant'}`}>
                  <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                </Card>
              </div>
            ))}
            {isLoading && (
              <div className="d-flex justify-content-start mb-3">
                <Card body className="message-card assistant">
                  <div className="d-flex justify-content-center align-items-center" style={{ height: '40px' }}>
                    <div className="dot-flashing"></div>
                  </div>
                </Card>
              </div>
            )}
            <div ref={messagesEndRef} />
          </Card.Body>
          <Card.Footer>
            <Form onSubmit={(e) => { e.preventDefault(); handleSend(); }}>
              <Row>
                <Col xs={10}>
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
                    placeholder="Type your message..."
                    disabled={isLoading}
                  />
                </Col>
                <Col xs={2} className="d-grid">
                  <Button variant="primary" type="submit" disabled={isLoading}>
                    Send
                  </Button>
                </Col>
              </Row>
            </Form>
          </Card.Footer>
        </Card>
      )}
    </Container>
  );
};

export default Chat;
