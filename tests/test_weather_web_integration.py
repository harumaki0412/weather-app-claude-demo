"""
Web版アプリケーション（weather_web.py）の統合テスト
"""

import pytest
import json
from unittest.mock import Mock, patch
from flask import url_for

from src.weather_web import WeatherWebApp
from src.models import WeatherData
from src.exceptions import CityNotFoundError, APIKeyError, APIConnectionError, APIResponseError


class TestWeatherWebAppInitialization:
    """WeatherWebApp初期化の統合テスト"""
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_web_app_initialization_success(self, test_config_file, mock_env_vars, suppress_logging):
        """正常な初期化テスト"""
        app = WeatherWebApp(test_config_file)
        
        assert app.config_path == test_config_file
        assert app.flask_app is not None
        assert app.weather_client is not None
        assert app.flask_app.config['TESTING'] is False  # デフォルトではTesting=False
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_web_app_flask_configuration(self, test_config_file, mock_env_vars, suppress_logging):
        """Flask設定の確認テスト"""
        app = WeatherWebApp(test_config_file)
        
        # テスト用設定ファイルの内容が反映されていることを確認
        assert app.flask_app.config['DEBUG'] is True
        assert app.flask_app.config['HOST'] == '127.0.0.1'
        assert app.flask_app.config['PORT'] == 5000
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_web_app_routes_registration(self, test_config_file, mock_env_vars, suppress_logging):
        """ルートが正しく登録されていることのテスト"""
        app = WeatherWebApp(test_config_file)
        
        # 登録されたルートを確認
        routes = [rule.rule for rule in app.flask_app.url_map.iter_rules()]
        
        expected_routes = [
            '/',
            '/weather',
            '/api/weather/<city_name>',
            '/api-test',
            '/health',
            '/static/<path:filename>'
        ]
        
        for expected_route in expected_routes:
            assert any(expected_route in route for route in routes), f"Route {expected_route} not found"


