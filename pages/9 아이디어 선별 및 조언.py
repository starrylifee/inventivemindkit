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

st.title('아이디어 선별 및 조언')

# 사용자 입력 구성
title = st.text_input("발명품의 성질을 나타낼 수 있는 제목을 적어주세요.")
ideas = st.text_area("발명품을 자세하게 적어주세요.")

# 문제 상황 생성 버튼
if st.button("인공지능아 내 최종 아이디어가 어때?"):
    # 프롬프트 구성
    prompt_parts = f"학생이 발명아이디어를 결정했습니다. {title}이라는 이름을 가진 발명품은 {ideas}입니다. 학생의 발명 아이디어를 듣고 평가해주세요. 창의성 30점, 효율성 30점, 현실성 40점으로 총 100점으로 평가해주세요. 평가는 깐깐하게 해주시고, 점수를 낮게 주면서 아주 엄하게 평가해주세요. "

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

