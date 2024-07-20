import streamlit as st
import pathlib
import google.generativeai as genai
import toml
import textwrap

st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# secrets.toml 파일 경로
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# secrets.toml 파일에서 API 키 값 가져오기
gemini_api_key3 = secrets.get("gemini_api_key3")
gemini_api_key4 = secrets.get("gemini_api_key4")

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
                                      "max_output_tokens": 30,
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

st.title('아이디어 탐색도구 (Brainstorming)')

# 사용자로부터의 새로운 입력을 받음
root_node = st.text_input("기본 단어를 입력하세요", key="root_node")
first_node = st.text_input("첫 번째 단어를 입력하세요", key="first_node")
second_node = st.text_input("두 번째 단어를 입력하세요", key="second_node")

if st.button("인공지능 아이디어 한 스푼 추가"):
    if root_node and first_node and second_node :  # 두 연결고리 모두 입력된 경우에만 진행

        # few-shot 프롬프트 구성
        prompt_parts = [
            f"{root_node}와{first_node}와 {second_node}는 브레인스토밍의 노드로 연결되어 있습니다. {second_node}와 직접적으로 연결된 세번째 노드로 사용할 연상되는 단어 5개를 출력해주세요.",
        ]

        # 첫 번째 API 키로 시도
        response_text = try_generate_content(gemini_api_key3, prompt_parts)
        
        # 첫 번째 API 키 실패 시, 두 번째 API 키로 재시도
        if response_text is None and gemini_api_key4 is not None:
            print("첫 번째 API 호출에 실패하여 두 번째 API 키로 재시도합니다.")
            response_text = try_generate_content(gemini_api_key4, prompt_parts)
        
        # 결과 출력
        if response_text is not None:
            st.markdown(to_markdown(response_text))
        else:
            st.error("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")
