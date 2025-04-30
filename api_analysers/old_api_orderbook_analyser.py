from datetime import datetime, timezone

import pandas as pd

from api_analysers.base_api_analyser import BaseAPIAnalyser


class OldAPIOrderBookAnalyser(BaseAPIAnalyser):
    def _convert_raw_data_to_dataframe(self) -> pd.DataFrame:
        records = []
        for entry in self.data:
            recv_time = datetime.strptime(
                entry['recv_time'], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)

            exchange_timestamp_us = int(entry['content']['datetime'])
            exchange_timestamp_ms = exchange_timestamp_us / 1000.0

            for order in entry['content']['list']:
                records.append({
                    'recv_time': recv_time,
                    'exchange_timestamp_ms': exchange_timestamp_ms,
                    'price': float(order['price']),
                    'quantity': float(order['quantity']),
                    'order_type': order['orderType'],
                    'total': int(order['total']),
                    'symbol': order['symbol']
                })

        return pd.DataFrame(records)

    def get_latency(self) -> pd.Series:
        grouped = self.df.groupby('recv_time').first().reset_index()
        recv_timestamps_ms = grouped['recv_time'].apply(
            lambda x: x.timestamp() * 1000)
        latency = recv_timestamps_ms - grouped['exchange_timestamp_ms']

        return latency
