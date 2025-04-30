from abc import ABC, abstractmethod
from typing import Any, Dict, List

import pandas as pd


class BaseAPIAnalyser(ABC):
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.df = self._convert_raw_data_to_dataframe()

    @abstractmethod
    def _convert_raw_data_to_dataframe(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_latency(self) -> pd.Series:
        pass

    def get_latency_stats(self) -> Dict[str, float]:
        latencies = self.get_latency()
        return {
            'mean_latency': latencies.mean(),
            'median_latency': latencies.median(),
            'min_latency': latencies.min(),
            'max_latency': latencies.max(),
            'std_latency': latencies.std()
        }
