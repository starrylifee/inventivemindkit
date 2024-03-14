import pathlib
import textwrap
import google.generativeai as genai
import streamlit as st
import toml
from PIL import Image
import io

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
                                      "max_output_tokens": 1024,
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
st.title("식물씨앗이 이동하는 방법 반영한")
st.title("발명아이디어 생성기")

# 사용자 입력 받기
item_name = st.text_input("물건의 이름을 입력하세요")

# 드롭다운을 이용한 씨앗 이동 방법 선택
seed_movement_method = st.selectbox(
    "식물의 씨앗이 이동하는 방법을 선택해주세요.",
    ["동물의 몸에 붙어 움직이기", "바람을 타고 날아가기", "수분에 의한 이동", "발사 메커니즘", "동물의 소화 후 배설"]
)

if st.button("아이디어 생성"):
    # few-shot 프롬프트 구성
    prompt_parts = [
        f"식물의 씨앗이 이동하는 방법은 크게 5가지가 있습니다.\n\n1. 동물의 몸에 붙어 움직이기\n2. 바람을 타고 날아가기\n3. 수분에 의한 이동\n4. 발사 메커니즘\n5. 동물의 소화 후 배설\n\n{seed_movement_method}를 이용해서 {item_name}의 기능을 개량할 수 있는 아이디어를 주세요.",
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
