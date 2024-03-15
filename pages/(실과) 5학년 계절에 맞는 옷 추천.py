import streamlit as st
import pandas as pd
import requests
from openai import OpenAI

# OpenWeatherMap API 키 설정
API_KEY = "79ee6b1a97442180efa505de6c43cee2"  # API 키를 입력하세요
OPENAI_API_KEY = st.sidebar.text_input("OpenAI API 키를 입력하세요.", type="password")

st.sidebar.markdown("""
    ## OpenAI API 키 입력
    아래에 OpenAI API 키를 입력하세요. 입력된 키는 안전하게 저장되며,
    이미지를 생성되는 데 사용됩니다. API가 입력되면 선택된 옷으로 코디를 할 수 있습니다.
""")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)


def get_coordinates(city_name):
    """도시 이름으로부터 위도와 경도를 검색합니다."""
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
    response = requests.get(geocode_url)
    data = response.json()
    if data:
        return data[0]['lat'], data[0]['lon']
    else:
        return None, None

def get_weather_data(lat, lon):
    """위도와 경도를 사용하여 현재 온도를 검색합니다."""
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(weather_url)
    weather_data = response.json()
    return weather_data['main']['temp']

def recommend_clothes(df, temperature):
    """온도에 따라 옷을 추천합니다."""
    if temperature < 10:
        return df[df['Category'] == '겨울']
    elif 10 <= temperature < 20:
        return df[df['Category'] == '봄/가을']
    else:
        return df[df['Category'] == '여름']

# 앱 타이틀
st.title("옷 추천 시스템")

# 날씨 정보 입력 방법 선택
weather_input_method = st.radio("날씨 정보 입력 방법을 선택하세요.", ('자동', '수동'))

temperature = None  # 초기 온도 설정
if weather_input_method == '자동':
    city_name = st.text_input("도시 이름을 입력하세요.")
    if city_name:
        lat, lon = get_coordinates(city_name)
        if lat is not None and lon is not None:
            temperature = get_weather_data(lat, lon)
            st.write(f"현재 온도(자동): {temperature:.2f}°C")
        else:
            st.error("해당 도시의 날씨 정보를 찾을 수 없습니다.")
else:
    temperature = st.slider("현재 온도를 입력하세요", min_value=-20, max_value=40, value=20)
    st.write(f"현재 온도(수동): {temperature}°C")

# 엑셀 파일 업로드 부분 추가
uploaded_file = st.file_uploader("옷 목록 엑셀 파일을 업로드하세요.", type=["xlsx"])

# 샘플 파일 다운로드 링크 추가
sample_file_url = "https://github.com/your_username/your_repository/blob/main/data/sample_clothes_100items.xlsx?raw=true"
st.markdown(f"샘플 파일로 연습해보고, 샘플처럼 자신의 옷을 정리해서 넣어보세요. [샘플 파일 다운로드]({sample_file_url})", unsafe_allow_html=True)

if uploaded_file is not None and temperature is not None:
    df = pd.read_excel(uploaded_file)
    recommended_clothes = recommend_clothes(df, temperature)
    st.write("추천 옷 목록:")

    selected_items_descriptions = []
    for index, row in recommended_clothes.iterrows():
        # 체크박스로 옷 선택
        if st.checkbox(f"{row['Item']} ({row['Color']}, {row['Material']})", key=row['Item']):
            selected_items_descriptions.append(f"{row['Item']}을 입고 있는")

    # 선택된 모든 옷 항목들을 하나의 프롬프트로 결합
    if selected_items_descriptions and OPENAI_API_KEY:
        combined_prompt = ", ".join(selected_items_descriptions[:-1]) + " 및 " + selected_items_descriptions[-1] + " 남자 1명과 여자 1명"
        
        if st.button("이미지 생성"):
            # DALL·E를 사용하여 이미지 생성 요청 (하나의 이미지로 여러 옷 항목 표현)
            image_response = client.images.generate(
                prompt=combined_prompt,
                n=1,
                size="1024x1024",
                model="dall-e-3",
                quality="standard",
            )
            # 생성된 이미지 URL 추출 및 표시
            generated_image_url = image_response.data[0].url
            st.image(generated_image_url, caption="Generated Image")
