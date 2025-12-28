from sec_edgar_downloader import Downloader

def test(email='dev@example.com'):
    try:
        dl = Downloader(email, 'test_downloads')
        print('Downloader created')
        try:
            dl.get('10-K', 'AAPL')
            print('Called dl.get with (filing, ticker)')
        except TypeError as e:
            print('TypeError with (filing, ticker):', e)
            try:
                dl.get('AAPL', '10-K')
                print('Called dl.get with (ticker, filing)')
            except Exception as e2:
                print('Both signatures failed:', e2)
    except Exception as e:
        print('Failed to create Downloader:', e)

if __name__ == '__main__':
    test()