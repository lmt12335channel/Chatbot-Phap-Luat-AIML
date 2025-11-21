import re

# ===========================================================================
# DANH SÁCH ĐỒNG NGHĨA & TỪ KHÓA (Synonyms & Keywords)
# ===========================================================================
# Mỗi danh sách con là một nhóm từ đồng nghĩa.
# Bot sẽ học tất cả các từ này để nhận diện câu hỏi tốt hơn.

SYNONYM_GROUPS = [
    # --- 1. GIAO THÔNG ---
    ["oto", "xe hoi", "xe con", "xe du lich", "xe 4 banh", "xe hop", "xe ban tai", "xe tai", "xe khach", "xe container", "xe dau keo", "xe romooc"],
    ["xe may", "xe gan may", "xe honda", "xe mo to", "xe 2 banh", "xe may dien", "xe dap dien", "mo to 2 banh", "xe tay ga", "xe so", "xe con tay", "xe pkl", "phan khoi lon"],
    ["gplx", "giay phep lai xe", "bang lai", "bang lai xe", "bang a1", "bang a2", "bang b1", "bang b2", "bang c", "bang d", "bang e", "bang fc", "the pet"],
    ["dang ky xe", "ca vet xe", "giay to xe", "giay chung nhan dang ky xe", "cavet", "giay chu quyen xe"],
    ["dang kiem", "kiem dinh", "so dang kiem", "tem dang kiem", "tram dang kiem", "phi bao tri duong bo", "phi duong bo"],
    ["bao hiem xe", "bao hiem trach nhiem dan su", "bao hiem bat buoc", "bao hiem xe may", "bao hiem o to"],
    ["nong do con", "uong ruou bia", "vi pham nong do con", "thoi nong do con", "say ruou", "xin", "co con", "nghi dinh 100", "do con"],
    ["toc do", "qua toc do", "chay nhanh", "ban toc do", "vi pham toc do", "loi toc do", "may ban toc do"],
    ["mu bao hiem", "khong doi mu", "non bao hiem", "khong doi non", "dau tran", "cai quai"],
    ["guong chieu hau", "khong guong", "thieu guong", "guong xe may", "guong o to"],
    ["den tin hieu", "vuot den do", "vuot den vang", "den xanh den do", "khong chap hanh tin hieu den"],
    ["lan duong", "sai lan", "lan tuyen", "di sai lan", "lan lan", "de vach", "chuyen lan khong tin hieu", "xi nhan"],
    ["nguoc chieu", "di nguoc chieu", "duong cam", "di vao duong cam", "duong mot chieu"],
    ["lang lach", "danh vong", "dua xe", "boc dau", "net po", "gay roi trat tu cong cong"],
    ["dung do", "do xe sai quy dinh", "dung xe sai quy dinh", "do xe trai phep", "do xe duoi long duong", "do xe tren via he"],
    ["gay tai nan", "tai nan giao thong", "dam xe", "va cham giao thong", "bo chay sau tai nan"],
    ["phat nguoi", "tra cuu phat nguoi", "camera phat nguoi", "thong bao vi pham", "nop phat qua buu dien"],

    # --- 2. CƯ TRÚ & ĐỊNH DANH ---
    ["cccd", "can cuoc cong dan", "can cuoc", "the can cuoc", "can cuoc gan chip", "cmnd", "chung minh nhan dan", "chung minh thu", "cmt"],
    ["dinh danh dien tu", "vneid", "tai khoan dinh danh", "muc 2", "tich hop giay to", "so dinh danh ca nhan"],
    ["thuong tru", "ho khau", "so ho khau", "dang ky thuong tru", "hktt", "nhap khau", "chuyen khau", "cat khau", "xoa dang ky thuong tru"],
    ["tam tru", "so tam tru", "dang ky tam tru", "kt3", "tam vang", "thong bao luu tru", "gia han tam tru"],
    ["xac nhan cu tru", "giay xac nhan cu tru", "ct07", "ct08", "thong tin cu tru"],

    # --- 3. ĐẤT ĐAI & NHÀ Ở ---
    ["so do", "so hong", "giay chung nhan quyen su dung dat", "gcnqsdd", "quyen so huu nha o", "so do so hong", "giay to dat"],
    ["dat tho cu", "dat o", "odt", "ont", "dat o tai do thi", "dat o tai nong thon"],
    ["dat nong nghiep", "dat trong lua", "dat trong cay lau nam", "dat rung", "dat nuoi trong thuy san"],
    ["dat 50 nam", "dat thuong mai dich vu", "dat du an", "dat nen", "dat xen ket"],
    ["sang ten", "chuyen nhuong", "mua ban dat", "hop dong mua ban nha dat", "tang cho dat", "thua ke dat dai"],
    ["tach thua", "hop thua", "chia dat", "chuyen muc dich su dung", "len tho cu", "xin len tho cu"],
    ["cap lai so do", "cap doi so do", "dinh chinh so do", "mat so do"],
    ["the chap", "vay ngan hang", "the chap so do", "giai chap", "xoa the chap"],
    ["tranh chap dat dai", "tranh chap ranh gioi", "lan chiem dat", "chong lan ranh gioi", "kien tung dat dai", "khoi kien dat dai"],
    ["xay dung trai phep", "xay dung khong phep", "xay dung sai phep", "lan chiem long le duong"],
    ["quy hoach", "dinh quy hoach", "dat quy hoach", "treo quy hoach", "den bu", "giai phong mat bang", "tai dinh cu"],

    # --- 4. HÌNH SỰ & TỆ NẠN ---
    ["trom cap", "an trom", "trom xe", "nhap nha", "moc tui"],
    ["cuop", "cuop giat", "cuop tai san", "tran lot", "cuong doat tai san"],
    ["lua dao", "lua dao chiem doat tai san", "lua tien", "lua dao qua mang", "da cap bien tuong"],
    ["lam dung tin nhiem", "vay tien khong tra", "bung tien", "giat no", "quyt no"],
    ["co y gay thuong tich", "danh nhau", "dam chem", "hanh hung", "giam dinh thuong tat"],
    ["giet nguoi", "giet nguoi cuop cua", "ngo sat"],
    ["hiep dam", "cuong buc", "xam hai tinh duc", "au dam", "quay roi tinh duc"],
    ["xuc pham danh du", "boi nho", "vu khong", "noi xau tren mang", "boc phot"],
    ["danh bac", "ca do", "xoc dia", "lo de", "ca do bong da", "to chuc danh bac"],
    ["ma tuy", "tang tru ma tuy", "buon ban ma tuy", "su dung trai phep chat ma tuy", "hut can", "keo ke", "bay lac"],
    ["mai dam", "mua ban dam", "moi gioi mai dam", "chua mai dam"],
    ["tin dung den", "cho vay nang lai", "boc bat ho", "doi no thue", "khung bo doi no"],
    ["khoi to", "bi can", "bi cao", "tam giam", "tam giu", "cam di khoi noi cu tru", "tai ngoai"],
    ["an treo", "cai tao khong giam giu", "phat tu", "tu chung than", "tu hinh"],
    ["tien an", "tien su", "xoa an tich", "ly lich tu phap"],

    # --- 5. HÔN NHÂN GIA ĐÌNH ---
    ["ket hon", "dang ky ket hon", "hon thu", "giay xac nhan tinh trang hon nhan", "giay doc than", "ket hon voi nguoi nuoc ngoai"],
    ["ly hon", "ly di", "don phuong", "thuan tinh", "toa an giai quyet ly hon"],
    ["gianh quyen nuoi con", "quyen tham con", "cap duong", "tien nuoi con", "tranh chap con chung"],
    ["tai san chung", "tai san rieng", "chia tai san ly hon", "no chung", "no rieng"],
    ["con ngoai gia thu", "nhan cha me con", "xet nghiem adn", "khai sinh cho con", "lam giay khai sinh", "nhan con nuoi"],
    ["bao luc gia dinh", "danh vo", "bao hanh"],

    # --- 6. LAO ĐỘNG ---
    ["hop dong lao dong", "hdld", "thu viec", "chinh thuc", "thoi vu", "part time", "full time"],
    ["luong", "tien luong", "luong co ban", "luong toi thieu vung", "luong thang 13", "thuong tet"],
    ["lam them gio", "tang ca", "ot", "lam dem", "lam ngay le"],
    ["nghi phep", "nghi phep nam", "nghi viec rieng", "nghi om", "nghi khong luong"],
    ["sa thai", "duoi viec", "cham dut hop dong", "don phuong cham dut", "boi thuong hop dong", "mat viec"],
    ["bao hiem xa hoi", "bhxh", "chot so", "gop so", "rut 1 lan", "bao hiem that nghiep", "tro cap that nghiep"],
    ["thai san", "che do thai san", "nghi sinh", "duong suc sau sinh", "kham thai", "trieu san"],

    # --- 7. DOANH NGHIỆP ---
    ["thanh lap cong ty", "mo cong ty", "dkkd", "giay phep kinh doanh", "ho kinh doanh ca the", "cong ty tnhh", "cong ty co phan"],
    ["von dieu le", "gop von", "chuyen nhuong von", "co dong", "thanh vien gop von"],
    ["nguoi dai dien phap luat", "giam doc", "chu tich hoi dong quan tri", "thay doi dang ky kinh doanh"],
    ["tam ngung kinh doanh", "giai the", "pha san", "nop don pha san", "thanh ly tai san"],
    ["con dau", "khac dau", "chu ky so", "token"],
    ["hoa don", "hoa don do", "hoa don gtgt", "hoa don dien tu", "xuat hoa don"],

    # --- 8. THUẾ ---
    ["thue tncn", "thue thu nhap ca nhan", "nguoi phu thuoc", "giam tru gia canh", "hoan thue"],
    ["thue tndn", "thue thu nhap doanh nghiep", "quyet toan thue", "bao cao tai chinh"],
    ["thue mon bai", "le phi mon bai", "thue gtgt", "thue vat", "ke khai thue"],
    ["ma so thue", "mst", "dang ky ma so thue", "tra cuu ma so thue"],

    # --- 9. SỞ HỮU TRÍ TUỆ ---
    ["ban quyen", "tac quyen", "quyen tac gia", "dang ky ban quyen", "vi pham ban quyen"],
    ["nhan hieu", "thuong hieu", "logo", "bao ho thuong hieu", "doc quyen thuong hieu", "hang nhai", "hang gia"],
    ["sang che", "giai phap huu ich", "kieu dang cong nghiep"],

    # --- 10. DÂN SỰ KHÁC ---
    ["thua ke", "di chuc", "lap di chuc", "di san", "thua ke khong di chuc", "hang thua ke"],
    ["hop dong dan su", "hop dong vay tien", "hop dong thue nha", "hop dong dat coc", "vi pham hop dong", "phat coc"],
    ["boi thuong thiet hai", "boi thuong ngoai hop dong"],
    ["toa an", "tand", "so tham", "phuc tham", "giam doc tham", "tai tham", "an phi", "tam ung an phi"],
    ["thi hanh an", "cuc thi hanh an", "cuong che thi hanh an"],
    ["cong chung", "chung thuc", "sao y", "van phong cong chung", "thua phat lai", "lap vi bang"],

    # --- 11. BỔ SUNG (NVQS & BHYT) ---
    ["nvqs", "nghia vu quan su", "di nghia vu", "kham nghia vu", "kham suc khoe", "hoan nghia vu", "tron nghia vu", "loi nghia vu", "xam minh"],
    ["bhyt", "bao hiem y te", "the bao hiem", "kham chua benh", "kham trai tuyen", "chuyen vien", "muc huong", "gia han the", "bhyt ho gia dinh"]
]

