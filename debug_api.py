#!/usr/bin/env python3
"""
API呼び出しのデバッグスクリプト
"""

import sys
import requests
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_api_call():
    """API呼び出しの詳細デバッグ"""
    from src import create_weather_client, setup_logging
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    setup_logging("DEBUG")
    
    api_key = os.getenv('OPENWEATHER_API_KEY')
    print(f"APIキー: {api_key[:8]}...{api_key[-4:]}")
    
    # 直接requests呼び出し
    print("\n=== 直接requests呼び出し ===")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': 'Tokyo',
        'appid': api_key,
        'units': 'metric',
        'lang': 'en'
    }
    
    print(f"URL: {url}")
    print(f"パラメータ: {params}")
    
    response = requests.get(url, params=params)
    print(f"ステータスコード: {response.status_code}")
    print(f"レスポンス: {response.text[:200]}...")
    
    # WeatherAPIクライアント呼び出し
    print("\n=== WeatherAPIクライアント呼び出し ===")
    try:
        client = create_weather_client()
        print("クライアント作成成功")
        
        # APIキー検証
        print("APIキー検証中...")
        is_valid = client.validate_api_key()
        print(f"APIキー有効: {is_valid}")
        
        # 実際の天気取得
        print("天気データ取得中...")
        weather = client.get_current_weather("Tokyo")
        print(f"取得成功: {weather}")
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_call()