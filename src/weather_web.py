#!/usr/bin/env python3
"""
Weather Web App - Flask ベースの天気情報取得Webアプリケーション
CLI版で作成したAPIクライアントを活用したユーザーフレンドリーなWebインターフェース
"""

__version__ = "1.0.0"

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src import create_weather_client, setup_logging
from src.exceptions import (
    CityNotFoundError,
    APIKeyError,
    APIConnectionError,
    APIResponseError,
    WeatherAPIError
)


class WeatherWebApp:
    """天気情報Webアプリケーションクラス"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Webアプリケーション初期化
        
        Args:
            config_path: 設定ファイルパス
        """
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.weather_client = None
        self.flask_app = None
        
        # Flask アプリケーション設定
        self._setup_flask_app()
        self._register_routes()
        
        # 天気APIクライアント初期化
        self._initialize_weather_client()
    
    def _setup_flask_app(self) -> None:
        """Flask アプリケーションの設定"""
        self.flask_app = Flask(
            __name__,
            template_folder=str(project_root / "templates"),
            static_folder=str(project_root / "static")
        )
        
        # セッション設定
        self.flask_app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'weather-app-secret-key-change-in-production')
        
        # 設定読み込み
        try:
            from src.utils import load_config
            config = load_config(self.config_path)
            web_config = config.get('web', {})
            
            self.flask_app.config.update({
                'DEBUG': web_config.get('debug', True),
                'HOST': web_config.get('host', '0.0.0.0'),
                'PORT': web_config.get('port', 5000)
            })
        except Exception as e:
            self.logger.warning(f"設定ファイル読み込みエラー、デフォルト設定を使用: {e}")
            self.flask_app.config.update({
                'DEBUG': True,
                'HOST': '0.0.0.0',
                'PORT': 5000
            })
    
    def _initialize_weather_client(self) -> None:
        """天気APIクライアントの初期化"""
        try:
            self.weather_client = create_weather_client(self.config_path)
            self.logger.info("天気APIクライアント初期化成功")
        except Exception as e:
            self.logger.error(f"天気APIクライアント初期化失敗: {e}")
            self.weather_client = None
    
    def _register_routes(self) -> None:
        """ルート登録"""
        
        @self.flask_app.route('/')
        def index():
            """ホームページ（天気検索ページ）"""
            return render_template('weather.html')
        
        @self.flask_app.route('/weather', methods=['GET', 'POST'])
        def weather():
            """天気情報取得・表示"""
            if request.method == 'GET':
                return render_template('weather.html')
            
            # POSTリクエスト処理
            city_name = request.form.get('city', '').strip()
            
            if not city_name:
                flash('都市名を入力してください', 'error')
                return render_template('weather.html')
            
            try:
                # APIクライアント状態確認
                if not self.weather_client:
                    flash('天気APIクライアントが初期化されていません。設定を確認してください。', 'error')
                    return render_template('weather.html')
                
                # 天気情報取得
                self.logger.info(f"天気情報取得開始: {city_name}")
                weather_data = self.weather_client.get_current_weather(city_name)
                
                self.logger.info(f"天気情報取得成功: {city_name}")
                return render_template('weather.html', weather_data=weather_data)
                
            except CityNotFoundError as e:
                error_msg = f"都市 '{e.city_name}' が見つかりません。英語での都市名入力を試してください。"
                flash(error_msg, 'error')
                self.logger.warning(f"都市が見つからない: {e.city_name}")
                
            except APIKeyError as e:
                error_msg = "APIキーが無効です。設定を確認してください。"
                flash(error_msg, 'error')
                self.logger.error(f"APIキーエラー: {e}")
                
            except APIConnectionError as e:
                error_msg = "天気情報サーバーに接続できません。インターネット接続を確認してください。"
                flash(error_msg, 'error')
                self.logger.error(f"接続エラー: {e}")
                
            except APIResponseError as e:
                if e.status_code == 429:
                    error_msg = "API使用制限に達しています。しばらく時間をおいて再試行してください。"
                else:
                    error_msg = f"天気情報の取得に失敗しました（エラーコード: {e.status_code}）"
                flash(error_msg, 'error')
                self.logger.error(f"API応答エラー: {e}")
                
            except WeatherAPIError as e:
                error_msg = f"天気情報の取得でエラーが発生しました: {e}"
                flash(error_msg, 'error')
                self.logger.error(f"天気APIエラー: {e}")
                
            except Exception as e:
                error_msg = "予期しないエラーが発生しました。しばらく時間をおいて再試行してください。"
                flash(error_msg, 'error')
                self.logger.exception(f"予期しないエラー: {e}")
            
            return render_template('weather.html')
        
        @self.flask_app.route('/api/weather/<city_name>')
        def api_weather(city_name: str):
            """天気情報API（JSON形式）"""
            try:
                if not self.weather_client:
                    return jsonify({
                        'error': 'APIクライアントが初期化されていません',
                        'status': 'error'
                    }), 500
                
                weather_data = self.weather_client.get_current_weather(city_name)
                
                return jsonify({
                    'status': 'success',
                    'data': weather_data.to_dict()
                })
                
            except CityNotFoundError as e:
                return jsonify({
                    'error': f"都市 '{e.city_name}' が見つかりません",
                    'status': 'error',
                    'error_type': 'city_not_found'
                }), 404
                
            except APIKeyError as e:
                return jsonify({
                    'error': 'APIキーが無効です',
                    'status': 'error',
                    'error_type': 'api_key_error'
                }), 401
                
            except APIConnectionError as e:
                return jsonify({
                    'error': '天気情報サーバーに接続できません',
                    'status': 'error',
                    'error_type': 'connection_error'
                }), 503
                
            except APIResponseError as e:
                return jsonify({
                    'error': f'API応答エラー: {e}',
                    'status': 'error',
                    'error_type': 'api_response_error',
                    'status_code': e.status_code
                }), 502
                
            except Exception as e:
                self.logger.exception(f"API endpoint error: {e}")
                return jsonify({
                    'error': '予期しないエラーが発生しました',
                    'status': 'error',
                    'error_type': 'unexpected_error'
                }), 500
        
        @self.flask_app.route('/api-test')
        def api_test():
            """API テストページ"""
            return render_template('api_test.html')
        
        @self.flask_app.route('/health')
        def health_check():
            """ヘルスチェックエンドポイント"""
            try:
                # APIクライアント状態確認
                client_status = "OK" if self.weather_client else "ERROR"
                
                # APIキー検証（軽量テスト）
                api_key_status = "OK"
                if self.weather_client:
                    try:
                        # 軽量なAPIキー検証
                        self.weather_client.validate_api_key()
                    except:
                        api_key_status = "ERROR"
                else:
                    api_key_status = "N/A"
                
                return jsonify({
                    'status': 'healthy' if client_status == "OK" and api_key_status == "OK" else 'unhealthy',
                    'timestamp': datetime.now().isoformat(),
                    'components': {
                        'weather_client': client_status,
                        'api_key': api_key_status
                    }
                })
                
            except Exception as e:
                self.logger.exception(f"Health check error: {e}")
                return jsonify({
                    'status': 'unhealthy',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }), 500
        
        @self.flask_app.route('/api/version')
        def version_info():
            """バージョン情報エンドポイント"""
            return jsonify({
                'version': __version__,
                'name': 'Weather Web App',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.flask_app.errorhandler(404)
        def not_found(error):
            """404エラーハンドラー"""
            return render_template('weather.html'), 404
        
        @self.flask_app.errorhandler(500)
        def internal_error(error):
            """500エラーハンドラー"""
            flash('内部エラーが発生しました。管理者に連絡してください。', 'error')
            return render_template('weather.html'), 500
    
    def run(self, debug: Optional[bool] = None, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Webアプリケーション実行
        
        Args:
            debug: デバッグモード
            host: ホストアドレス
            port: ポート番号
        """
        run_debug = debug if debug is not None else self.flask_app.config.get('DEBUG', True)
        run_host = host if host is not None else self.flask_app.config.get('HOST', '0.0.0.0')
        run_port = port if port is not None else self.flask_app.config.get('PORT', 5000)
        
        self.logger.info(f"Weather Web App starting on http://{run_host}:{run_port}")
        self.flask_app.run(debug=run_debug, host=run_host, port=run_port)


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Weather Web App - Flask 天気情報アプリ")
    parser.add_argument('--host', default='0.0.0.0', help='ホストアドレス')
    parser.add_argument('--port', type=int, default=5000, help='ポート番号')
    parser.add_argument('--debug', action='store_true', help='デバッグモード')
    parser.add_argument('--config', default='config.yaml', help='設定ファイルパス')
    parser.add_argument('--verbose', action='store_true', help='詳細ログ')
    
    args = parser.parse_args()
    
    # ログ設定
    log_level = "DEBUG" if args.verbose or args.debug else "INFO"
    setup_logging(log_level)
    
    try:
        # Webアプリケーション作成・実行
        app = WeatherWebApp(args.config)
        app.run(debug=args.debug, host=args.host, port=args.port)
        
    except KeyboardInterrupt:
        print("\nアプリケーションが停止されました")
    except Exception as e:
        logging.getLogger(__name__).exception(f"アプリケーション実行エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()