# ===========================================================================
# HÀM HỖ TRỢ (UTILS)
# ===========================================================================

def get_legal_whitelist():
    """
    Trả về một danh sách phẳng chứa TẤT CẢ các từ khóa/cụm từ quan trọng.
    Danh sách này đã được chuẩn hóa (lowercase, không dấu, bỏ ký tự lạ).
    """
    whitelist = set()
    for group in SYNONYM_GROUPS:
        for word in group:
            # Chuẩn hóa sơ bộ tại đây để đảm bảo nhất quán với dữ liệu đầu vào
            text = word.lower()
            text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
            text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
            text = re.sub(r'[ìíịỉĩ]', 'i', text)
            text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
            text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
            text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
            text = re.sub(r'đ', 'd', text)
            text = re.sub(r'[^\w\s]', '', text)
            clean_word = re.sub(r'\s+', ' ', text).strip()
            
            if clean_word:
                whitelist.add(clean_word)
            
    return list(whitelist)

def get_synonym_replacement_map():
    """
    (Tùy chọn) Trả về Map để thay thế từ đồng nghĩa về từ chuẩn.
    Ví dụ: 'xe hoi' -> 'OTO', 'xe con' -> 'OTO'
    Hàm này có thể dùng để tiền xử lý câu hỏi user trước khi đưa vào mô hình.
    """
    mapping = {}
    for group in SYNONYM_GROUPS:
        if not group: continue
        representative = group[0].upper() # Lấy từ đầu tiên làm đại diện, viết hoa
        
        for word in group:
            text = word.lower()
            text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
            text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
            text = re.sub(r'[ìíịỉĩ]', 'i', text)
            text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
            text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
            text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
            text = re.sub(r'đ', 'd', text)
            text = re.sub(r'[^\w\s]', '', text)
            clean_key = re.sub(r'\s+', ' ', text).strip()
            
            mapping[clean_key] = representative
    return mapping

# Test nhanh khi chạy trực tiếp file này
if __name__ == "__main__":
    wl = get_legal_whitelist()
    print(f"Tổng số từ khóa whitelist: {len(wl)}")
    print(f"Ví dụ: {wl[:10]}")