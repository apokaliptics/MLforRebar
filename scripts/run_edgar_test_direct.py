from scripts.download_edgar import main

if __name__ == '__main__':
    # Run a small test for AAPL only
    main(tickers_file='scripts/test_tickers.txt', max_files=5, out='datasets/edgar_md_test', email='dev@example.com')
