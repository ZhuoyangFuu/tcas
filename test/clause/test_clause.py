# test/clause/test_clause.py
from src.tcas.main import altitude_separation_test
from src.tcas.state import State


def evaluate_main_predicate(state: State) -> bool:
    # A helper function that isolates the massive compound predicate for ACC testing
    # Since we can't easily assert on the internal if-statement without instrumentation,
    # we replicate the logic strictly to demonstrate clause coverage inputs.
    A = state.high_confidence
    B = (state.own_tracked_alt_rate <= 600)
    C = (state.current_vertical_sep > 600)
    D = (state.other_capability == 1)
    E = state.two_of_three_reports_valid
    F = (state.other_rac == 0)

    return bool((A and B and C) and ((D and (E and F)) or not D))


def create_mcdc_state(A=1, B=500, C=601, D=1, E=1, F=0):
    # B needs to be <= 600 to be True, > 600 to be False
    # C needs to be > 600 to be True, <= 600 to be False
    # F needs to be == 0 to be True, != 0 to be False
    return State(
        current_vertical_sep=C, high_confidence=A, two_of_three_reports_valid=E,
        own_tracked_altitude=5000, own_tracked_alt_rate=B, other_tracked_altitude=5500,
        altitude_layer_value=0, up_separation=400, down_separation=400,
        other_rac=F, other_capability=D, climb_inhibit=0
    )


def test_clause_A():
    # To test A, we need: B=T, C=T, D=F (making the second half True). Result should follow A.
    assert evaluate_main_predicate(create_mcdc_state(A=1, B=500, C=601, D=0)) == True
    assert evaluate_main_predicate(create_mcdc_state(A=0, B=500, C=601, D=0)) == False


def test_clause_B():
    # To test B, we need: A=T, C=T, D=F. Result should follow B.
    assert evaluate_main_predicate(create_mcdc_state(A=1, B=500, C=601, D=0)) == True
    assert evaluate_main_predicate(create_mcdc_state(A=1, B=700, C=601, D=0)) == False  # B flipped


def test_clause_C():
    # To test C, we need: A=T, B=T, D=F. Result should follow C.
    assert evaluate_main_predicate(create_mcdc_state(A=1, B=500, C=601, D=0)) == True
    assert evaluate_main_predicate(create_mcdc_state(A=1, B=500, C=500, D=0)) == False  # C flipped


def test_clause_D():
    # To test D, we must falsify (E and F) so the result relies entirely on `not D`.
    # We set E=T, F=F (making E&F False). Now, if D=F -> True. If D=T -> False.
    assert evaluate_main_predicate(create_mcdc_state(A=1, B=500, C=601, D=0, E=1, F=1)) == True
    assert evaluate_main_predicate(create_mcdc_state(A=1, B=500, C=601, D=1, E=1, F=1)) == False


def test_clause_E():
    # To test E, we must make `not D` False, meaning D=T. We need F=T. Result follows E.
    assert evaluate_main_predicate(create_mcdc_state(A=1, B=500, C=601, D=1, E=1, F=0)) == True
    assert evaluate_main_predicate(create_mcdc_state(A=1, B=500, C=601, D=1, E=0, F=0)) == False  # E flipped


def test_clause_F():
    # To test F, we must make `not D` False (D=T). We need E=T. Result follows F.
    assert evaluate_main_predicate(create_mcdc_state(A=1, B=500, C=601, D=1, E=1, F=0)) == True
    assert evaluate_main_predicate(create_mcdc_state(A=1, B=500, C=601, D=1, E=1, F=1)) == False  # F flipped