import streamlit as st
import random
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

# generated_elements를 빈 리스트로 초기화
generated_elements = []

# 기존 코드에 이 라인 추가:
elements_to_choose_from = []  # 이 리스트를 빈 리스트로 초기화

# 세션 상태 초기화
if 'chosen_element' not in st.session_state:
    st.session_state.chosen_element = ''
if 'forced_combination_idea' not in st.session_state:
    st.session_state.forced_combination_idea = ''
if 'generated_elements' not in st.session_state:
    st.session_state.generated_elements = []

st.title('아이디어 탐색도구 (강제결합)')

# 1. 문제 정의
st.markdown("### 1. 문제 정의")
problem = st.text_input("", placeholder="예: 집에서 더 편안하게 작업할 수 있는 방법 찾기")
st.markdown("---")

# 2. 요소 선정 방식 선택
st.markdown("### 2. 요소 선정 방식을 선택하세요:")
element_selection_method = st.radio("", ('다른 사람에게 요청', '인공지능이 단어 생성'))
st.markdown("---")

# 3. 무작위 요소 선택 방식 선택
st.markdown("### 3. 요소 선택 방식을 선택하세요:")
element_choice_method = st.radio("", ('짝꿍이 선택', '자동으로 랜덤 선택'))
st.markdown("---")

# 다른 사람에게 요청 시나리오
if element_selection_method == '다른 사람에게 요청':
    custom_elements_input = st.text_input("4개의 단어를 입력하세요 (콤마로 구분):")
    custom_elements = custom_elements_input.split(',') if custom_elements_input else []
    elements_to_choose_from = custom_elements  # 이 라인은 변경 없음

# 인공지능이 단어 생성 시나리오
if element_selection_method == '인공지능이 단어 생성':
    if st.button("단어생성"):
        if problem:
            # 프롬프트 구성
            prompt_parts = [
                f"강제결합법을 이용하려 발명하려 합니다. 이 인공지능은 세상에 있는 단어중 아무거나 4개를 생성합니다. 단어는 콤마로 구분하여 한줄로 적어주세요.",
            ]

            # 첫 번째 API 키로 시도
            response_text = try_generate_content(gemini_api_key3, prompt_parts)

            # 첫 번째 API 키 실패 시, 두 번째 API 키로 재시도
            if response_text is None and gemini_api_key4 is not None:
                print("첫 번째 API 호출에 실패하여 두 번째 API 키로 재시도합니다.")
                response_text = try_generate_content(gemini_api_key4, prompt_parts)

            if response_text is not None:
                # 세션 상태의 generated_elements를 업데이트
                st.session_state.generated_elements = response_text.split(',')
                for word in st.session_state.generated_elements:
                    st.write(word)
            else:
                st.error("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")
        else:
            st.error("문제를 넣어주세요.")


# 짝꿍이 선택하는 경우
if element_choice_method == '짝꿍이 선택' and 'generated_elements' in st.session_state:
    st.session_state.chosen_element = st.radio("선택할 요소:", st.session_state.generated_elements)

# 자동으로 랜덤 선택하는 경우
if element_choice_method == '자동으로 랜덤 선택' and 'generated_elements' in st.session_state:
    if st.button("랜덤 요소 선택"):
        st.session_state.chosen_element = random.choice(st.session_state.generated_elements)
        st.write("랜덤으로 선택된 요소:", st.session_state.chosen_element)

# 강제 결합 아이디어 사용자가 입력
st.session_state.forced_combination_idea = st.text_area("선택된 요소들을 바탕으로 새로운 아이디어를 제시하세요:")

# 아이디어 평가 버튼
if st.button("인공지능아 내 생각 어떄?"):
    if problem and st.session_state.chosen_element and st.session_state.forced_combination_idea:
        # 프롬프트 구성
        prompt_parts = [
            f"강제결합법을 이용하려 학생이 아이디어를 생성했습니다. 문제는 '{problem}'이고, 강제결합된 단어는 '{st.session_state.chosen_element}'입니다. 둘을 합해서 만든 아이디어는 '{st.session_state.forced_combination_idea}'입니다. 평가해주고 칭찬해주세요.",
        ]

        # 첫 번째 API 키로 시도
        response_text = try_generate_content(gemini_api_key3, prompt_parts)

        # 첫 번째 API 키 실패 시, 두 번째 API 키로 재시도
        if response_text is None and gemini_api_key4 is not None:
            print("첫 번째 API 호출에 실패하여 두 번째 API 키로 재시도합니다.")
            response_text = try_generate_content(gemini_api_key4, prompt_parts)

        if response_text is not None:
            st.write(response_text)
        else:
            st.error("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")
    else:
        st.error("문제, 선택된 단어, 또는 아이디어를 입력하지 않았습니다.")


