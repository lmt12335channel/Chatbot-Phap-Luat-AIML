import pandas as pd
import re
import numpy as np
from tqdm import tqdm
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
import legal_dictionary
import bot_config
import sys

# --- CẤU HÌNH ---
INPUT_DATA_DIRECTORY = '../data/dataset'
STOPWORD_FILE = '../data/vietnamese_stopwords.txt'
PROCESSED_QA_FILE = '../data/intermediate_qa_ULTIMATE.parquet'
FINAL_AIML_FILE = '../data/phapluat_final.aiml'
# Số lượng dòng để test (Để None nếu muốn chạy hết 460k dòng)
# Khuyến nghị: Test 10.000 - 20.000 dòng trước
NUM_ROWS_TO_TEST = 20000 

# --- TỐI ƯU HÓA CHUỖI (Siêu tốc độ) ---
# Bảng dịch mã ASCII để bỏ dấu tiếng Việt nhanh gấp 20 lần Regex
TRANS_CHARS = {
    'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a', 'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a', 'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'đ': 'd', 'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e', 'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i', 'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o', 'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o', 'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u', 'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u', 'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y'
}
TRANS_TABLE = str.maketrans(TRANS_CHARS)
RE_CLEAN = re.compile(r'[^a-z0-9\s]') # Chỉ giữ chữ cái và số
RE_SPACE = re.compile(r'\s+') # Gộp khoảng trắng

# --- UTILS ---
def load_stopwords(filepath):
    stopwords = set()
    try:
        path = Path(filepath)
        if path.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip(): stopwords.add(line.strip())
    except: pass
    return stopwords

VIETNAMESE_STOPWORDS = load_stopwords(STOPWORD_FILE)

def normalize_text(text: str) -> str:
    if not isinstance(text, str): return ""
    # 1. Chuyển thường
    s = text.lower()
    # 2. Bỏ dấu (Siêu tốc)
    s = s.translate(TRANS_TABLE)
    # 3. Xóa ký tự lạ
    s = RE_CLEAN.sub(' ', s)
    # 4. Gộp khoảng trắng
    return RE_SPACE.sub(' ', s).strip()

def normalize_aiml_pattern(text: str) -> str:
    return normalize_text(text).upper()

def clean_xml_invalid_chars(text: str) -> str:
    if not isinstance(text, str): return ""
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Xóa các ký tự điều khiển rác
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text).strip()

def split_into_sentences(text: str) -> list:
    if not isinstance(text, str): return []
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\n)\s', text)
    return [s.strip() for s in sentences if s.strip() and len(s.split()) > 2]

# --- LOGIC TÌM CÂU TRẢ LỜI ---
def format_answer_with_citation(answer_text):
    match = re.search(r'(điều \d+|khoản \d+)', answer_text, re.IGNORECASE)
    if match:
        citation = match.group(0).title()
        if not answer_text.lower().startswith(citation.lower()):
            return f"Theo {citation}: {answer_text}"
    return answer_text

def find_best_answer_ultimate(row):
    question = row.get('question', '')
    context_list = row.get('context', [])
    
    if not isinstance(question, str) or not question.strip(): return ""
    if context_list is None: return ""
    # Xử lý Numpy Array an toàn
    if isinstance(context_list, np.ndarray): context_list = context_list.tolist()
    if not context_list: return ""

    valid_contexts = [str(c) for c in context_list if str(c).strip()]
    if not valid_contexts: return ""
    
    full_text = ' '.join(valid_contexts)
    sentences = split_into_sentences(full_text)
    if not sentences: return ""
    
    try:
        # Tối ưu Vectorizer: Tắt IDF để chạy nhanh hơn (chỉ cần so khớp từ)
        vectorizer = TfidfVectorizer(norm='l2', use_idf=False, smooth_idf=False, sublinear_tf=False, preprocessor=normalize_text)
        tfidf_matrix = vectorizer.fit_transform([question] + sentences)
        
        # Tính Cosine Similarity
        cosine_sims = (tfidf_matrix[0:1] * tfidf_matrix[1:].T).toarray()[0]
        
        # Lấy câu tốt nhất
        sorted_indices = np.argsort(cosine_sims)[::-1]
        best_sentence = ""
        
        for idx in sorted_indices:
            candidate = sentences[idx]
            # Lọc câu quá ngắn (tiêu đề rác)
            if len(candidate.split()) >= 6:
                best_sentence = candidate
                break
        
        if not best_sentence and len(sorted_indices) > 0:
            best_sentence = sentences[sorted_indices[0]]

        if best_sentence: return format_answer_with_citation(best_sentence)
        return ""
    except: return ""

# --- TẠO PATTERN TỪ KHÓA ---
def extract_keywords_optimized(question, vectorizer, feature_names, top_n=4):
    try:
        response = vectorizer.transform([question])
        sorted_items = sorted(zip(response.tocoo().col, response.tocoo().data), key=lambda x: (x[1], x[0]), reverse=True)
        keywords = []
        
        # Lọc Stopwords (đã chuẩn hóa từ trước)
        # Lưu ý: Vectorizer đã được train với vocab sạch nên ở đây ko cần check lại stopword nữa
        for idx, score in sorted_items[:top_n]:
            word = feature_names[idx]
            if len(word) > 2: # Bỏ từ quá ngắn
                keywords.append(word.upper())
        
        if not keywords: return None
        
        # Sắp xếp lại theo thứ tự xuất hiện trong câu hỏi
        normalized_q = normalize_text(question)
        keyword_positions = []
        for kw in keywords:
            pos = normalized_q.find(kw.lower())
            if pos != -1: keyword_positions.append((pos, kw))
        keyword_positions.sort(key=lambda x: x[0])
        ordered_keywords = [k[1] for k in keyword_positions]
        
        if len(ordered_keywords) < 2: return None
        return "* " + " * ".join(ordered_keywords) + " *"
    except: return None

