import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal
import aiml
import os
import re
import time
import sys
import datetime
import sqlite3
from functools import lru_cache

# --- CẤU HÌNH ---
DB_FILE = "chatbot_data.db"
BRAIN_FILE = "../data/bot_brain.brn"
AIML_FILES = [
    "../data/aiml_advanced.aiml",
    "../data/greetings.aiml",
    "../data/manual_fixes.aiml",
    "../data/phapluat_final.aiml"
]
FALLBACK_KEYWORD = "Xin lỗi, tôi chưa hiểu"

try:
    import conversation_config
    print("Đã tải cấu hình từ conversation_config.py")
except ImportError:
    class conversation_config:
        API_PORT = 5000
        ALLOW_ORIGINS = ["*"]
        TOPIC_SUGGESTIONS = {}

# --- 1. DATABASE ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        message_id TEXT,
        vote TEXT,
        reason TEXT,
        created_at TIMESTAMP
    )
    ''')
    # Thêm cột 'frequency' để đếm số lần xuất hiện của câu hỏi lỗi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS missing_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT UNIQUE, 
        bot_response TEXT,
        frequency INTEGER DEFAULT 1,
        created_at TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database (SQLite) đã sẵn sàng!")

init_db()

# --- APP ---
app = FastAPI(title="AI Legal Chatbot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(conversation_config, 'ALLOW_ORIGINS', ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kernel = aiml.Kernel()
sys.setrecursionlimit(5000)

TRANS_CHARS = {
    'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a', 'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a', 'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'đ': 'd', 'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e', 'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i', 'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o', 'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o', 'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u', 'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u', 'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y'
}
TRANS_TABLE = str.maketrans(TRANS_CHARS)
RE_CLEAN = re.compile(r'[^a-z0-9\s]')
RE_SPACE = re.compile(r'\s+')

@lru_cache(maxsize=4096)
def normalize_aiml_pattern(text: str) -> str:
    if not text: return ""
    s = text.lower().translate(TRANS_TABLE)
    s = RE_CLEAN.sub(' ', s)
    return RE_SPACE.sub(' ', s).strip().upper()

@lru_cache(maxsize=1024)
def get_cached_response(norm_q):
    response = kernel.respond(norm_q)
    if not response:
        response = kernel.respond(f"* {norm_q} *")
    return response

def init_bot(force_reload=False):
    print("-> Đang nạp bộ não AIML...")
    if force_reload and os.path.exists(BRAIN_FILE):
        try: os.remove(BRAIN_FILE)
        except: pass
    if os.path.exists(BRAIN_FILE) and not force_reload:
        kernel.bootstrap(brainFile=BRAIN_FILE)
    else:
        kernel.resetBrain()
        for f in AIML_FILES:
            if os.path.exists(f):
                try: kernel.learn(f)
                except Exception as e: print(f"[WARN] Lỗi file {f}: {e}")
        kernel.saveBrain(BRAIN_FILE)
    print("-> Bot đã sẵn sàng!")

init_bot()

# --- 2. BỘ LỌC CHẤT LƯỢNG LOG (NEW FEATURE) ---
def is_question_worth_logging(question: str) -> bool:
    """
    Kiểm tra xem câu hỏi có đáng lưu vào DB không.
    Trả về True nếu câu hỏi 'sạch', False nếu là rác.
    """
    q = question.strip()
    
    # 1. Lọc độ dài: Quá ngắn (dưới 4 ký tự) hoặc quá dài (trên 200 ký tự spam)
    if len(q) < 4 or len(q) > 200:
        return False
    
    # 2. Lọc ký tự: Chỉ toàn số hoặc ký tự đặc biệt (VD: "12345", "@@@")
    # Regex: Phải có ít nhất 1 ký tự chữ cái
    if not re.search(r'[a-zA-Z]', q):
        return False
        
    # 3. Lọc Spam lặp ký tự (VD: "aaaaaaa", "huhu")
    # Nếu 1 ký tự lặp lại chiếm quá 50% độ dài chuỗi -> Rác
    for char in set(q):
        if q.count(char) > len(q) * 0.5 and len(q) > 5:
            return False
            
    return True

def log_to_db_missing(question, response):
    # BƯỚC 1: LỌC RÁC
    if not is_question_worth_logging(question):
        print(f"[LOG] Bỏ qua câu hỏi rác: {question}")
        return

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            # BƯỚC 2: NẾU ĐÃ CÓ THÌ TĂNG BIẾN ĐẾM (FREQUENCY) THAY VÌ GHI DÒNG MỚI
            # Điều này giúp Admin biết câu nào được hỏi nhiều nhất
            cur.execute("SELECT id, frequency FROM missing_questions WHERE question = ?", (question,))
            row = cur.fetchone()
            
            if row:
                new_freq = row[1] + 1
                cur.execute("UPDATE missing_questions SET frequency = ?, created_at = ? WHERE id = ?", 
                           (new_freq, datetime.datetime.now(), row[0]))
            else:
                cur.execute("INSERT INTO missing_questions (question, bot_response, frequency, created_at) VALUES (?, ?, 1, ?)", 
                            (question, response, datetime.datetime.now()))
            conn.commit()
        print(f"[LOG] Đã ghi nhận câu hỏi lỗi: {question}")
    except Exception as e:
        print(f"[ERR] Lỗi ghi DB Missing: {e}")

def log_to_db_feedback(data):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO feedback (conversation_id, message_id, vote, reason, created_at) VALUES (?, ?, ?, ?, ?)",
                        (data['conversation_id'], data['message_id'], data['vote'], data.get('reason', ''), data['timestamp']))
            conn.commit()
    except Exception as e:
        print(f"[ERR] Lỗi ghi DB Feedback: {e}")

# --- API MODELS & ENDPOINTS ---
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)

class FeedbackRequest(BaseModel):
    conversation_id: str
    message_id: str
    vote: Literal["like", "dislike"]
    reason: Optional[str] = None

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/ask")
def ask(request: ChatRequest, background_tasks: BackgroundTasks):
    try:
        raw_question = request.question
        norm_q = normalize_aiml_pattern(raw_question)
        response = get_cached_response(norm_q)
        
        is_fallback = False
        if not response or FALLBACK_KEYWORD in response:
            is_fallback = True
            background_tasks.add_task(log_to_db_missing, raw_question, response)
            if not response:
                response = "Xin lỗi, tôi chưa hiểu rõ câu hỏi này. Bạn có thể chọn một chủ đề dưới đây không?"

        current_topic = kernel.getPredicate("topic", "user")
        suggestions = []
        topic_config = getattr(conversation_config, 'TOPIC_SUGGESTIONS', {})
        
        if is_fallback:
            suggestions = topic_config.get("DEFAULT", [])
        elif current_topic and current_topic in topic_config:
            suggestions = topic_config[current_topic]
        else:
            suggestions = topic_config.get("DEFAULT", [])

        time.sleep(min(0.8, len(response) * 0.005))

        return {"answer": response, "topic": current_topic, "suggestions": suggestions}
    except Exception as e:
        print(f"SERVER ERROR: {e}")
        raise HTTPException(status_code=500, detail="Internal Error")

@app.post("/api/feedback")
async def receive_feedback(request: FeedbackRequest, background_tasks: BackgroundTasks):
    data = request.dict()
    data["timestamp"] = datetime.datetime.now().isoformat()
    background_tasks.add_task(log_to_db_feedback, data)
    return {"status": "success"}

@app.get("/reload")
def reload():
    normalize_aiml_pattern.cache_clear()
    get_cached_response.cache_clear()
    init_bot(force_reload=True)
    return {"status": "success"}

if __name__ == "__main__":
    PORT = getattr(conversation_config, 'API_PORT', 5000)
    uvicorn.run(app, host="0.0.0.0", port=PORT)