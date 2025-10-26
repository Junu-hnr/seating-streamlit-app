import json
from typing import List, Dict, Any
import io

def create_save_data(
    roster: List[str], 
    pre_assigned: Dict[int, str], 
    disabled_seats: List[int],
    rows: int,
    cols: int
) -> str:
    """
    현재 앱 상태(명단, 설정)를 JSON 문자열로 직렬화합니다.
    - 입력: 세션 상태의 주요 데이터
    - 반환: JSON 형식의 문자열
    """
    save_dict = {
        "roster": roster,
        "pre_assigned": pre_assigned,
        "disabled_seats": disabled_seats,
        "layout": {"rows": rows, "cols": cols}
    }
    return json.dumps(save_dict, ensure_ascii=False, indent=2)

def load_data_from_file(uploaded_file: io.BytesIO) -> Dict[str, Any]:
    """
    업로드된 JSON 파일(BytesIO)을 읽어 딕셔너리로 파싱합니다.
    - 입력: st.file_uploader로 받은 파일 객체
    - 반환: 앱 상태 데이터가 담긴 딕셔너리
    - 예외 처리: 유효하지 않은 JSON 파일이나 필수 키가 없는 경우 예외 발생
    """
    data = json.load(uploaded_file)
    
    # 필수 키 검증
    if not all(k in data for k in ["roster", "pre_assigned", "disabled_seats", "layout"]):
        raise ValueError("필수 키가 누락된 파일입니다.")
        
    return data