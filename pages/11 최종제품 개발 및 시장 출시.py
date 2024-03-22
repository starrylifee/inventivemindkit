import streamlit as st
import pathlib
import google.generativeai as genai
import toml


# 현재 파일의 위치를 기반으로 secrets.toml 파일의 경로를 설정
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일을 읽어 API 키 값을 가져옴
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

gemini_api_key5 = secrets.get("gemini_api_key5")
gemini_api_key6 = secrets.get("gemini_api_key6")

# 인공지능 모델을 이용해 콘텐츠를 생성하는 함수
def try_generate_content(api_key, prompt_parts):
    # API 설정
    genai.configure(api_key=api_key)
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
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        st.error(f"API 호출 실패: {str(e)}")
        return None

st.title('최종제품 개발 및 시장 출시')


# 제품 정보 입력 받기
product_name = st.text_input("제품 이름")
product_description = st.text_area("제품 설명")

# 타겟 시장 세부 정보 입력 받기
country = st.selectbox("타겟 국가", ["국가 선택", "한국", "미국", "일본", "중국", "유럽"])
age_range = st.slider("타겟 연령대", 0, 100, (20, 50))
interests = st.multiselect("관심사", ["기술", "음악", "여행", "운동", "게임", "요리", "예술", "과학"])

# 문제 상황 생성 버튼
if st.button("인공지능아 제작 조언을 부탁해"):
    # 프롬프트 구성
    prompt_parts = f"제품 이름: {product_name}\n제품 설명: {product_description}\n타겟 국가: {country}\n타겟 연령대: {age_range}\n관심사: {', '.join(interests)}\n\n위 정보를 기반으로 시장 분석과 마케팅 전략을 제안해주세요."

    # 첫 번째 API 키로 콘텐츠 생성 시도
    response_text = try_generate_content(gemini_api_key5, prompt_parts)

    # 첫 번째 시도가 실패했을 경우, 두 번째 API 키로 재시도
    if response_text is None and gemini_api_key6:
        st.write("첫 번째 API 호출에 실패하여 두 번째 API 키로 재시도합니다.")
        response_text = try_generate_content(gemini_api_key6, prompt_parts)

    # 생성된 문제 상황 표시
    if response_text:
        st.write(response_text)  # 저장된 텍스트를 화면에 출력
    else:
        st.error("문제 상황 생성에 실패했습니다. 나중에 다시 시도해주세요.")