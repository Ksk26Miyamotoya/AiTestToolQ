import sys
from src.main import main

if __name__ == "__main__":
    # Python 3.12以上が必要
    if sys.version_info < (3, 12):
        print("エラー: Python 3.12以上が必要です")
        sys.exit(1)
    main()
