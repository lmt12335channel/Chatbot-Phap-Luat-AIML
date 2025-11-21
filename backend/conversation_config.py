# ==============================================================================
# FILE CẤU HÌNH HỆ THỐNG CHATBOT
# ==============================================================================

# 1. CẤU HÌNH SERVER
API_PORT = 5000
ALLOW_ORIGINS = ["*"]

# 2. CẤU HÌNH GỢI Ý (SUGGESTION CHIPS)
# LƯU Ý: Đây là dữ liệu mẫu. Hãy chạy "python generate_suggestions.py" 
# để cập nhật dữ liệu thật từ file dataset của bạn.

TOPIC_SUGGESTIONS = {
    "HONNHAN": [
        "Thủ tục ly hôn thuận tình",
        "Hồ sơ đăng ký kết hôn cần gì",
        "Quyền nuôi con khi ly hôn",
        "Chia tài sản chung vợ chồng"
    ],
    "DATDAI": [
        "Thủ tục sang tên sổ đỏ",
        "Phí cấp mới sổ đỏ là bao nhiêu",
        "Giải quyết tranh chấp đất đai",
        "Điều kiện tách thửa đất thổ cư"
    ],
    "GIAOTHONG": [
        "Mức phạt nồng độ cồn xe máy",
        "Vượt đèn đỏ phạt bao nhiêu tiền",
        "Thủ tục cấp lại bằng lái xe",
        "Lỗi đi sai làn đường ô tô"
    ],
    "CUTRU": [
        "Thủ tục làm căn cước công dân",
        "Cách đăng ký tài khoản định danh VNeID",
        "Thủ tục đăng ký thường trú",
        "Xin giấy xác nhận cư trú ở đâu"
    ],
    "HINHSU": [
        "Mức phạt tội trộm cắp tài sản",
        "Đánh bạc bao nhiêu tiền thì bị bắt",
        "Tội cố ý gây thương tích",
        "Tàng trữ trái phép chất ma túy"
    ],
    "QUANSU": [
        "Độ tuổi đi nghĩa vụ quân sự",
        "Các trường hợp được tạm hoãn nghĩa vụ",
        "Khám sức khỏe nghĩa vụ quân sự",
        "Cận thị có phải đi bộ đội không"
    ],
    "DOANHNGHIEP": [
        "Hồ sơ thành lập công ty TNHH",
        "Thủ tục giải thể doanh nghiệp",
        "Đăng ký hộ kinh doanh cá thể",
        "Vốn điều lệ tối thiểu là bao nhiêu"
    ],
    "LAODONG": [
        "Điều kiện hưởng bảo hiểm thất nghiệp",
        "Cách tính tiền bảo hiểm xã hội 1 lần",
        "Chế độ thai sản mới nhất",
        "Quy định về chấm dứt hợp đồng lao động"
    ],
    "THUE": [
        "Cách tính thuế thu nhập cá nhân",
        "Quyết toán thuế cuối năm",
        "Thủ tục đăng ký mã số thuế",
        "Lệ phí trước bạ nhà đất"
    ],
    "HANHCHINH": [
        "Thủ tục chứng thực sao y bản chính",
        "Đăng ký khai sinh cho con",
        "Thủ tục khiếu nại quyết định hành chính",
        "Xử phạt vi phạm hành chính"
    ],
    "DEFAULT": [
        "Tra cứu luật Giao thông",
        "Tư vấn Hôn nhân gia đình",
        "Thủ tục Đất đai nhà ở",
        "Chế độ Bảo hiểm xã hội"
    ]
}