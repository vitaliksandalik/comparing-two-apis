import json

from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from scipy import stats

from api_analysers import NewAPIOrderBookAnalyser, OldAPIOrderBookAnalyser


class OrderBookAPIAnalysis:
    def __init__(self, old_api_data: List[Dict[str, Any]], new_api_data: List[Dict[str, Any]]):
        self.old_orderbook_api_analyser = OldAPIOrderBookAnalyser(old_api_data)
        self.new_orderbook_api_analyser = NewAPIOrderBookAnalyser(new_api_data)

    def run_complete_analysis_and_save_reports(self) -> Tuple[pd.DataFrame, Dict]:
        comparison_df = self._create_comparison_dataframe()

        comparison_df.to_csv(
            'reports/orderbook_latency_comparison.csv', index=False)

        self._plot_latency_comparison()
        self._plot_detailed_latency_bars()

        stats_results = self._perform_statistical_test()

        byte_size_df = self._compare_byte_size()
        byte_size_df.to_csv(
            'reports/orderbook_byte_size_comparison.csv', index=False)
        self._plot_byte_size_comparison()

        print("\n=== Orderbook API Comparison Results ===\n")
        print(comparison_df)

        print("\n=== Statistical Tests ===")
        print(
            f"Is difference statistically significant? {stats_results['is_difference_significant']}")
        print(f"Better API for latency: {stats_results['better_api']}")

        self._print_byte_size_comparison(byte_size_df)

        return comparison_df, stats_results

    def _create_comparison_dataframe(self) -> pd.DataFrame:
        old_latency = self.old_orderbook_api_analyser.get_latency_stats()
        new_latency = self.new_orderbook_api_analyser.get_latency_stats()

        return pd.DataFrame({
            'Metric': [
                'Mean Latency (ms)', 'Median Latency (ms)', 'Min Latency (ms)',
                'Max Latency (ms)', 'Std Dev Latency (ms)'
            ],
            'Old API': [
                old_latency['mean_latency'],
                old_latency['median_latency'],
                old_latency['min_latency'],
                old_latency['max_latency'],
                old_latency['std_latency'],
            ],
            'New API': [
                new_latency['mean_latency'],
                new_latency['median_latency'],
                new_latency['min_latency'],
                new_latency['max_latency'],
                new_latency['std_latency'],
            ]
        })

    @staticmethod
    def _compare_byte_size() -> pd.DataFrame:
        old_api_ask = {
            "total": "1",
            "orderType": "ask",
            "quantity": "0.0387",
            "price": "133331000",
            "symbol": "ABC_USD"
        }

        old_api_bid = {
            "total": "2",
            "orderType": "bid",
            "quantity": "0.9006",
            "price": "133281000",
            "symbol": "ABC_USD"
        }

        old_api_container = {
            "type": "orderbookdepth",
            "content": {
                "datetime": "1732796700879952",
                "list": [old_api_ask, old_api_bid]
            },
            "recv_time": "2024-11-28 12:25:01.071989"
        }

        new_api_entry = {
            "ap": 133331000,
            "bp": 133281000,
            "as": 0.0387,
            "bs": 0.9006
        }

        new_api_container = {
            "ty": "orderbook",
            "cd": "USD-ABC",
            "tas": 0.2823,
            "tbs": 1.1529,
            "obu": [new_api_entry],
            "lv": 1,
            "tms": 1732796701204,
            "st": "REALTIME",
            "recv_time": "2024-11-28 12:25:01.414389"
        }

        old_api_ask_bytes = len(json.dumps(old_api_ask))
        old_api_bid_bytes = len(json.dumps(old_api_bid))
        old_api_total_bytes = old_api_ask_bytes + old_api_bid_bytes

        old_api_message_bytes = len(json.dumps(old_api_container))

        new_api_entry_bytes = len(json.dumps(new_api_entry))
        new_api_message_bytes = len(json.dumps(new_api_container))

        entry_size_reduction = (
            1 - new_api_entry_bytes / old_api_total_bytes) * 100
        message_size_reduction = (
            1 - new_api_message_bytes / old_api_message_bytes) * 100

        raw_data_df = pd.DataFrame({
            'Metric': [
                'Old API: Single Ask Entry Size (bytes)',
                'Old API: Single Bid Entry Size (bytes)',
                'Old API: Total (Ask + Bid) (bytes)',
                'New API: Single Combined Entry (bytes)',
                'Entry Size Reduction (%)',
                'Old API: Full Message Size (bytes)',
                'New API: Full Message Size (bytes)',
                'Full Message Size Reduction (%)',
            ],
            'Value': [
                old_api_ask_bytes,
                old_api_bid_bytes,
                old_api_total_bytes,
                new_api_entry_bytes,
                f"{entry_size_reduction:.2f}%",
                old_api_message_bytes,
                new_api_message_bytes,
                f"{message_size_reduction:.2f}%",
            ]
        })

        plot_data = [
            {'Category': 'Entry Size',
                'API': 'Old API (Ask + Bid)', 'Bytes': old_api_total_bytes},
            {'Category': 'Entry Size',
                'API': 'New API (Combined)', 'Bytes': new_api_entry_bytes},

            {'Category': 'Message Size', 'API': 'Old API',
                'Bytes': old_api_message_bytes},
            {'Category': 'Message Size', 'API': 'New API',
                'Bytes': new_api_message_bytes}
        ]

        plot_df = pd.DataFrame(plot_data)

        plot_df.attrs['entry_size_reduction'] = f"{entry_size_reduction:.2f}%"
        plot_df.attrs['message_size_reduction'] = f"{message_size_reduction:.2f}%"

        plot_df.attrs['raw_data'] = raw_data_df

        return plot_df

    def _perform_statistical_test(self) -> Dict[str, Any]:
        old_latency = self.old_orderbook_api_analyser.get_latency()
        new_latency = self.new_orderbook_api_analyser.get_latency()

        t_stat, p_val = stats.ttest_ind(
            old_latency, new_latency, equal_var=False)

        w_stat, w_p_val = stats.mannwhitneyu(old_latency, new_latency)

        return {
            't_statistic': t_stat,
            'p_value': p_val,
            'wilcoxon_statistic': w_stat,
            'wilcoxon_p_value': w_p_val,
            'is_difference_significant': p_val < 0.05,
            'better_api': 'New API' if old_latency.mean() > new_latency.mean() else 'Old API'
        }

    def export_detailed_metrics(self, file_path='reports/orderbook_detailed_metrics.csv') -> pd.DataFrame:
        old_latency = self.old_orderbook_api_analyser.get_latency()
        new_latency = self.new_orderbook_api_analyser.get_latency()

        old_df = pd.DataFrame({
            'API': 'Old API',
            'Message': range(1, len(old_latency) + 1),
            'Latency (ms)': old_latency.values,
        })

        new_df = pd.DataFrame({
            'API': 'New API',
            'Message': range(1, len(new_latency) + 1),
            'Latency (ms)': new_latency.values,
        })

        combined_df = pd.concat([old_df, new_df], ignore_index=True)
        combined_df.to_csv(file_path, index=False)

        return combined_df

    def _plot_latency_comparison(self, save_path: str = 'reports/orderbook_latency_comparison.png') -> None:
        old_latency = self.old_orderbook_api_analyser.get_latency()
        new_latency = self.new_orderbook_api_analyser.get_latency()

        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        plt.boxplot([old_latency, new_latency],
                    tick_labels=['Old API', 'New API'])
        plt.title('Orderbook Latency Distribution (ms)')
        plt.ylabel('Milliseconds')
        plt.grid(True, linestyle='--', alpha=0.7)

        plt.subplot(1, 2, 2)
        old_mean = old_latency.mean()
        new_mean = new_latency.mean()
        plt.bar(['Old API', 'New API'], [old_mean, new_mean])
        plt.title(
            f'Mean Orderbook Latency: Old={old_mean:.2f}ms, New={new_mean:.2f}ms')
        plt.ylabel('Milliseconds')

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    def _plot_detailed_latency_bars(self, save_path='reports/orderbook_detailed_latency.png') -> None:
        combined_df = self.export_detailed_metrics()

        plt.figure(figsize=(14, 8))

        ax = sns.barplot(x='Message', y='Latency (ms)',
                         hue='API', data=combined_df)

        old_api_data = combined_df[combined_df['API'] == 'Old API']
        new_api_data = combined_df[combined_df['API'] == 'New API']

        old_mean = old_api_data['Latency (ms)'].mean()
        new_mean = new_api_data['Latency (ms)'].mean()

        ax.axhline(old_mean, color='blue', linestyle='--',
                   label=f'Old API Mean: {old_mean:.2f}ms')
        ax.axhline(new_mean, color='orange', linestyle='--',
                   label=f'New API Mean: {new_mean:.2f}ms')

        percent_improvement = ((old_mean - new_mean) / old_mean * 100)
        improvement_text = f"Improvement: {percent_improvement:.2f}%"

        plt.title('Orderbook API Latency Comparison by Message')
        plt.xlabel('Message Number')
        plt.ylabel('Latency (ms)')

        plt.annotate(improvement_text, xy=(0.02, 0.95), xycoords='axes fraction',
                     fontsize=12, fontweight='bold',
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

        handles, labels = ax.get_legend_handles_labels()
        plt.legend(handles=handles, labels=labels)

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    def _plot_byte_size_comparison(self, save_path='reports/orderbook_byte_size_comparison.png') -> None:
        plot_df = self._compare_byte_size()

        plt.figure(figsize=(12, 8))

        ax = sns.barplot(x='Category', y='Bytes', hue='API', data=plot_df)

        for container in ax.containers:
            ax.bar_label(container)

        plt.title('Orderbook Byte Size Comparison')
        plt.ylabel('Size in Bytes')
        plt.grid(True, linestyle='--', alpha=0.7, axis='y')

        entry_reduction = plot_df.attrs['entry_size_reduction']
        message_reduction = plot_df.attrs['message_size_reduction']

        plt.annotate(f"Reduction: {entry_reduction}",
                     xy=(0, 0), xytext=(0.18, 0.90), textcoords='figure fraction',
                     fontsize=10, fontweight='bold')

        plt.annotate(f"Reduction: {message_reduction}",
                     xy=(0, 0), xytext=(0.68, 0.90), textcoords='figure fraction',
                     fontsize=10, fontweight='bold')

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def _print_byte_size_comparison(byte_size_df: pd.DataFrame) -> None:
        print("\n=== Byte Size Comparison ===")

        raw_data = byte_size_df.attrs['raw_data']

        print("Entry Size Comparison:")
        print(f"  Old API (Ask + Bid): {raw_data.loc[2, 'Value']} bytes")
        print(f"  New API (Combined): {raw_data.loc[3, 'Value']} bytes")
        print(f"  Reduction: {raw_data.loc[4, 'Value']}")

        print("\nFull Message Size Comparison:")
        print(f"  Old API: {raw_data.loc[5, 'Value']} bytes")
        print(f"  New API: {raw_data.loc[6, 'Value']} bytes")
        print(f"  Reduction: {raw_data.loc[7, 'Value']}")
