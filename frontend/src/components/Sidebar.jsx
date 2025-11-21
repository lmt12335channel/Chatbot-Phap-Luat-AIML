import { Plus, Trash2, X, User, Moon, Sun, MessageSquare, Download } from 'lucide-react';

const Sidebar = ({ 
  isOpen, 
  onClose, 
  onNewChat, 
  onClearAll,
  onExportPDF, 
  sessions = [], 
  currentId,       
  onSelectSession, 
  onDeleteSession, 
  theme, 
  toggleTheme 
}) => {
  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewChat}>
          <Plus size={18} /> Cuộc hội thoại mới
        </button>
        <button className="close-sidebar-btn" onClick={onClose}>
           <X size={24} />
        </button>
      </div>
      
      <div className="sidebar-content">
        <div className="menu-label">Lịch sử chat</div>
        
        <div className="session-list">
          {!sessions || sessions.length === 0 ? (
            <div className="history-placeholder" style={{padding: '10px', color: '#9ca3af', fontSize: '13px'}}>
              Chưa có lịch sử trò chuyện.
            </div>
          ) : (
            sessions.map((session) => (
              <div 
                key={session.id} 
                className={`history-item-row ${session.id === currentId ? 'active' : ''}`}
                onClick={() => onSelectSession(session)}
              >
                <div className="history-icon">
                  <MessageSquare size={16} />
                </div>
                <div className="history-title" title={session.title}>
                  {session.title || "Cuộc hội thoại mới"}
                </div>
                <button 
                  className="delete-session-btn" 
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.id);
                  }}
                  title="Xóa"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>

        <div className="menu-label" style={{marginTop: '20px'}}>Công cụ</div>
        
        {/* Nút Xuất PDF */}
        <button className="history-item" onClick={onExportPDF}>
           <Download size={16} /> Xuất PDF
        </button>

        <button className="history-item" onClick={onClearAll}>
           <Trash2 size={16} /> Xóa tất cả lịch sử
        </button>
      </div>

      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="avatar-small"><User size={20} /></div>
          <div className="user-info">
            <span className="name">Sinh viên</span>
            <span className="plan">Đồ án Tốt nghiệp</span>
          </div>
          <div style={{flex: 1}}></div>
          <button className="theme-toggle-btn" onClick={toggleTheme} title="Đổi giao diện">
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;