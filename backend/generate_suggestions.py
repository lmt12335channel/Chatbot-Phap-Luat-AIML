import pandas as pd
import re
import json
import os
import glob
import random
from collections import Counter

# --- CẤU HÌNH ---
INPUT_DATA_PATH = '../data/dataset' 

# --- BỘ TỪ KHÓA MỞ RỘNG (RICH KEYWORDS) ---
# Đây là bộ lọc để phân loại câu hỏi vào các nhóm chủ đề
TOPIC_KEYWORDS = {
    "HONNHAN": [
        "ly hôn", "li hôn", "ly dị", "li dị", "kết hôn", "hôn nhân", 
        "tài sản chung", "tài sản riêng", "chia tài sản", 
        "nuôi con", "quyền nuôi con", "cấp dưỡng", "trợ cấp nuôi con",
        "đăng ký kết hôn", "hủy hôn", "chung sống như vợ chồng",
        "bạo lực gia đình", "người thứ ba", "ngoại tình", 
        "con riêng", "con chung", "tranh chấp nuôi con", "thừa kế", 
        "di chúc", "tước quyền nuôi con", "ly thân"
    ],
    "DATDAI": [
        "sổ đỏ", "sổ hồng", "giấy chứng nhận", "quyền sử dụng đất",
        "chuyển nhượng đất", "sang tên", "tách thửa", "hợp thửa",
        "mua bán đất", "giá đất", "thổ cư", "đất ao", "đất vườn",
        "chuyển mục đích", "đền bù", "giải tỏa", "quy hoạch",
        "tranh chấp đất", "lấn chiếm đất", "tặng cho đất",
        "đất dự án", "đất nông nghiệp", "đất phi nông nghiệp",
        "đất ở", "sổ đỏ giả", "xây dựng không phép"
    ],
    "GIAOTHONG": [
        "giao thông", "vi phạm giao thông", "xử phạt", "phạt nguội",
        "bằng lái", "gplx", "giấy phép lái xe", 
        "xe máy", "ô tô", "đăng kiểm", "tem đăng kiểm",
        "biển số", "biển kiểm soát", 
        "nồng độ cồn", "thổi nồng độ cồn", 
        "tước bằng", "tước giấy phép", 
        "vượt đèn đỏ", "đi sai làn", "dừng đỗ sai quy định",
        "tai nạn giao thông"
    ],
    "CUTRU": [
        "cư trú", "tạm trú", "thường trú", "hộ khẩu", 
        "cắt khẩu", "nhập khẩu", "tạm vắng",
        "cccd", "căn cước", "căn cước công dân", 
        "cmnd", "chứng minh nhân dân",
        "vneid", "định danh điện tử",
        "đổi cccd", "mất cccd", "làm lại căn cước"
    ],
    "HINHSU": [
        "hình sự", "tội phạm", "truy tố", "khởi tố", 
        "bị can", "bị cáo", "tạm giam", 
        "án treo", "án tù", "phạt tù", 
        "trộm cắp", "cướp", "giết người", "hiếp dâm",
        "đánh bạc", "tổ chức đánh bạc", 
        "ma túy", "sử dụng ma túy", "mua bán ma túy",
        "lừa đảo", "chiếm đoạt", "gây thương tích", 
        "bạo hành", "cưỡng đoạt",
        "quấy rối", "làm nhục người khác"
    ],
    "QUANSU": [
        "nghĩa vụ quân sự", "nghĩa vụ", "nhập ngũ", 
        "tạm hoãn", "miễn nghĩa vụ", "đi bộ đội", 
        "dân quân tự vệ", "khám sức khỏe", "xuất ngũ",
        "trốn nghĩa vụ", "bị gọi nhập ngũ"
    ],
    "DOANHNGHIEP": [
        "doanh nghiệp", "công ty", "hộ kinh doanh", 
        "đăng ký kinh doanh", "giấy phép kinh doanh",
        "thành lập công ty", "giải thể", "phá sản",
        "cổ phần", "vốn điều lệ", "góp vốn",
        "tnhh", "công ty tnhh", "công ty cổ phần",
        "hóa đơn điện tử", "taxcode", "mã số thuế doanh nghiệp"
    ],
    "LAODONG": [
        "lao động", "hợp đồng lao động", "thử việc",
        "sa thải", "thôi việc", "chấm dứt hợp đồng",
        "tranh chấp lao động", "bảo hiểm xã hội", "bhxh",
        "bảo hiểm y tế", "bhyt", 
        "thai sản", "nghỉ thai sản",
        "ốm đau", "hưu trí", "tăng ca", "làm thêm giờ",
        "lương", "lương cơ bản", "bảng lương",
        "thất nghiệp"
    ],
    "THUE": [
        "thuế", "thuế tncn", "thu nhập cá nhân", 
        "thuế tndn", "thuế doanh nghiệp", 
        "kê khai thuế", "nộp thuế", "hoàn thuế", 
        "hóa đơn", "hóa đơn điện tử", 
        "lệ phí trước bạ", "mã số thuế", "mst cá nhân"
    ],
    "HANHCHINH": [
        "hành chính", "xử phạt hành chính", 
        "khiếu nại", "tố cáo", 
        "công chứng", "chứng thực",
        "ủy ban", "ủy ban nhân dân", 
        "giấy khai sinh", "trích lục", "hộ tịch", 
        "giấy tờ tùy thân", "mất giấy tờ", 
        "xin cấp lại", "thủ tục hành chính"
    ],
    "DANSU": [
    "dân sự", "hợp đồng", "bồi thường", "thiệt hại",
    "tranh chấp hợp đồng", "ủy quyền", "vay tiền", "nợ", 
    "đòi nợ", "lãi suất", "quyền dân sự"
    ]
    "CONGNGHE": [
        "lừa đảo online", "scam", "hack", "an ninh mạng",
        "lộ thông tin", "đánh cắp dữ liệu", 
        "facebook bị hack", "mất tài khoản", "lừa đảo qua mạng"
    ]

}

