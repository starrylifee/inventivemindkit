import pathlib
import textwrap
import google.generativeai as genai
import streamlit as st
import toml

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

def to_markdown(text):
    text = text.replace('•', '*')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

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

# 스트림릿 앱 인터페이스 구성 수정
st.title("우리 주변의 불편한 점 찾기")

# 사용자 입력 받기
item_name = st.text_input("물건의 이름을 입력하세요")

if st.button("불편한 점 출력"):
    # few-shot 프롬프트 구성
    prompt_parts = [
        "아래는 초등학생이 생성한 물건별 불편했던 3가지 경험입니다.\ninput은 물건의 이름입니다.\noutput은 불편했던 경험입니다.\n\n물건의 이름을 확인하고 불편했던 경험 3가지를 출력해주세요.",
        "input: 스마트워치",
        "output: 자주 충전해야 하는 불편함이 있다. 화면이 작아 세부 정보 확인이 어렵다. 방수 기능이 부족해 수영 등의 활동에 제한적이다.",
        "input: 전자레인지",
        "output: 음식을 고르게 데우지 못하는 경우가 있다. 내부 청소가 번거롭다. 전자파에 대한 건강 우려가 있다.",
        f"input: {item_name}",
        "output: ",
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
