import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import matplotlib.pyplot as plt
import plotly.express as px

# --- 기본 설정 ---
st.set_page_config(layout="wide", page_title="나의 스마트 비서: 포커스 & 성장 도우미")

# --- 세션 상태 초기화 ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = [] # Smart Pomodoro: {'name', 'complexity', 'focus_time', 'break_time', 'logged_focus_minutes', 'feedback'}
if 'pomodoro_running' not in st.session_state:
    st.session_state.pomodoro_running = False
if 'current_pomodoro_stage' not in st.session_state:
    st.session_state.current_pomodoro_stage = 'focus' # 'focus' or 'break'
if 'remaining_time' not in st.session_state:
    st.session_state.remaining_time = 0
if 'pomodoro_start_time' not in st.session_state:
    st.session_state.pomodoro_start_time = None
if 'pomodoro_task_name' not in st.session_state:
    st.session_state.pomodoro_task_name = ""

if 'habits' not in st.session_state:
    st.session_state.habits = [] # {'id', 'name', 'creation_date', 'tracking': {date: bool}}
if 'reflections' not in st.session_state:
    st.session_state.reflections = {} # {date: {'q1', 'q2', 'q3', 'summary', 'sentiment'}}

# --- 헬퍼 함수 ---
def get_today_date_str():
    return datetime.now().strftime("%Y-%m-%d")

