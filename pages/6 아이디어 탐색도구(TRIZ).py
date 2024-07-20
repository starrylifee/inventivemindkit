import streamlit as st
import pathlib
import google.generativeai as genai
import toml
import textwrap

hide_github_icon = """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK{ display: none; }
    #MainMenu{ visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
"""

st.markdown(hide_github_icon, unsafe_allow_html=True)

# secrets.toml 파일 경로
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# secrets.toml 파일에서 API 키 값 가져오기
gemini_api_key3 = secrets.get("gemini_api_key3")
gemini_api_key4 = secrets.get("gemini_api_key4")


# 사용자 선택과 인공지능 추천 결과를 저장하기 위한 세션 상태 초기화
if 'selected_techniques' not in st.session_state:
    st.session_state['selected_techniques'] = []


triz_techniques = {
    "분할 (Segmentation)": "대상을 부분으로 나누거나, 분리할 수 있는 것으로 만들기.",
    "추출 (Extraction)": "필요한 부분만을 추출하거나 분리하기.",
    "지역적 품질 (Local Quality)": "대상의 구조를 비균등하게 만들기, 각 부분마다 다른 기능이나 특성을 갖게 하기.",
    "비대칭 (Asymmetry)": "대상을 대칭이 아니게 만들기, 대칭적인 대상을 비대칭적으로 변형하기.",
    "결합 (Merging)": "유사한 또는 서로 다른 대상을 결합하여 운영하기.",
    "범용성 (Universality)": "다목적으로 사용할 수 있게 만들기.",
    "중첩 (Nesting)": "하나의 객체를 다른 객체 안에 넣기.",
    "중량 제거 (Counter-Weight)": "대상의 무게를 줄이거나, 중력의 영향을 상쇄하기 위해 반대 무게를 사용하기.",
    "사전 대응 (Prior Counter-Action)": "예상되는 반대 행동을 미리 취하기.",
    "사전 행동 (Prior Action)": "필요한 조건을 미리 준비하거나 미리 실행하기.",
    "쿠션 (Cushion in Advance)": "예상되는 손실을 미리 방지하기 위해 조치를 취하기.",
    "등가물 (Equipotentiality)": "작업 조건을 변화시키지 않고 작업을 수행하기.",
    "역전 (Inversion)": "대상을 반대로 하거나 환경을 반대로 바꾸기.",
    "구면화 (Spheroidality)": "직선을 곡선으로, 평면을 구면으로 바꾸기.",
    "동적성 (Dynamics)": "대상이나 환경을 변화시킬 수 있게 만들기.",
    "부분 또는 과잉 작동 (Partial or Excessive Action)": "필요 이상으로 많이 또는 부족하게 작동시키기.",
    "차원 이동 (Transition to Another Dimension)": "대상을 여러 차원으로 확장하기.",
    "기계적 진동 (Mechanical Vibration)": "진동을 가하거나 진동의 주파수를 변경하기.",
    "주기적 작동 (Periodic Action)": "행동을 주기적으로 반복하기.",
    "유용성의 지속 (Continuity of Useful Action)": "지속적으로 작동하게 만들기.",
    "급속하게 (Rushing Through)": "과정을 빠르게 진행하기.",
    "환원 (Convert Harm into Benefit)": "해로운 요소를 유용하게 변환하기.",
    "피드백 (Feedback)": "작동 결과를 제어하는 데 사용하기.",
    "매개체 (Mediator)": "임시 또는 중간 매개체 사용하기.",
    "자기 서비스 (Self-Service)": "객체가 자신의 도움이나 자신의 문제를 스스로 해결하게 만들기.",
    "복사 (Copying)": "비싸거나 불편한 것 대신 저렴하거나 편리한 복사본을 사용하기.",
    "저렴한 단기 사용 (Cheap Short-Living Objects)": "장기간 사용하는 대신에 한 번 사용하고 버릴 수 있는 저렴한 버전을 사용하기.",
    "기계 시스템의 대체 (Replacement of Mechanical System)": "기계식 시스템을 센서, 자기장 등으로 대체하기.",
    "유체 사용 (Use of Fluids)": "고체 부품을 가스나 액체로 대체하기.",
    "유연한 껍질이나 얇은 필름 (Flexible Shells and Thin Films)": "대상을 유연한 껍질이나 얇은 필름으로 감싸기.",
    "구멍 뚫기 (Porous Materials)": "대상을 다공성으로 만들어 내부에 무언가를 채우기.",
    "색 변경 (Color Changes)": "대상의 색을 변경하거나 색의 투명도를 변화시키기.",
    "동질성 (Homogeneity)": "대상이나 대상의 환경을 동질적인 재료로 만들기.",
    "폐기물 또는 부산물 제거 (Discarding and Recovering)": "사용 후 버리거나 복원할 수 있는 부분을 만들기.",
    "매개변수 변화 (Parameter Changes)": "대상의 물리적 상태를 변화시키기 (예: 온도, 압력).",
    "상태 변환 (Phase Transition)": "물질의 상태를 변화시키기 (예: 고체에서 액체로).",
    "열 확장 (Thermal Expansion)": "물질의 열팽창 또는 열수축을 이용하기.",
    "강화된 산소 (Enriched Oxygen)": "산소 함량을 높여 과정의 효율을 증가시키기.",
    "휴지 상태 (Inert Atmosphere)": "반응을 막기 위해 비활성 가스나 환경을 사용하기.",
    "복합 재료 (Composite Materials)": "필요한 성질을 갖는 복합 재료 사용하기."
    }

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

