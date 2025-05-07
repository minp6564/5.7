import streamlit as st
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

st.set_page_config(page_title="GPT SNS 챗봇", layout="centered")
st.title("💬 GPT-4.1-mini 챗봇")

# ✅ API Key session_state 저장
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
st.session_state.api_key = st.text_input("🔑 OpenAI API Key", type="password", value=st.session_state.api_key)

# ✅ 대화 저장
if "messages" not in st.session_state:
    st.session_state.messages = []

# ✅ 대화 초기화 버튼
col1, _ = st.columns([1, 6])
with col1:
    if st.button("🧹 대화 초기화"):
        st.session_state.messages = []

# ✅ 말풍선 스타일
def render_message(role, content):
    css = """
    <div style='text-align: {align}; margin: 10px 0;'>
        <span style='background-color: {color}; padding: 10px 15px; border-radius: 20px; display: inline-block; max-width: 80%;'>
            {text}</span>
    </div>
    """
    if role == "user":
        return css.format(align="right", color="#DCF8C6", text=content)
    else:
        return css.format(align="left", color="#F1F0F0", text=content)

for msg in st.session_state.messages:
    st.markdown(render_message(msg["role"], msg["content"]), unsafe_allow_html=True)

# ✅ @st.cache_data 적용 (응답 캐싱)
@st.cache_data(show_spinner=False)
def get_cached_gpt_response(api_key: str, messages: list[ChatCompletionMessageParam]) -> str:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

# ✅ 사용자 입력 (label 왼쪽)
with st.container():
    left, right = st.columns([1, 5])
    with left:
        st.markdown("**질문을 입력하세요:**")
    with right:
        user_input = st.text_input("", key="chat_input", placeholder="내용을 입력하세요...")

# ✅ 입력 처리
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(render_message("user", user_input), unsafe_allow_html=True)

    try:
        chat_messages: list[ChatCompletionMessageParam] = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        reply = get_cached_gpt_response(st.session_state.api_key, chat_messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.markdown(render_message("assistant", reply), unsafe_allow_html=True)
        st.session_state["chat_input"] = ""  # 입력창 초기화
    except Exception as e:
        st.error(f"❌ 에러 발생: {str(e)}")