def clean_text(text):
    """Làm sạch văn bản cơ bản"""
    text = str(text).strip()
    # Xóa các ký tự rác đầu câu (gạch đầu dòng, số thứ tự)
    text = re.sub(r'^[-•*+\d\.]+\s*', '', text)
    return text

def classify_question(question):
    """Phân loại câu hỏi vào chủ đề dựa trên từ khóa"""
    q_lower = question.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in q_lower:
                return topic
    return "DEFAULT"

def analyze_unclassified(questions):
    """Phân tích các câu chưa phân loại để tìm từ khóa mới"""
    print("\n--- 🔍 PHÂN TÍCH DỮ LIỆU CHƯA PHÂN LOẠI (DEFAULT) ---")
    print("Các từ khóa xuất hiện nhiều nhất trong nhóm DEFAULT (Gợi ý để bạn thêm vào TOPIC_KEYWORDS):")
    
    all_words = []
    for q in questions:
        # Tách từ đơn giản
        words = re.findall(r'\w+', q.lower())
        # Lọc từ quá ngắn (như: là, và, có...)
        words = [w for w in words if len(w) > 3] 
        all_words.extend(words)
    
    counter = Counter(all_words)
    top_20 = counter.most_common(20)
    
    for word, count in top_20:
        print(f"   - {word}: {count} lần")
    print("-" * 60)