# --- 1. 지능형 집중 타이머 (Smart Pomodoro) 모듈 ---
def smart_pomodoro_module():
    st.header("🧠 지능형 집중 타이머")
    st.write("당신의 작업 유형에 맞춰 최적의 집중 시간을 제안해 드립니다.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("💡 새로운 작업 설정")
        task_name = st.text_input("수행할 작업 이름", key="pomodoro_task_input")

        # ⭐️ AI 기반 작업 복잡성 추론 (간단화된 버전)
        complexity_options = ["매우 쉬움", "쉬움", "보통", "어려움", "매우 어려움"]
        selected_complexity = st.selectbox("작업 복잡성 (AI가 추론했다고 가정)", complexity_options, key="complexity_select")

        # ⭐️ 복잡성에 따른 집중/휴식 시간 제안 로직 (AI 시뮬레이션)
        focus_minutes = 25
        break_minutes = 5

        if selected_complexity == "매우 쉬움":
            focus_minutes = 15
            break_minutes = 3
        elif selected_complexity == "쉬움":
            focus_minutes = 20
            break_minutes = 4
        elif selected_complexity == "보통":
            focus_minutes = 25
            break_minutes = 5
        elif selected_complexity == "어려움":
            focus_minutes = 35
            break_minutes = 7
        elif selected_complexity == "매우 어려움":
            focus_minutes = 45
            break_minutes = 10

        st.info(f"✨ AI의 제안: 집중 {focus_minutes}분 / 휴식 {break_minutes}분")

        if st.button("작업 추가 및 시작 준비", key="add_task_button"):
            if task_name:
                st.session_state.pomodoro_task_name = task_name
                st.session_state.current_pomodoro_stage = 'focus'
                st.session_state.remaining_time = focus_minutes * 60
                st.session_state.pomodoro_running = False # Reset for start
                st.session_state.pomodoro_start_time = None
                st.session_state.tasks.append({
                    'name': task_name,
                    'complexity': selected_complexity,
                    'focus_time': focus_minutes,
                    'break_time': break_minutes,
                    'logged_focus_minutes': 0,
                    'feedback': None,
                    'date': get_today_date_str()
                })
                st.success(f"'{task_name}' 작업을 준비했습니다. 이제 타이머를 시작할 수 있습니다!")
                st.rerun()
            else:
                st.warning("작업 이름을 입력해주세요!")

    with col2:
        st.subheader("⏱️ 현재 타이머")
        if st.session_state.pomodoro_task_name:
            st.write(f"**작업:** {st.session_state.pomodoro_task_name}")
            status_text = st.empty()
            time_display = st.empty()

            if not st.session_state.pomodoro_running:
                status_text.write(f"상태: {st.session_state.current_pomodoro_stage} 준비중...")
                minutes = st.session_state.remaining_time // 60
                seconds = st.session_state.remaining_time % 60
                time_display.write(f"남은 시간: **{minutes:02d}:{seconds:02d}**")

            # 시작/중지 버튼
            if st.session_state.pomodoro_running:
                if st.button("중지", key="stop_pomodoro"):
                    st.session_state.pomodoro_running = False
                    status_text.warning("타이머 중지됨.")
                    st.rerun()
            else:
                if st.button("시작", key="start_pomodoro"):
                    st.session_state.pomodoro_running = True
                    st.session_state.pomodoro_start_time = datetime.now()
                    st.rerun()

            if st.session_state.pomodoro_running:
                # ⭐️ 논블로킹 타이머 시뮬레이션
                placeholder = st.empty()
                while st.session_state.remaining_time > 0 and st.session_state.pomodoro_running:
                    # 실제 시간을 계산하여 남은 시간 업데이트
                    elapsed_time = (datetime.now() - st.session_state.pomodoro_start_time).total_seconds()
                    
                    # 현재 단계의 총 시간 (task_idx를 찾아서 가져와야 함)
                    current_task = next((t for t in st.session_state.tasks if t['name'] == st.session_state.pomodoro_task_name), None)
                    if current_task:
                        if st.session_state.current_pomodoro_stage == 'focus':
                            total_stage_time = current_task['focus_time'] * 60
                        else:
                            total_stage_time = current_task['break_time'] * 60
                    else: # Fallback if task not found
                        total_stage_time = st.session_state.remaining_time # This is not ideal, implies constant value


                    st.session_state.remaining_time = max(0, int(total_stage_time - elapsed_time))

                    minutes = st.session_state.remaining_time // 60
                    seconds = st.session_state.remaining_time % 60
                    placeholder.write(f"상태: **{st.session_state.current_pomodoro_stage.capitalize()}** 🏃\n남은 시간: **{minutes:02d}:{seconds:02d}**")
                    time.sleep(1) # 1초마다 업데이트

                if st.session_state.remaining_time <= 0 and st.session_state.pomodoro_running:
                    st.session_state.pomodoro_running = False
                    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3", loop=False) # 알림음

                    if st.session_state.current_pomodoro_stage == 'focus':
                        st.success(f"🎊 {st.session_state.pomodoro_task_name} 집중 시간 완료! 🎉")
                        # ⭐️ AI 기반 휴식 시간 제안 (간단화된 버전)
                        suggested_break_action = random.choice([
                            "잠시 스트레칭하며 몸을 풀어보세요.",
                            "창 밖을 보며 눈을 쉬게 해주세요.",
                            "물 한 잔 마시며 재충전하세요.",
                            "좋아하는 음악을 짧게 들어보세요.",
                            "간단한 심호흡으로 마음을 진정시켜보세요."
                        ])
                        st.info(f"🌿 휴식 시간! {suggested_break_action}")
                        
                        # Update task log with completed focus minutes
                        for i, task in enumerate(st.session_state.tasks):
                            if task['name'] == st.session_state.pomodoro_task_name:
                                st.session_state.tasks[i]['logged_focus_minutes'] += current_task['focus_time']
                                break

                        st.session_state.current_pomodoro_stage = 'break'
                        st.session_state.remaining_time = current_task['break_time'] * 60
                        if st.button("휴식 시작", key="start_break_after_focus"):
                             st.session_state.pomodoro_running = True
                             st.session_state.pomodoro_start_time = datetime.now()
                             st.rerun()

                    elif st.session_state.current_pomodoro_stage == 'break':
                        st.success("✅ 휴식 시간 완료! 다시 집중할 준비 되셨나요?")
                        
                        # 피드백 입력
                        feedback = st.radio("집중도는 어떠셨나요?", ["매우 좋음", "좋음", "보통", "나쁨", "매우 나쁨"], key=f"feedback_{st.session_state.pomodoro_task_name}")
                        if st.button("피드백 제출 및 완료", key="complete_pomodoro_task"):
                            for i, task in enumerate(st.session_state.tasks):
                                if task['name'] == st.session_state.pomodoro_task_name:
                                    st.session_state.tasks[i]['feedback'] = feedback
                                    break
                            st.session_state.pomodoro_task_name = ""
                            st.info("작업이 완료되고 피드백이 저장되었습니다.")
                            st.rerun()

        else:
            st.info("왼쪽에서 작업을 추가해주세요.")

    st.markdown("---")
    st.subheader("📈 집중 기록")
    if st.session_state.tasks:
        df_tasks = pd.DataFrame(st.session_state.tasks)
        df_tasks['date'] = pd.to_datetime(df_tasks['date'])
        
        st.dataframe(df_tasks[['date', 'name', 'complexity', 'focus_time', 'logged_focus_minutes', 'feedback']].sort_values(by='date', ascending=False))
        
        # ⭐️ 개인별 최적 집중 시간/피드백 시각화 (예시)
        daily_focus = df_tasks.groupby('date')['logged_focus_minutes'].sum().reset_index()
        fig_daily = px.line(daily_focus, x='date', y='logged_focus_minutes', title='일별 총 집중 시간')
        st.plotly_chart(fig_daily)

        # 피드백 분포
        feedback_counts = df_tasks['feedback'].value_counts().reset_index()
        feedback_counts.columns = ['Feedback', 'Count']
        fig_feedback = px.pie(feedback_counts, names='Feedback', values='Count', title='집중도 피드백 분포')
        st.plotly_chart(fig_feedback)
    else:
        st.info("아직 집중 기록이 없습니다. 새로운 작업을 시작해보세요!")


# --- 2. 습관 분석기 모듈 ---
def habit_analyzer_module():
    st.header("💖 습관 분석기")
    st.write("당신의 습관을 기록하고, 그 속에서 당신의 성향을 발견하세요.")

    st.subheader("✅ 나의 습관 관리")
    habit_name = st.text_input("새로운 습관 추가", key="new_habit_input")
    if st.button("습관 추가", key="add_habit_button"):
        if habit_name:
            if not any(h['name'] == habit_name for h in st.session_state.habits):
                st.session_state.habits.append({
                    'id': len(st.session_state.habits) + 1,
                    'name': habit_name,
                    'creation_date': get_today_date_str(),
                    'tracking': {}
                })
                st.success(f"'{habit_name}' 습관이 추가되었습니다!")
            else:
                st.warning("이미 존재하는 습관입니다.")
        else:
            st.warning("습관 이름을 입력해주세요.")
    
    st.markdown("---")
    st.subheader("📊 오늘의 습관 기록")
    today = get_today_date_str()
    if st.session_state.habits:
        for i, habit in enumerate(st.session_state.habits):
            # 오늘의 기록이 없으면 False로 초기화
            if today not in habit['tracking']:
                habit['tracking'][today] = False
            
            checked = st.checkbox(
                f"[{habit['name']}] 오늘 달성?", 
                value=habit['tracking'].get(today, False), 
                key=f"habit_check_{habit['id']}_{today}"
            )
            if checked != habit['tracking'][today]:
                st.session_state.habits[i]['tracking'][today] = checked
                st.success(f"'{habit['name']}' 습관 기록 완료!")
                st.rerun() # Re-run to update status properly
    else:
        st.info("아직 추가된 습관이 없습니다. 위에서 새로운 습관을 추가해주세요.")

    st.markdown("---")
    st.subheader("⭐ 나의 행동 성향 프로파일링 (AI 시뮬레이션)")
    if st.session_state.habits:
        habit_stats = []
        for habit in st.session_state.habits:
            completed_days = sum(1 for date, completed in habit['tracking'].items() if completed)
            total_days = (datetime.now() - datetime.strptime(habit['creation_date'], "%Y-%m-%d")).days + 1
            if total_days == 0: total_days = 1 # Avoid division by zero for habits added today
            
            completion_rate = (completed_days / total_days) * 100 if total_days > 0 else 0
            habit_stats.append({'name': habit['name'], 'completed_days': completed_days, 'total_days': total_days, 'rate': completion_rate})
        
        df_habit_stats = pd.DataFrame(habit_stats)
        st.dataframe(df_habit_stats.sort_values(by='rate', ascending=False), hide_index=True)

        st.markdown("##### 💡 AI 분석 리포트")
        # ⭐️ AI 기반 성향 프로파일링 (간단화된 버전)
        st.write("당신의 습관 데이터를 분석한 결과입니다:")
        profile_messages = []

        if df_habit_stats['rate'].mean() > 70:
            profile_messages.append("✨ **꾸준함의 아이콘!** 전반적으로 습관 달성률이 높아 강한 의지와 꾸준함을 가지고 계십니다.")
        elif df_habit_stats['rate'].mean() < 40:
            profile_messages.append("💪 **새로운 시작을 위한 도약!** 아직 습관 형성이 어려울 수 있습니다. 작은 목표부터 시작해보는 건 어떠세요?")
        
        top_habit = df_habit_stats.loc[df_habit_stats['rate'].idxmax()]
        if top_habit['rate'] > 50:
            profile_messages.append(f"✅ 특히 **'{top_habit['name']}'** 습관에서 높은 성과를 보여, 해당 분야에 대한 집중력과 흥미가 뛰어납니다.")
            
        # Example for specific habits -> personality traits
        if any(h['name'] == '운동' and h['rate'] > 70 for h in habit_stats):
            profile_messages.append("🏃‍♀️ **활동적인 에너자이저!** 운동 습관이 잘 잡혀 있어 건강하고 활기찬 성향을 가지고 계십니다.")
        if any(h['name'] == '독서' and h['rate'] > 70 for h in habit_stats):
            profile_messages.append("📚 **지적인 탐구자!** 독서를 통해 꾸준히 지식을 쌓는 탐구적인 성향이 돋보입니다.")

        if profile_messages:
            for msg in profile_messages:
                st.success(msg)
        else:
            st.info("아직 분석할 데이터가 부족하거나, 특별한 성향 패턴을 발견하지 못했습니다.")
        
        # 일별 습관 달성률 시각화 (예시)
        all_dates = sorted(list(set(date for h in st.session_state.habits for date in h['tracking'].keys())))
        
        if all_dates:
            daily_completion_data = []
            for date_str in all_dates:
                completed_count = sum(1 for h in st.session_state.habits if h['tracking'].get(date_str, False))
                total_habits_on_date = sum(1 for h in st.session_state.habits if h['creation_date'] <= date_str) # Only count habits that existed
                
                if total_habits_on_date > 0:
                    daily_completion_data.append({'Date': date_str, 'Completion Rate': (completed_count / total_habits_on_date) * 100})
            
            if daily_completion_data:
                df_daily_completion = pd.DataFrame(daily_completion_data)
                df_daily_completion['Date'] = pd.to_datetime(df_daily_completion['Date'])
                fig = px.line(df_daily_completion, x='Date', y='Completion Rate', title='일별 전체 습관 달성률 추이')
                st.plotly_chart(fig)

    else:
        st.info("습관 분석을 위해 먼저 습관을 추가하고 기록해주세요.")


# --- 3. 자기전 회고 도우미 모듈 ---
def evening_reflection_module():
    st.header("🌙 자기전 회고 도우미")
    st.write("AI와 함께 하루를 되돌아보고 의미를 발견하세요.")

    today = get_today_date_str()
    st.subheader(f"🗓️ {today} 오늘 하루 회고하기")

    # 이미 오늘 회고를 작성했는지 확인
    if today in st.session_state.reflections:
        st.info("오늘은 이미 회고를 작성하셨습니다! 내일 다시 만나요.")
        st.markdown("---")
        st.subheader("오늘의 회고 내용")
        reflect_data = st.session_state.reflections[today]
        st.write(f"**오늘 기뻤던 일:** {reflect_data['q1']}")
        st.write(f"**오늘 배운 점:** {reflect_data['q2']}")
        st.write(f"**내일 기대하는 것:** {reflect_data['q3']}")
        st.markdown("##### 📝 AI 요약:")
        st.success(reflect_data['summary'])
        st.markdown(f"##### ✨ 오늘의 감성 점수: **{reflect_data['sentiment'].capitalize()}**")
    else:
        q1 = st.text_area("✍️ 오늘 기뻤던 일 한 가지는 무엇인가요?", key="reflect_q1")
        q2 = st.text_area("💡 오늘 새롭게 배우거나 느낀 점은 무엇인가요?", key="reflect_q2")
        q3 = st.text_area("🌟 내일 가장 기대하는 것은 무엇인가요?", key="reflect_q3")

        if st.button("회고 완료 및 AI 분석 시작", key="submit_reflection"):
            if q1 and q2 and q3:
                # ⭐️ AI 요약 및 감성 분석 (간단화된 버전)
                full_text = f"기뻤던 일: {q1}. 배운 점: {q2}. 내일 기대: {q3}."
                
                # 가상의 AI 요약 (키워드 추출 및 재구성)
                summary = f"오늘 하루는 '{q1}'으로 기뻤고, '{q2}'를 배운 의미 있는 하루였습니다. 내일은 '{q3}'를 기대하고 있습니다."
                
                # 가상의 AI 감성 분석 (간단한 키워드 기반)
                positive_keywords = ["기뻤", "배운", "기대", "좋은", "행복", "성공", "만족"]
                negative_keywords = ["힘들", "어렵", "실패", "슬픔", "짜증", "걱정"]
                
                sentiment_score = 0
                for keyword in positive_keywords:
                    if keyword in full_text:
                        sentiment_score += 1
                for keyword in negative_keywords:
                    if keyword in full_text:
                        sentiment_score -= 1
                
                if sentiment_score > 0:
                    sentiment = "긍정적"
                elif sentiment_score < 0:
                    sentiment = "부정적"
                else:
                    sentiment = "중립적"

                st.session_state.reflections[today] = {
                    'q1': q1,
                    'q2': q2,
                    'q3': q3,
                    'summary': summary,
                    'sentiment': sentiment
                }
                st.success("회고가 저장되고 AI 분석이 완료되었습니다!")
                st.rerun()
            else:
                st.warning("모든 질문에 답해주세요.")

    st.markdown("---")
    st.subheader("📚 나의 회고 기록 모아보기")
    if st.session_state.reflections:
        reflection_data_list = []
        for date, data in st.session_state.reflections.items():
            reflection_data_list.append({
                '날짜': date,
                '요약': data['summary'],
                '감성': data['sentiment']
            })
        
        df_reflections = pd.DataFrame(reflection_data_list)
        df_reflections['날짜'] = pd.to_datetime(df_reflections['날짜'])
        st.dataframe(df_reflections.sort_values(by='날짜', ascending=False), hide_index=True)

        # ⭐️ 감성 변화 추이 시각화
        sentiment_counts = df_reflections['감성'].value_counts().reset_index()
        sentiment_counts.columns = ['감성', '횟수']
        fig_sentiment = px.pie(sentiment_counts, names='감성', values='횟수', title='전반적인 감성 분포')
        st.plotly_chart(fig_sentiment)

        # 일별 감성 변화
        daily_sentiment_mapping = {"긍정적": 1, "중립적": 0, "부정적": -1}
        df_reflections['감성_점수'] = df_reflections['감성'].map(daily_sentiment_mapping)
        fig_daily_sentiment = px.line(df_reflections.sort_values('날짜'), x='날짜', y='감성_점수', title='일별 감성 추이 (긍정:1, 중립:0, 부정:-1)')
        st.plotly_chart(fig_daily_sentiment)


    else:
        st.info("아직 작성된 회고가 없습니다.")


# --- 메인 앱 레이아웃 ---
st.title("🚀 나의 스마트 비서: 포커스 & 성장 도우미")
st.markdown("---")

# 사이드바 메뉴
selected_module = st.sidebar.radio(
    "메뉴",
    ("🧠 집중 타이머", "💖 습관 분석기", "🌙 자기전 회고"),
    key="main_menu_selection"
)

if selected_module == "🧠 집중 타이머":
    smart_pomodoro_module()
elif selected_module == "💖 습관 분석기":
    habit_analyzer_module()
elif selected_module == "🌙 자기전 회고":
    evening_reflection_module()

st.sidebar.markdown("---")
st.sidebar.write("✨ 당신의 하루를 더 스마트하게!")

# 사용자 가입 유도 (게스트 계정 컨셉)
st.sidebar.markdown("---")
st.sidebar.subheader("😊 잠깐만요!")
st.sidebar.info("더 많은 기능과 데이터 영구 저장을 위해 지금 바로 **가입**해보시는 건 어때요? 😉")

