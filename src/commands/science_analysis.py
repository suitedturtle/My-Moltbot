import numpy as np
import re


class ScienceAnalysisCommand:
    def __init__(self):
        self.expected = [0, 25, 50, 75, 100]

    def parse_one_line_command(self, command_text):
        """Parse: 'ANALYZE MY CLAWBOT: Expected [0,25,50,75,100] mm → Actual [0.1,24.8,...] mm'"""
        actual_match = re.search(r'Actual\s*\[([\d\.,\s]+)\]', command_text)
        if not actual_match:
            raise ValueError("Could not parse actual measurements from command")

        actual = [float(x.strip()) for x in actual_match.group(1).split(',')]

        expected_match = re.search(r'Expected\s*\[([\d\.,\s]+)\]', command_text)
        expected = (
            [float(x.strip()) for x in expected_match.group(1).split(',')]
            if expected_match else self.expected
        )

        precision_match = re.search(r'±([\d\.]+)\s*mm', command_text)
        precision = float(precision_match.group(1)) if precision_match else 0.2

        if len(actual) != len(expected):
            raise ValueError(
                f"Measurement count mismatch: expected {len(expected)} values, got {len(actual)}"
            )

        return {'expected': expected, 'actual': actual, 'precision': precision}

    def calculate_errors(self, expected, actual):
        exp = np.array(expected)
        act = np.array(actual)
        return {
            'absolute': np.abs(act - exp).tolist(),
            'signed': (act - exp).tolist(),
            'max': float(np.max(np.abs(act - exp))),
            'mean': float(np.mean(np.abs(act - exp))),
            'rms': float(np.sqrt(np.mean((act - exp) ** 2))),
        }

    def calculate_z_scores(self, expected, actual, precision):
        exp = np.array(expected)
        act = np.array(actual)
        z = (act - exp) / precision
        return {
            'values': z.tolist(),
            'max_abs': float(np.max(np.abs(z))),
            'within_1sigma': int(np.sum(np.abs(z) <= 1)),
            'within_2sigma': int(np.sum(np.abs(z) <= 2)),
        }

    def detect_pattern(self, actual):
        arr = np.array(actual)
        diffs = np.diff(arr)

        if np.all(diffs > 0):
            trend = "consistently increasing"
        elif np.all(diffs < 0):
            trend = "consistently decreasing"
        elif np.std(diffs) < 0.1:
            trend = "uniform spacing"
        else:
            trend = "irregular"

        signed_errors = np.array(actual) - np.array(self.expected[:len(actual)])
        if np.all(signed_errors > 0):
            bias = "systematic positive bias (overshooting)"
        elif np.all(signed_errors < 0):
            bias = "systematic negative bias (undershooting)"
        else:
            bias = "mixed (no consistent direction)"

        return {'trend': trend, 'bias': bias}

    def generate_recommendation(self, parsed):
        errors = self.calculate_errors(parsed['expected'], parsed['actual'])
        z = self.calculate_z_scores(parsed['expected'], parsed['actual'], parsed['precision'])
        n = len(parsed['actual'])

        if errors['max'] <= parsed['precision']:
            return "All measurements within precision tolerance. No calibration needed."
        if z['within_2sigma'] == n:
            return "Measurements within 2σ. Minor drift detected — schedule routine calibration."
        if errors['mean'] > parsed['precision'] * 3:
            return "Mean error exceeds 3× precision threshold. Immediate recalibration required."
        return (
            f"Max error {errors['max']:.3f} mm exceeds ±{parsed['precision']} mm tolerance. "
            "Recalibration recommended before next operation."
        )

    def format_report(self, parsed, errors, z_scores, pattern, recommendation):
        lines = [
            "=== Clawbot Science Analysis Report ===",
            f"Positions tested : {parsed['expected']}",
            f"Actual readings  : {[round(a, 3) for a in parsed['actual']]}",
            f"Precision target : ±{parsed['precision']} mm",
            "",
            "--- Error Analysis ---",
            f"Max error  : {errors['max']:.3f} mm",
            f"Mean error : {errors['mean']:.3f} mm",
            f"RMS error  : {errors['rms']:.3f} mm",
            f"Per-point  : {[round(e, 3) for e in errors['absolute']]}",
            "",
            "--- Z-Score Analysis ---",
            f"Z-scores   : {[round(z, 2) for z in z_scores['values']]}",
            f"Within 1σ  : {z_scores['within_1sigma']}/{len(parsed['actual'])}",
            f"Within 2σ  : {z_scores['within_2sigma']}/{len(parsed['actual'])}",
            "",
            "--- Movement Pattern ---",
            f"Trend : {pattern['trend']}",
            f"Bias  : {pattern['bias']}",
            "",
            "--- Recommendation ---",
            recommendation,
            "=" * 38,
        ]
        return "\n".join(lines)

    def execute(self, command_text):
        parsed = self.parse_one_line_command(command_text)
        errors = self.calculate_errors(parsed['expected'], parsed['actual'])
        z_scores = self.calculate_z_scores(parsed['expected'], parsed['actual'], parsed['precision'])
        pattern = self.detect_pattern(parsed['actual'])
        recommendation = self.generate_recommendation(parsed)
        return self.format_report(parsed, errors, z_scores, pattern, recommendation)


def setup(bot):
    bot.add_command(ScienceAnalysisCommand())
