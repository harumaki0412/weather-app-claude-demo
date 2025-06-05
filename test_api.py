#!/usr/bin/env python3
"""
API動作確認用テストスクリプト
実際にAPIを呼び出して動作を確認します
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import create_weather_client, setup_logging
from src.exceptions import WeatherAPIError


def main():
    """メイン実行関数"""
    # ログ設定
    setup_logging("DEBUG")
    
    try:
        # APIクライアント作成
        print("=== Weather API テスト ===")
        client = create_weather_client()
        
        # APIキー検証
        print("\n1. APIキー検証中...")
        if client.validate_api_key():
            print("✓ APIキーは有効です")
        else:
            print("✗ APIキーが無効です")
            return
        
        # テスト都市での天気取得
        test_cities = ["Tokyo", "London", "New York", "InvalidCity"]
        
        for city in test_cities:
            print(f"\n2. {city}の天気情報取得中...")
            try:
                weather = client.get_current_weather(city)
                print(f"✓ 成功:")
                print(weather)
                print(f"JSON: {weather.to_dict()}")
            except WeatherAPIError as e:
                print(f"✗ エラー: {e}")
    
    except Exception as e:
        print(f"予期しないエラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()