# # 1. 문제 정의
# problem = st.text_input("문제를 정의하세요:", placeholder="예: 집에서 더 편안하게 작업할 수 있는 방법 찾기")


# # 2. 요소 선정 방식 선택
# element_selection_method = st.radio("요소 선정 방식을 선택하세요:", ('다른 사람에게 요청', '인공지능이 단어 생성'))

# if element_selection_method == '다른 사람에게 요청':
#     # 사용자가 직접 입력
#     custom_elements = st.text_input("4개의 단어를 입력하세요 (콤마로 구분):").split(',')
# else:
#     # 인공지능 평가 버튼
#     if st.button("단어생성"):
#         if problem :
#             # 프롬프트 구성
#             prompt_parts = [
#                 f"강제결합법을 이용하려 발명하려 합니다. 이 인공지능은 세상에 있는 단어중 아무거나 4개를 생성합니다. 단어는 콤마로 구분하여 한줄로 적어주세요.",
#             ]

#             # 첫 번째 API 키로 시도
#             response_text = try_generate_content(gemini_api_key3, prompt_parts)
                    
#             # 첫 번째 API 키 실패 시, 두 번째 API 키로 재시도
#             if response_text is None and gemini_api_key4 is not None:
#                 print("첫 번째 API 호출에 실패하여 두 번째 API 키로 재시도합니다.")
#                 response_text = try_generate_content(gemini_api_key4, prompt_parts)
                    
#                     # 결과 출력
#             if response_text is not None:
#                 generated_elements = response_text.split(',')
#                 st.markdown(to_markdown(response_text))
#             else:
#                 st.error("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")
#         else:
#             st.error("문제를 넣어주세요.")
                
# # 3. 무작위 요소 선택 방식 선택
# element_choice_method = st.radio("요소 선택 방식을 선택하세요:", ('짝꿍이 선택', '자동으로 랜덤 선택'))

# # 짝꿍이 선택할 요소 목록 준비
# if element_selection_method == '다른 사람에게 요청':
#     elements_to_choose_from = custom_elements
# else:
#     # API 호출로 받은 단어들이 포함된 리스트를 사용
#     elements_to_choose_from = generated_elements

# # 짝꿍이 선택하는 경우 - 라디오 버튼을 사용하여 하나의 요소 선택
# if element_choice_method == '짝꿍이 선택':
#     chosen_element = st.radio("선택할 요소:", elements_to_choose_from)

#     # 선택된 요소 표시
#     if chosen_element:
#         st.write("짝꿍이 선택한 요소:", chosen_element)

# # 자동으로 랜덤 선택하는 경우 - 버튼 클릭으로 랜덤 요소 선택
# if element_choice_method == '자동으로 랜덤 선택':
#     # '랜덤 요소 선택' 버튼 추가
#     if st.button("랜덤 요소 선택"):
#         # 리스트가 비어 있는지 확인
#         if elements_to_choose_from:
#             chosen_element = random.choice(elements_to_choose_from)
#             st.write("랜덤으로 선택된 요소:", chosen_element)
#         else:
#             st.error("선택할 요소가 없습니다. 먼저 요소를 생성하거나 입력해주세요.")


# #4. 강제 결합 아이디어 사용자가 입력
# forced_combination_idea = st.text_area("선택된 요소들을 바탕으로 새로운 아이디어를 제시하세요:")

# #5. 아이디어 평가 (간단한 피드백 제공)
# if forced_combination_idea:
# # 여기서는 간단한 긍정적 피드백을 제공합니다. 실제 앱에서는 더 복잡한 평가 로직을 구현할 수 있습니다.
#     st.success("창의적인 아이디어를 제출해주셔서 감사합니다! 다음 단계로 넘어가 보세요.")
