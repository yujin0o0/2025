import streamlit as st
from datetime import datetime, timedelta
import time
import random

# --- 기본 설정 (페이지 레이아웃 및 타이틀) ---
st.set_page_config(
    layout="wide",
    page_title="나의 스마트 비서: 포커스 & 성장 도우미",
    initial_sidebar_state="expanded" # 사이드바 기본 확장
)

# --- 세션 상태 초기화 ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = [] # Smart Pomodoro: {'name', 'complexity_level', 'focus_duration_minutes', 'break_duration_minutes', 'logged_focus_minutes', 'feedback', 'date'}
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
    st.session_state.reflections = {} # {date: {'q1', 'q2', 'q3', 'summary', 'sentiment_level'}}

# --- 헬퍼 함수 ---
def get_today_date_str():
    return datetime.now().strftime("%Y-%m-%d")

# --- 모듈별 함수 정의 ---

# 1. 지능형 집중 타이머 (Smart Pomodoro) 모듈
def smart_pomodoro_module():
    st.markdown("## 🧠 집중력 부스터! 지능형 집중 타이머 🚀")
    st.write("당신의 작업 스타일에 맞춰 최적의 집중과 휴식 시간을 제안해 드립니다. 지금 바로 생산성을 최대로 끌어올리세요!")

    st.markdown("---") # 시각적 구분선

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🎯 새로운 작업 설정하기")
        task_name = st.text_input("수행할 작업 이름을 입력하세요", key="pomodoro_task_input", placeholder="예: 보고서 작성, 코딩 학습")

        # ⭐️ AI 기반 작업 복잡성 추론 (규칙 기반 시뮬레이션)
        complexity_options = ["15분", "20분", "25분", "30분", "35분", "40분", "45분", "50분"]
        selected_complexity = st.selectbox("집중 시간 설정", complexity_options, key="complexity_select")

        # ⭐️ 복잡성에 따른 집중/휴식 시간 제안 로직 (AI 시뮬레이션)
        focus_minutes_suggestion = 25
        break_minutes_suggestion = 5

        if selected_complexity == "15분":
            focus_minutes_suggestion = 15
            break_minutes_suggestion = 5
        elif selected_complexity == "20분":
            focus_minutes_suggestion = 20
            break_minutes_suggestion = 5
        elif selected_complexity == "25분":
            focus_minutes_suggestion = 25
            break_minutes_suggestion = 5
        elif selected_complexity == "30분":
            focus_minutes_suggestion = 30
            break_minutes_suggestion = 5
        elif selected_complexity == "35분":
            focus_minutes_suggestion = 35
            break_minutes_suggestion = 5
        elif selected_complexity == "40분":
            focus_minutes_suggestion = 40
            break_minutes_suggestion = 10
        elif selected_complexity == "45분":
            focus_minutes_suggestion = 45
            break_minutes_suggestion = 10
        elif selected_complexity == "50분":
            focus_minutes_suggestion = 50
            break_minutes_suggestion = 10



        st.success(f"✨ AI의 최적화된 제안: **집중 {focus_minutes_suggestion}분** / **휴식 {break_minutes_suggestion}분**")

        if st.button("🚀 작업 추가 및 타이머 시작 준비", key="add_task_button", use_container_width=True):
            if task_name:
                st.session_state.pomodoro_task_name = task_name
                st.session_state.current_pomodoro_stage = 'focus'
                st.session_state.remaining_time = focus_minutes_suggestion * 60 # Initial setup
                st.session_state.pomodoro_running = False # Reset for start
                st.session_state.pomodoro_start_time = None
                
                # Check if task already exists in current session, update it. Otherwise add.
                task_found = False
                for i, task in enumerate(st.session_state.tasks):
                    # Check for an existing task with the same name on the same day that is not yet completed (feedback is None)
                    if task['name'] == task_name and task['date'] == get_today_date_str() and task['feedback'] is None:
                        st.session_state.tasks[i].update({
                            'complexity_level': selected_complexity,
                            'focus_duration_minutes': focus_minutes_suggestion,
                            'break_duration_minutes': break_minutes_suggestion,
                        })
                        task_found = True
                        break
                if not task_found:
                    st.session_state.tasks.append({
                        'name': task_name,
                        'complexity_level': selected_complexity,
                        'focus_duration_minutes': focus_minutes_suggestion,
                        'break_duration_minutes': break_minutes_suggestion,
                        'logged_focus_minutes': 0, # Total focus minutes logged for this task
                        'feedback': None, # To mark task as incomplete initially
                        'date': get_today_date_str()
                    })
                st.success(f"🎉 '{task_name}' 작업을 위해 타이머가 준비되었습니다. '시작' 버튼을 눌러 집중하세요!")
                st.rerun() # Refresh to show timer status
            else:
                st.warning("앗, 작업 이름을 입력해야 시작할 수 있어요! 😅")

    with col2:
        st.markdown("### ⏱️ 현재 타이머 상태")
        if st.session_state.pomodoro_task_name:
            st.write(f"**진행 중인 작업:** **`{st.session_state.pomodoro_task_name}`**")
            
            # --- 남은 시간 디스플레이! 크고 아름답게! ---
            time_placeholder = st.empty() # Timer will update here
            
            # Find the current task being run to get its configured focus/break times
            current_task_details = next((t for t in st.session_state.tasks if t['name'] == st.session_state.pomodoro_task_name and t['date'] == get_today_date_str() and t['feedback'] is None), None)
            
            if current_task_details is None:
                st.error("현재 진행 중인 작업 정보가 없어요 😥 새 작업을 다시 설정해주세요!")
                st.session_state.pomodoro_task_name = "" 
                return

            # Display initial state before timer starts
            if not st.session_state.pomodoro_running:
                minutes = st.session_state.remaining_time // 60
                seconds = st.session_state.remaining_time % 60
                time_placeholder.markdown(
                    f"<div style='text-align: center; font-size: 1.5em; font-weight: bold;'>{st.session_state.current_pomodoro_stage.capitalize()} 준비</div>"
                    f"<div style='text-align: center; font-size: 4em; font-weight: bolder; color: #FF6347;'>{minutes:02d}:{seconds:02d}</div>",
                    unsafe_allow_html=True
                )
            
            # Buttons
            button_col1, button_col2 = st.columns(2)
            with button_col1:
                if st.session_state.pomodoro_running:
                    if st.button("⏹️ 중지하기", key="stop_pomodoro", use_container_width=True):
                        st.session_state.pomodoro_running = False
                        st.session_state.pomodoro_start_time = None
                        st.warning("타이머가 잠시 멈췄어요. 다시 시작하거나 재설정하세요.")
                        st.rerun()
                else:
                    if st.button("▶️ 시작하기", key="start_pomodoro", use_container_width=True):
                        st.session_state.pomodoro_running = True
                        if st.session_state.current_pomodoro_stage == 'focus':
                            st.session_state.remaining_time = current_task_details['focus_duration_minutes'] * 60
                        else: # break
                            st.session_state.remaining_time = current_task_details['break_duration_minutes'] * 60
                        st.session_state.pomodoro_start_time = datetime.now()
                        st.rerun()

            if st.session_state.pomodoro_running:
                start_time_of_stage = st.session_state.pomodoro_start_time
                initial_remaining_for_stage = st.session_state.remaining_time # This holds the actual seconds configured for the stage

                while st.session_state.remaining_time > 0 and st.session_state.pomodoro_running:
                    elapsed_seconds = int((datetime.now() - start_time_of_stage).total_seconds())
                    st.session_state.remaining_time = max(0, initial_remaining_for_stage - elapsed_seconds)

                    minutes = st.session_state.remaining_time // 60
                    seconds = st.session_state.remaining_time % 60
                    
                    # 🚀🚀🚀 남은 시간 표시 스타일 강화! 🚀🚀🚀
                    current_stage_text = "집중 중" if st.session_state.current_pomodoro_stage == 'focus' else "휴식 중"
                    timer_color = "#28a745" if st.session_state.current_pomodoro_stage == 'focus' else "#007bff"
                    time_placeholder.markdown(
                        f"<div style='text-align: center; font-size: 1.5em; font-weight: bold;'>{current_stage_text} 🏃</div>"
                        f"<div style='text-align: center; font-size: 4em; font-weight: bolder; color: {timer_color};'>{minutes:02d}:{seconds:02d}</div>",
                        unsafe_allow_html=True
                    )
                    time.sleep(1) # 1초 대기

                if st.session_state.remaining_time <= 0 and st.session_state.pomodoro_running:
                    st.session_state.pomodoro_running = False
                    st.session_state.pomodoro_start_time = None

                    st.balloons() # 시각적 완료 알림

                    if st.session_state.current_pomodoro_stage == 'focus':
                        st.success(f"🎊 **'{st.session_state.pomodoro_task_name}' 집중 시간 완료!** 잠시 숨을 돌려요 🎉")
                        suggested_break_action = random.choice([
                            "잠시 스트레칭하며 몸을 풀어보세요.",
                            "창 밖을 보며 눈을 쉬게 해주세요.",
                            "물 한 잔 마시며 재충전하세요.",
                            "가벼운 명상으로 마음을 진정시켜보세요."
                        ])
                        st.info(f"🌿 **AI의 휴식 제안:** {suggested_break_action}")
                        
                        for i, task in enumerate(st.session_state.tasks):
                            if task['name'] == st.session_state.pomodoro_task_name and task['date'] == get_today_date_str() and task['feedback'] is None:
                                st.session_state.tasks[i]['logged_focus_minutes'] += current_task_details['focus_duration_minutes']
                                break

                        st.session_state.current_pomodoro_stage = 'break'
                        if st.button("🧘‍♀️ 휴식 시간 시작!", key="start_break_after_focus", use_container_width=True):
                             st.session_state.pomodoro_running = True
                             st.session_state.pomodoro_start_time = datetime.now()
                             st.rerun()
                    elif st.session_state.current_pomodoro_stage == 'break':
                        st.success("✅ **휴식 시간도 완료!** 이제 다시 활기찬 집중을 시작할 준비 되셨나요?")
                        
                        feedback = st.radio("오늘 집중도는 어떠셨나요?", ["매우 좋음", "좋음", "보통", "나쁨", "매우 나쁨"], key=f"feedback_rating_{st.session_state.pomodoro_task_name}_{get_today_date_str()}")
                        if st.button("✅ 피드백 제출 및 작업 완료", key="complete_pomodoro_task", use_container_width=True):
                            for i, task in enumerate(st.session_state.tasks):
                                if task['name'] == st.session_state.pomodoro_task_name and task['date'] == get_today_date_str() and task['feedback'] is None:
                                    st.session_state.tasks[i]['feedback'] = feedback
                                    break
                            st.session_state.pomodoro_task_name = ""
                            st.info("✨ 수고하셨습니다! 작업이 성공적으로 완료되고 피드백이 저장되었습니다.")
                            st.rerun()
            else: # If timer not running and task is set up
                st.info("💡 시작 버튼을 눌러 집중 타이머를 가동해보세요!")

        else:
            st.info("✨ 왼쪽에서 새로운 집중 작업을 설정해주세요. 당신의 생산성을 높여줄 거예요!")

    st.markdown("---")
    st.markdown("### 📈 나의 집중 기록 한눈에 보기")
    if st.session_state.tasks:
        st.markdown("##### 📅 전체 집중 세션 이력:")
        # Display task data
        for task in reversed(st.session_state.tasks): # Show latest first
            feedback_display = task['feedback'] if task['feedback'] else "진행 중 / 미완료"
            st.markdown(
                f"- **날짜:** `{task['date']}`\n"
                f"  **작업:** `{task['name']}` (난이도: `{task['complexity_level'].split(' ')[0]}`)\n" # '매우 쉬움 (간단한 응답)' -> '매우 쉬움'
                f"  **집중 시간:** `{task['logged_focus_minutes']}`분 (목표 `{task['focus_duration_minutes']}`분)\n"
                f"  **피드백:** **`{feedback_display}`**"
            )
            st.markdown("---") # 각 기록별 구분선
        
        st.markdown("##### 📊 나의 집중 패턴 분석 리포트:")
        completed_tasks = [t for t in st.session_state.tasks if t['feedback'] is not None]
        if completed_tasks:
            total_logged_minutes = sum(t['logged_focus_minutes'] for t in completed_tasks)
            st.write(f"🚀 **총 집중 기록 시간:** **`{total_logged_minutes}`분** 동안 열심히 집중하셨네요!")

            # Feedback distribution (manual count)
            feedback_counts = {}
            for task in completed_tasks:
                feedback_counts[task['feedback']] = feedback_counts.get(task['feedback'], 0) + 1
            
            if feedback_counts:
                st.write("- **집중도 피드백 분포:**")
                for fb, count in feedback_counts.items():
                    st.write(f"  - `{fb}`: `{count}`회 (총 {len(completed_tasks)}회 중)")
            else:
                st.info("피드백 데이터가 아직 부족해요. 작업을 더 많이 완료해주세요!")
        else:
            st.info("아직 완료된 집중 기록이 없습니다. 타이머를 사용해서 기록을 쌓아보세요!")
    else:
        st.info("아직 집중 기록이 없습니다. 첫 번째 작업을 시작하고 멋진 기록을 만들어보세요! 😊")


