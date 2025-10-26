import pandas as pd
import io
from typing import Dict, List

def generate_excel_bytes(placement: Dict[int, str], rows: int, cols: int) -> bytes:
    """
    자리 배치 결과를 엑셀 파일(bytes)로 변환합니다.
    - 입력: 배치 결과 딕셔너리, 가로/세로 크기
    - 반환: 엑셀 파일의 raw bytes
    """
    
    # 2D 리스트 초기화 (빈 좌석은 "" 처리)
    grid_data = [["" for _ in range(cols)] for _ in range(rows)]
    
    # placement 딕셔너리를 2D 리스트에 매핑
    for seat_index, student_name in placement.items():
        row = seat_index // cols
        col = seat_index % cols
        if row < rows and col < cols:
            grid_data[row][col] = student_name
            
    # Pandas DataFrame 생성
    # 교탁(앞쪽)이 0행이 되도록 인덱스 설정
    df = pd.DataFrame(grid_data)
    df.index = [f"{i+1}번째 줄" for i in range(rows)]
    df.columns = [f"{i+1}번째 분단" for i in range(cols)]

    # DataFrame을 Excel 바이트로 변환
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='자리배치도')
        
    return output.getvalue()