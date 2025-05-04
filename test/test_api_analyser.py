import unittest
import os

import pandas as pd

from analysis import OrderBookAPIAnalysis
from test.mock_samples import TEST_NEW_API_SAMPLES, TEST_OLD_API_SAMPLES


class TestAPIComparisonAnalyser(unittest.TestCase):
    def setUp(self):
        self.analyser = OrderBookAPIAnalysis(
            TEST_OLD_API_SAMPLES, TEST_NEW_API_SAMPLES)

    def test_create_comparison_dataframe(self):
        df = self.analyser._create_comparison_dataframe()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)
        self.assertEqual(df.columns.tolist(), ['Metric', 'Old API', 'New API'])

        latency_row = df[df['Metric'] == 'Mean Latency (ms)']
        self.assertEqual(len(latency_row), 1)
        self.assertTrue(isinstance(latency_row['Old API'].iloc[0], float))
        self.assertTrue(isinstance(latency_row['New API'].iloc[0], float))

    def test_perform_statistical_test(self):
        results = self.analyser._perform_statistical_test()
        self.assertIsInstance(results, dict)
        self.assertTrue('t_statistic' in results)
        self.assertTrue('p_value' in results)
        self.assertTrue('wilcoxon_statistic' in results)
        self.assertTrue('wilcoxon_p_value' in results)
        self.assertTrue('is_difference_significant' in results)
        self.assertTrue('better_api' in results)

        self.assertIn(results['better_api'], ['Old API', 'New API'])

    def test_export_detailed_metrics(self):
        test_file = 'test_orderbook_metrics.csv'
        df = self.analyser.export_detailed_metrics(test_file)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(os.path.exists(test_file))

        loaded_df = pd.read_csv(test_file)
        self.assertEqual(len(loaded_df), len(
            TEST_OLD_API_SAMPLES) + len(TEST_NEW_API_SAMPLES))
        self.assertTrue('API' in loaded_df.columns)
        self.assertTrue('Latency (ms)' in loaded_df.columns)

        os.remove(test_file)

    def test_run_complete_analysis_and_save_reports(self):
        comparison_df, stats_results = self.analyser.run_complete_analysis_and_save_reports()
        self.assertIsInstance(comparison_df, pd.DataFrame)
        self.assertIsInstance(stats_results, dict)

        self.assertTrue(os.path.exists(
            'reports/orderbook_byte_size_message_comparison.csv'))
        self.assertTrue(os.path.exists(
            'reports/orderbook_byte_size_message_comparison.png'))
        self.assertTrue(os.path.exists(
            'reports/orderbook_latency_comparison.csv'))
        self.assertTrue(os.path.exists(
            'reports/orderbook_latency_by_message.png'))
        self.assertTrue(os.path.exists(
            'reports/orderbook_latency_by_message.csv'))
        self.assertTrue(os.path.exists(
            'reports/orderbook_latency_comparison.png'))


if __name__ == '__main__':
    unittest.main()
