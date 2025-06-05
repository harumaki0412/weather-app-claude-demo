#!/usr/bin/env python3
"""
Web版起動テスト
実際にサーバーを起動せずに、Flaskアプリケーションの初期化テスト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_web_app_initialization():
    """Webアプリケーション初期化テスト"""
    try:
        from src.weather_web import WeatherWebApp
        from src import setup_logging
        
        setup_logging("INFO")
        
        print("=== Web版初期化テスト ===")
        
        # Webアプリケーション作成
        app = WeatherWebApp()
        
        print("✓ WeatherWebApp初期化成功")
        
        # Flask アプリケーション確認
        flask_app = app.flask_app
        if flask_app:
            print("✓ Flask アプリケーション作成成功")
            print(f"  - デバッグモード: {flask_app.config.get('DEBUG')}")
            print(f"  - ホスト: {flask_app.config.get('HOST')}")
            print(f"  - ポート: {flask_app.config.get('PORT')}")
        else:
            print("✗ Flask アプリケーション作成失敗")
            return False
        
        # 天気クライアント確認
        if app.weather_client:
            print("✓ 天気APIクライアント初期化成功")
        else:
            print("⚠ 天気APIクライアント初期化失敗（APIキー無効）")
        
        # ルート確認
        with flask_app.app_context():
            from flask import url_for
            routes = []
            for rule in flask_app.url_map.iter_rules():
                routes.append(f"{rule.methods} {rule}")
            
            print("✓ 登録されたルート:")
            for route in sorted(routes):
                print(f"  - {route}")
        
        print("\n=== テスト完了 ===")
        print("Webアプリケーションは正常に初期化できます")
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_web_app_initialization()
    sys.exit(0 if success else 1)