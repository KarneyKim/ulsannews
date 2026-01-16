import streamlit as st
import google.generativeai as genai
from datetime import datetime

# 1. API 설정 및 AI 모델 초기화
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 페이지 설정
st.set_page_config(page_title="AI 학교 신문 작성기", layout="wide")

# 스타일링 (CSS)
st.markdown("""
    <style>
    .news-box {
        background-color: white;
        padding: 40px;
        border: 1px solid #ddd;
        font-family: 'Malgun Gothic', sans-serif;
        color: #333;
    }
    .news-title {
        font-size: 32px;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 15px;
        border-bottom: 2px solid #000;
        padding-bottom: 10px;
    }
    .news-meta {
        display: flex;
        justify-content: space-between;
        font-size: 14px;
        color: #666;
        margin-bottom: 20px;
    }
    .news-content {
        font-size: 18px;
        line-height: 1.8;
        text-align: justify;
    }
    .news-content:first-letter {
        font-size: 50px;
        font-weight: bold;
        float: left;
        margin-right: 8px;
        line-height: 1;
    }
    .interview-box {
        background-color: #f9f9f9;
        border-left: 5px solid #333;
        padding: 15px;
        margin-top: 25px;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📰 AI 학교 신문 기사 제작소")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("기사 정보 입력")
    author = st.text_input("작성 기자", placeholder="이름을 입력하세요")
    date = st.date_input("발행 날짜", datetime.now())
    
    uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"])
    
    event_memo = st.text_area("사건 메모 (AI가 다듬어줍니다)", 
                             placeholder="누가, 언제, 어디서 무엇을 했는지 핵심만 적어주세요.", height=150)
    
    interview_memo = st.text_area("인터뷰 메모", placeholder="인터뷰 대상과 내용을 입력하세요.")

    if st.button("✨ AI 기사 완성하기"):
        if not event_memo:
            st.error("기사 메모를 입력해야 AI가 작성할 수 있습니다.")
        else:
            with st.spinner("AI가 실제 기사 양식으로 문장을 다듬고 있습니다..."):
                prompt = f"""
                다음 메모를 바탕으로 실제 뉴스 기사를 작성해줘.
                내용: {event_memo}
                인터뷰: {interview_memo}
                
                [지침]
                1. 첫 문장은 반드시 육하원칙이 포함된 리드문으로 작성할 것.
                2. 전체 문장은 최소 10문장 이상의 전문적인 기사체(~다.)로 작성할 것.
                3. 출력은 반드시 다음 형식을 지킬 것:
                제목: [기사제목]
                본문: [기사본문]
                인터뷰: [다듬어진 인터뷰]
                """
                
                response = model.generate_content(prompt)
                full_text = response.text
                
                # 데이터 파싱
                try:
                    st.session_state.title = full_text.split("제목:")[1].split("본문:")[0].strip()
                    st.session_state.body = full_text.split("본문:")[1].split("인터뷰:")[0].strip()
                    st.session_state.interview = full_text.split("인터뷰:")[1].strip()
                except:
                    st.error("AI 응답 형식이 올바르지 않습니다. 다시 시도해 주세요.")

with col2:
    st.subheader("신문 미리보기")
    
    if 'title' in st.session_state:
        st.markdown(f"""
            <div class="news-box">
                <div style="text-align:center; font-weight:bold; letter-spacing:5px;">THE SCHOOL TIMES</div>
                <hr>
                <div class="news-title">{st.session_state.title}</div>
                <div class="news-meta">
                    <span>{date.strftime('%Y-%m-%d')}</span>
                    <span><b>{author}</b> 기자</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)
            
        st.markdown(f"""
            <div class="news-box">
                <div class="news-content">{st.session_state.body}</div>
                <div class="interview-box">"{st.session_state.interview}"</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("왼쪽에서 정보를 입력하고 'AI 기사 완성하기' 버튼을 눌러주세요.")
