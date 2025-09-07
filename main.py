import scraper
import analysis
import os

def main():
    # Step 1: Run scraper
    print("Running scraper...")
    scraper.run()

    # Step 2: Run analysis
    print("Running analysis...")
    analysis.run()

if __name__ == "__main__":
    main()