def check_smart_routing(question_normalized):
    for key, srai_target in bot_config.SMART_ROUTING_MAP.items():
        if key in question_normalized:
            if "dieu " in question_normalized or "khoan " in question_normalized or "luat so" in question_normalized:
                continue 
            return srai_target
    return None

# --- MAIN ---
def main():
    print(f"[AIML BUILDER] Starting High Performance Process (Windows)...")
    
    # 1. ĐỌC DỮ LIỆU (Dùng engine pyarrow nếu có)
    processed_qa_path = Path(PROCESSED_QA_FILE)
    if processed_qa_path.exists():
        print(f"-> Load cache: {PROCESSED_QA_FILE}")
        try:
            df = pd.read_parquet(processed_qa_path, engine='pyarrow')
        except:
             df = pd.read_parquet(processed_qa_path) # Fallback default engine
    else:
        print(f"-> Reading raw dataset...")
        try:
            try:
                df_full = pd.read_parquet(INPUT_DATA_DIRECTORY, engine='pyarrow')
            except:
                df_full = pd.read_parquet(INPUT_DATA_DIRECTORY)
        except Exception as e:
            print(f"[ERROR] Không đọc được dataset: {e}")
            return

        if NUM_ROWS_TO_TEST:
            print(f"-> [TEST MODE] Sampling {NUM_ROWS_TO_TEST} rows.")
            df = df_full.head(NUM_ROWS_TO_TEST).copy()
        else:
            df = df_full.copy()
            
        print("-> Extracting Answers...")
        tqdm.pandas()
        df['answer'] = df.progress_apply(find_best_answer_ultimate, axis=1)
        df = df[df['answer'] != ''][['question', 'answer']]
        # Lưu cache để lần sau chạy nhanh hơn
        # Tạo thư mục cha nếu chưa tồn tại
        processed_qa_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(processed_qa_path)

    # 2. GOM NHÓM DỮ LIỆU
    grouped = df.groupby('answer')['question'].apply(list).reset_index()

    # 3. HUẤN LUYỆN VECTORIZER (Để tìm từ khóa)
    print("-> Training Keyword Vectorizer...")
    legal_vocab = legal_dictionary.get_legal_whitelist()
    flat_vocab = set()
    
    # Chuẩn hóa stopwords 1 lần duy nhất
    norm_stopwords = set(normalize_text(w) for w in VIETNAMESE_STOPWORDS)
    
    for term in legal_vocab:
        for w in term.split():
            w_norm = normalize_text(w)
            if len(w) > 1 and w_norm not in norm_stopwords: 
                flat_vocab.add(w)
    
    keyword_vectorizer = TfidfVectorizer(preprocessor=normalize_text, vocabulary=list(flat_vocab), use_idf=True)
    all_q = [q for sublist in grouped['question'] for q in sublist]
    
    if all_q: keyword_vectorizer.fit(all_q)
    feature_names = keyword_vectorizer.get_feature_names_out()
    
    # 4. GHI FILE AIML (Buffer Write)
    print(f"-> Generating {FINAL_AIML_FILE}...")
    
    # Đảm bảo thư mục output tồn tại
    Path(FINAL_AIML_FILE).parent.mkdir(parents=True, exist_ok=True)

    # Dùng buffer 1MB để ghi file nhanh hơn
    with open(FINAL_AIML_FILE, "w", encoding="utf-8", buffering=1024*1024) as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<aiml version="1.0">\n\n')
        
        routed_cnt = 0
        normal_cnt = 0

        for index, row in tqdm(grouped.iterrows(), total=len(grouped)):
            raw_answer = clean_xml_invalid_chars(row['answer'])
            questions = row['question']
            if not questions: continue
            
            canonical_q = min(questions, key=len)
            canonical_pat = normalize_aiml_pattern(canonical_q)
            if not canonical_pat: continue

            # Smart Routing
            routing_target = check_smart_routing(normalize_text(canonical_q))
            
            final_template = ""
            if routing_target:
                final_template = f'<srai>{routing_target}</srai>'
                routed_cnt += 1
            else:
                # Soft-touch template
                final_template = bot_config.create_conversational_template(raw_answer)
                normal_cnt += 1
            
            # Write Pattern Chính
            # Viết gọn trên 1 dòng để file nhẹ hơn
            f.write(f'<category><pattern>{canonical_pat}</pattern><template>{final_template}</template></category>\n')
            
            # Write Keyword Pattern
            if not routing_target:
                kw_pattern = extract_keywords_optimized(canonical_q, keyword_vectorizer, feature_names, top_n=4)
                if kw_pattern and kw_pattern != f"* {canonical_pat} *":
                    f.write(f'<category><pattern>{kw_pattern}</pattern><template><srai>{canonical_pat}</srai></template></category>\n')

            # Write Variants (Tối đa 2)
            for q in questions[:2]:
                pat = normalize_aiml_pattern(q)
                if pat and pat != canonical_pat:
                    f.write(f'<category><pattern>{pat}</pattern><template><srai>{canonical_pat}</srai></template></category>\n')
                    f.write(f'<category><pattern>* {pat} *</pattern><template><srai>{canonical_pat}</srai></template></category>\n')

        f.write('</aiml>')
    
    print(f"\n[SUCCESS] File generated successfully!")
    print(f"- Total Q&A: {len(grouped)}")
    print(f"- Smart Routed: {routed_cnt}")
    print(f"- Static Q&A: {normal_cnt}")

if __name__ == '__main__':
    main()