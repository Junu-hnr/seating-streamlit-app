import pytest
from utils.seating_algorithm import generate_placement, get_neighbors

def test_generate_placement():
    # Test case 1: Basic placement with no constraints
    roster = ["Alice", "Bob", "Charlie"]
    pre_assigned = {}
    disabled_seats = []
    keep_apart = []
    rows = 2
    cols = 2
    
    placement = generate_placement(roster, pre_assigned, disabled_seats, keep_apart, rows, cols)
    
    assert len(placement) == len(roster)
    assert all(student in placement.values() for student in roster)

    # Test case 2: Pre-assigned seats
    roster = ["Alice", "Bob", "Charlie"]
    pre_assigned = {0: "Alice"}
    disabled_seats = []
    keep_apart = []
    rows = 2
    cols = 2
    
    placement = generate_placement(roster, pre_assigned, disabled_seats, keep_apart, rows, cols)
    
    assert placement[0] == "Alice"
    assert len(placement) == len(roster)

    # Test case 3: Disabled seats
    roster = ["Alice", "Bob", "Charlie"]
    pre_assigned = {}
    disabled_seats = [1]
    keep_apart = []
    rows = 2
    cols = 2
    
    placement = generate_placement(roster, pre_assigned, disabled_seats, keep_apart, rows, cols)
    
    assert 1 not in placement  # Seat 1 should not be occupied
    assert len(placement) == len(roster)

    # Test case 4: Keep apart constraint
    roster = ["Alice", "Bob", "Charlie"]
    pre_assigned = {}
    disabled_seats = []
    keep_apart = ["Alice", "Bob"]
    rows = 2
    cols = 2
    
    placement = generate_placement(roster, pre_assigned, disabled_seats, keep_apart, rows, cols)
    
    # Check that Alice and Bob are not adjacent (use get_neighbors for correctness)
    alice_idx = list(placement.keys())[list(placement.values()).index("Alice")]
    bob_idx = list(placement.keys())[list(placement.values()).index("Bob")]
    assert bob_idx not in get_neighbors(alice_idx, rows, cols)

    # Test case 5: More students than available seats (force by disabling a seat)
    roster = ["Alice", "Bob", "Charlie", "David"]
    pre_assigned = {}
    disabled_seats = [0]  # disable one seat so only 3 seats remain
    keep_apart = []
    rows = 2
    cols = 2

    with pytest.raises(ValueError, match="배치할 학생 수보다 배치 가능한 좌석 수가 적습니다."):
        generate_placement(roster, pre_assigned, disabled_seats, keep_apart, rows, cols)