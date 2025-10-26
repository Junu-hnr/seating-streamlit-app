import random
from typing import List, Dict, Set

def generate_placement(
    roster: List[str], 
    pre_assigned: Dict[int, str], 
    disabled_seats: List[int], 
    keep_apart: List[str], 
    rows: int, 
    cols: int
) -> Dict[int, str]:
    """
    모든 조건을 고려하여 자리 배치를 생성합니다.
    - 입력: 학생 명단, 사전 지정, 비활성화, 띄우기 대상, 배열 크기
    - 반환: {좌석_인덱스: 학생명} 딕셔너리
    - 참고: 배치 불가능 등 엣지 케이스 발생 시 예외(Exception) 발생 가능
    """
    
    placement: Dict[int, str] = pre_assigned.copy()
    students_to_place = [s for s in roster if s not in placement.values()]
    
    total_seats = rows * cols
    occupied_seats: Set[int] = set(placement.keys()) | set(disabled_seats)
    available_seats: List[int] = [
        i for i in range(total_seats) if i not in occupied_seats
    ]
    
    if len(students_to_place) > len(available_seats):
        raise ValueError("배치할 학생 수보다 배치 가능한 좌석 수가 적습니다.")
        
    keep_apart_students = [s for s in students_to_place if s in keep_apart]
    other_students = [s for s in students_to_place if s not in keep_apart]
    
    random.shuffle(keep_apart_students)
    random.shuffle(other_students)
    random.shuffle(available_seats)
    
    keep_apart_set = set(keep_apart)
    
    for student in keep_apart_students:
        placed = False
        for i in range(len(available_seats)):
            seat_index = available_seats[i]
            is_safe = True
            neighbors = get_neighbors(seat_index, rows, cols)
            
            for neighbor_idx in neighbors:
                if neighbor_idx in placement and placement[neighbor_idx] in keep_apart_set:
                    is_safe = False
                    break
            
            if is_safe:
                placement[seat_index] = student
                available_seats.pop(i)
                placed = True
                break
        
        if not placed:
            seat_index = available_seats.pop(0)
            placement[seat_index] = student
            
    for student in other_students:
        seat_index = available_seats.pop(0)
        placement[seat_index] = student
        
    return placement

def get_neighbors(seat_index: int, rows: int, cols: int) -> List[int]:
    """
    주어진 좌석의 상하좌우 인접 좌석 인덱스를 반환합니다.
    (배열 경계 고려)
    """
    neighbors = []
    row, col = seat_index // cols, seat_index % cols
    
    if row > 0: neighbors.append(seat_index - cols)
    if row < rows - 1: neighbors.append(seat_index + cols)
    if col > 0: neighbors.append(seat_index - 1)
    if col < cols - 1: neighbors.append(seat_index + 1)
    
    return neighbors