def load_data_optimized(path):
    print(f"-> Đang kiểm tra đường dẫn: {path}")
    try:
        if os.path.isdir(path):
            files = glob.glob(os.path.join(path, "*.parquet"))
            if not files: files = glob.glob(os.path.join(path, "**/*.parquet"), recursive=True)
            
            if not files:
                print("⚠️ Không tìm thấy file .parquet nào.")
                return pd.DataFrame()
                
            print(f"-> Phát hiện {len(files)} file Parquet. Đang đọc...")
            df_list = []
            for f in files:
                try:
                    # Chỉ đọc cột question để tiết kiệm RAM tối đa
                    df_part = pd.read_parquet(f, columns=['question'])
                    df_list.append(df_part)
                except: pass
            
            return pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()

        elif os.path.isfile(path):
            if path.endswith('.parquet'): return pd.read_parquet(path, columns=['question'])
            elif path.endswith('.xlsx'): return pd.read_excel(path, usecols=['question'])
            elif path.endswith('.csv'): return pd.read_csv(path, usecols=['question'])
        
        return pd.DataFrame()

    except Exception as e:
        print(f"❌ Lỗi đọc dữ liệu: {e}")
        return pd.DataFrame()

def main():
    print("="*60)
    print("   TOOL TẠO GỢI Ý TỰ ĐỘNG (PHIÊN BẢN THÔNG MINH)")
    print("="*60)
    
    df = load_data_optimized(INPUT_DATA_PATH)
    
    if df.empty:
        print("❌ Không đọc được dữ liệu!")
        return

    total_rows = len(df)
    print(f"✅ Đã tải: {total_rows:,} câu hỏi.")
    
    # Nếu dữ liệu quá lớn, lấy mẫu để xử lý nhanh
    if total_rows > 100000:
        print("-> Dữ liệu lớn, lấy mẫu ngẫu nhiên 100,000 dòng để phân tích...")
        df = df.sample(n=100000, random_state=42)

    suggestions_map = {k: [] for k in TOPIC_KEYWORDS.keys()}
    suggestions_map["DEFAULT"] = []
    
    # Danh sách tạm để chứa các câu Default phục vụ phân tích
    default_questions_for_analysis = []

    count = 0
    for _, row in df.iterrows():
        question = clean_text(row.get('question', ''))
        
        # Lọc câu có độ dài đẹp (để hiển thị lên chip)
        if 20 < len(question) < 65:
            if not re.search('[a-zA-Z]', question): continue
            
            topic = classify_question(question)
            
            # Lưu lại câu Default để phân tích sau
            if topic == "DEFAULT":
                default_questions_for_analysis.append(question)

            # Thêm vào danh sách gợi ý (chỉ cần khoảng 20 câu mỗi loại để random)
            if len(suggestions_map[topic]) < 20:
                formatted_q = question[0].upper() + question[1:].rstrip('?.')
                if formatted_q not in suggestions_map[topic]:
                    suggestions_map[topic].append(formatted_q)
    
    # --- PHÂN TÍCH DỮ LIỆU CÒN SÓT ---
    if len(default_questions_for_analysis) > 0:
        # Phân tích mẫu 5000 câu default để tìm từ khóa mới
        analyze_sample = default_questions_for_analysis[:5000]
        analyze_unclassified(analyze_sample)

    # --- XUẤT KẾT QUẢ ---
    print("\n" + "="*60)
    print("👇 COPY TOÀN BỘ ĐOẠN DƯỚI ĐÂY VÀO FILE: conversation_config.py 👇")
    print("="*60 + "\n")
    
    print("TOPIC_SUGGESTIONS = {")
    for topic, questions in suggestions_map.items():
        if not questions:
            # Fallback nếu không tìm thấy
            kw = TOPIC_KEYWORDS.get(topic, ["pháp luật"])[0]
            questions = [f"Quy định về {kw}", f"Luật {kw} mới nhất", f"Tư vấn {kw}", f"Thủ tục liên quan {kw}"]
        
        selected_questions = questions[:4]
        if len(questions) > 4:
            selected_questions = random.sample(questions, 4)

        print(f'    "{topic}": [')
        for q in selected_questions:
            print(f'        "{q}",')
        print('    ],')
    print("}")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()