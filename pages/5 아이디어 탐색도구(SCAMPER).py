import streamlit as st
import pathlib
import google.generativeai as genai
import toml
import textwrap

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


def to_markdown(text):
    text = text.replace('•', '*')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

st.title('아이디어 탐색도구 (SCAMPER)')

things = st.text_input("어떤 물건을 개량하고 싶나요?", key="things")

# SCAMPER 기법 선택
scamper_technique = st.radio("SCAMPER 기법을 선택하세요.", 
                             ["대체하기", "결합하기", "조정하기", "수정/확대/축소하기", "다른 용도로 사용하기", "제거하기", "재배열하기"])


if scamper_technique == "대체하기":

    substitute_what = st.text_input("어떤 요소를 대체할 것인가?", key="substitute_what")
    substitute_with = st.text_input("어떤 것으로 대체할 것인가?", key="substitute_with")
    st.markdown("(예시)자전거 바퀴를 특수 고무로 바꿔 조용하고 부드러운 주행을 가능하게 한다.")

    if st.button("인공지능아 어떻게 생각해?"):
        if things and substitute_what and substitute_with : 

            # 프롬프트 구성
            prompt_parts = [
                f"{things}를 발명기법을 이용하려 수정하려 합니다. {things}에 있는{substitute_what}을 {substitute_with}로 바꾸면 {things}가 어떻게 좋아질까요? 상상하여 이야기를 해주고 창의성 30점, 현실성 30점, 유용성40점으로 평가해주세요.",
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


elif scamper_technique == "결합하기":
    combine_what = st.text_input("어떤 물건을 결합할 것인가?", key="combine_what")
    st.markdown("(예시)연필과 지우개를 결합해 쓰고 지우는 기능을 하나로 합친다.")

    if st.button("인공지능아 어떻게 생각해?"):
        if things and combine_what : 

            # 프롬프트 구성
            prompt_parts = [
                f"{things}를 발명기법을 이용하려 수정하려 합니다. {things}와 {combine_what}을 결합한 물건이 생기면 {things}가 어떻게 좋아질까요? 상상하여 이야기를 해주고 창의성 30점, 현실성 30점, 유용성40점으로 평가해주세요.",
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

elif scamper_technique == "조정하기":
    adapt_to = st.text_input("어떤 새로운 상황이나 요구에 맞게 조정할 것인가?", key="adapt_to")
    st.markdown("(예시)특별한 코팅을 추가하여 햇빛 아래에서 자동으로 색이 짙어지는 선글라스로 변환된다.")

    if st.button("인공지능아 어떻게 생각해?"):
        if things and adapt_to:
            # 프롬프트 구성
            prompt_parts = [
                f"{things}를 {adapt_to}에 맞게 조정한다면 어떤 새로운 기능이나 형태가 가능할까요? 창의성, 현실성, 유용성을 기준으로 아이디어를 제안해주세요."
            
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


elif scamper_technique == "수정/확대/축소하기":
    modify_what = st.text_input("어떤 부분을 수정, 확대 또는 축소할 것인가?", key="modify_what")
    scale_option = st.radio("확대 또는 축소 중 선택하세요.", ('확대', '축소'), key="scale_option")
    st.markdown("(예시)물병의 크기를 조절할 수 있도록 디자인하여 사용자가 필요에 따라 크기를 변경할 수 있게 한다.")

    
    if st.button("인공지능아 어떻게 생각해?"):
        if things and modify_what:
            # 프롬프트 구성
            prompt_parts = [
                f"{things}의 {modify_what}을 {scale_option}한다면 어떤 새로운 기능이나 형태가 가능할까요? 창의성, 현실성, 유용성을 기준으로 아이디어를 제안해주세요."
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


elif scamper_technique == "다른 용도로 사용하기":
    new_use = st.text_input("어떤 새로운 용도를 생각하고 있나요?", key="new_use")
    st.markdown("(예시)오래된 티셔츠를 재활용하여 쇼핑백으로 만들어 환경 보호에 기여한다.")

    if st.button("인공지능아 어떻게 생각해?"):
        if things and new_use:
            # 프롬프트 구성
            prompt_parts = [
                f"{things}을(를) 다른 방식으로 사용하는 아이디어는 {new_use}입니다. 이 새로운 용도가 발명품의 유용성을 어떻게 향상시킬 수 있는지, 그리고 이 변화가 발명품에 어떤 새로운 가치를 추가할 수 있는지에 대해 설명해주세요."
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

elif scamper_technique == "제거하기":

    remove_what = st.text_input("어떤 요소를 제거할 것인가?", key="remove_what")
    st.markdown("(예시)휴대폰에서 불필요한 기능을 제거하여 사용자 경험을 단순화하고 배터리 수명을 연장한다.")

    if st.button("인공지능아 어떻게 생각해?"):
        if things and remove_what:
        
            prompt_parts = [
                f"{things}에서 {remove_what}를 제거함으로써 발명품이 어떻게 달라질지, 제거가 창의성, 현실성, 유용성에 어떤 영향을 미칠지에 대해 설명해주세요."
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


elif scamper_technique == "재배열하기":
    rearrange_what = st.text_input("어떤 요소들의 순서를 어떻게 바꿀 것인가?", key="rearrange_what")
    st.markdown("(예시)책상 서랍의 구성을 재배열하여 더 효율적으로 물건을 정리하고 접근성을 개선한다.")

    if st.button("인공지능아 어떻게 생각해?"):
        if things and rearrange_what:
        
            prompt_parts = [
                f"{things}에서 {rearrange_what}함으로써 발명품이 어떻게 달라질지, 제거가 창의성, 현실성, 유용성에 어떤 영향을 미칠지에 대해 설명해주세요."
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