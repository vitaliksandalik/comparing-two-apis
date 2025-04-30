import unittest
import pandas as pd

from api_analysers import NewAPIOrderBookAnalyser, OldAPIOrderBookAnalyser
from test.mock_samples import TEST_NEW_API_SAMPLES, TEST_OLD_API_SAMPLES


class TestOldAPIOrderBookAnalyser(unittest.TestCase):
    def setUp(self):
        self.analyser = OldAPIOrderBookAnalyser(TEST_OLD_API_SAMPLES)

    def test_convert_raw_data_to_dataframe(self):
        df = self.analyser.df
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue('recv_time' in df.columns)
        self.assertTrue('exchange_timestamp_ms' in df.columns)
        self.assertTrue('price' in df.columns)
        self.assertTrue('quantity' in df.columns)

    def test_get_latency(self):
        latency = self.analyser.get_latency()
        self.assertIsInstance(latency, pd.Series)
        self.assertEqual(len(latency), len(TEST_OLD_API_SAMPLES))

        self.assertTrue(all(latency > 0))
        self.assertTrue(all(latency < 1000))

        self.assertTrue(latency.mean() > 100)
        self.assertTrue(latency.mean() < 250)


class TestNewAPIOrderBookAnalyser(unittest.TestCase):
    def setUp(self):
        self.analyser = NewAPIOrderBookAnalyser(TEST_NEW_API_SAMPLES)

    def test_convert_raw_data_to_dataframe(self):
        df = self.analyser.df
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue('recv_time' in df.columns)
        self.assertTrue('exchange_timestamp_ms' in df.columns)
        self.assertTrue('ask_price' in df.columns)
        self.assertTrue('bid_price' in df.columns)
        self.assertTrue('ask_size' in df.columns)
        self.assertTrue('bid_size' in df.columns)

    def test_get_latency(self):
        latency = self.analyser.get_latency()
        self.assertIsInstance(latency, pd.Series)
        self.assertEqual(len(latency), len(TEST_NEW_API_SAMPLES))

        self.assertTrue(all(latency > 0))
        self.assertTrue(all(latency < 1000))

        self.assertTrue(latency.mean() > 100)
        self.assertTrue(latency.mean() < 250)


if __name__ == '__main__':
    unittest.main()