# 2. 습관 분석기 모듈
def habit_analyzer_module():
    st.markdown("## 💖 습관 파워업! 행동 성향 프로파일러 ✨")
    st.write("당신의 작은 습관들이 어떻게 큰 변화를 만드는지 기록하고, 숨겨진 당신의 행동 성향을 발견해보세요.")
    
    st.markdown("---")

    st.markdown("### ✅ 나의 소중한 습관 관리")
    habit_name = st.text_input("추가하고 싶은 새로운 습관은 무엇인가요?", key="new_habit_input", placeholder="예: 매일 물 8잔 마시기, 아침 일찍 일어나기")
    if st.button("➕ 새 습관 추가하기", key="add_habit_button", use_container_width=True):
        if habit_name:
            if not any(h['name'] == habit_name for h in st.session_state.habits):
                st.session_state.habits.append({
                    'id': len(st.session_state.habits) + 1,
                    'name': habit_name,
                    'creation_date': get_today_date_str(),
                    'tracking': {}
                })
                st.success(f"🌟 '{habit_name}' 습관이 성공적으로 추가되었습니다!")
            else:
                st.warning("이런! 이미 같은 이름의 습관이 있어요. 다른 이름을 써볼까요? 🤔")
        else:
            st.warning("습관 이름을 입력해주세요. 어떤 좋은 습관을 만들고 싶으신가요? 🌱")
    
    st.markdown("---")
    st.markdown("### 📅 오늘의 습관 달성 기록하기")
    today = get_today_date_str()
    if st.session_state.habits:
        # Streamlit recreates widgets on each run, so checkbox states must be carefully managed.
        # We handle state update for each checkbox. If any changes, rerun will reflect them.
        for i, habit in enumerate(st.session_state.habits):
            if today not in habit['tracking']:
                st.session_state.habits[i]['tracking'][today] = False
            
            initial_checked_state = st.session_state.habits[i]['tracking'][today]
            checked_this_run = st.checkbox(
                f"**[{habit['name']}]** 오늘 달성했나요?", 
                value=initial_checked_state, 
                key=f"habit_check_{habit['id']}_{today}"
            )
            
            if checked_this_run != initial_checked_state:
                st.session_state.habits[i]['tracking'][today] = checked_this_run
                st.info(f"☑️ '{habit['name']}' 습관 기록이 업데이트되었습니다!") # Inform user instantly
                st.rerun() # Trigger a rerun to update immediately, though user interaction can cause it anyway
    else:
        st.info("아직 추가된 습관이 없어요. 위에서 첫 번째 습관을 추가해보세요! 🌈")

    st.markdown("---")
    st.markdown("### ⭐ AI가 분석한 나의 행동 성향 프로파일")
    if st.session_state.habits:
        habit_stats = []
        for habit in st.session_state.habits:
            completed_days = sum(1 for date, completed in habit['tracking'].items() if completed)
            
            start_date_obj = datetime.strptime(habit['creation_date'], "%Y-%m-%d")
            total_days_tracked = (datetime.now() - start_date_obj).days + 1
            
            if total_days_tracked <= 0: total_days_tracked = 1 # Safety for new habits
            
            completion_rate = (completed_days / total_days_tracked) * 100
            habit_stats.append({
                'name': habit['name'], 
                'completed_days': completed_days, 
                'total_days_tracked': total_days_tracked, 
                'rate': completion_rate
            })
        
        habit_stats_sorted = sorted(habit_stats, key=lambda x: x['rate'], reverse=True)
        st.markdown("##### ✅ 현재 나의 습관별 달성률 현황:")
        for hs in habit_stats_sorted:
            st.write(f"- **`{hs['name']}`**: `{hs['rate']:.1f}`% 달성 (`{hs['completed_days']}`/`{hs['total_days_tracked']}`일 기록)")

        st.markdown("##### 💡 AI가 읽어주는 당신의 행동 패턴:")
        profile_messages = []

        overall_rates = [h['rate'] for h in habit_stats if h['total_days_tracked'] > 1] # Exclude habits created today for avg
        if overall_rates:
            avg_rate = sum(overall_rates) / len(overall_rates)
            if avg_rate > 75:
                profile_messages.append("✨ **최고의 꾸준함!** 당신은 목표를 향해 흔들림 없이 나아가는 **강력한 의지의 소유자**입니다.")
            elif avg_rate > 50:
                profile_messages.append("👍 **성장 중인 노력파!** 꾸준함이 돋보이며, 조금 더 동기 부여된다면 엄청난 잠재력을 발휘할 거예요.")
            else:
                profile_messages.append("🌱 **새로운 시작의 씨앗!** 아직은 습관 형성이 낯설지만, 작은 성공부터 쌓아나갈 준비가 되어 있습니다. 응원해요!")
        
        if habit_stats_sorted and habit_stats_sorted[0]['rate'] > 60:
            top_habit = habit_stats_sorted[0]
            profile_messages.append(f"👑 특히 **`'{top_habit['name']}'`** 습관에서 압도적인 성과를 보여, 이 분야에 대한 **남다른 열정과 집중력**이 있음을 알 수 있습니다.")
            
        # Specific habits -> personality traits
        if any(h['name'].lower() in ['운동', 'exercise', '걷기', '달리기', '산책'] and h['rate'] > 70 for h in habit_stats):
            profile_messages.append("🏃‍♀️ **에너지 넘치는 활동가!** 꾸준한 운동 습관은 당신이 얼마나 **활기차고 긍정적인지**를 보여줍니다.")
        if any(h['name'].lower() in ['독서', 'reading', '공부', '학습'] and h['rate'] > 70 for h in habit_stats):
            profile_messages.append("📚 **지식 탐구형 인재!** 독서를 통해 끊임없이 배우고 성장하려는 **지적인 호기심**이 뛰어납니다.")
        if any(h['name'].lower() in ['일기쓰기', '명상', '자기전 회고'] and h['rate'] > 70 for h in habit_stats):
            profile_messages.append("🧘‍♀️ **자기 성찰가!** 내면의 소리에 귀 기울이며 자신을 이해하고 발전시키려는 **현명한 태도**가 돋보입니다.")

        if profile_messages:
            for msg in profile_messages:
                st.success(msg)
        else:
            st.info("아직 분석할 데이터가 부족하거나, 특별한 성향 패턴을 발견하지 못했습니다. 더 많은 습관을 기록하고 당신을 발견해보세요! 🔍")
        
        st.markdown("##### 📈 일별 습관 달성률 변화 추이:")
        all_dates_set = set()
        for habit in st.session_state.habits:
            for date_key in habit['tracking'].keys():
                all_dates_set.add(date_key)
        
        all_dates_sorted = sorted(list(all_dates_set))
        
        if all_dates_sorted:
            for date_str in all_dates_sorted:
                completed_count = sum(1 for h in st.session_state.habits if h['tracking'].get(date_str, False))
                total_habits_on_date = sum(1 for h in st.session_state.habits if datetime.strptime(h['creation_date'], "%Y-%m-%d") <= datetime.strptime(date_str, "%Y-%m-%d"))
                
                if total_habits_on_date > 0:
                    daily_rate = (completed_count / total_habits_on_date) * 100
                    st.write(f"- `{date_str}`: `{int(daily_rate)}`% 달성 (성공 `{completed_count}`개 / 총 `{total_habits_on_date}`개)")
        else:
            st.info("달성률 추이를 볼 데이터가 아직 부족합니다. 습관을 꾸준히 기록해주세요! 🗓️")
    else:
        st.info("습관 분석을 위해 먼저 습관을 추가하고 매일 기록해주세요. 당신의 잠재력을 깨울 시간! 💖")


