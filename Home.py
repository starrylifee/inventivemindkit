import streamlit as st

# 홈 페이지의 타이틀 설정
st.title('초등학생용 인공지능도구 모음 홈페이지')

# 애플리케이션 소개
st.markdown("""
    ## 🌟 안녕하세요!
    이 애플리케이션은 여러 가지 인공지능 도구들을 모아 놓은 곳입니다.
""")

# 추가적인 정보 제공
st.markdown("""
    ## 🚀 시작하기
    왼쪽의 탐색 바를 사용하여 원하는 도구를 선택하고 사용해 보세요. > 표시를 누르면 인공지능 도구 리스트가 나옵니다.
""")

# 도구 1: 내 작품 평가 받기
st.subheader('(미술) 내 작품 평가 받기')
st.write('이 도구를 사용하면 내가 그린 그림의 제목을 추천해주고, 장점과 보완할 점을 알려줍니다.')

# 구글 폼 링크 추가
st.markdown("""
    ## 📝 인공지능 수업 도구 의뢰
    이 특별한 인공지능 수업 도구가 필요하신가요? 제작해드리겠습니다. [이곳을 클릭](https://forms.gle/HC8ePNYhQzoX2Mio9)하여 의뢰 구글 폼에 접속해 주세요.
""", unsafe_allow_html=True)
