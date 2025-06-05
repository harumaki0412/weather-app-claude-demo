#!/usr/bin/env python3
"""
OpenWeatherMap APIキー検証スクリプト
実際のAPIキーが正しく設定されているかテストします
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_api_key():
    """APIキーの検証"""
    print("=== OpenWeatherMap APIキー検証 ===\n")
    
    try:
        from src import create_weather_client, setup_logging
        from src.exceptions import APIKeyError, APIConnectionError, CityNotFoundError
        from dotenv import load_dotenv
        
        # 環境変数読み込み
        load_dotenv()
        
        # ログレベルを下げて見やすくする
        setup_logging("ERROR")
        
        # 1. 環境変数確認
        api_key = os.getenv('OPENWEATHER_API_KEY')
        print(f"1. 環境変数確認:")
        if api_key:
            # APIキーの一部だけ表示（セキュリティ）
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "短すぎる"
            print(f"   ✓ APIキーが設定されています: {masked_key}")
        else:
            print("   ✗ APIキーが設定されていません")
            print("   .envファイルのOPENWEATHER_API_KEYを確認してください")
            return False
        
        # 2. クライアント初期化
        print(f"\n2. APIクライアント初期化:")
        try:
            client = create_weather_client()
            print("   ✓ クライアント初期化成功")
        except Exception as e:
            print(f"   ✗ クライアント初期化失敗: {e}")
            return False
        
        # 3. APIキー有効性チェック
        print(f"\n3. APIキー有効性チェック:")
        try:
            if client.validate_api_key():
                print("   ✓ APIキーは有効です")
            else:
                print("   ✗ APIキーが無効です")
                return False
        except APIKeyError:
            print("   ✗ APIキーが無効です")
            print("   OpenWeatherMapで正しいAPIキーを確認してください")
            return False
        except APIConnectionError:
            print("   ⚠ ネットワーク接続エラー（インターネット接続を確認）")
            return False
        
        # 4. 実際の天気データ取得テスト
        print(f"\n4. 実際の天気データ取得テスト:")
        test_cities = ["Tokyo", "London", "New York"]
        
        for city in test_cities:
            try:
                print(f"   {city}の天気を取得中...")
                weather = client.get_current_weather(city)
                print(f"   ✓ {city}: {weather.description}, {weather.temperature}°C")
            except CityNotFoundError:
                print(f"   ⚠ {city}: 都市が見つかりません")
            except Exception as e:
                print(f"   ✗ {city}: エラー - {e}")
                return False
        
        print(f"\n=== 検証完了 ===")
        print("✅ APIキーが正常に動作しています！")
        print("\n次のコマンドで実際にアプリを試せます:")
        print("  CLI版: ./weather Tokyo")
        print("  Web版: ./web")
        return True
        
    except ImportError as e:
        print(f"✗ インポートエラー: {e}")
        print("pip install -r requirements.txt を実行してください")
        return False
    except Exception as e:
        print(f"✗ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_troubleshooting():
    """トラブルシューティング情報"""
    print("\n🔧 トラブルシューティング:")
    print("\n1. APIキーが無効な場合:")
    print("   - OpenWeatherMapでAPIキーを再確認")
    print("   - 新しいAPIキーは有効化まで最大2時間かかります")
    print("   - 無料プランの制限を確認（60calls/min, 1000calls/day）")
    
    print("\n2. .envファイルの設定例:")
    print("   OPENWEATHER_API_KEY=your_32_character_api_key_here")
    
    print("\n3. 環境変数の直接設定（一時的）:")
    print("   export OPENWEATHER_API_KEY='your_api_key'")
    
    print("\n4. APIキー取得サイト:")
    print("   https://home.openweathermap.org/api_keys")

if __name__ == "__main__":
    success = verify_api_key()
    
    if not success:
        show_troubleshooting()
        sys.exit(1)
    
    sys.exit(0)