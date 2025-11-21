import { Send, Mic, Square } from 'lucide-react';

const InputArea = ({ 
  input, 
  setInput, 
  onSend, 
  isLoading, 
  isListening, 
  startListening,
  suggestions = [], 
  showSuggestions 
}) => {
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="input-wrapper">
      <div className="input-area-content">
        {showSuggestions && suggestions.length > 0 && (
           <div className="chips-scroll">
            {suggestions.map((sugg, idx) => (
              <button key={idx} className="chip" onClick={() => onSend(sugg)}>
                {sugg}
              </button>
            ))}
          </div>
        )}
        
        <div className="input-container">
          <input 
            type="text" 
            placeholder={isListening ? "Đang nghe..." : "Nhập câu hỏi pháp luật..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading || isListening}
            className={isListening ? "listening" : ""}
          />
          
          <button 
            className={`mic-btn ${isListening ? 'active' : ''}`} 
            onClick={startListening}
            disabled={isLoading}
            title="Nhập bằng giọng nói"
          >
            {isListening ? <Square size={16} fill="currentColor" /> : <Mic size={20} />}
          </button>

          <button 
            onClick={() => onSend()} 
            disabled={isLoading || (!input && !isListening)} 
            className="send-btn"
            title="Gửi tin nhắn"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
      
      <div className="footer-text">
        Kết quả chỉ mang tính tham khảo.
      </div>
    </div>
  );
};

export default InputArea;