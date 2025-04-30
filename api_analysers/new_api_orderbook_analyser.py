from datetime import datetime, timezone

import pandas as pd

from api_analysers.base_api_analyser import BaseAPIAnalyser


class NewAPIOrderBookAnalyser(BaseAPIAnalyser):
    def _convert_raw_data_to_dataframe(self) -> pd.DataFrame:
        records = []
        for entry in self.data:
            recv_time = datetime.strptime(
                entry['recv_time'], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)

            exchange_timestamp_ms = int(entry['tms'])

            for order in entry['obu']:
                records.append({
                    'recv_time': recv_time,
                    'exchange_timestamp_ms': exchange_timestamp_ms,
                    'ask_price': float(order['ap']),
                    'bid_price': float(order['bp']),
                    'ask_size': float(order['as']),
                    'bid_size': float(order['bs']),
                    'symbol': entry['cd']
                })

        return pd.DataFrame(records)

    def get_latency(self) -> pd.Series:
        grouped = self.df.groupby('recv_time').first().reset_index()
        recv_timestamps_ms = grouped['recv_time'].apply(
            lambda x: x.timestamp() * 1000)
        latency = recv_timestamps_ms - grouped['exchange_timestamp_ms']

        return latency
