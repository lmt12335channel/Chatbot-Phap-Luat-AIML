# ==============================================================================
# CẤU HÌNH HỘI THOẠI & ROUTING
# ==============================================================================

# 1. CẤU HÌNH CÂU DẪN (Mở đầu) - Tạo sự tự nhiên
PREFIXES = [
    "Theo quy định hiện hành:",
    "Về vấn đề này, pháp luật quy định như sau:",
    "Dựa trên cơ sở dữ liệu văn bản luật:",
    "Thông tin pháp lý bạn cần tìm là:",
    "Xin gửi đến bạn nội dung trích dẫn:",
    "Căn cứ vào các văn bản pháp luật liên quan:"
]

# 2. CẤU HÌNH CÂU KẾT (Gợi ý) - Kêu gọi hành động tiếp theo
SUFFIXES = [
    "Bạn có cần giải thích rõ hơn về điều khoản này không?",
    "Nếu cần hỗ trợ chủ đề khác, hãy gõ 'Menu' nhé.",
    "Hy vọng thông tin này giúp ích cho bạn.",
    "Bạn còn thắc mắc nào khác về vấn đề này không?",
    "Hãy cho tôi biết nếu bạn cần thêm thông tin chi tiết.",
    "Lưu ý: Thông tin trên chỉ mang tính chất tham khảo."
]

# 3. CẤU HÌNH SMART ROUTING (Bẻ ghi chủ đề)
# Khi câu hỏi chứa từ khóa (key), Bot sẽ chuyển hướng (srai) sang chủ đề (value)
# Value ở đây thường là các pattern tổng quát đã định nghĩa trong file AIML
SMART_ROUTING_MAP = {
    # --- GIAO TIẾP CƠ BẢN ---
    "chao ban": "GREETINGS",
    "xin chao": "GREETINGS",
    "hello": "GREETINGS",
    "hi": "GREETINGS",
    "tam biet": "GOODBYE",
    "hen gap lai": "GOODBYE",
    "tu van phap luat": "LEGAL_HELP",
    "tro giup": "HELP",

    # --- HÔN NHÂN ---
    "ly hon": "KICH HOAT HON NHAN",
    "ket hon": "KICH HOAT HON NHAN",
    "nuoi con": "KICH HOAT HON NHAN",
    "tai san chung": "KICH HOAT HON NHAN",
    "don phuong": "KICH HOAT HON NHAN",
    "thuan tinh": "KICH HOAT HON NHAN",
    
    # --- ĐẤT ĐAI ---
    "so do": "KICH HOAT DAT DAI",
    "sang ten": "KICH HOAT DAT DAI",
    "tranh chap dat": "KICH HOAT DAT DAI",
    "tach thua": "KICH HOAT DAT DAI",
    "cap moi": "KICH HOAT DAT DAI",
    
    # --- GIAO THÔNG ---
    "nong do con": "KICH HOAT GIAO THONG",
    "vuot den do": "KICH HOAT GIAO THONG",
    "muc phat": "KICH HOAT GIAO THONG",
    "toc do": "KICH HOAT GIAO THONG",
    "giay phep lai xe": "KICH HOAT GIAO THONG",
    "bang lai": "KICH HOAT GIAO THONG",
    
    # --- CƯ TRÚ ---
    "cccd": "KICH HOAT CU TRU",
    "can cuoc": "KICH HOAT CU TRU",
    "vneid": "KICH HOAT CU TRU",
    "dinh danh dien tu": "KICH HOAT CU TRU",
    "ho khau": "KICH HOAT CU TRU",
    "tam tru": "KICH HOAT CU TRU",
    
    # --- QUÂN SỰ ---
    "nghia vu quan su": "KICH HOAT QUAN SU",
    "nvqs": "KICH HOAT QUAN SU",
    "kham suc khoe": "KICH HOAT QUAN SU",
    "nhap ngu": "KICH HOAT QUAN SU",
    "tam hoan": "KICH HOAT QUAN SU",
    
    # --- HÌNH SỰ ---
    "hinh su": "KICH HOAT HINH SU",
    "trom cap": "KICH HOAT HINH SU",
    "danh bac": "KICH HOAT HINH SU",
    "ma tuy": "KICH HOAT HINH SU",
    "thuong tich": "KICH HOAT HINH SU",
    "danh nguoi": "KICH HOAT HINH SU",
    
    # --- DOANH NGHIỆP ---
    "thanh lap cong ty": "KICH HOAT DOANH NGHIEP",
    "ho kinh doanh": "KICH HOAT DOANH NGHIEP",
    "giai the": "KICH HOAT DOANH NGHIEP",
    "mo cong ty": "KICH HOAT DOANH NGHIEP",
    
    # --- LAO ĐỘNG ---
    "bao hiem xa hoi": "KICH HOAT LAO DONG",
    "bhxh": "KICH HOAT LAO DONG",
    "that nghiep": "KICH HOAT LAO DONG",
    "thai san": "KICH HOAT LAO DONG",
    "hop dong lao dong": "KICH HOAT LAO DONG",
    "luong toi thieu": "KICH HOAT LAO DONG"
}

# --- HÀM TẠO TEMPLATE XML ---
def create_conversational_template(raw_answer):
    """
    Hàm này nhận vào câu trả lời thô, trả về XML template có random prefix/suffix
    để câu trả lời của Bot không bị nhàm chán.
    """
    # Tạo danh sách các thẻ <li> cho AIML xử lý random
    prefix_block = "\n        ".join([f"<li>{p}</li>" for p in PREFIXES])
    suffix_block = "\n        ".join([f"<li>{s}</li>" for s in SUFFIXES])
    
    # Cấu trúc AIML: <random> chọn 1 trong các <li>
    template = f"""
    <random>
        {prefix_block}
    </random>
    <br/><br/>
    {raw_answer}
    <br/><br/>
    <random>
        {suffix_block}
    </random>
    """
    return template