import streamlit as st
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
import fitz
st.set_page_config(page_title="GPT 웹앱", layout="centered")

# --- 사이드바 메뉴 ---
page = st.sidebar.selectbox("페이지를 선택하세요", [
    "💬 일반 챗봇",
    "📚 도서관 챗봇",
    "📄 문서 챗봇"  # ✅ 실습 4 페이지 추가
])


# --- API Key 유지 ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
st.session_state.api_key = st.text_input("🔑 OpenAI API Key", type="password", value=st.session_state.api_key)

if not st.session_state.api_key:
    st.warning("먼저 OpenAI API Key를 입력하세요.")
    st.stop()

# --- 스타일 정의 ---
user_css = """
<div style='text-align: right; margin: 10px 0;'>
    <span style='background-color: #DCF8C6; padding: 10px 15px; border-radius: 20px; display: inline-block; max-width: 80%;'>
        {}</span>
</div>
"""
bot_css = """
<div style='text-align: left; margin: 10px 0;'>
    <span style='background-color: #F1F0F0; padding: 10px 15px; border-radius: 20px; display: inline-block; max-width: 80%;'>
        {}</span>
</div>
"""

# --- 일반 챗봇 페이지 ---
if page == "💬 일반 챗봇":
    st.markdown("<h1 style='text-align: center;'>💬 GPT-4.1-mini 챗봇</h1>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.button("🧹 대화 초기화"):
        st.session_state.messages = []

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(user_css.format(msg["content"]), unsafe_allow_html=True)
        else:
            st.markdown(bot_css.format(msg["content"]), unsafe_allow_html=True)

    if prompt := st.chat_input("질문을 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(user_css.format(prompt), unsafe_allow_html=True)

        try:
            client = OpenAI(api_key=st.session_state.api_key)
            chat_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=chat_messages,
                temperature=0.7
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.markdown(bot_css.format(reply), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ 에러 발생: {str(e)}")

# --- 도서관 챗봇 페이지 ---



elif page == "📚 도서관 챗봇":
    st.markdown("<h1 style='text-align: center;'>📚 국립부경대학교 도서관 챗봇</h1>", unsafe_allow_html=True)

    # 규정 불러오기
    @st.cache_data
    def load_library_rules():
        with open("library_rules.txt", "r", encoding="utf-8") as f:
            return f.read()
            
    library_rules = load_library_rules()


    if "chatbot_history" not in st.session_state:
        st.session_state.chatbot_history = []

    if st.button("🧹 대화 초기화"):
        st.session_state.chatbot_history = []

    for msg in st.session_state.chatbot_history:
        if msg["role"] == "user":
            st.markdown(user_css.format(msg["content"]), unsafe_allow_html=True)
        else:
            st.markdown(bot_css.format(msg["content"]), unsafe_allow_html=True)

    if question := st.chat_input("도서관 규정에 대해 질문하세요..."):
        st.session_state.chatbot_history.append({"role": "user", "content": question})
        st.markdown(user_css.format(question), unsafe_allow_html=True)

        try:
            client = OpenAI(api_key=st.session_state.api_key)
            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 부경대학교 도서관 규정을 기반으로 답변하는 도우미입니다. 아래 규정을 참고하여 정확하게 답변하세요:\n\n" + library_rules
                    },
                    {"role": "user", "content": question}
                ],
                temperature=0.3
            )
            reply = response.choices[0].message.content
            st.session_state.chatbot_history.append({"role": "assistant", "content": reply})
            st.markdown(bot_css.format(reply), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ 오류 발생: {str(e)}")


# --- PDF에서 텍스트 추출 ---
def extract_text_from_pdf(uploaded_pdf) -> str:
    pdf = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    text = ""
    for page in pdf:
        text += page.get_text()
    return text

# --- 페이지 시작 ---
elif page == "📄 문서 챗봇":
    st.markdown("<h1 style='text-align: center;'>📄 PDF 기반 문서 챗봇</h1>", unsafe_allow_html=True)

    # PDF 업로드
    uploaded_pdf = st.file_uploader("📂 PDF 파일을 업로드하세요", type="pdf")

    if uploaded_pdf:
        try:
            document_text = extract_text_from_pdf(uploaded_pdf)
            st.success("✅ PDF 텍스트 추출 성공!")

            if "pdfchat_history" not in st.session_state:
                st.session_state.pdfchat_history = []

            if st.button("🧹 대화 초기화"):
                st.session_state.pdfchat_history = []

            # 이전 대화 출력
            for msg in st.session_state.pdfchat_history:
                if msg["role"] == "user":
                    st.markdown(user_css.format(msg["content"]), unsafe_allow_html=True)
                else:
                    st.markdown(bot_css.format(msg["content"]), unsafe_allow_html=True)

            # 사용자 질문
            if query := st.chat_input("업로드된 문서에 대해 질문하세요..."):
                st.session_state.pdfchat_history.append({"role": "user", "content": query})
                st.markdown(user_css.format(query), unsafe_allow_html=True)

                try:
                    client = OpenAI(api_key=st.session_state.api_key)
                    response = client.chat.completions.create(
                        model="gpt-4-1106-preview",
                        messages=[
                            {
                                "role": "system",
                                "content": "다음은 사용자가 업로드한 PDF 문서의 내용입니다. 이 내용을 참고해 사용자 질문에 정확하고 간결하게 답하세요:\n\n" + document_text[:8000]  # 길이 제한
                            },
                            {"role": "user", "content": query}
                        ],
                        temperature=0.3
                    )
                    answer = response.choices[0].message.content
                    st.session_state.pdfchat_history.append({"role": "assistant", "content": answer})
                    st.markdown(bot_css.format(answer), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ GPT 오류: {str(e)}")
        except Exception as e:
            st.error(f"❌ PDF 추출 실패: {str(e)}")
    else:
        st.info("📄 PDF 문서를 업로드하세요.")
