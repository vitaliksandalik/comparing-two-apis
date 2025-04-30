from analysis import OrderBookAPIAnalysis
from data import OLD_API_SAMPLES, NEW_API_SAMPLES


def main():
    analyser = OrderBookAPIAnalysis(OLD_API_SAMPLES, NEW_API_SAMPLES)
    analyser.run_complete_analysis_and_save_reports()
    print("\nReports saved to reports/ directory.")


if __name__ == "__main__":
    main()
