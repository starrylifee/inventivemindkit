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

# 스트림릿 앱 인터페이스 구성
st.title("학생 미술 작품 반론 생성기")

# 사용자 입력 받기
claim = st.text_input("주장을 입력하세요")
reason1 = st.text_area("첫 번째 근거를 입력하세요")
reason2 = st.text_area("두 번째 근거를 입력하세요")

if st.button("반론 생성"):
    # few-shot 프롬프트 구성
    prompt_parts = [
        "아래는 초등학생이 쓴 주장과 근거 2가지 입니다.\ninput은 주장입니다.\ninput 1은 첫번째 근거 입니다.\ninput3는 두번째 근거 입니다.\n주장과 근거를 확인하고, 예상되는 반론을 말해주세요",
        "input: 학교에서는 환경 보호를 위해 일회용품 사용을 금지해야 합니다.",
        "input 2: 일회용품은 분해되는데 많은 시간이 걸리고, 이로 인해 환경 오염이 심각해집니다.",
        "input 3: 학교에서 다시 사용할 수 있는 그릇과 식기를 사용하면 쓰레기 발생량을 크게 줄일 수 있습니다.",
        "output: 일회용품을 사용하지 않으면 학교에서 설거지와 같은 추가적인 노동이 필요하게 됩니다.",
        "input: 학교에서 학생들의 휴대폰 사용을 금지해야 합니다.",
        "input 2: 휴대폰 사용은 수업 중 집중력을 떨어뜨리고 학업 성적에 부정적인 영향을 미칩니다.",
        "input 3: 학교에서 휴대폰 사용을 금지하면 학생들 사이의 사이버 불링 문제를 줄일 수 있습니다.",
        "output: 휴대폰은 긴급 상황 시 연락 수단으로 필요하며, 학습 자료로도 활용될 수 있습니다.",
        "input: 모든 학생은 매일 아침 운동을 해야 합니다.",
        "input 2: 아침 운동은 학생들의 체력을 증진시키고, 집중력을 향상시킵니다.",
        "input 3: 정기적인 운동은 스트레스를 줄이고 정신 건강에 긍정적인 영향을 미칩니다.",
        "output: 모든 학생이 운동을 좋아하거나 할 수 있는 건강 상태가 아닐 수 있습니다.",
        "input: 학교 급식은 더 건강한 식단으로 전환되어야 합니다.",
        "input 2: 건강한 식단은 학생들의 학업 성적과 건강에 긍정적인 영향을 미칩니다.",
        "input 3: 영양가 있는 식단은 학생들의 신체적, 정신적 발달에 중요합니다.",
        "output: 건강식 급식은 맛이 없고, 학생들이 좋아하지 않을 수 있습니다.",
        "input: 학생들은 하교 후 학원에 가기보다는 자유 시간을 더 많이 가져야 합니다.",
        "input 2: 자유 시간은 학생들이 취미 활동을 하거나 휴식을 취하는 데 도움이 됩니다.",
        "input 3: 과도한 학원 수업은 학생들의 스트레스를 증가시키고, 자유롭게 생각하는 능력을 저해할 수 있습니다.",
        "output: 학원 수업은 학생들이 학업에서 더 나은 성적을 얻는 데 필요할 수 있습니다.",
        f"input: {claim}",
        f"input 2: {reason1}",
        f"input 3: {reason2}",
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
