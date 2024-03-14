import pathlib
import textwrap
import google.generativeai as genai
import streamlit as st
import toml
from PIL import Image
import io
from openai import OpenAI

def to_markdown(text):
    text = text.replace('•', '*')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

# secrets.toml 파일 경로
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# secrets.toml 파일에서 API 키 값 가져오기
gemini_api_key1 = secrets.get("gemini_api_key1")
gemini_api_key2 = secrets.get("gemini_api_key2")

# OpenAI API 키 입력을 위한 사이드바 설정
openai_api_key = st.sidebar.text_input("OpenAI API 키를 입력하세요.", type="password")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=openai_api_key)


def try_generate_content(api_key, image):
    # API 키를 설정
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro-vision')
    try:
        # 콘텐츠 생성 시도
        response = model.generate_content(["이 사진은 화석표본입니다. 화석의 이름을 말해주고, 화석 생물이 살았던 모습도 자세히 묘사해주세요.", image])
        response.resolve()
        return response
    except Exception as e:
        # 예외 발생시 None 반환
        print(f"API 호출 실패: {e}")
        return None

# 핸드폰 사진 업로드 기능 추가
uploaded_file = st.file_uploader("핸드폰으로 화석표본을 가로로 찍어주세요.")

# 이미지가 업로드되었는지 확인git init

if uploaded_file is not None:
    # 이미지 바이트 문자열로 변환
    img_bytes = uploaded_file.read()

    # bytes 타입의 이미지 데이터를 PIL.Image.Image 객체로 변환
    img = Image.open(io.BytesIO(img_bytes))

    # 첫 번째 API 키로 시도
    response = try_generate_content(gemini_api_key1, img)
    
    # 첫 번째 API 키 실패 시, 두 번째 API 키로 재시도
    if response is None and gemini_api_key2 is not None:
        print("첫 번째 API 호출에 실패하여 두 번째 API 키로 재시도합니다.")
        response = try_generate_content(gemini_api_key2, img)
    
    # 결과가 성공적으로 반환되었는지 확인
    if response is not None:
        # 결과 표시
        st.image(img)  # 업로드된 사진 출력
        generated_text = response.text  # response.text를 변수에 저장
        st.markdown(response.text)

        # 이미지 생성 버튼
        if st.button("이미지 생성"):
            try:
                # DALL·E를 사용하여 이미지 생성 요청
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=generated_text,  # 분석된 텍스트를 프롬프트로 사용
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                # 생성된 이미지 URL 추출 및 표시
                generated_image_url = image_response.data[0].url
                st.image(generated_image_url, caption="Generated Image")
            except Exception as e:
                st.error(f"이미지 생성 중 오류가 발생했습니다: {e}")
    else:
        st.markdown("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")
    

else:
    st.markdown("핸드폰 사진을 업로드하세요.")
