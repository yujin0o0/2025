# ultra_glass_mbti.py
import streamlit as st
import random

# ----------------------------
# 16가지 MBTI 데이터
# ----------------------------
mbti_data = {
    "ISTJ": {"desc": "책임감이 강하고 체계적이며 안정성을 중시합니다.",
             "jobs": ["회계사", "데이터 분석가", "행정 공무원", "품질 관리 전문가", "법률 사무원"]},
    "ISFJ": {"desc": "헌신적이고 세심하며 타인을 잘 돌봅니다.",
             "jobs": ["간호사", "교사", "상담사", "사회복지사", "비서"]},
    "INFJ": {"desc": "이상주의적이며 깊은 통찰력을 지닙니다.",
             "jobs": ["심리학자", "상담사", "작가", "교육 컨설턴트", "사회복지사"]},
    "INTJ": {"desc": "전략적이고 분석적이며 장기 계획을 잘 세웁니다.",
             "jobs": ["연구원", "전략 컨설턴트", "엔지니어", "데이터 과학자", "발명가"]},
    "ISTP": {"desc": "문제 해결 능력이 뛰어나고 모험심이 있습니다.",
             "jobs": ["기술자", "응급구조사", "파일럿", "자동차 정비사", "탐험가"]},
    "ISFP": {"desc": "감성적이고 온화하며 미적 감각이 뛰어납니다.",
             "jobs": ["디자이너", "작곡가", "사진작가", "예술가", "플로리스트"]},
    "INFP": {"desc": "창의적이며 가치 중심적으로 살아갑니다.",
             "jobs": ["소설가", "상담사", "사회운동가", "심리학자", "교육자"]},
    "INTP": {"desc": "논리적이고 분석적이며 아이디어 탐구를 즐깁니다.",
             "jobs": ["과학자", "프로그래머", "발명가", "철학자", "데이터 분석가"]},
    "ESTP": {"desc": "활동적이고 즉흥적이며 도전을 즐깁니다.",
             "jobs": ["기업가", "세일즈 전문가", "운동선수", "경찰관", "파일럿"]},
    "ESFP": {"desc": "사교적이고 에너지가 넘치며 현재를 즐깁니다.",
             "jobs": ["배우", "이벤트 플래너", "여행 가이드", "방송인", "메이크업 아티스트"]},
    "ENFP": {"desc": "창의적이고 열정적이며 다양한 가능성을 탐구합니다.",
             "jobs": ["마케팅 전문가", "작가", "창업가", "광고 기획자", "콘텐츠 크리에이터"]},
    "ENTP": {"desc": "도전 정신이 강하고 새로운 시도를 즐깁니다.",
             "jobs": ["벤처기업가", "PD", "변호사", "기술 컨설턴트", "세일즈 전문가"]},
    "ESTJ": {"desc": "조직적이고 실용적이며 효율을 중시합니다.",
             "jobs": ["경영자", "군인", "프로젝트 매니저", "행정관", "감독관"]},
    "ESFJ": {"desc": "사람들을 돕고 화합을 중요시합니다.",
             "jobs": ["간호사", "교사", "HR 매니저", "사회복지사", "고객 서비스 전문가"]},
    "ENFJ": {"desc": "리더십이 뛰어나고 타인의 성장을 돕습니다.",
             "jobs": ["리더십 코치", "홍보 전문가", "외교관", "교육자", "비영리 단체 활동가"]},
    "ENTJ": {"desc": "목표 지향적이고 조직을 이끄는 데 능숙합니다.",
             "jobs": ["CEO", "전략 컨설턴트", "변호사", "투자 은행가", "기업 관리자"]}
}

# MBTI 색상 매핑
mbti_colors = {
    "I": "#6c63ff", "E": "#ff6584",
    "S": "#4cafef", "N": "#f5a623",
    "T": "#26de81", "F": "#ff9ff3",
    "J": "#45aaf2", "P": "#fd9644"
}

# ----------------------------
# Streamlit 설정
# ----------------------------
st.set_page_config(page_title="✨ 초호화 MBTI 진로 추천", page_icon="💎", layout="centered")

# ----------------------------
# CSS
# ----------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Baloo+2&display=swap');
        body {
            font-family: 'Baloo 2', cursive;
            background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #a1c4fd, #c2e9fb);
            background-size: 400% 400%;
            animation: gradientBG 12s ease infinite;
        }
        @keyframes gradientBG {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        .title {
            font-size: 48px;
            text-align: center;
            color: white;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        }
        .glass-card {
            backdrop-filter: blur(12px) saturate(150%);
            -webkit-backdrop-filter: blur(12px) saturate(150%);
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 25px;
            color: white;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(31,38,135,0.37);
        }
        .career-card {
            background: rgba(255,255,255,0.15);
            border-radius: 15px;
            padding: 12px;
            margin: 8px 0;
            font-size: 18px;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        .career-card:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }
        .stButton>button {
            background: linear-gradient(45deg, #ff6f91, #ff9671, #ffc75f);
            background-size: 300% 300%;
            animation: shine 4s linear infinite;
            color: white;
            font-size: 20px;
            font-weight: bold;
            border-radius: 12px;
            padding: 12px 30px;
            border: none;
            box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
        }
        @keyframes shine {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# UI
# ----------------------------
st.markdown("<div class='title'>💎 초호화 MBTI 성격 & 직업 추천 🌈</div>", unsafe_allow_html=True)
mbti_list = list(mbti_data.keys())
selected_mbti = st.selectbox("🔮 당신의 MBTI를 선택하세요", mbti_list)

if st.button("🌟 결과 보기 🌟"):
    info = mbti_data[selected_mbti]
    color_code = "".join([mbti_colors[ch] for ch in selected_mbti])
    st.markdown(f"<div class='glass-card'><h2 style='color:{mbti_colors[selected_mbti[0]]}'>{selected_mbti}</h2><p>{info['desc']}</p></div>", unsafe_allow_html=True)
    for job in info["jobs"]:
        emoji = random.choice(["💼", "🚀", "🎨", "📚", "💡", "🛠️", "🌏", "🏆", "🎯"])
        st.markdown(f"<div class='career-card'>{emoji} {job}</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2025 Ultra Glass MBTI Career App | Designed with ❤️")
