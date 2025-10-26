import streamlit as st
import utils.data_manager as dm
import utils.excel_export as ee
import utils.seating_algorithm as sa
from typing import List, Dict, Any

# --- 1. 페이지 설정 및 세션 상태 초기화 ---
st.set_page_config(layout="wide", page_title="자리배치 프로그램")

# 세션 상태(session_state) 초기화
def init_session_state():
    defaults = {
        "roster": [],           # List[str]
        "placement": {},        # Dict[int, str]
        "pre_assigned": {},     # Dict[int, str]
        "disabled_seats": [],   # List[int]
        "keep_apart": [],       # List[str]
        "layout_rows": 6,
        "layout_cols": 6
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# --- 2. 콜백 함수 정의 (UI 인터랙션용) ---

def handle_roster_update():
    """st.text_area의 명단을 st.session_state.roster에 반영"""
    roster_text = st.session_state.get("roster_input_area", "")
    st.session_state.roster = [
        name.strip() for name in roster_text.split('\n') if name.strip()
    ]
    # 명단 변경 시 기존 배치 초기화
    st.session_state.placement = {}

def handle_file_load():
    """파일 업로드 시 세션 상태 복원"""
    uploaded_file = st.session_state.get("file_uploader_key")
    if uploaded_file:
        try:
            data = dm.load_data_from_file(uploaded_file)
            st.session_state.roster = data.get("roster", [])
            st.session_state.pre_assigned = {int(k): v for k, v in data.get("pre_assigned", {}).items()}
            st.session_state.disabled_seats = data.get("disabled_seats", [])
            st.session_state.layout_rows = data.get("layout", {}).get("rows", 6)
            st.session_state.layout_cols = data.get("layout", {}).get("cols", 6)
            
            # 로드 성공 시 roster_input_area도 동기화
            st.session_state.roster_input_area = "\n".join(st.session_state.roster)
            st.success("데이터를 성공적으로 불러왔습니다.")
        except Exception as e:
            st.error(f"파일 로드 실패: {e}")

def handle_run_placement():
    """자리 배치 실행 버튼 클릭 시 알고리즘 호출"""
    try:
        placement = sa.generate_placement(
            roster=st.session_state.roster,
            pre_assigned=st.session_state.pre_assigned,
            disabled_seats=st.session_state.disabled_seats,
            keep_apart=st.session_state.keep_apart,
            rows=st.session_state.layout_rows,
            cols=st.session_state.layout_cols
        )
        st.session_state.placement = placement
        st.success("자리 배치가 완료되었습니다.")
    except Exception as e:
        st.error(f"배치 실패: {e}")

# --- 3. 사이드바 UI ---

with st.sidebar:
    st.title("자리배치 설정")

    # 1. 명단 입력
    st.header("1. 학생 명단")
    st.text_area(
        "학생 이름을 한 줄에 한 명씩 입력하세요.",
        key="roster_input_area",
        on_change=handle_roster_update,
        height=250
    )
    st.button("명단 적용", on_click=handle_roster_update)
    
    # 2. 데이터 저장/불러오기
    st.header("2. 데이터 관리")
    st.file_uploader(
        "설정 불러오기 (.json)", 
        type="json", 
        key="file_uploader_key",
        on_change=handle_file_load
    )
    
    # 저장 버튼 데이터 생성
    save_data_json = dm.create_save_data(
        st.session_state.roster,
        st.session_state.pre_assigned,
        st.session_state.disabled_seats,
        st.session_state.layout_rows,
        st.session_state.layout_cols
    )
    st.download_button(
        label="현재 설정 저장하기 (.json)",
        data=save_data_json,
        file_name="seating_config.json",
        mime="application/json"
    )

    # 3. 배열 설정
    st.header("3. 책상 배열")
    c1, c2 = st.columns(2)
    st.session_state.layout_rows = c1.number_input("세로 줄 (행)", min_value=1, value=st.session_state.layout_rows)
    st.session_state.layout_cols = c2.number_input("가로 줄 (열)", min_value=1, value=st.session_state.layout_cols)

    # 4. 배치 설정
    st.header("4. 배치 알고리즘")
    st.session_state.keep_apart = st.multiselect(
        "자리 띄우기 대상",
        options=st.session_state.roster,
        default=st.session_state.keep_apart,
        help="선택된 학생들은 서로 인접(상하좌우)하지 않게 배치됩니다."
    )
    
    # 5. 실행
    st.header("5. 실행")
    st.button("🚀 자리 배치 실행!", type="primary", on_click=handle_run_placement)
    
    if st.session_state.placement:
        # 엑셀 다운로드 버튼
        excel_bytes = ee.generate_excel_bytes(
            st.session_state.placement,
            st.session_state.layout_rows,
            st.session_state.layout_cols
        )
        st.download_button(
            label="📊 엑셀로 다운로드",
            data=excel_bytes,
            file_name="seating_chart.xlsx"
        )

# --- 4. 메인 화면 UI (자리 배치 그리드) ---

st.title("교실 자리 배치도")
st.info("각 좌석의 옵션을 변경하여 '사전 지정' 또는 '비활성화' 할 수 있습니다. 설정 후 사이드바에서 '자리 배치 실행'을 누르세요.")

# 보기 모드 전환
view_mode = st.radio(
    "보기 모드", 
    ["교사 기준 (배치도)", "학생 기준 (이름순)"], 
    horizontal=True
)

if view_mode == "교사 기준 (배치도)":
    st.header("칠판 (앞)")
    st.markdown("---")
    
    rows = st.session_state.layout_rows
    cols = st.session_state.layout_cols
    total_seats = rows * cols
    
    # 그리드 생성
    for i in range(rows):
        st_cols = st.columns(cols)
        for j in range(cols):
            seat_index = (i * cols) + j
            
            with st_cols[j]:
                with st.container(border=True):
                    # 현재 상태 파악
                    student_name = st.session_state.placement.get(seat_index)
                    is_disabled = seat_index in st.session_state.disabled_seats
                    pre_assigned_student = st.session_state.pre_assigned.get(seat_index)
                    
                    # 1. 좌석 상태 표시
                    if is_disabled:
                        st.markdown(f"**자리 {seat_index + 1}**\n(비활성화)")
                    elif pre_assigned_student:
                        st.markdown(f"**자리 {seat_index + 1}**\n(지정: {pre_assigned_student})")
                    elif student_name:
                        st.markdown(f"**자리 {seat_index + 1}**\n### {student_name}")
                    else:
                        st.markdown(f"**자리 {seat_index + 1}**\n(빈 자리)")
                    
                    # 2. 좌석 설정 UI (비활성화, 사전지정)
                    
                    # 비활성화 토글
                    if st.checkbox("비활성화", value=is_disabled, key=f"disable_{seat_index}"):
                        if not is_disabled:
                            st.session_state.disabled_seats.append(seat_index)
                            st.session_state.pre_assigned.pop(seat_index, None) # 비활성화 시 사전지정 해제
                    else:
                        if is_disabled:
                            st.session_state.disabled_seats.remove(seat_index)
                            
                    # 사전 지정 셀렉트박스
                    options = ["- (지정 안 함)"] + st.session_state.roster
                    current_pre_assign_index = 0
                    if pre_assigned_student in options:
                        current_pre_assign_index = options.index(pre_assigned_student)
                    
                    selected_student = st.selectbox(
                        "학생 지정",
                        options=options,
                        index=current_pre_assign_index,
                        key=f"pre_{seat_index}",
                        label_visibility="collapsed"
                    )
                    
                    if selected_student != "- (지정 안 함)":
                        st.session_state.pre_assigned[seat_index] = selected_student
                        st.session_state.disabled_seats.remove(seat_index) # 사전지정 시 비활성화 해제
                    else:
                        st.session_state.pre_assigned.pop(seat_index, None)

else: # 학생 기준 (이름순) 보기
    st.header("학생별 좌석 번호")
    
    if not st.session_state.placement:
        st.warning("먼저 자리 배치를 실행해주세요.")
    else:
        # 배치 결과를 학생 이름 기준으로 정렬
        placement_inverted = {student: seat for seat, student in st.session_state.placement.items()}
        
        c1, c2 = st.columns(2)
        col_count = 0
        
        # 전체 명단 기준으로 조회
        for student in sorted(st.session_state.roster):
            seat_number = placement_inverted.get(student)
            
            target_col = c1 if col_count % 2 == 0 else c2
            if seat_number is not None:
                target_col.markdown(f"- **{student}**: {seat_number + 1}번 자리")
            else:
                # 사전 지정 등으로 인해 명단에 있지만 배치되지 않은 경우
                target_col.markdown(f"- *{student}*: (배치되지 않음)*")
            col_count += 1