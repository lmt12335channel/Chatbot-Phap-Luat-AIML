import ReactMarkdown from 'react-markdown';
import { Bot, User, Lightbulb, ThumbsUp, ThumbsDown, Copy } from 'lucide-react';

const ChatFeed = ({ 
  messages, 
  isLoading, 
  suggestions, 
  onSend, 
  onFeedback, 
  messagesEndRef 
}) => {
  
  // Hàm copy tin nhắn
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // Có thể thêm toast thông báo ở đây
  };

  return (
    <div className="chat-feed">
      {messages.length === 0 ? (
        <div className="welcome-screen">
          <div className="logo-large"><Bot size={60} /></div>
          <h2>Xin chào! Tôi là Trợ lý Pháp luật.</h2>
          <div className="suggestions-grid">
            {suggestions.map((sugg, idx) => (
              <div key={idx} className="suggestion-card" onClick={() => onSend(sugg)}>
                <Lightbulb size={20} color="var(--primary-color)" />
                <div className="text">{sugg}</div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg, index) => (
            <div key={index} className={`chat-row ${msg.sender}`}>
              <div className="chat-content">
                <div className={`avatar ${msg.sender}`}>
                  {msg.sender === 'bot' ? <Bot size={20} /> : <User size={20} />}
                </div>
                <div className="message-container">
                  <div className="sender-name">
                    {msg.sender === 'bot' ? 'Luật Sư AIML' : 'Bạn'}
                  </div>
                  
                  <div className="message-bubble">
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                  </div>

                  {/* Buttons Feedback cho Bot */}
                  {msg.sender === 'bot' && (
                    <div className="message-actions">
                      <button 
                        onClick={() => onFeedback(msg.id, 'like')} 
                        className={`action-btn ${msg.vote === 'like' ? 'liked' : ''}`}
                        title="Hữu ích"
                      >
                        <ThumbsUp size={14} />
                      </button>
                      <button 
                        onClick={() => onFeedback(msg.id, 'dislike')} 
                        className={`action-btn ${msg.vote === 'dislike' ? 'disliked' : ''}`}
                        title="Không hữu ích"
                      >
                        <ThumbsDown size={14} />
                      </button>
                      <div className="divider">|</div>
                      <button onClick={() => copyToClipboard(msg.text)} className="action-btn" title="Sao chép">
                        <Copy size={14} />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="chat-row bot">
              <div className="chat-content">
                <div className="avatar bot"><Bot size={20} /></div>
                <div className="message-bubble typing">
                  <div className="dot"></div><div className="dot"></div><div className="dot"></div>
                </div>
              </div>
            </div>
          )}
          {/* Element để auto scroll */}
          <div ref={messagesEndRef} style={{float: 'left', clear: 'both'}} />
        </>
      )}
    </div>
  );
};

export default ChatFeed;