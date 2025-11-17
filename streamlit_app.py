import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="부경대 도서관 챗봇", layout="centered")

# -------------------------------
# 🔑 API Key 입력
# -------------------------------
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

st.session_state.api_key = st.text_input("🔑 OpenAI API Key", type="password", value=st.session_state.api_key)

if not st.session_state.api_key:
    st.warning("먼저 OpenAI API Key를 입력하세요.")
    st.stop()

client = OpenAI(api_key=st.session_state.api_key)

# -------------------------------
# 🎨 스타일 정의
# -------------------------------
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

# -------------------------------
# 📚 도서관 규정 불러오기
# -------------------------------
@st.cache_data
def load_library_rules():
    with open("library_rules.txt", "r", encoding="utf-8") as f:
        return f.read()

library_rules = load_library_rules()

# -------------------------------
# 💬 챗봇 페이지
# -------------------------------
st.markdown("<h1 style='text-align: center;'>📚 부경대학교 도서관 챗봇</h1>", unsafe_allow_html=True)

# 대화 히스토리 저장
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 초기화 버튼
if st.button("🧹 대화 초기화"):
    st.session_state.chat_history = []

# 이전 대화 출력
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(user_css.format(msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(bot_css.format(msg["content"]), unsafe_allow_html=True)

# -------------------------------
# ✏️ 사용자 입력
# -------------------------------
if question := st.chat_input("도서관 규정에 대해 질문하세요..."):

    st.session_state.chat_history.append({"role": "user", "content": question})
    st.markdown(user_css.format(question), unsafe_allow_html=True)

    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 부경대학교 도서관 규정을 기반으로 답변하는 도우미입니다. 다음은 도서관 규정입니다:\n\n" + library_rules
                },
                {"role": "user", "content": question}
            ]
        )
        reply = response.choices[0].message.content

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.markdown(bot_css.format(reply), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")