# 3. 자기전 회고 도우미 모듈
def evening_reflection_module():
    st.markdown("## 🌙 마음챙김 저널: 자기 전 회고 도우미 📝")
    st.write("AI와 함께 하루를 차분히 되돌아보고, 오늘의 의미를 발견하며 내일을 위한 성장의 씨앗을 심어보세요.")

    st.markdown("---")

    today = get_today_date_str()
    st.markdown(f"### 🌅 `{today}` 오늘 하루 회고하기")

    if today in st.session_state.reflections:
        st.info("😊 **이미 오늘 회고를 작성하셨군요!** 멋진 하루의 마무리를 하셨네요. 내일 또 만나요! 👋")
        st.markdown("---")
        st.markdown("### ✨ 오늘 회고한 내용 요약")
        reflect_data = st.session_state.reflections[today]
        st.write(f"**💖 오늘 기뻤던 일:** **`{reflect_data['q1']}`**")
        st.write(f"**🧠 오늘 배운 점:** **`{reflect_data['q2']}`**")
        st.write(f"**🚀 내일 기대하는 것:** **`{reflect_data['q3']}`**")
        st.markdown("##### 📝 AI의 하루 브리핑:")
        st.success(f"'{reflect_data['summary']}'")
        st.markdown(f"##### ✨ 오늘의 감성 점수: **`{reflect_data['sentiment_level'].capitalize()}`**")
    else:
        st.markdown("간단한 질문에 답하며 오늘 하루를 되돌아볼까요? 💭")
        q1 = st.text_area("✍️ 오늘 가장 기뻤던 일 한 가지는 무엇인가요?", key="reflect_q1", placeholder="예: 뜻밖의 칭찬을 들었다.")
        q2 = st.text_area("💡 오늘 새롭게 배우거나 깨달은 점은 무엇인가요?", key="reflect_q2", placeholder="예: 새로운 코딩 방법을 익혔다.")
        q3 = st.text_area("🌟 내일 가장 기대하는 것은 무엇인가요?", key="reflect_q3", placeholder="예: 오랜만에 친구와 만날 생각에 설렌다.")

        if st.button("✨ 회고 완료 및 AI 분석 시작!", key="submit_reflection", use_container_width=True):
            if q1 and q2 and q3:
                # ⭐️ AI 요약 및 감성 분석 (규칙 기반 시뮬레이션)
                full_text = f"기뻤던 일: {q1}. 배운 점: {q2}. 내일 기대: {q3}."
                
                summary = f"오늘 하루는 '{q1}'으로 기뻤고, '{q2}'를 배운 의미 있는 하루였습니다. 내일은 '{q3}'를 기대하고 있습니다."
                
                positive_keywords = ["기뻤", "배운", "기대", "좋은", "행복", "성공", "만족", "재미", "즐거웠", "흥미로웠", "감사", "평화", "따뜻", "행운", "뿌듯"]
                negative_keywords = ["힘들", "어렵", "실패", "슬픔", "짜증", "걱정", "지쳤", "불안", "화났", "불편", "스트레스", "실망", "피곤"]
                
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
                    'sentiment_level': sentiment
                }
                st.success("🎉 회고가 저장되고 AI 분석이 완료되었습니다! 잠시 후 회고 기록에서 확인해보세요.")
                st.rerun()
            else:
                st.warning("앗, 모든 질문에 답해주셔야 AI가 멋진 분석을 해줄 수 있어요! 😅")

    st.markdown("---")
    st.markdown("### 📚 나의 회고 기록 갤러리")
    if st.session_state.reflections:
        reflection_data_list = []
        for date, data in st.session_state.reflections.items():
            reflection_data_list.append({
                '날짜': date,
                '요약': data['summary'],
                '감성': data['sentiment_level']
            })
        
        reflection_data_list_sorted = sorted(reflection_data_list, key=lambda x: x['날짜'], reverse=True)

        st.markdown("##### 📝 전체 회고 목록:")
        for ref_entry in reflection_data_list_sorted:
            st.markdown(f"- **날짜:** `{ref_entry['날짜']}`,\n  **감성:** `{ref_entry['감성']}`,\n  **요약:** `{ref_entry['요약']}`")
            st.markdown("---")
        
        st.markdown("##### 📊 나의 감성 변화 트렌드:")
        sentiment_counts = {}
        for entry in reflection_data_list:
            sentiment_counts[entry['감성']] = sentiment_counts.get(entry['감성'], 0) + 1
        
        if sentiment_counts:
            for sentiment, count in sentiment_counts.items():
                st.write(f"- **`{sentiment}`:** `{count}`회")
        else:
            st.info("아직 감성 분석 데이터가 부족해요. 회고를 더 많이 작성해주세요! ✏️")

        st.markdown("##### 📈 일별 감성 변화 추이:")
        for ref_entry in sorted(reflection_data_list, key=lambda x: x['날짜']):
            st.write(f"- `{ref_entry['날짜']}`: **`{ref_entry['감성']}`**")

    else:
        st.info("아직 작성된 회고가 없어요. 오늘 하루를 기록하고 당신의 내면을 탐험해보세요! 🚀")


# --- 메인 앱 레이아웃 ---
st.title("🌟 나의 스마트 비서: 포커스 & 성장 도우미 🌟")
st.markdown("✨ AI와 함께 당신의 집중력, 습관, 그리고 성장을 관리해보세요!")

st.markdown("<br>", unsafe_allow_html=True) # 공백 추가

# 사이드바 메뉴 (더욱 매력적으로)
selected_module = st.sidebar.radio(
    "어떤 기능이 필요하신가요? 🤔",
    ("🧠 집중 타이머", "💖 습관 분석기", "🌙 자기전 회고"),
    key="main_menu_selection"
)

# 모듈 선택에 따른 내용 표시
if selected_module == "🧠 집중 타이머":
    smart_pomodoro_module()
elif selected_module == "💖 습관 분석기":
    habit_analyzer_module()
elif selected_module == "🌙 자기전 회고":
    evening_reflection_module()

st.sidebar.markdown("---")
st.sidebar.markdown("✨ **오늘도 멋진 하루를 보내세요!**")

