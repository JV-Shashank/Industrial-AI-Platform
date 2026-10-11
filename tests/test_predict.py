
import unittest

from src.predict import predict_failure, validate_readings


SAMPLE_READINGS = {
    "air_temperature": 300.0,
    "process_temperature": 310.0,
    "rotational_speed": 1500,
    "torque": 40.0,
    "tool_wear": 100,
    "product_type": "M",
}


class TestPredictionEngine(unittest.TestCase):

    def test_valid_readings(self):
        validate_readings(SAMPLE_READINGS)

    def test_invalid_product_type(self):
        readings = SAMPLE_READINGS.copy()
        readings["product_type"] = "X"

        with self.assertRaises(ValueError):
            validate_readings(readings)

    def test_negative_torque(self):
        readings = SAMPLE_READINGS.copy()
        readings["torque"] = -5

        with self.assertRaises(ValueError):
            validate_readings(readings)

    def test_missing_field(self):
        readings = SAMPLE_READINGS.copy()
        del readings["tool_wear"]

        with self.assertRaises(ValueError):
            validate_readings(readings)

    def test_prediction_output(self):
        result = predict_failure(SAMPLE_READINGS)

        self.assertIn("failure_probability", result)
        self.assertIn("predicted_failure", result)
        self.assertIn("risk_level", result)

        self.assertGreaterEqual(
            result["failure_probability"], 0.0
        )
        self.assertLessEqual(
            result["failure_probability"], 1.0
        )
        self.assertIn(result["predicted_failure"], [0, 1])
        self.assertIn(
            result["risk_level"],
            ["Low", "Medium", "High"],
        )


if __name__ == "__main__":
    unittest.main()
