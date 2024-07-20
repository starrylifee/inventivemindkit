import streamlit as st
import random
import requests
import html
import re
import pathlib
import textwrap
import google.generativeai as genai
import toml

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

# secrets.toml 파일 경로
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# secrets.toml 파일에서 API 키 값 가져오기
gemini_api_key1 = secrets.get("gemini_api_key1")
gemini_api_key2 = secrets.get("gemini_api_key4")

# 질문 목록
questions = [
    "이 문제가 지역 사회에 어떤 영향을 미치나요?",
    "이 문제로 인한 경제적, 사회적, 환경적 손실은 어느 정도로 추정되나요?",
    "이 문제가 현재까지 얼마나 확산되었나요?",
    "이 문제의 주된 원인은 무엇이라고 생각하나요?",
    "이 문제를 해결하기 위해 이전에 어떤 방법이 시도되었나요?",
    "이전 시도들이 성공하지 못한 이유는 무엇이라고 생각하나요?",
    "이 문제로 인해 가장 큰 영향을 받는 인구 집단은 누구인가요?",
    "이 문제를 해결할 수 있는 잠재적인 해결책으로 무엇이 있을까요?",
    "이 문제를 해결하는 데 도움이 될 수 있는 지역 사회의 자원은 무엇인가요?",
]

# 스트림릿 세션 상태 초기화
if 'question_indices' not in st.session_state:
    st.session_state['question_indices'] = [random.randint(0, len(questions) - 1) for _ in range(2)]

def generate_new_question(index):
    """새로운 질문을 생성하고 세션 상태를 업데이트합니다."""
    new_index = random.randint(0, len(questions) - 1)
    st.session_state.question_indices[index] = new_index

# 위키미디어에서 페이지 도입부를 가져오는 함수
def get_page_intro(pageid):
    URL = "https://ko.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "prop": "extracts",
        "exintro": "true",
        "explaintext": "true",
        "pageids": pageid,
        "format": "json"
    }
    
    response = requests.get(URL, params=PARAMS)
    data = response.json()
    page = next(iter(data['query']['pages'].values()))
    intro = page.get('extract', 'No intro found.')
    return intro

# 변경된 위키미디어에서 정보를 검색하고 결과를 반환하는 함수
def get_wiki_info(query):
    URL = "https://ko.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json"
    }

    response = requests.get(url=URL, params=PARAMS)
    data = response.json()

    if data["query"]["search"]:
        first_result = data["query"]["search"][0]
        pageid = first_result["pageid"]
        
        # 여기에서 get_page_intro 함수를 사용하여 페이지 도입부를 가져옵니다.
        intro = get_page_intro(pageid)
        
        # HTML 태그 제거 및 반환
        clean_intro = html.unescape(re.sub('<[^<]+?>', '', intro))
        return first_result["title"], clean_intro
    else:
        return "No results found", "Please try a different search term."

# few-shot 프롬프트 구성 함수 수정
def try_generate_content(api_key, prompt_parts):
    # API 키를 설정
    genai.configure(api_key=api_key)
    
    # 설정된 모델 변경
    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                  generation_config={
                                      "temperature": 0.9,
                                      "top_p": 1,
                                      "top_k": 1,
                                      "max_output_tokens": 2048,
                                  },
                                  safety_settings=[
                                      {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                      {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                      {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                      {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                  ])
    try:
        # 콘텐츠 생성 시도
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        # 예외 발생시 None 반환
        print(f"API 호출 실패: {e}")
        return None


def to_markdown(text):
    text = text.replace('•', '*')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

# 스트림릿 앱 시작
st.title("문제이해하기")

# 문제 입력 받기
problem = st.text_input("내가 문제로 인식한 것", "")

# 질문과 답변 섹션
if problem:
    # session_state에 질문 인덱스를 초기화
    if 'q1_index' not in st.session_state:
        st.session_state.q1_index = random.randint(0, len(questions)-1)
    if 'q2_index' not in st.session_state:
        st.session_state.q2_index = random.randint(0, len(questions)-1)
    
    # 첫 번째 질문과 재질문 버튼
    q1 = questions[st.session_state.q1_index]
    answer1 = st.text_input(f"질문 1: {q1}", key="q1")
    
    if st.button("다른 질문 받기 1"):
        st.session_state.q1_index = random.randint(0, len(questions)-1)

    # 두 번째 질문과 재질문 버튼
    q2 = questions[st.session_state.q2_index]
    answer2 = st.text_input(f"질문 2: {q2}", key="q2")
    
    if st.button("다른 질문 받기 2"):
        st.session_state.q2_index = random.randint(0, len(questions)-1)

st.markdown("<hr>", unsafe_allow_html=True)

if st.button("인공지능의 생각은?"):
    
    # few-shot 프롬프트 구성
    prompt_parts = [
        f"{problem}을 해결하기 위한 학생의 노력이 기특합니다. {q1}에 대한 답은 {answer1}이고, {q2}에 대한 답은 {answer2} 입니다. 학생의 답변을 보고 칭찬해주고, 문제해결을 기대하는 말을 해주세요.",
    ]

    # 첫 번째 API 키로 시도
    response_text = try_generate_content(gemini_api_key1, prompt_parts)
    
    # 첫 번째 API 키 실패 시, 두 번째 API 키로 재시도
    if response_text is None and gemini_api_key2 is not None:
        print("첫 번째 API 호출에 실패하여 두 번째 API 키로 재시도합니다.")
        response_text = try_generate_content(gemini_api_key2, prompt_parts)
    
    # 결과 출력
    if response_text is not None:
        st.markdown(to_markdown(response_text))
    else:
        st.error("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")

st.markdown("<hr>", unsafe_allow_html=True)

# '위키미디어에서 배경 정보 검색하기' 버튼 추가
if st.button("위키미디어에서 배경 정보 검색하기"):
    if problem:  # 'problem'은 사용자가 입력한 문제
        title, snippet = get_wiki_info(problem)
        st.write(f"### {title}")
        st.write(snippet)
    else:
        st.write("문제에 대한 정보를 먼저 입력해주세요.")