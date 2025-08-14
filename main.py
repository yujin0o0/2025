# ultra_fancy_mbti_career_app.py
import streamlit as st
import random

# ----------------------------
# 데이터: MBTI 유형별 진로 추천
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
# Streamlit 페이지 설정
# ----------------------------
st.set_page_config(page_title="💎 초호화 MBTI 진로 추천", page_icon="🌈", layout="centered")

# ----------------------------
# CSS 애니메이션 + 스타일
# ----------------------------
st.markdown("""
    <style>
        /* 움직이는 배경 */
        body {
            background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #fcb69f, #ffdde1);
            background-size: 400% 400%;
            animation: gradientBG 10s ease infinite;
            font-family: 'Trebuchet MS', sans-serif;
        }
        @keyframes gradientBG {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        /* 제목 */
        .title {
            font-size: 50px;
            text-align: center;
            color: white;
            text-shadow: 3px 3px 8px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }

        /* 버튼 */
        .stButton>button {
            background: linear-gradient(45deg, #ff6f91, #ff9671, #ffc75f);
            background-size: 300% 300%;
            animation: shine 3s linear infinite;
            color: white;
            font-size: 20px;
            font-weight: bold;
            border-radius: 12px;
            padding: 12px 30px;
            border: none;
            box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.08);
            box-shadow: 0px 8px 20px rgba(0,0,0,0.4);
        }
        @keyframes shine {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        /* 결과 카드 */
        .career-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            padding: 20px;
            margin: 15px 0;
            font-size: 20px;
            text-align: center;
            font-weight: bold;
            color: #444;
            box-shadow: 0 5px 25px rgba(0,0,0,0.2);
            transform: perspective(600px) rotateX(0deg);
            transition: all 0.4s ease;
        }
        .career-card:hover {
            transform: perspective(600px) rotateX(5deg) scale(1.05);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# UI
# ----------------------------
st.markdown("<div class='title'>💎 초호화 MBTI 기반 진로 추천 🌈</div>", unsafe_allow_html=True)
st.write("✨ 당신의 MBTI 성향을 선택하면, 반짝이는 추천 직업을 보여드립니다! ✨")

mbti_types = list(career_recommendations.keys())
selected_mbti = st.selectbox("🔮 당신의 MBTI를 선택하세요", mbti_types)

if st.button("🌟 진로 추천 보기 🌟"):
    careers = career_recommendations.get(selected_mbti, [])
    if careers:
        st.markdown(f"## 🌈 {selected_mbti} 유형의 추천 직업 🌈")
        for job in careers:
            emoji = random.choice(["💼", "🚀", "🎨", "📚", "💡", "🛠️"])
            st.markdown(f"<div class='career-card'>{emoji} {job}</div>", unsafe_allow_html=True)
    else:
        st.warning("데이터가 없습니다 😢")

st.markdown("---")
st.caption("© 2025 Ultra Fancy MBTI Career App | Designed with 💖")