class TestWeatherWebAppRoutes:
    """Webアプリケーションルートの統合テスト"""
    
    @pytest.fixture
    def client(self, test_config_file, mock_env_vars, suppress_logging):
        """テストクライアントを作成"""
        app = WeatherWebApp(test_config_file)
        app.flask_app.config['TESTING'] = True
        app.flask_app.config['WTF_CSRF_ENABLED'] = False
        return app.flask_app.test_client()
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_index_route(self, client):
        """ホームページルート（/）のテスト"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'weather.html' in response.data or b'\xe5\xa4\xa9\xe6\xb0\x97' in response.data  # '天気' in UTF-8
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_weather_route_get(self, client):
        """天気ルート（/weather GET）のテスト"""
        response = client.get('/weather')
        
        assert response.status_code == 200
        # weather.htmlテンプレートが使用されていることを確認
        assert response.content_type.startswith('text/html')
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_api_test_route(self, client):
        """APIテストルート（/api-test）のテスト"""
        response = client.get('/api-test')
        
        assert response.status_code == 200
        # api_test.htmlテンプレートが使用されていることを確認
        assert response.content_type.startswith('text/html')
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_health_route(self, client):
        """ヘルスチェックルート（/health）のテスト"""
        response = client.get('/health')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data
        assert 'components' in data
        assert 'weather_client' in data['components']
        assert 'api_key' in data['components']
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_404_error_handler(self, client):
        """404エラーハンドラーのテスト"""
        response = client.get('/nonexistent-route')
        
        assert response.status_code == 404
        # カスタム404ページまたはベーステンプレートが使用されることを確認
        assert response.content_type.startswith('text/html')


class TestWeatherWebAppWeatherEndpoint:
    """天気情報エンドポイントの統合テスト"""
    
    @pytest.fixture
    def client_with_mock_weather_client(self, test_config_file, mock_env_vars, suppress_logging):
        """モック化された天気クライアントを持つテストクライアントを作成"""
        app = WeatherWebApp(test_config_file)
        app.flask_app.config['TESTING'] = True
        app.flask_app.config['WTF_CSRF_ENABLED'] = False
        
        # WeatherClientをモック化
        mock_client = Mock()
        app.weather_client = mock_client
        
        return app.flask_app.test_client(), mock_client
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_weather_post_success(self, client_with_mock_weather_client, sample_weather_data):
        """天気検索POST成功のテスト"""
        client, mock_client = client_with_mock_weather_client
        mock_client.get_current_weather.return_value = sample_weather_data
        
        response = client.post('/weather', data={'city': 'Tokyo'})
        
        assert response.status_code == 200
        mock_client.get_current_weather.assert_called_once_with('Tokyo')
        
        # レスポンスにTokyo、気温、天気情報が含まれていることを確認
        response_text = response.data.decode('utf-8')
        assert 'Tokyo' in response_text
        assert '25.5' in response_text
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_weather_post_empty_city(self, client_with_mock_weather_client):
        """空の都市名でのPOSTテスト"""
        client, mock_client = client_with_mock_weather_client
        
        response = client.post('/weather', data={'city': ''})
        
        assert response.status_code == 200
        # get_current_weatherは呼ばれない
        mock_client.get_current_weather.assert_not_called()
        
        # エラーメッセージが含まれていることを確認
        response_text = response.data.decode('utf-8')
        assert 'error' in response_text.lower() or 'エラー' in response_text
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_weather_post_city_not_found(self, client_with_mock_weather_client):
        """都市が見つからない場合のPOSTテスト"""
        client, mock_client = client_with_mock_weather_client
        mock_client.get_current_weather.side_effect = CityNotFoundError('UnknownCity')
        
        response = client.post('/weather', data={'city': 'UnknownCity'})
        
        assert response.status_code == 200
        mock_client.get_current_weather.assert_called_once_with('UnknownCity')
        
        # エラーメッセージが含まれていることを確認
        response_text = response.data.decode('utf-8')
        assert '見つかりません' in response_text or 'not found' in response_text.lower()
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_weather_post_api_key_error(self, client_with_mock_weather_client):
        """APIキーエラーの場合のPOSTテスト"""
        client, mock_client = client_with_mock_weather_client
        mock_client.get_current_weather.side_effect = APIKeyError('Invalid API key')
        
        response = client.post('/weather', data={'city': 'Tokyo'})
        
        assert response.status_code == 200
        
        # APIキーエラーメッセージが含まれていることを確認
        response_text = response.data.decode('utf-8')
        assert 'APIキー' in response_text or 'api key' in response_text.lower()
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_weather_post_connection_error(self, client_with_mock_weather_client):
        """接続エラーの場合のPOSTテスト"""
        client, mock_client = client_with_mock_weather_client
        mock_client.get_current_weather.side_effect = APIConnectionError('Connection failed')
        
        response = client.post('/weather', data={'city': 'Tokyo'})
        
        assert response.status_code == 200
        
        # 接続エラーメッセージが含まれていることを確認
        response_text = response.data.decode('utf-8')
        assert '接続' in response_text or 'connection' in response_text.lower()


class TestWeatherWebAppAPIEndpoint:
    """JSON APIエンドポイントの統合テスト"""
    
    @pytest.fixture
    def client_with_mock_weather_client(self, test_config_file, mock_env_vars, suppress_logging):
        """モック化された天気クライアントを持つテストクライアントを作成"""
        app = WeatherWebApp(test_config_file)
        app.flask_app.config['TESTING'] = True
        
        # WeatherClientをモック化
        mock_client = Mock()
        app.weather_client = mock_client
        
        return app.flask_app.test_client(), mock_client
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_api_weather_success(self, client_with_mock_weather_client, sample_weather_data):
        """API天気情報取得成功のテスト"""
        client, mock_client = client_with_mock_weather_client
        mock_client.get_current_weather.return_value = sample_weather_data
        
        response = client.get('/api/weather/Tokyo')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        mock_client.get_current_weather.assert_called_once_with('Tokyo')
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert data['data']['city_name'] == 'Tokyo'
        assert data['data']['temperature'] == 25.5
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_api_weather_city_not_found(self, client_with_mock_weather_client):
        """API都市が見つからない場合のテスト"""
        client, mock_client = client_with_mock_weather_client
        mock_client.get_current_weather.side_effect = CityNotFoundError('UnknownCity')
        
        response = client.get('/api/weather/UnknownCity')
        
        assert response.status_code == 404
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['error_type'] == 'city_not_found'
        assert 'UnknownCity' in data['error']
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_api_weather_api_key_error(self, client_with_mock_weather_client):
        """APIキーエラーの場合のAPIテスト"""
        client, mock_client = client_with_mock_weather_client
        mock_client.get_current_weather.side_effect = APIKeyError('Invalid API key')
        
        response = client.get('/api/weather/Tokyo')
        
        assert response.status_code == 401
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['error_type'] == 'api_key_error'
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_api_weather_connection_error(self, client_with_mock_weather_client):
        """接続エラーの場合のAPIテスト"""
        client, mock_client = client_with_mock_weather_client
        mock_client.get_current_weather.side_effect = APIConnectionError('Connection failed')
        
        response = client.get('/api/weather/Tokyo')
        
        assert response.status_code == 503
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['error_type'] == 'connection_error'
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_api_weather_response_error(self, client_with_mock_weather_client):
        """API応答エラーの場合のテスト"""
        client, mock_client = client_with_mock_weather_client
        mock_client.get_current_weather.side_effect = APIResponseError(429, 'Too Many Requests')
        
        response = client.get('/api/weather/Tokyo')
        
        assert response.status_code == 502
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['error_type'] == 'api_response_error'
        assert data['status_code'] == 429
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_api_weather_special_characters_in_city(self, client_with_mock_weather_client, sample_weather_data):
        """特殊文字を含む都市名でのAPIテスト"""
        client, mock_client = client_with_mock_weather_client
        
        # São Paulo（URL エンコード: S%C3%A3o%20Paulo）
        sample_weather_data.city_name = "São Paulo"
        mock_client.get_current_weather.return_value = sample_weather_data
        
        response = client.get('/api/weather/S%C3%A3o%20Paulo')
        
        assert response.status_code == 200
        mock_client.get_current_weather.assert_called_once_with('São Paulo')
        
        data = json.loads(response.data)
        assert data['data']['city_name'] == 'São Paulo'


class TestWeatherWebAppHealthEndpoint:
    """ヘルスチェックエンドポイントの統合テスト"""
    
    @pytest.fixture
    def client_with_health_scenarios(self, test_config_file, mock_env_vars, suppress_logging):
        """ヘルスチェック用のテストクライアントを作成"""
        app = WeatherWebApp(test_config_file)
        app.flask_app.config['TESTING'] = True
        return app.flask_app.test_client(), app
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_health_check_healthy(self, client_with_health_scenarios):
        """正常なヘルスチェックテスト"""
        client, app = client_with_health_scenarios
        
        # 正常なWeatherClientをモック
        mock_client = Mock()
        mock_client.validate_api_key.return_value = True
        app.weather_client = mock_client
        
        response = client.get('/health')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['components']['weather_client'] == 'OK'
        assert data['components']['api_key'] == 'OK'
        assert 'timestamp' in data
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_health_check_unhealthy_no_client(self, client_with_health_scenarios):
        """クライアントが初期化されていない場合のヘルスチェック"""
        client, app = client_with_health_scenarios
        
        # WeatherClientをNoneに設定
        app.weather_client = None
        
        response = client.get('/health')
        
        assert response.status_code == 200  # ヘルスチェック自体は200で応答
        
        data = json.loads(response.data)
        assert data['status'] == 'unhealthy'
        assert data['components']['weather_client'] == 'ERROR'
        assert data['components']['api_key'] == 'N/A'
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_health_check_invalid_api_key(self, client_with_health_scenarios):
        """無効なAPIキーの場合のヘルスチェック"""
        client, app = client_with_health_scenarios
        
        # APIキー検証が失敗するWeatherClientをモック
        mock_client = Mock()
        mock_client.validate_api_key.side_effect = Exception("API key validation failed")
        app.weather_client = mock_client
        
        response = client.get('/health')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'unhealthy'
        assert data['components']['weather_client'] == 'OK'
        assert data['components']['api_key'] == 'ERROR'


class TestWeatherWebAppErrorHandling:
    """エラーハンドリングの統合テスト"""
    
    @pytest.fixture
    def client_with_error_scenarios(self, test_config_file, mock_env_vars, suppress_logging):
        """エラーシナリオ用のテストクライアントを作成"""
        app = WeatherWebApp(test_config_file)
        app.flask_app.config['TESTING'] = True
        app.flask_app.config['WTF_CSRF_ENABLED'] = False
        
        # WeatherClientが初期化されていない状況をシミュレート
        app.weather_client = None
        
        return app.flask_app.test_client()
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_weather_endpoint_no_client_initialization(self, client_with_error_scenarios):
        """WeatherClientが初期化されていない場合のテスト"""
        response = client_with_error_scenarios.post('/weather', data={'city': 'Tokyo'})
        
        assert response.status_code == 200
        
        # エラーメッセージが含まれていることを確認
        response_text = response.data.decode('utf-8')
        assert 'error' in response_text.lower() or 'エラー' in response_text
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_api_endpoint_no_client_initialization(self, client_with_error_scenarios):
        """API版でWeatherClientが初期化されていない場合のテスト"""
        response = client_with_error_scenarios.get('/api/weather/Tokyo')
        
        assert response.status_code == 500
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'APIクライアントが初期化されていません' in data['error']
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_500_error_handler(self, test_config_file, mock_env_vars, suppress_logging):
        """500エラーハンドラーのテスト"""
        app = WeatherWebApp(test_config_file)
        app.flask_app.config['TESTING'] = True
        
        # 意図的に500エラーを発生させるルートを追加
        @app.flask_app.route('/test-500-error')
        def test_500():
            raise Exception("Test 500 error")
        
        client = app.flask_app.test_client()
        response = client.get('/test-500-error')
        
        assert response.status_code == 500
        assert response.content_type.startswith('text/html')


class TestWeatherWebAppSecurity:
    """セキュリティ関連の統合テスト"""
    
    @pytest.fixture
    def client(self, test_config_file, mock_env_vars, suppress_logging):
        """テストクライアントを作成"""
        app = WeatherWebApp(test_config_file)
        app.flask_app.config['TESTING'] = True
        return app.flask_app.test_client()
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_xss_prevention_in_city_input(self, client):
        """XSS攻撃防止のテスト"""
        # XSSペイロードを含む都市名
        malicious_city = "<script>alert('XSS')</script>"
        
        response = client.post('/weather', data={'city': malicious_city})
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        
        # スクリプトタグがエスケープされているか、そのまま実行されないことを確認
        assert '<script>' not in response_text or '&lt;script&gt;' in response_text
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_sql_injection_prevention(self, client):
        """SQL インジェクション防止のテスト（該当しないが念のため）"""
        # SQL インジェクションペイロード
        malicious_city = "'; DROP TABLE users; --"
        
        response = client.post('/weather', data={'city': malicious_city})
        
        # アプリケーションがクラッシュせず、正常にレスポンスを返すことを確認
        assert response.status_code == 200
    
    @pytest.mark.integration
    @pytest.mark.web
    def test_very_long_input_handling(self, client):
        """非常に長い入力の処理テスト"""
        # 10KB の長い都市名
        very_long_city = "A" * 10240
        
        response = client.post('/weather', data={'city': very_long_city})
        
        # アプリケーションがクラッシュせず、適切に処理することを確認
        assert response.status_code == 200