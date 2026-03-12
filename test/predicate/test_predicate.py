# test/predicate/test_predicate.py
from src.tcas.main import altitude_separation_test, positive_ra_alt_thresh, inhibit_biased_climb
from src.tcas.state import State

def create_base_state(**kwargs):
    # Helper to easily create states with defaults, overriding only what is needed
    base = {
        "current_vertical_sep": 601, "high_confidence": 1, "two_of_three_reports_valid": 1,
        "own_tracked_altitude": 5000, "own_tracked_alt_rate": 500, "other_tracked_altitude": 5500,
        "altitude_layer_value": 0, "up_separation": 400, "down_separation": 400,
        "other_rac": 0, "other_capability": 1, "climb_inhibit": 0,
        "positive_ra_alt_thresh_0": 400, "positive_ra_alt_thresh_1": 0,
        "positive_ra_alt_thresh_2": 0, "positive_ra_alt_thresh_3": 0
    }
    base.update(kwargs)
    return State(**base)

def test_layer_coverage():
    # Satisfies Predicate Coverage for: positive_ra_alt_thresh (layer == 0, 1, 2, 3)
    # Each must be evaluated True and False at some point.
    assert positive_ra_alt_thresh(create_base_state(altitude_layer_value=0), 0) == 400
    assert positive_ra_alt_thresh(create_base_state(altitude_layer_value=1), 1) == 0
    assert positive_ra_alt_thresh(create_base_state(altitude_layer_value=2), 2) == 0
    assert positive_ra_alt_thresh(create_base_state(altitude_layer_value=3), 3) == 0
    assert positive_ra_alt_thresh(create_base_state(altitude_layer_value=4), 4) == 0 # Default return

def test_climb_inhibit_coverage():
    # Satisfies Predicate Coverage for: state.climb_inhibit (True and False)
    assert inhibit_biased_climb(create_base_state(climb_inhibit=1, up_separation=100)) == 200 # True branch (+100)
    assert inhibit_biased_climb(create_base_state(climb_inhibit=0, up_separation=100)) == 100 # False branch

def test_alt_sep_main_predicate_false():
    # Satisfies Predicate Coverage for: main altitude_separation_test predicate = FALSE
    state = create_base_state(high_confidence=0) # Immediately falsifies the first condition
    assert altitude_separation_test(state) == 0

def test_alt_sep_upward_ra():
    # Satisfies Predicate Coverage for:
    # - main predicate = TRUE
    # - need_upward_RA = TRUE, need_downward_RA = FALSE
    # - inhibit_biased_climb > down_separation (True and False logic)
    state = create_base_state(
        other_tracked_altitude=6000, # own below threat -> need upward
        up_separation=500, down_separation=300,
        current_vertical_sep=601, own_tracked_alt_rate=500,
        high_confidence=1, other_capability=0 # bypasses capability checks
    )
    assert altitude_separation_test(state) == 1

def test_alt_sep_downward_ra():
    # Satisfies Predicate Coverage for:
    # - need_upward_RA = FALSE, need_downward_RA = TRUE
    state = create_base_state(
        other_tracked_altitude=4000, # own above threat -> need downward
        up_separation=300, down_separation=500,
        current_vertical_sep=601, own_tracked_alt_rate=500,
        high_confidence=1, other_capability=0
    )
    assert altitude_separation_test(state) == 2

def test_alt_sep_both_ra():
    # Satisfies Predicate Coverage for: need_upward_RA = TRUE AND need_downward_RA = TRUE
    # This requires forcing both non_crossing biased functions to evaluate to True.
    state = create_base_state(
        other_tracked_altitude=5000, # perfectly equal altitude (forces neither strictly above/below logic edge cases)
        up_separation=500, down_separation=500,
        current_vertical_sep=601, own_tracked_alt_rate=500,
        high_confidence=1, other_capability=0,
        positive_ra_alt_thresh_0=0 # alim = 0
    )
    # Depending on exact evaluation of own_below/above, setting alt equal makes both False.
    # Wait, if both are False, `not own_below` is True, `not own_above` is True.
    # Therefore, need_upward = True and need_downward = True.
    assert altitude_separation_test(state) == 0 # Triggers the `if need_upward_RA and need_downward_RA: alt_sep = 0`