st.title('아이디어 탐색도구 (TRIZ)')

# 사용자 입력
item_to_improve = st.text_input("개선하고 싶은 물건을 입력하세요:")

# 사용자가 스스로 기법을 선택할 것인지, AI 추천을 받을 것인지 선택
choice = st.radio("TRIZ 기법 선택 방법:", ["내가 스스로 발명기법 고르기", "인공지능의 추천 받아보기"])

if choice == "내가 스스로 발명기법 고르기":
    st.write("아래에서 마음에 드는 TRIZ 기법을 최대 2개까지 선택하세요:")

    # 컬럼 레이아웃 생성
    col1, col2 = st.columns(2)

    # 기법 목록을 반으로 나눔
    half = len(triz_techniques) // 2
    triz_techniques_items = list(triz_techniques.items())

    # 체크박스 선택 상태를 관리하는 함수
    def manage_selection(technique, key_suffix):
        with st.spinner("처리 중..."):
            # 선택 상태가 변경되었는지 확인
            current_selection = st.checkbox(technique, key=technique + key_suffix, value=technique in st.session_state['selected_techniques'])

            # 선택된 경우, 선택 목록에 추가
            if current_selection and technique not in st.session_state['selected_techniques']:
                if len(st.session_state['selected_techniques']) < 2:
                    st.session_state['selected_techniques'].append(technique)
                else:
                    st.warning("최대 2개까지만 선택할 수 있습니다.")
                    st.checkbox(technique, key=technique + key_suffix, value=False)  # 초과 선택 시 체크박스를 다시 해제
            elif not current_selection and technique in st.session_state['selected_techniques']:
                # 선택이 취소된 경우, 선택 목록에서 제거
                st.session_state['selected_techniques'].remove(technique)

    # 첫 번째 컬럼에 첫 번째 절반의 체크박스 배치
    with col1:
        for technique, _ in triz_techniques_items[:half]:
            manage_selection(technique, "1")

    # 두 번째 컬럼에 나머지 체크박스 배치
    with col2:
        for technique, _ in triz_techniques_items[half:]:
            manage_selection(technique, "2")


    # 선택된 기법 표시
    if st.session_state['selected_techniques']:
        st.write("선택된 기법:")
        for selected_technique in st.session_state['selected_techniques']:
            st.write(f"- {selected_technique}")


    # 사용자의 개선 아이디어 입력 받기
    improvement_idea = st.text_area("나의 개선 아이디어를 입력하세요:")

    # 인공지능 평가 버튼
    if st.button("인공지능 평가"):
        if item_to_improve and improvement_idea and st.session_state['selected_techniques']:
            # 프롬프트 구성
            prompt_parts = [
                f"{item_to_improve}를 발명기법을 이용하려 개선하려 합니다. {triz_techniques}에 있는40가지의 발명 기법 중에 {selected_technique}을 선택하여 {improvement_idea}를 생각해냈습니다. 아이디어에 대한 평가와 칭찬을 해주세요.",
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

elif choice == "인공지능의 추천 받아보기":
    # 인공지능 추천 로직 (가상 코드, 실제 구현 필요)
    if st.button("인공지능아 어떤 방법이 좋을까?"):
        if item_to_improve : 

            # 프롬프트 구성
            prompt_parts = [
                f"{item_to_improve}를 발명기법을 이용하려 개선하려 합니다. {triz_techniques}에 있는40가지의 발명 기법 중에 {item_to_improve}를 개선하기에 알맞는 발명기법을 3가지만 추천해주세요. 예시는 들지 말고 학생의 사고를 촉진할 확산적 질문으로 마무리해주세요.",
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
