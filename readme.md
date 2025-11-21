# **⚖️ TRỢ LÝ ẢO TƯ VẤN PHÁP LUẬT VIỆT NAM (AI-POWERED CHATBOT)**
**Đồ án Tốt nghiệp Kỹ sư Công nghệ thông tin** > Hệ thống Chatbot Hybrid kết hợp AIML truyền thống và Kỹ thuật trích xuất thông tin hiện đại.
## **🌟 Tổng Quan**
Dự án xây dựng một Chatbot thông minh hỗ trợ người dân tra cứu nhanh các quy định pháp luật Việt Nam. Hệ thống sử dụng kiến trúc **Hybrid**, kết hợp khả năng điều hướng hội thoại của **AIML** với khả năng tìm kiếm văn bản chính xác bằng **TF-IDF/Cosine Similarity**.
### **✨ Tính Năng Nổi Bật**
#### **🧠 Xử Lý Thông Minh (Backend)**
1. **Smart Routing:** Tự động phân loại câu hỏi và điều hướng đến các chuyên đề cụ thể (Hôn nhân, Đất đai, Hình sự...).
1. **High Performance:** \* Chuyển đổi từ Flask sang **FastAPI** (Uvicorn) để tăng tốc độ xử lý bất đồng bộ.
   1. Tối ưu hóa xử lý chuỗi (String Processing) nhanh gấp 20 lần so với Regex thông thường.
   1. Cơ chế **Caching (LRU Cache)** giúp trả lời tức thì các câu hỏi lặp lại.
1. **Feedback Loop:** Hệ thống API ghi nhận đánh giá (Like/Dislike) từ người dùng để cải thiện dữ liệu.
1. **Context Awareness:** Ghi nhớ ngữ cảnh hội thoại cơ bản.
#### **💻 Giao Diện Hiện Đại (Frontend)**
1. **Voice-to-Text:** Hỗ trợ nhập liệu bằng giọng nói tiếng Việt.
1. **Dark/Light Mode:** Chế độ giao diện Sáng/Tối bảo vệ mắt.
1. **Responsive Design:** Tương thích hoàn hảo trên PC, Tablet và Mobile.
1. **Markdown Support:** Hiển thị câu trả lời đẹp mắt (in đậm, danh sách, trích dẫn luật).
## **🛠️ Công Nghệ Sử Dụng**

|**Thành phần**|**Công nghệ**|
| :- | :- |
|**Ngôn ngữ**|Python 3.8+, JavaScript (ES6+)|
|**Backend**|**FastAPI**, Uvicorn, Python-AIML|
|**NLP/AI**|Scikit-learn (TF-IDF), Pandas, NumPy|
|**Frontend**|**ReactJS**, Vite, Axios|
|**UI/UX**|CSS Variables (Theming), Lucide React Icons|
## **🚀 Hướng Dẫn Cài Đặt & Chạy**
### **1. Yêu cầu hệ thống**
- Python 3.8 trở lên.
- Node.js (v16+) hoặc Bun.
### **2. Cài đặt Backend (Server)**
Di chuyển vào thư mục chứa mã nguồn backend:

cd backend

Cài đặt các thư viện phụ thuộc:

pip install -r requirements.txt

⚠️ Bước quan trọng: Tạo dữ liệu trí tuệ (Brain Building)

Trước khi chạy server, bạn cần chạy script để "học" dữ liệu từ các file Excel/Parquet và sinh ra file AIML:

\# Chạy script build (đã tối ưu)\
python convert_to_aiml.py

*Sau khi chạy xong, kiểm tra thư mục data đã có file phapluat\_final.aiml chưa.*

**Khởi động Server:**

python main.py

*Server sẽ chạy tại: http://localhost:5000*
### **3. Cài đặt Frontend (Giao diện)**
Mở một terminal mới và di chuyển vào thư mục frontend:

cd frontend

Cài đặt package:

\# Dùng npm\
npm install\
\# Hoặc dùng Bun (nhanh hơn)\
bun install

Khởi chạy ứng dụng:

npm run dev

*Truy cập trình duyệt tại địa chỉ hiển thị (thường là http://localhost:5173)*
## **📂 Cấu Trúc Dự Án**
PROJECT\_ROOT\
├── 📂 data/                   # Chứa dữ liệu huấn luyện\
│   ├── dataset/               # Dữ liệu thô (Parquet/Excel)\
│   ├── phapluat\_final.aiml    # File kiến thức sinh tự động\
│   ├── aiml\_advanced.aiml     # Kịch bản hội thoại\
│   ├── greetings.aiml          # Kịch bản hỏi đáp giao tiếp\
│   ├── manual\_fixes.aiml     # Kịch bản sửa lỗi\
│   └── bot\_brain.brn          # File não binary (tải nhanh)\
│\
├── 📂 backend/                # Mã nguồn Python\
│   ├── app.py                 # FastAPI Server (Entry point)\
│   ├── convert_to_aiml.py     # Script huấn luyện/sinh dữ liệu\
│   └── requirements.txt       # Danh sách thư viện\
│\
├──  📂 scripts/                  # Mã nguồn Python\
│      ├── convert_to_aiml.py     # Script huấn luyện/sinh dữ liệu\
│      ├── legal\_dictionary.py   # Từ điển từ khóa pháp lý\
│      ├── bot\_config.py         # Cấu hình phản hồi\
│\
└── 📂 frontend/               # Mã nguồn ReactJS\
`    `├── src/\
`    `│   ├── App.jsx            # Logic chính\
`    `│   ├── App.css            # Style bố cục\
`    `│   ├── index.css          # Theme (Dark/Light vars)\
`    `│   └── main.jsx           # Render root\
`    `└── package.json
## **🔌 API Documentation**
Backend cung cấp các API chính sau:

|**Method**|**Endpoint**|**Mô tả**|
| :- | :- | :- |
|GET|/|Health check (Kiểm tra server sống).|
|POST|/ask|Gửi câu hỏi. Body: { "question": "..." }|
|POST|/api/feedback|Gửi đánh giá. Body: { "message\_id": "...", "vote": "like" }|
|GET|/reload|Nạp lại dữ liệu AIML mà không cần tắt server.|
## **🔧 Ghi chú Quản trị**
- **Log câu hỏi lỗi:** Kiểm tra file data/missing\_questions\_log.txt để xem những câu hỏi mà Bot chưa trả lời được, từ đó bổ sung dữ liệu.
- **Log Feedback:** Kiểm tra file feedback\_log.json để xem người dùng đánh giá chất lượng câu trả lời thế nào.
