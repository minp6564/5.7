import streamlit as st
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

st.set_page_config(page_title="Chat SNS 스타일", layout="centered")
st.markdown("<h1 style='text-align: center;'>💬 GPT-4.1-mini 챗봇</h1>", unsafe_allow_html=True)

# API Key 입력
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
st.session_state.api_key = st.text_input("🔑 OpenAI API Key", type="password", value=st.session_state.api_key)

# 대화 저장소
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 대화 초기화 버튼 왼쪽 정렬
col1, col2 = st.columns([1, 6])
with col1:
    if st.button("🧹 대화 초기화"):
        st.session_state.messages = []

# 말풍선 스타일
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

# 채팅 출력
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(user_css.format(msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(bot_css.format(msg["content"]), unsafe_allow_html=True)

# ✅ 커스텀 입력창 (왼쪽에 label 붙이기)
with st.container():
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown("**질문을 입력하세요:**")
    with col2:
        user_input = st.text_input("", placeholder="내용을 입력하세요...", key="custom_input")

# GPT 호출 및 응답
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(user_css.format(user_input), unsafe_allow_html=True)

    try:
        client = OpenAI(api_key=st.session_state.api_key)

        chat_messages: list[ChatCompletionMessageParam] = [
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

        # 입력창 초기화
        st.session_state["custom_input"] = ""

    except Exception as e:
        st.error(f"❌ 에러 발생: {str(e)}")
