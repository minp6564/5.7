import streamlit as st
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

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


# --- PDF 챗봇 페이지 ---
elif page == "📄 문서 챗봇":
    st.markdown("<h1 style='text-align: center;'>📄 문서 기반 챗봇</h1>", unsafe_allow_html=True)

    # 문서 업로드
    uploaded_file = st.file_uploader("📂 텍스트 파일을 업로드하세요 (.txt)", type="txt")

    # 문서 로딩
    if uploaded_file:
        document_text = uploaded_file.read().decode("utf-8")

        st.success("✅ 문서가 성공적으로 업로드되었습니다.")

        # 대화 이력 초기화
        if "docchat_history" not in st.session_state:
            st.session_state.docchat_history = []

        if st.button("🧹 대화 초기화"):
            st.session_state.docchat_history = []

        # 대화 출력
        for msg in st.session_state.docchat_history:
            if msg["role"] == "user":
                st.markdown(user_css.format(msg["content"]), unsafe_allow_html=True)
            else:
                st.markdown(bot_css.format(msg["content"]), unsafe_allow_html=True)

        # 사용자 질문
        if query := st.chat_input("문서에 대해 질문하세요..."):
            st.session_state.docchat_history.append({"role": "user", "content": query})
            st.markdown(user_css.format(query), unsafe_allow_html=True)

            try:
                client = OpenAI(api_key=st.session_state.api_key)

                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 업로드된 문서 내용을 바탕으로 답변하는 문서 분석 어시스턴트입니다. 문서 내용은 다음과 같습니다:\n\n" + document_text
                        },
                        {"role": "user", "content": query}
                    ],
                    temperature=0.3
                )

                answer = response.choices[0].message.content
                st.session_state.docchat_history.append({"role": "assistant", "content": answer})
                st.markdown(bot_css.format(answer), unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")

    else:
        st.info("📄 먼저 문서를 업로드해주세요.")


