#!/usr/bin/env python3
"""
Web版エンドポイントテスト
実際のHTTPリクエストなしでFlaskアプリケーションのエンドポイントをテスト
"""

import sys
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_web_endpoints():
    """Webエンドポイントテスト"""
    try:
        from src.weather_web import WeatherWebApp
        from src import setup_logging
        
        setup_logging("ERROR")  # エラーログのみ表示
        
        print("=== Web版エンドポイントテスト ===")
        
        # Webアプリケーション作成
        app = WeatherWebApp()
        flask_app = app.flask_app
        
        # テストクライアント作成
        with flask_app.test_client() as client:
            
            # 1. ホームページテスト
            print("\n1. ホームページ (/) テスト")
            response = client.get('/')
            print(f"   ステータス: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ ホームページ正常レスポンス")
            else:
                print(f"   ✗ ホームページエラー: {response.status_code}")
            
            # 2. ヘルスチェックテスト
            print("\n2. ヘルスチェック (/health) テスト")
            response = client.get('/health')
            print(f"   ステータス: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    health_data = response.get_json()
                    print(f"   レスポンス: {json.dumps(health_data, indent=2, ensure_ascii=False)}")
                    print("   ✓ ヘルスチェック正常レスポンス")
                except:
                    print("   ⚠ JSONデータ解析失敗")
            else:
                print(f"   ✗ ヘルスチェックエラー: {response.status_code}")
            
            # 3. APIテストページ
            print("\n3. APIテストページ (/api-test) テスト")
            response = client.get('/api-test')
            print(f"   ステータス: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ APIテストページ正常レスポンス")
            else:
                print(f"   ✗ APIテストページエラー: {response.status_code}")
            
            # 4. 天気API（無効なAPIキーでエラーレスポンステスト）
            print("\n4. 天気API (/api/weather/Tokyo) テスト")
            response = client.get('/api/weather/Tokyo')
            print(f"   ステータス: {response.status_code}")
            
            try:
                api_data = response.get_json()
                print(f"   レスポンス: {json.dumps(api_data, indent=2, ensure_ascii=False)}")
                
                if response.status_code == 401:
                    print("   ✓ APIキーエラーが正常に処理されました")
                elif response.status_code == 200:
                    print("   ✓ API正常レスポンス（有効なAPIキー）")
                else:
                    print(f"   ⚠ 予期しないステータス: {response.status_code}")
            except:
                print("   ⚠ JSONデータ解析失敗")
            
            # 5. POSTリクエストテスト（天気検索）
            print("\n5. 天気検索フォーム (/weather POST) テスト")
            response = client.post('/weather', data={'city': 'Tokyo'})
            print(f"   ステータス: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ 天気検索フォーム正常処理")
            else:
                print(f"   ✗ 天気検索フォームエラー: {response.status_code}")
        
        print("\n=== エンドポイントテスト完了 ===")
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_web_endpoints()
    sys.exit(0 if success else 1)