import streamlit as st
from datetime import datetime, timedelta
import time
import random

# --- 기본 설정 ---
st.set_page_config(layout="wide", page_title="나의 스마트 비서: 포커스 & 성장 도우미")

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

# --- 1. 지능형 집중 타이머 (Smart Pomodoro) 모듈 ---
def smart_pomodoro_module():
    st.header("🧠 지능형 집중 타이머")
    st.write("당신의 작업 유형에 맞춰 최적의 집중 시간을 제안해 드립니다.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("💡 새로운 작업 설정")
        task_name = st.text_input("수행할 작업 이름", key="pomodoro_task_input")

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
            break_minutes_suggestion = 5
        elif selected_complexity == "45분":
            focus_minutes_suggestion = 45
            break_minutes_suggestion = 5
        elif selected_complexity == "50분":
            focus_minutes_suggestion = 50
            break_minutes_suggestion = 10

        st.info(f"✨ AI의 제안: 집중 {focus_minutes_suggestion}분 / 휴식 {break_minutes_suggestion}분")

        if st.button("작업 추가 및 시작 준비", key="add_task_button"):
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
                st.success(f"'{task_name}' 작업을 준비했습니다. 이제 타이머를 시작할 수 있습니다!")
                st.rerun() # Refresh to show timer status
            else:
                st.warning("작업 이름을 입력해주세요!")

    with col2:
        st.subheader("⏱️ 현재 타이머")
        if st.session_state.pomodoro_task_name:
            st.write(f"**작업:** {st.session_state.pomodoro_task_name}")
            status_text = st.empty()
            time_display = st.empty()

            # Find the current task being run to get its configured focus/break times
            # It's crucial to retrieve the *current* task from tasks list by name AND date
            current_task_details = next((t for t in st.session_state.tasks if t['name'] == st.session_state.pomodoro_task_name and t['date'] == get_today_date_str() and t['feedback'] is None), None)
            
            if current_task_details is None: # Task might have been completed or not found correctly
                st.warning("현재 진행 중인 작업 정보가 없거나 이미 완료된 작업입니다. 새 작업을 시작해주세요.")
                st.session_state.pomodoro_task_name = "" # Reset invalid task
                return

            if not st.session_state.pomodoro_running:
                status_text.write(f"상태: {st.session_state.current_pomodoro_stage.capitalize()} 준비중...")
                minutes = st.session_state.remaining_time // 60
                seconds = st.session_state.remaining_time % 60
                time_display.write(f"남은 시간: **{minutes:02d}:{seconds:02d}**")

            # Start/Stop Buttons
            if st.session_state.pomodoro_running:
                if st.button("중지", key="stop_pomodoro"):
                    st.session_state.pomodoro_running = False
                    st.session_state.pomodoro_start_time = None # Reset start time on stop
                    status_text.warning("타이머 중지됨.")
                    st.rerun() # Refresh to show stopped state
            else:
                if st.button("시작", key="start_pomodoro"):
                    st.session_state.pomodoro_running = True
                    # Set remaining time and start time for the current stage
                    if st.session_state.current_pomodoro_stage == 'focus':
                         st.session_state.remaining_time = current_task_details['focus_duration_minutes'] * 60
                    else: # break
                         st.session_state.remaining_time = current_task_details['break_duration_minutes'] * 60
                    st.session_state.pomodoro_start_time = datetime.now()
                    st.rerun() # Refresh to start timer loop

            if st.session_state.pomodoro_running:
                # ⭐️ 논블로킹 타이머 시뮬레이션
                time_placeholder = st.empty() # Placeholder for time updates
                start_time = st.session_state.pomodoro_start_time
                original_remaining_on_start = st.session_state.remaining_time # Store for accurate elapsed time calculation

                while st.session_state.remaining_time > 0 and st.session_state.pomodoro_running:
                    elapsed_seconds = int((datetime.now() - start_time).total_seconds())
                    
                    # Remaining time should be original duration minus elapsed_seconds
                    st.session_state.remaining_time = max(0, original_remaining_on_start - elapsed_seconds)

                    minutes = st.session_state.remaining_time // 60
                    seconds = st.session_state.remaining_time % 60
                    
                    time_placeholder.markdown(f"상태: **{st.session_state.current_pomodoro_stage.capitalize()}** 🏃\n남은 시간: **{minutes:02d}:{seconds:02d}**")
                    time.sleep(1) # Wait for 1 second

                # Timer finished naturally or was stopped due to remaining_time <= 0
                if st.session_state.remaining_time <= 0 and st.session_state.pomodoro_running: # If it finished successfully
                    st.session_state.pomodoro_running = False
                    st.session_state.pomodoro_start_time = None # Reset start time for next stage

                    st.balloons() # Visual notification for completion

                    if st.session_state.current_pomodoro_stage == 'focus':
                        st.success(f"🎊 {st.session_state.pomodoro_task_name} 집중 시간 완료! 🎉")
                        # ⭐️ AI 기반 휴식 시간 제안 (간단화된 버전)
                        suggested_break_action = random.choice([
                            "잠시 스트레칭하며 몸을 풀어보세요.",
                            "창 밖을 보며 눈을 쉬게 해주세요.",
                            "물 한 잔 마시며 재충전하세요.",
                            "가벼운 명상으로 마음을 진정시켜보세요."
                        ])
                        st.info(f"🌿 휴식 시간! {suggested_break_action}")
                        
                        # Update task log with completed focus minutes
                        for i, task in enumerate(st.session_state.tasks):
                            if task['name'] == st.session_state.pomodoro_task_name and task['date'] == get_today_date_str() and task['feedback'] is None:
                                st.session_state.tasks[i]['logged_focus_minutes'] += current_task_details['focus_duration_minutes'] # Add minutes
                                break

                        st.session_state.current_pomodoro_stage = 'break'
                        # Remaining time for break will be set when break starts
                        if st.button("휴식 시작", key="start_break_after_focus"):
                             st.session_state.pomodoro_running = True
                             st.session_state.pomodoro_start_time = datetime.now() # Start new timer
                             st.rerun() # Trigger a rerun to start break timer
                    elif st.session_state.current_pomodoro_stage == 'break':
                        st.success("✅ 휴식 시간 완료! 다시 집중할 준비 되셨나요?")
                        
                        # 피드백 입력
                        feedback = st.radio("집중도는 어떠셨나요?", ["매우 좋음", "좋음", "보통", "나쁨", "매우 나쁨"], key=f"feedback_rating_{st.session_state.pomodoro_task_name}_{get_today_date_str()}")
                        if st.button("피드백 제출 및 완료", key="complete_pomodoro_task"):
                            for i, task in enumerate(st.session_state.tasks):
                                if task['name'] == st.session_state.pomodoro_task_name and task['date'] == get_today_date_str() and task['feedback'] is None:
                                    st.session_state.tasks[i]['feedback'] = feedback
                                    break
                            st.session_state.pomodoro_task_name = "" # Clear current running task
                            st.info("작업이 완료되고 피드백이 저장되었습니다.")
                            st.rerun() # Refresh UI
                elif not st.session_state.pomodoro_running: # If timer was explicitly stopped
                    st.info("타이머가 멈춰 있습니다. 다시 시작하려면 '시작' 버튼을 누르세요.")
            else: # If timer not running and task is set up
                st.info("타이머가 멈춰 있습니다. '시작' 버튼을 눌러주세요.")


        else:
            st.info("왼쪽에서 작업을 추가해주세요.")

    st.markdown("---")
    st.subheader("📈 집중 기록 요약")
    if st.session_state.tasks:
        st.write("---")
        st.write("#### 전체 집중 기록:")
        
        # Display task data
        for task in reversed(st.session_state.tasks): # Show latest first
            feedback_display = task['feedback'] if task['feedback'] else "진행 중"
            st.markdown(f"- **날짜:** {task['date']}, **작업:** {task['name']} ({task['complexity_level']})\n  **집중:** {task['logged_focus_minutes']}분 (목표 {task['focus_duration_minutes']}분), **피드백:** {feedback_display}")
        
        st.write("---")

        # ⭐️ 개인별 최적 집중 시간/피드백 요약 (간단 시각화 대신 텍스트 요약)
        st.write("#### 나의 집중 패턴 분석:")
        
        completed_tasks = [t for t in st.session_state.tasks if t['feedback'] is not None]
        if completed_tasks:
            total_logged_minutes = sum(t['logged_focus_minutes'] for t in completed_tasks)
            st.write(f"- 총 기록된 집중 시간: **{total_logged_minutes}분**")

            # Feedback distribution (manual count)
            feedback_counts = {}
            for task in completed_tasks:
                feedback_counts[task['feedback']] = feedback_counts.get(task['feedback'], 0) + 1
            
            if feedback_counts:
                st.write("- 집중도 피드백 분포:")
                for fb, count in feedback_counts.items():
                    st.write(f"  - {fb}: {count}회")
            else:
                st.info("피드백 데이터가 충분하지 않습니다.")
        else:
            st.info("아직 완료된 집중 기록이 없습니다.")
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
                    'tracking': {} # {date: bool}
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
        # Create a list to track checked states for rerunning
        # Streamlit recreates widgets on each run, so checkbox states must be carefully managed.
        # This loop will display checkboxes, and their changes will trigger a rerun.
        # We don't want to rerun *inside* the loop for every change, just let Streamlit handle it.
        
        updated_habits = False
        for i, habit in enumerate(st.session_state.habits):
            # Ensure today's tracking key exists
            if today not in habit['tracking']:
                st.session_state.habits[i]['tracking'][today] = False # Default to not checked
            
            initial_checked_state = st.session_state.habits[i]['tracking'][today]
            checked_this_run = st.checkbox(
                f"[{habit['name']}] 오늘 달성?", 
                value=initial_checked_state, 
                key=f"habit_check_{habit['id']}_{today}"
            )
            
            if checked_this_run != initial_checked_state:
                st.session_state.habits[i]['tracking'][today] = checked_this_run
                updated_habits = True # Mark that a habit was updated

        if updated_habits:
            st.rerun() # Only rerun if any checkbox state actually changed
    else:
        st.info("아직 추가된 습관이 없습니다. 위에서 새로운 습관을 추가해주세요.")

    st.markdown("---")
    st.subheader("⭐ 나의 행동 성향 프로파일링 (AI 시뮬레이션)")
    if st.session_state.habits:
        habit_stats = []
        for habit in st.session_state.habits:
            completed_days = sum(1 for date, completed in habit['tracking'].items() if completed)
            
            # Calculate total days from creation to today
            start_date_obj = datetime.strptime(habit['creation_date'], "%Y-%m-%d")
            total_days_tracked = (datetime.now() - start_date_obj).days + 1
            
            if total_days_tracked <= 0: total_days_tracked = 1 # Avoid division by zero, at least 1 day if created today
            
            completion_rate = (completed_days / total_days_tracked) * 100
            habit_stats.append({
                'name': habit['name'], 
                'completed_days': completed_days, 
                'total_days_tracked': total_days_tracked, 
                'rate': completion_rate
            })
        
        # Manually sort for display
        habit_stats_sorted = sorted(habit_stats, key=lambda x: x['rate'], reverse=True)
        st.write("##### 현재 습관 달성률:")
        for hs in habit_stats_sorted:
            st.write(f"- **{hs['name']}**: {hs['rate']:.1f}% 달성 ({hs['completed_days']}/{hs['total_days_tracked']}일)")

        st.markdown("##### 💡 AI 분석 리포트")
        # ⭐️ AI 기반 성향 프로파일링 (규칙 기반 시뮬레이션)
        st.write("당신의 습관 데이터를 분석한 결과입니다:")
        profile_messages = []

        overall_rates = [h['rate'] for h in habit_stats]
        if overall_rates:
            avg_rate = sum(overall_rates) / len(overall_rates)
            if avg_rate > 70:
                profile_messages.append("✨ **꾸준함의 아이콘!** 전반적으로 습관 달성률이 높아 강한 의지와 꾸준함을 가지고 계십니다.")
            elif avg_rate < 40:
                profile_messages.append("💪 **새로운 시작을 위한 도약!** 아직 습관 형성이 어려울 수 있습니다. 작은 목표부터 시작해보는 건 어떠세요?")
            else:
                profile_messages.append("👍 **노력하고 있는 당신을 응원합니다!** 꾸준히 기록하며 스스로를 발견하는 시간을 가져보세요.")
        
        if habit_stats_sorted and habit_stats_sorted[0]['rate'] > 50:
            top_habit = habit_stats_sorted[0]
            profile_messages.append(f"✅ 특히 **'{top_habit['name']}'** 습관에서 높은 성과를 보여, 해당 분야에 대한 집중력과 흥미가 뛰어납니다.")
            
        # Example for specific habits -> personality traits
        # Check for specific habits by name and good completion rate
        if any(h['name'].lower() in ['운동', 'exercise', '산책'] and h['rate'] > 70 for h in habit_stats):
            profile_messages.append("🏃‍♀️ **활동적인 에너자이저!** 운동 습관이 잘 잡혀 있어 건강하고 활기찬 성향을 가지고 계십니다.")
        if any(h['name'].lower() in ['독서', 'reading', '공부'] and h['rate'] > 70 for h in habit_stats):
            profile_messages.append("📚 **지적인 탐구자!** 독서를 통해 꾸준히 지식을 쌓는 탐구적인 성향이 돋보입니다.")

        if profile_messages:
            for msg in profile_messages:
                st.success(msg)
        else:
            st.info("아직 분석할 데이터가 부족하거나, 특별한 성향 패턴을 발견하지 못했습니다. 더 많은 습관을 기록해주세요!")
        
        # ⭐️ 일별 습관 달성률 추이 (간단 텍스트로)
        st.markdown("##### 일별 습관 달성 추이:")
        # Collect all unique dates from all habits' tracking
        all_dates_set = set()
        for habit in st.session_state.habits:
            for date_key in habit['tracking'].keys():
                all_dates_set.add(date_key)
        
        all_dates_sorted = sorted(list(all_dates_set))
        
        if all_dates_sorted:
            for date_str in all_dates_sorted:
                completed_count = sum(1 for h in st.session_state.habits if h['tracking'].get(date_str, False))
                
                # Count habits that were created before or on this specific date, and are still active
                total_habits_on_date = sum(1 for h in st.session_state.habits if datetime.strptime(h['creation_date'], "%Y-%m-%d") <= datetime.strptime(date_str, "%Y-%m-%d"))
                
                if total_habits_on_date > 0:
                    daily_rate = (completed_count / total_habits_on_date) * 100
                    st.write(f"- {date_str}: {int(daily_rate)}% 달성 (달성 {completed_count}/{total_habits_on_date}개)")
                else:
                    st.write(f"- {date_str}: 기록 없음") # Should not happen if all_dates_sorted contains valid dates
        else:
            st.info("달성률 추이를 볼 데이터가 없습니다.")


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
        st.markdown(f"##### ✨ 오늘의 감성 점수: **{reflect_data['sentiment_level'].capitalize()}**")
    else:
        q1 = st.text_area("✍️ 오늘 기뻤던 일 한 가지는 무엇인가요?", key="reflect_q1")
        q2 = st.text_area("💡 오늘 새롭게 배우거나 느낀 점은 무엇인가요?", key="reflect_q2")
        q3 = st.text_area("🌟 내일 가장 기대하는 것은 무엇인가요?", key="reflect_q3")

        if st.button("회고 완료 및 AI 분석 시작", key="submit_reflection"):
            if q1 and q2 and q3:
                # ⭐️ AI 요약 및 감성 분석 (규칙 기반 시뮬레이션)
                full_text = f"기뻤던 일: {q1}. 배운 점: {q2}. 내일 기대: {q3}."
                
                # 가상의 AI 요약 (키워드 추출 및 재구성)
                summary = f"오늘 하루는 '{q1}'으로 기뻤고, '{q2}'를 배운 의미 있는 하루였습니다. 내일은 '{q3}'를 기대하고 있습니다."
                
                # 가상의 AI 감성 분석 (간단한 키워드 기반)
                # 더 다양한 키워드 추가하여 감성 분석 로직 강화
                positive_keywords = ["기뻤", "배운", "기대", "좋은", "행복", "성공", "만족", "재미", "즐거웠", "흥미로웠", "감사", "평화", "따뜻", "행운"]
                negative_keywords = ["힘들", "어렵", "실패", "슬픔", "짜증", "걱정", "지쳤", "불안", "화났", "불편", "스트레스", "실망"]
                
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
                '감성': data['sentiment_level']
            })
        
        # Manually sort for display
        reflection_data_list_sorted = sorted(reflection_data_list, key=lambda x: x['날짜'], reverse=True)

        st.write("##### 전체 회고 목록:")
        for ref_entry in reflection_data_list_sorted:
            st.write(f"- **날짜:** {ref_entry['날짜']}, **감성:** {ref_entry['감성']}, **요약:** {ref_entry['요약']}")
        
        st.markdown("---")

        # ⭐️ 감성 변화 추이 요약 (간단 텍스트 또는 그래프 대신 숫자 분포)
        st.write("##### 나의 감성 분석 요약:")
        sentiment_counts = {}
        for entry in reflection_data_list:
            sentiment_counts[entry['감성']] = sentiment_counts.get(entry['감성'], 0) + 1
        
        if sentiment_counts:
            for sentiment, count in sentiment_counts.items():
                st.write(f"- **{sentiment}:** {count}회")
        else:
            st.info("아직 감성 분석 데이터가 없습니다.")

        # 일별 감성 변화 (간단 텍스트로)
        st.write("##### 일별 감성 변화 추이:")
        # Sort by date for chronological display
        for ref_entry in sorted(reflection_data_list, key=lambda x: x['날짜']):
            st.write(f"- {ref_entry['날짜']}: {ref_entry['감성']}")

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

