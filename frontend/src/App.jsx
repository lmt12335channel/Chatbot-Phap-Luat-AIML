import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Menu, Gavel, Moon, Sun } from 'lucide-react';

// Import Components (Đảm bảo đường dẫn đúng)
import Sidebar from './components/Sidebar';
import ChatFeed from './components/ChatFeed';
import InputArea from './components/InputArea';

// Import CSS
import './index.css';
import './App.css';

const generateId = () => '_' + Math.random().toString(36).substr(2, 9);

function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');
  const [conversationId, setConversationId] = useState(() => localStorage.getItem('last_conversation_id') || generateId());
  
  // Quản lý danh sách các đoạn chat
  const [sessions, setSessions] = useState(() => {
    try {
      const saved = localStorage.getItem('chat_sessions');
      return saved ? JSON.parse(saved) || [] : [];
    } catch (e) {
      return [];
    }
  });

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const DEFAULT_SUGGESTIONS = [
    "Thủ tục ly hôn thuận tình", 
    "Sang tên sổ đỏ cần gì?", 
    "Mức phạt nồng độ cồn", 
    "Làm CCCD gắn chip"
  ];
  const [suggestions, setSuggestions] = useState(DEFAULT_SUGGESTIONS);

  const messagesEndRef = useRef(null);

  // --- EFFECTS ---
  
  // Load tin nhắn khi chọn session khác
  useEffect(() => {
    const currentSession = sessions.find(s => s.id === conversationId);
    if (currentSession) {
      setMessages(currentSession.messages || []);
    } else {
      setMessages([]); 
      setSuggestions(DEFAULT_SUGGESTIONS);
    }
    localStorage.setItem('last_conversation_id', conversationId);
  }, [conversationId]);

  // Lưu tin nhắn vào session hiện tại
  useEffect(() => {
    if (messages.length > 0) {
      setSessions(prevSessions => {
        const safeSessions = Array.isArray(prevSessions) ? prevSessions : [];
        const existingIndex = safeSessions.findIndex(s => s.id === conversationId);
        
        const title = messages[0].sender === 'user' 
          ? messages[0].text.substring(0, 30) + (messages[0].text.length > 30 ? "..." : "")
          : "Cuộc hội thoại mới";

        const updatedSession = { 
          id: conversationId, 
          title: existingIndex > -1 ? safeSessions[existingIndex].title : title, 
          messages: messages,
          timestamp: Date.now()
        };

        let newSessions;
        if (existingIndex > -1) {
          newSessions = [...safeSessions];
          newSessions[existingIndex] = updatedSession;
          newSessions.splice(existingIndex, 1);
          newSessions.unshift(updatedSession);
        } else {
          newSessions = [updatedSession, ...safeSessions];
        }
        return newSessions;
      });
    }
  }, [messages, conversationId]);

  useEffect(() => { localStorage.setItem('chat_sessions', JSON.stringify(sessions)); }, [sessions]);
  useEffect(() => { document.documentElement.setAttribute('data-theme', theme); localStorage.setItem('theme', theme); }, [theme]);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isLoading]);

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

  // --- LOGIC ---

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert("Trình duyệt không hỗ trợ. Hãy dùng Google Chrome.");
      return;
    }
    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = 'vi-VN';
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(prev => prev + (prev ? " " : "") + transcript);
    };
    recognition.start();
  };

  const handleSend = async (textToSend) => {
    const msgText = textToSend || input;
    if (!msgText.trim()) return;

    const userMsg = { id: generateId(), sender: 'user', text: msgText };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);
    setSuggestions([]); 

    setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }), 100);

    try {
      const res = await axios.post('http://127.0.0.1:5000/ask', { question: msgText });
      const data = res.data;
      const botMsg = { id: generateId(), sender: 'bot', text: data.answer, vote: null };
      setMessages(prev => [...prev, botMsg]);
      if (data.suggestions && data.suggestions.length > 0) {
        setSuggestions(data.suggestions);
      }
    } catch (error) {
      setMessages(prev => [...prev, { id: generateId(), sender: 'bot', text: '⚠️ Lỗi kết nối Server!' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (messageId, voteType) => {
    setMessages(prev => prev.map(msg => msg.id === messageId ? { ...msg, vote: voteType } : msg));
    try {
      await axios.post('http://127.0.0.1:5000/api/feedback', {
        conversation_id: conversationId,
        message_id: messageId,
        vote: voteType
      });
    } catch (error) { console.error(error); }
  };

  // Tạo Chat Mới
  const handleNewChat = () => {
    setConversationId(generateId());
    setMessages([]);
    setSuggestions(DEFAULT_SUGGESTIONS);
    setIsSidebarOpen(false);
  };

  // Chọn Chat Cũ
  const handleSelectSession = (session) => {
    setConversationId(session.id);
    setIsSidebarOpen(false);
  };

  // Xóa 1 Chat
  const handleDeleteSession = (sessionId) => {
    if (window.confirm("Bạn muốn xóa cuộc hội thoại này?")) {
      const newSessions = sessions.filter(s => s.id !== sessionId);
      setSessions(newSessions);
      if (sessionId === conversationId) {
        handleNewChat();
      }
    }
  };

  // Xóa Tất Cả
  const handleClearAll = () => {
    if (window.confirm("Xóa TOÀN BỘ lịch sử?")) {
      setSessions([]);
      handleNewChat();
    }
  };

  // Xuất PDF (Dùng trình duyệt in)
  const handleExportPDF = () => {
    window.print();
  };

  return (
    <div className="app-layout">
      <Sidebar 
        isOpen={isSidebarOpen} 
        onClose={() => setIsSidebarOpen(false)} 
        onNewChat={handleNewChat} 
        onClearAll={handleClearAll} 
        onExportPDF={handleExportPDF}
        sessions={sessions} 
        currentId={conversationId} 
        onSelectSession={handleSelectSession} 
        onDeleteSession={handleDeleteSession} 
        theme={theme} 
        toggleTheme={toggleTheme} 
      />

      <main className="main-chat">
        <header className="top-bar">
          <button className="menu-btn" onClick={() => setIsSidebarOpen(true)}><Menu size={24} /></button>
          <div className="brand">
            <Gavel size={24} strokeWidth={2.5} /> <span>Luật Sư AIML</span>
          </div>
          <div style={{flex:1}}></div>
          <button className="theme-toggle-btn" onClick={toggleTheme}>
              {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          </button>
        </header>

        <ChatFeed 
          messages={messages}
          isLoading={isLoading}
          suggestions={suggestions}
          onSend={handleSend}
          onFeedback={handleFeedback}
          messagesEndRef={messagesEndRef}
        />

        <InputArea 
          input={input}
          setInput={setInput}
          onSend={handleSend}
          isLoading={isLoading}
          isListening={isListening}
          startListening={startListening}
          suggestions={suggestions}
          showSuggestions={messages.length > 0 && !isLoading}
        />
      </main>

      {isSidebarOpen && <div className="overlay" onClick={() => setIsSidebarOpen(false)}></div>}
    </div>
  );
}

export default App;