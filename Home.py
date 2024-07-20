import streamlit as st

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

# 홈 페이지의 타이틀 설정
st.title('초등학생용 인공지능 발명도구 모음')

# 애플리케이션 소개
st.markdown("""
    ## 🌟 안녕하세요!
    이 애플리케이션은 여러분이 발명을 할 때 도움을 줄 수 있는 도구들을 모아 놓은 곳입니다.
""")

# 추가적인 정보 제공
st.markdown("""
    ## 🚀 시작하기
    왼쪽의 탐색 바를 사용하여 원하는 도구를 선택하고 사용해 보세요.  '>' 표시를 누르면 인공지능 도구 리스트가 나옵니다.
""")

# 구글 폼 링크 추가
st.markdown("""
    ## 📝 인공지능 수업 도구 의뢰
    특별한 인공지능 수업 도구가 필요하신가요?  직접 제작해드리겠습니다.  [이곳을 클릭](https://forms.gle/HC8ePNYhQzoX2Mio9)하여 구글 폼에 접속해 주세요.
""", unsafe_allow_html=True)