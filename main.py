# mbti_career_app.py
import streamlit as st

# ----------------------------
# MBTI 유형별 진로 추천 데이터
# ----------------------------
career_recommendations = {
    "ISTJ": ["회계사", "데이터 분석가", "행정 공무원"],
    "ISFJ": ["간호사", "교사", "상담사"],
    "INFJ": ["작가", "심리학자", "사회복지사"],
    "INTJ": ["연구원", "전략 컨설턴트", "엔지니어"],
    "ISTP": ["기술자", "응급구조사", "파일럿"],
    "ISFP": ["디자이너", "작곡가", "사진작가"],
    "INFP": ["소설가", "상담사", "사회운동가"],
    "INTP": ["과학자", "프로그래머", "발명가"],
    "ESTP": ["기업가", "세일즈 전문가", "운동선수"],
    "ESFP": ["배우", "이벤트 플래너", "여행 가이드"],
    "ENFP": ["마케팅 전문가", "작가", "창업가"],
    "ENTP": ["벤처기업가", "PD", "변호사"],
    "ESTJ": ["경영자", "군인", "프로젝트 매니저"],
    "ESFJ": ["간호사", "교사", "HR 매니저"],
    "ENFJ": ["리더십 코치", "홍보 전문가", "외교관"],
    "ENTJ": ["CEO", "전략 컨설턴트", "변호사"]
}

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="MBTI 기반 진로 추천", page_icon="🎯", layout="centered")

st.title("🎯 MBTI 기반 진로 추천 웹앱")
st.write("당신의 MBTI 성향을 선택하면, 어울리는 직업을 추천해드립니다!")

# MBTI 선택
mbti_types = list(career_recommendations.keys())
selected_mbti = st.selectbox("당신의 MBTI를 선택하세요", mbti_types)

# 결과 버튼
if st.button("진로 추천 보기"):
    careers = career_recommendations.get(selected_mbti, [])
    if careers:
        st.success(f"✅ {selected_mbti} 유형에 어울리는 진로")
        for job in careers:
            st.write(f"- {job}")
    else:
        st.warning("해당 MBTI 유형에 대한 데이터가 없습니다.")

# 푸터
st.markdown("---")
st.caption("© 2025 MBTI Career Education App | Streamlit Demo")

