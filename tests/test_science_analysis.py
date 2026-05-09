import pytest
from src.commands.science_analysis import ScienceAnalysisCommand

CMD = ScienceAnalysisCommand()


def test_parse_basic():
    parsed = CMD.parse_one_line_command(
        "ANALYZE MY CLAWBOT: Expected [0,25,50,75,100] mm → Actual [0.1,24.8,49.9,75.3,100.2] mm"
    )
    assert parsed["expected"] == [0, 25, 50, 75, 100]
    assert parsed["actual"] == [0.1, 24.8, 49.9, 75.3, 100.2]
    assert parsed["precision"] == 0.2


def test_parse_custom_precision():
    parsed = CMD.parse_one_line_command(
        "ANALYZE MY CLAWBOT: Expected [0,50,100] mm → Actual [0.5,49.5,100.5] mm ±0.5mm"
    )
    assert parsed["precision"] == 0.5


def test_parse_missing_actual_raises():
    with pytest.raises(ValueError, match="Could not parse"):
        CMD.parse_one_line_command("ANALYZE MY CLAWBOT: Expected [0,25] mm")


def test_parse_mismatched_lengths_raises():
    with pytest.raises(ValueError, match="count mismatch"):
        CMD.parse_one_line_command(
            "ANALYZE MY CLAWBOT: Expected [0,25,50] mm → Actual [1,2,3,4,5] mm"
        )


def test_calculate_errors_perfect():
    errors = CMD.calculate_errors([0, 25, 50], [0, 25, 50])
    assert errors["max"] == 0.0
    assert errors["mean"] == 0.0
    assert errors["rms"] == 0.0
    assert errors["absolute"] == [0.0, 0.0, 0.0]


def test_calculate_errors_values():
    errors = CMD.calculate_errors([0, 25, 50], [0.1, 24.8, 50.3])
    assert round(errors["max"], 4) == 0.3
    assert round(errors["mean"], 4) == round((0.1 + 0.2 + 0.3) / 3, 4)


def test_calculate_z_scores():
    # Use 0.15 offset (z=0.75) to avoid floating-point boundary issues at z=1.0
    z = CMD.calculate_z_scores([0, 25, 50], [0.15, 25.15, 50.15], precision=0.2)
    assert all(round(v, 4) == 0.75 for v in z["values"])
    assert z["within_1sigma"] == 3
    assert z["within_2sigma"] == 3


def test_detect_pattern_increasing():
    pattern = CMD.detect_pattern([0, 25, 50, 75, 100])
    assert pattern["trend"] == "consistently increasing"


def test_detect_pattern_bias_positive():
    pattern = CMD.detect_pattern([0.5, 25.5, 50.5, 75.5, 100.5])
    assert "positive" in pattern["bias"]


def test_detect_pattern_bias_negative():
    pattern = CMD.detect_pattern([-0.5, 24.5, 49.5, 74.5, 99.5])
    assert "negative" in pattern["bias"]


def test_generate_recommendation_all_clear():
    parsed = {"expected": [0, 25, 50], "actual": [0.05, 25.05, 50.05], "precision": 0.2}
    rec = CMD.generate_recommendation(parsed)
    assert "No calibration needed" in rec


def test_generate_recommendation_immediate():
    parsed = {"expected": [0, 25, 50], "actual": [2.0, 27.0, 52.0], "precision": 0.2}
    rec = CMD.generate_recommendation(parsed)
    assert "Immediate" in rec


def test_execute_returns_report():
    result = CMD.execute(
        "ANALYZE MY CLAWBOT: Expected [0,25,50,75,100] mm → Actual [0.1,24.8,49.9,75.3,100.2] mm"
    )
    assert "Clawbot Science Analysis Report" in result
    assert "Error Analysis" in result
    assert "Recommendation" in result
