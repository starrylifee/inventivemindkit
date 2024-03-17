import pathlib
import textwrap
import google.generativeai as genai
import streamlit as st
import toml
from PIL import Image
import io
import random

# 세션 상태 초기화
if 'response_text' not in st.session_state:
    st.session_state['response_text'] = ""
if 'response_text_problem' not in st.session_state:
    st.session_state['response_text_problem'] = ""
if 'comparison' not in st.session_state:
    st.session_state['comparison'] = ""
if 'student_input' not in st.session_state:
    st.session_state['student_input'] = ""

# to_markdown 함수
def to_markdown(text):
    text = text.replace('•', '*')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

# 사용자 입력을 세션 상태에 저장하는 함수
def save_student_input():
    st.session_state['student_input'] = st.session_state['student_input_text']

# secrets.toml 파일 경로 및 읽기
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# API 키 가져오기
gemini_api_key7 = secrets.get("gemini_api_key7")
gemini_api_key8 = secrets.get("gemini_api_key8")

# 콘텐츠 생성 함수
def try_generate_content(api_key, prompt_parts):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                  generation_config={
                                      "temperature": 0.9,
                                      "top_p": 1,
                                      "top_k": 1,
                                      "max_output_tokens": 1024,
                                  },
                                  safety_settings=[
                                      {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                      {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                      {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                      {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                  ])
    try:
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        print(f"API 호출 실패: {e}")
        return None

# 랜덤 단어 데이터
words_database = {
    "단어1": ["남색", "파랑", "캠핑", "스테이크", "쇼핑몰", "늑대", "만두", "헬리콥터", "오토바이", "바둑", "기차", "돼지", "과학자", "호랑이", "고양이"],
    "단어2": ["사자", "김밥", "독서", "가수", "핫 에어 발룬", "분노", "고래", "비행기", "서핑", "그림그리기", "청록", "버스", "라멘", "배우", "자전거"],
    "단어3": ["디자이너", "노래하기", "기쁨", "소방관", "빨강", "게임", "타코", "판다", "운동선수", "배", "미술관", "감사", "병원", "사진찍기", "초록"]
}

st.title("생활속 온도의 중요성")

# Streamlit 페이지 레이아웃을 두 개의 컬럼으로 나눕니다.
col1, col2 = st.columns([1, 1])  # 왼쪽 컬럼은 입력을 위한 공간, 오른쪽 컬럼은 출력을 위한 넓은 공간을 할당합니다.

with col1:  # 왼쪽 컬럼 시작

    # 카테고리에서 단어 선택
    word1 = st.selectbox("첫 번째 카테고리에서 단어를 선택하세요.", words_database["단어1"], key='word1')
    word2 = st.selectbox("두 번째 카테고리에서 단어를 선택하세요.", words_database["단어2"], key='word2')
    word3 = st.selectbox("세 번째 카테고리에서 단어를 선택하세요.", words_database["단어3"], key='word3')

    if st.button("단어 생성 및 문장 만들기", key="generate"):
        prompt = f"주어진 단어 '{word1}', '{word2}', '{word3}'를 이용하여 창의적인 하나의 문장을 만들어주세요."
        prompt_parts = [prompt]
        response = try_generate_content(gemini_api_key7, prompt_parts)
        if response is None and gemini_api_key8 is not None:
            response = try_generate_content(gemini_api_key8, prompt_parts)
        if response is not None:
            st.session_state['response_text'] = response
        else:
            st.error("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")


    # 사용자 입력을 받고 세션 상태에 저장
    student_input = st.text_input("온도를 측정하지 않았을 때 생기는 문제는 무엇인가요?", value=st.session_state['student_input'], on_change=save_student_input, key='student_input_text')

    if st.button("인공지능의 생각은?", key="ai_thoughts"):
        prompt = f"{st.session_state['response_text']} 상황에서 온도를 측정하지 않았을 때 생기는 문제를 상상해서 3문장 정도의 짧은 글로 적어주세요."
        prompt_parts = [prompt]
        st.session_state['response_text_problem'] = try_generate_content(gemini_api_key7, prompt_parts)

        # 첫 번째 시도가 실패했고, 두 번째 API 키가 있을 경우 재시도
        if st.session_state['response_text_problem'] is None and gemini_api_key8 is not None:
            st.session_state['response_text_problem'] = try_generate_content(gemini_api_key8, prompt_parts)
        
        # 두 번째 시도까지 실패했거나, 첫 번째 시도에서 None을 반환한 경우
        if st.session_state['response_text_problem'] is None:
            st.error("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")


    # "학생의 생각과 인공지능의 생각을 비교해서 학생을 칭찬해주세요." 버튼을 추가
    if st.button("학생의 생각과 인공지능의 생각 비교 및 칭찬", key="praise"):
        # 학생의 생각과 인공지능의 생각을 포함하는 새로운 프롬프트 생성
        if 'student_input' in st.session_state and 'response_text_problem' in st.session_state:
            comparison_prompt = f"학생의 생각: {st.session_state['student_input']}.\n" \
                                f"인공지능의 생각: {st.session_state['response_text_problem']}.\n" \
                                "이 두 생각을 바탕으로 학생을 칭찬하는 문장을 생성해주세요."
            # 생성형 API를 호출하여 칭찬 문장 생성
            praise_text = try_generate_content(gemini_api_key7, [comparison_prompt])
            
            # API 호출 실패 시, 두 번째 API 키로 재시도
            if praise_text is None and gemini_api_key8 is not None:
                praise_text = try_generate_content(gemini_api_key8, [comparison_prompt])
            
            # 생성된 칭찬 문장을 세션 상태에 저장 및 출력
            if praise_text is not None:
                st.session_state['praise_text'] = praise_text
            else:
                st.error("칭찬 문장 생성에 실패했습니다. 나중에 다시 시도해주세요.")
        else:
            st.error("학생의 생각과 인공지능의 생각을 먼저 입력해주세요.")

with col2:  # 오른쪽 컬럼 시작

    # 생성된 문장을 보여주는 부분
    if 'response_text' in st.session_state and st.session_state['response_text']:
        st.markdown("### 📝 생성된 문장:")
        st.markdown(f"> {st.session_state['response_text']}")

    # 학생의 생각을 보여주는 부분
    if 'student_input' in st.session_state and st.session_state['student_input']:
        st.markdown("### 🤔 학생의 생각:")
        st.markdown(f"> {st.session_state['student_input']}")

    # 인공지능의 생각을 보여주는 부분
    if 'response_text_problem' in st.session_state and st.session_state['response_text_problem']:
        st.markdown("### 🧠 인공지능의 생각:")
        st.markdown(f"> {st.session_state['response_text_problem']}")

    # 칭찬 문장을 보여주는 부분
    if 'praise_text' in st.session_state and st.session_state['praise_text']:
        st.markdown("### 🌟 칭찬 문장:")
        st.markdown(f"> {st.session_state['praise_text']}")
