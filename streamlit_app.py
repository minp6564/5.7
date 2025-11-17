import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="마약류 법률·예방 챗봇", layout="centered")

client = OpenAI(api_key="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")

# --------------------------------------------------
# 🎨 Chat bubble styles
# --------------------------------------------------
user_css = """
<div style='text-align: right; margin: 10px 0;'>
    <span style='background-color: #DCF8C6; padding: 10px 15px; 
    border-radius: 20px; display: inline-block; max-width: 80%;'>
        {}</span>
</div>
"""

bot_css = """
<div style='text-align: left; margin: 10px 0;'>
    <span style='background-color: #F1F0F0; padding: 10px 15px; 
    border-radius: 20px; display: inline-block; max-width: 80%;'>
        {}</span>
</div>
"""

# --------------------------------------------------
# 📄 Load "마약류 취급 관련 법률" 텍스트 파일
# (기존 library_rules.txt 위치 그대로 사용)
# --------------------------------------------------
@st.cache_data
def load_law_document():
    with open("library_rules.txt", "r", encoding="utf-8") as f:
        return f.read()

drug_law_text = load_law_document()

# --------------------------------------------------
# 🧠 System Prompt (마약 예방·법률 설명 전용 모델)
# --------------------------------------------------
SYSTEM_PROMPT = """
당신은 '마약류 예방, 교육, 법률 안내'를 전문적으로 제공하는 챗봇입니다.

아래 문서는 마약류 취급 관련 법률 및 규정입니다.
이 내용을 기반으로 사용자 질문에 정확하고 책임감 있게 답변하세요.

[당신이 할 수 있는 것]
- 마약류 관리법 및 관련 규정 설명
- 소지/투약/제조/밀매 시의 법적 처벌 안내
- 중독 증상, 건강 위험성, 부작용 설명
- 중독 치료기관·상담 번호 안내
- 마약류 예방 교육 제공
- 법적 보호 제도, 신고 제도 안내

[절대 하면 안 되는 것]
- 마약 제조 방법, 구매 방법, 복용 방법 설명
- 법망 회피 방법, 단속 피하기 조언
- 불법 행위를 돕는 정보 제공
- 특정 약물 오남용을 조장하는 말

요청이 불법적 목적일 경우 반드시 정중히 거절하고
대신 합법적·건강한 도움과 정보를 제공하세요.
"""

# --------------------------------------------------
# 💬 Chatbot UI
# --------------------------------------------------
st.markdown("<h1 style='text-align: center;'>🚨 마약류 법률·예방 안내 챗봇</h1>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("🧹 대화 초기화"):
    st.session_state.chat_history = []

# 히스토리 출력
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(user_css.format(msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(bot_css.format(msg["content"]), unsafe_allow_html=True)

# --------------------------------------------------
# ✏ 사용자 입력
# --------------------------------------------------
if question := st.chat_input("마약류 관련 법률, 처벌, 예방 등에 대해 질문하세요..."):

    st.session_state.chat_history.append({"role": "user", "content": question})
    st.markdown(user_css.format(question), unsafe_allow_html=True)

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\n\n[법률 문서]\n" + drug_law_text},
                *st.session_state.chat_history
            ]
        )

        reply = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.markdown(bot_css.format(reply), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")
