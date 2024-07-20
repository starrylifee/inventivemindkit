import streamlit as st
import pathlib
import google.generativeai as genai
import toml
import textwrap

hide_github_icon = """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK{ display: none; }
    #MainMenu{ visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
"""

st.markdown(hide_github_icon, unsafe_allow_html=True)

# 세션 상태 초기화 함수
def reset_session():
    for key in st.session_state.keys():
        del st.session_state[key]

# 세션 상태에 초기 값 설정 함수
def initialize_session_state():
    if 'change_target' not in st.session_state:
        st.session_state.change_target = ''
    if 'change_method' not in st.session_state:
        st.session_state.change_method = ''
    if 'problem_statement' not in st.session_state:
        st.session_state.problem_statement = ''
    if 'reversed_problem' not in st.session_state:
        st.session_state.reversed_problem = ''
    if 'solution_ideas' not in st.session_state:
        st.session_state.solution_ideas = ''
    if 'original_problem_solution' not in st.session_state:
        st.session_state.original_problem_solution = ''

# secrets.toml 파일 경로
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# secrets.toml 파일에서 API 키 값 가져오기
gemini_api_key5 = secrets.get("gemini_api_key5")
gemini_api_key6 = secrets.get("gemini_api_key6")

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
        st.error(f"API 호출 실패: {str(e)}")
        return None
    
def to_markdown(text):
    text = text.replace('•', '*')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

# 앱 초기화 및 세션 상태 관리
if 'initialized' not in st.session_state:
    reset_session()
    st.session_state.initialized = True  # 세션 상태가 초기화되었음을 표시

st.title('아이디어 탐색도구 (Problem Reversal)')


# 입력 및 선택 구성 요소
change_target = st.text_input("1. 무엇을 바꾸고 싶은가요? (예: 생산성, 고객 유치량, 배터리수명, 자동차 연비, 컴퓨터 속도 등)", key='change_target')
change_method = st.text_input("2. 어떻게 바꾸고 싶은가요? (향상, 늘리기, 줄이기, 빠르게 하기)", key='change_method')


# 문제상황 생성
if st.button("인공지능아 문제상황 생성해줘"):
    # 프롬프트 구성
    prompt_parts = [
        f"학생이 발명을 위한 문제상황을 생성했습니다. {st.session_state.change_target}을 {st.session_state.change_method}로 바꾸고 싶어합니다. '{st.session_state.change_target}을 {st.session_state.change_method}하게 바꾸고 싶다.' 처럼 딱 한문장으로 문제상황을 표현해주세요.",
    ]

    # 첫 번째 API 키로 시도
    response_text = try_generate_content(gemini_api_key5, prompt_parts)

    # 첫 번째 API 키 실패 시, 두 번째 API 키로 재시도
    if response_text is None and gemini_api_key6 is not None:
        print("첫 번째 API 호출에 실패하여 두 번째 API 키로 재시도합니다.")
        response_text = try_generate_content(gemini_api_key6, prompt_parts)

    if response_text is not None:
        # 세션 상태의 problem_statement 업데이트
        st.session_state.problem_statement = response_text
        st.write(st.session_state.problem_statement)
    else:
        st.error("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")


# 문제 반전
if st.button("인공지능아 문제상황 뒤집어줘"):
    # 프롬프트 구성
    prompt_parts = [
        f"{st.session_state.problem_statement}는 학생이 만들어낸 문제상황입니다. 이를 Problem Reversal 기법을 활용하여 반전문장을 만들어주세요.",
    ]

    # 첫 번째 API 키로 시도
    response_text = try_generate_content(gemini_api_key5, prompt_parts)

    # 첫 번째 API 키 실패 시, 두 번째 API 키로 재시도
    if response_text is None and gemini_api_key6 is not None:
        print("첫 번째 API 호출에 실패하여 두 번째 API 키로 재시도합니다.")
        response_text = try_generate_content(gemini_api_key6, prompt_parts)

    if response_text is not None:
        # 세션 상태의 problem_statement 업데이트
        st.session_state.reversed_problem = response_text
        st.write(st.session_state.reversed_problem)
    else:
        st.error("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")

# 반전 문제 해결 아이디어 입력
solution_ideas = st.text_area("반전문제를 해결하려면 어떻게 해야 할까요? (2가지 제안)", key='solution_ideas')

# 원래 문제 해결 방안 제시
original_problem_solution = st.text_area("그러면 원래 문제를 해결하려면 어떻게 해야 할까요?", key='original_problem_solution')

# 세션 초기화 버튼
if st.button("세션 초기화"):
    reset_session()
    st.experimental_rerun()  # 스트림릿 앱을 다시 실행하여 세션을 초기화합니다.