import unittest

from datetime import datetime, timedelta, timezone

from analysis import OrderBookAPIAnalysis
from api_analysers import NewAPIOrderBookAnalyser, OldAPIOrderBookAnalyser


class TestWithMockData(unittest.TestCase):
    def setUp(self):
        self.mock_old_api_data = self._generate_mock_old_api_data()
        self.mock_new_api_data = self._generate_mock_new_api_data()

        self.old_orderbook_api_analyser = OldAPIOrderBookAnalyser(
            self.mock_old_api_data)
        self.new_orderbook_api_analyser = NewAPIOrderBookAnalyser(
            self.mock_new_api_data)
        self.orderbook_api_analysis = OrderBookAPIAnalysis(
            self.mock_old_api_data, self.mock_new_api_data)

    @staticmethod
    def _generate_mock_old_api_data():
        base_time = datetime(2025, 4, 29, 12, 0, 0, tzinfo=timezone.utc)

        mock_data = []

        exchange_time = int(base_time.timestamp() * 1000000)

        recv_time_1 = base_time + timedelta(milliseconds=150)
        recv_time_2 = base_time + timedelta(milliseconds=200)
        recv_time_3 = base_time + timedelta(milliseconds=250)

        mock_data.append({
            "type": "orderbookdepth",
            "content": {
                "datetime": str(exchange_time),
                "list": [
                    {
                        "total": "2",
                        "orderType": "bid",
                        "quantity": "0.1",
                        "price": "10000",
                        "symbol": "ABC_USD"
                    }
                ]
            },
            "recv_time": recv_time_1.strftime("%Y-%m-%d %H:%M:%S.%f")
        })

        mock_data.append({
            "type": "orderbookdepth",
            "content": {
                "datetime": str(exchange_time),
                "list": [
                    {
                        "total": "2",
                        "orderType": "bid",
                        "quantity": "0.2",
                        "price": "10010",
                        "symbol": "ABC_USD"
                    }
                ]
            },
            "recv_time": recv_time_2.strftime("%Y-%m-%d %H:%M:%S.%f")
        })

        mock_data.append({
            "type": "orderbookdepth",
            "content": {
                "datetime": str(exchange_time),
                "list": [
                    {
                        "total": "2",
                        "orderType": "bid",
                        "quantity": "0.3",
                        "price": "10020",
                        "symbol": "ABC_USD"
                    }
                ]
            },
            "recv_time": recv_time_3.strftime("%Y-%m-%d %H:%M:%S.%f")
        })

        return mock_data

    @staticmethod
    def _generate_mock_new_api_data():
        base_time = datetime(2025, 4, 29, 12, 0, 0, tzinfo=timezone.utc)

        exchange_time = int(base_time.timestamp() * 1000)

        recv_time_1 = base_time + timedelta(milliseconds=100)
        recv_time_2 = base_time + timedelta(milliseconds=120)
        recv_time_3 = base_time + timedelta(milliseconds=140)

        mock_data = []

        mock_data.append({
            "ty": "orderbook",
            "cd": "USD-ABC",
            "tas": 0.5,
            "tbs": 0.6,
            "obu": [
                {"ap": 10000, "bp": 9900, "as": 0.1, "bs": 0.2},
                {"ap": 10010, "bp": 9890, "as": 0.2, "bs": 0.3},
                {"ap": 10020, "bp": 9880, "as": 0.3, "bs": 0.4}
            ],
            "lv": 1,
            "tms": exchange_time,
            "st": "REALTIME",
            "recv_time": recv_time_1.strftime("%Y-%m-%d %H:%M:%S.%f")
        })

        mock_data.append({
            "ty": "orderbook",
            "cd": "USD-ABC",
            "tas": 1.0,
            "tbs": 1.2,
            "obu": [
                {"ap": 10010, "bp": 9910, "as": 0.1, "bs": 0.2},
                {"ap": 10020, "bp": 9900, "as": 0.2, "bs": 0.3},
                {"ap": 10030, "bp": 9890, "as": 0.3, "bs": 0.4}
            ],
            "lv": 1,
            "tms": exchange_time,
            "st": "REALTIME",
            "recv_time": recv_time_2.strftime("%Y-%m-%d %H:%M:%S.%f")
        })

        mock_data.append({
            "ty": "orderbook",
            "cd": "USD-ABC",
            "tas": 1.5,
            "tbs": 1.8,
            "obu": [
                {"ap": 10020, "bp": 9920, "as": 0.1, "bs": 0.2},
                {"ap": 10030, "bp": 9910, "as": 0.2, "bs": 0.3},
                {"ap": 10040, "bp": 9900, "as": 0.3, "bs": 0.4}
            ],
            "lv": 1,
            "tms": exchange_time,
            "st": "REALTIME",
            "recv_time": recv_time_3.strftime("%Y-%m-%d %H:%M:%S.%f")
        })

        return mock_data

    def test_mock_latency_calculation(self):
        old_latency = self.old_orderbook_api_analyser.get_latency()
        new_latency = self.new_orderbook_api_analyser.get_latency()

        self.assertEqual(len(old_latency), 3)
        self.assertEqual(len(new_latency), 3)

        expected_old_latencies_ms = [150, 200, 250]
        expected_new_latencies_ms = [100, 120, 140]

        for i, expected in enumerate(expected_old_latencies_ms):
            self.assertEqual(old_latency.iloc[i], expected)

        for i, expected in enumerate(expected_new_latencies_ms):
            self.assertEqual(new_latency.iloc[i], expected)

        old_mean = old_latency.mean()
        new_mean = new_latency.mean()

        self.assertEqual(old_mean, 200)  # (200+150+250)/3 = 200
        self.assertEqual(new_mean, 120)  # (100+120+140)/3 = 120

    def test_mock_stats(self):
        stats = self.orderbook_api_analysis._perform_statistical_test()
        self.assertEqual(stats['better_api'], 'New API')

        comparison_df = self.orderbook_api_analysis._create_comparison_dataframe()
        old_mean = comparison_df[comparison_df['Metric']
                                 == 'Mean Latency (ms)']['Old API'].values[0]
        new_mean = comparison_df[comparison_df['Metric']
                                 == 'Mean Latency (ms)']['New API'].values[0]
        self.assertGreater(old_mean, new_mean)


if __name__ == '__main__':
    unittest.main()
