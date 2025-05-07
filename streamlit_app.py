import streamlit as st
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

# 페이지 설정
st.set_page_config(page_title="ChatGPT 스타일 챗봇", layout="wide")
st.title("💬 GPT-4.1-mini 챗봇")

# API 키 입력
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

st.session_state.api_key = st.text_input("🔑 OpenAI API Key", type="password", value=st.session_state.api_key)

# 메시지 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Clear 버튼
if st.button("🧹 대화 초기화"):
    st.session_state.messages = []

# 이전 메시지 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력 받기
if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        client = OpenAI(api_key=st.session_state.api_key)

        # 메시지 형식 맞추기
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
        with st.chat_message("assistant"):
            st.markdown(reply)

    except Exception as e:
        with st.chat_message("assistant"):
            st.error(f"❌ 에러 발생: {str(e)}")
