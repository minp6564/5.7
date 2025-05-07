import streamlit as st
import openai

# 페이지 기본 설정
st.set_page_config(page_title="GPT-4.1-mini Chat", layout="centered")

st.title("GPT-4.1-mini 질문 응답 웹앱")

# API Key 입력 받기
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

st.session_state.api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.api_key)

# 질문 입력 받기
question = st.text_input("질문을 입력하세요:")

# 응답 캐싱 함수
@st.cache_data(show_spinner=True)
def get_gpt_response(api_key, user_input):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",  # gpt-4.1-mini
        messages=[
            {"role": "system", "content": "당신은 친절한 AI 어시스턴트입니다."},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

# 응답 버튼
if st.button("답변 받기"):
    if st.session_state.api_key and question:
        try:
            answer = get_gpt_response(st.session_state.api_key, question)
            st.success("응답:")
            st.write(answer)
        except Exception as e:
            st.error(f"에러 발생: {str(e)}")
    else:
        st.warning("API Key와 질문을 모두 입력하세요.")
