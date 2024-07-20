import streamlit as st
import pathlib
import google.generativeai as genai
import toml
from PIL import Image
import io
from openai import OpenAI

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

# 현재 파일의 위치를 기반으로 secrets.toml 파일의 경로를 설정
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일을 읽어 API 키 값을 가져옴
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

gemini_api_key5 = secrets.get("gemini_api_key5")
gemini_api_key6 = secrets.get("gemini_api_key6")

# 사이드바에 OpenAI API 키 입력 받기
api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요", type="password")
client = OpenAI(api_key=api_key)

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

st.title('프로토타입 제작 및 테스트')


# 사용자 입력 구성
title = st.text_input("발명품의 성질을 나타낼 수 있는 제목을 적어주세요.")
ideas = st.text_area("발명품을 프로토타입을 만들 계획을 자세하게 적어주세요.")
meterials = st.text_input("프로토타입을 만들 재료는 무엇인가요?")

# 문제 상황 생성 버튼
if st.button("인공지능아 제작 조언을 부탁해"):
    # 프롬프트 구성
    prompt_parts = f"학생이 발명아이디어를 결정했습니다. {title}이라는 이름을 가진 발명품은 {meterials} 로 만들 예정인 {ideas}입니다. 학생의 발명 아이디어를 듣고 제작과 관련된 조언을 해주세요. "

    # 첫 번째 API 키로 콘텐츠 생성 시도
    response_text = try_generate_content(gemini_api_key5, prompt_parts)

    # 첫 번째 시도가 실패했을 경우, 두 번째 API 키로 재시도
    if response_text is None and gemini_api_key6:
        st.write("첫 번째 API 호출에 실패하여 두 번째 API 키로 재시도합니다.")
        response_text = try_generate_content(gemini_api_key6, prompt_parts)

    # 생성된 문제 상황 표시
    if response_text:
        st.session_state.problem_statement = response_text  # 생성된 텍스트를 세션 상태에 저장
        st.write(st.session_state.problem_statement)  # 저장된 텍스트를 화면에 출력
    else:
        st.error("문제 상황 생성에 실패했습니다. 나중에 다시 시도해주세요.")

# 프로토타입 이미지 생성 버튼
if st.button("프로토타입 이미지 생성"):
    # 프롬프트 구성
    image_prompt = f"{meterials}로 만든, {ideas}인 {title}"

    try:
        # DALL·E를 사용하여 이미지 생성 요청
        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        # 생성된 이미지 표시
        generated_image_url = response.data[0].url
        st.image(generated_image_url, caption="프로토타입")

        # 이미지 다운로드 링크 제공
        st.markdown(f"[이미지 다운로드]({generated_image_url})", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"이미지 생성 중 오류 발생: {e}")
