import streamlit as st
import random

# 1. 문제 정의
problem = st.text_input("문제를 정의하세요:")

# 2. 요소 선정 방식 선택
element_selection_method = st.radio("요소 선정 방식을 선택하세요:", ('다른 사람에게 요청', '인공지능이 단어 생성'))

if element_selection_method == '다른 사람에게 요청':
    # 사용자가 직접 입력
    custom_elements = st.text_input("4개의 단어를 입력하세요 (콤마로 구분):").split(',')
else:
    # 인공지능이 생성
    predefined_words = ['커피', '우주', '자전거', '식물', '음악', '책', '테크놀로지', '여행']
    generated_elements = random.sample(predefined_words, 4)
    st.write("인공지능이 선택한 단어:", generated_elements)

# 3. 무작위 요소 선택 방식 선택
element_choice_method = st.radio("요소 선택 방식을 선택하세요:", ('짝꿍이 선택', '자동으로 랜덤 선택'))

if element_choice_method == '짝꿍이 선택':
    # 사용자가 직접 입력
    chosen_element = st.text_input("선택된 요소를 입력하세요:")
else:
    # 자동으로 랜덤 선택
    if element_selection_method == '다른 사람에게 요청':
        chosen_element = random.choice(custom_elements)
    else:
        chosen_element = random.choice(generated_elements)

        st.write("랜덤으로 선택된 요소:", chosen_element)

#4. 강제 결합 아이디어 사용자가 입력
forced_combination_idea = st.text_area("선택된 요소들을 바탕으로 새로운 아이디어를 제시하세요:")

#5. 아이디어 평가 (간단한 피드백 제공)
if forced_combination_idea:
# 여기서는 간단한 긍정적 피드백을 제공합니다. 실제 앱에서는 더 복잡한 평가 로직을 구현할 수 있습니다.
st.success("창의적인 아이디어를 제출해주셔서 감사합니다! 다음 단계로 넘어가 보세요.")
