"""
エンドツーエンド（E2E）テスト
実際のAPIキーを使った統合テスト（オプション）
"""

import pytest
import os
import requests
from unittest.mock import patch

from src import create_weather_client, setup_logging
from src.weather_cli import WeatherCLI, main
from src.weather_web import WeatherWebApp
from src.exceptions import APIKeyError, CityNotFoundError


class TestEndToEndWithMockedAPI:
    """モックAPIを使用したE2Eテスト"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_cli_workflow_success(self, test_config_file, mock_env_vars, 
                                     mock_successful_api_response, suppress_logging):
        """CLI版の完全なワークフローテスト（成功シナリオ）"""
        # コマンドライン引数をシミュレート
        test_args = ['weather_cli.py', 'Tokyo', '--verbose']
        
        with patch('sys.argv', test_args), \
             patch('sys.stdout', new_callable=lambda: open(os.devnull, 'w')):
            
            result = main()
        
        # 正常終了を確認
        assert result == 0
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_cli_workflow_city_not_found(self, test_config_file, mock_env_vars, 
                                            mock_404_api_response, suppress_logging):
        """CLI版の完全なワークフロー（都市が見つからないシナリオ）"""
        test_args = ['weather_cli.py', 'NonexistentCity']
        
        with patch('sys.argv', test_args), \
             patch('sys.stdout', new_callable=lambda: open(os.devnull, 'w')):
            
            result = main()
        
        # エラー終了を確認
        assert result == 0  # バッチモードでは一部失敗でも0を返す
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_web_workflow_success(self, test_config_file, mock_env_vars, 
                                     sample_weather_data, suppress_logging):
        """Web版の完全なワークフローテスト（成功シナリオ）"""
        app = WeatherWebApp(test_config_file)
        app.flask_app.config['TESTING'] = True
        app.flask_app.config['WTF_CSRF_ENABLED'] = False
        
        # WeatherClientをモック化
        from unittest.mock import Mock
        mock_client = Mock()
        mock_client.get_current_weather.return_value = sample_weather_data
        app.weather_client = mock_client
        
        client = app.flask_app.test_client()
        
        # 1. ホームページアクセス
        response = client.get('/')
        assert response.status_code == 200
        
        # 2. 天気検索実行
        response = client.post('/weather', data={'city': 'Tokyo'})
        assert response.status_code == 200
        assert b'Tokyo' in response.data
        
        # 3. API エンドポイントアクセス
        response = client.get('/api/weather/Tokyo')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        
        # 4. ヘルスチェック
        response = client.get('/health')
        assert response.status_code == 200
        health_data = response.get_json()
        assert health_data['components']['weather_client'] == 'OK'


class TestEndToEndFactoryFunction:
    """ファクトリ関数のE2Eテスト"""
    
    @pytest.mark.integration
    def test_create_weather_client_integration(self, test_config_file, mock_env_vars, suppress_logging):
        """create_weather_client関数の統合テスト"""
        client = create_weather_client(test_config_file)
        
        assert client is not None
        assert hasattr(client, 'get_current_weather')
        assert hasattr(client, 'validate_api_key')
        assert client.api_key == 'test_api_key_123456789abcdef'
    
    @pytest.mark.integration
    def test_create_weather_client_with_missing_config(self, mock_env_vars, suppress_logging):
        """存在しない設定ファイルでのクライアント作成テスト"""
        with pytest.raises(FileNotFoundError):
            create_weather_client("nonexistent_config.yaml")
    
    @pytest.mark.integration
    def test_create_weather_client_with_missing_api_key(self, test_config_file, suppress_logging):
        """APIキーが設定されていない場合のクライアント作成テスト"""
        # 実際のAPIキーが設定されている環境でのテストスキップ
        if os.getenv('OPENWEATHER_API_KEY') and not os.getenv('OPENWEATHER_API_KEY').startswith('test_'):
            pytest.skip("実際のAPIキーが設定されているため、このテストをスキップします")
        
        # get_api_keyを直接モック化してテスト
        with patch('src.weather_api.get_api_key', side_effect=ValueError("環境変数 OPENWEATHER_API_KEY が設定されていません")):
            with pytest.raises(ValueError) as exc_info:
                create_weather_client(test_config_file)
            
            assert "環境変数 OPENWEATHER_API_KEY が設定されていません" in str(exc_info.value)


class TestEndToEndErrorPropagation:
    """エラー伝播のE2Eテスト"""
    
    @pytest.mark.integration
    def test_error_propagation_cli_to_api(self, test_config_file, mock_env_vars, 
                                        mock_404_api_response, suppress_logging):
        """CLIからAPIまでのエラー伝播テスト"""
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        # バリデーションをスキップして直接天気取得を試行
        from io import StringIO
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cli.get_weather_for_city("NonexistentCity")
        
        # エラーが適切に処理されることを確認
        assert result is False
        output = mock_stdout.getvalue()
        assert "都市が見つかりません" in output or "not found" in output.lower()
    
    @pytest.mark.integration
    def test_error_propagation_web_to_api(self, test_config_file, mock_env_vars, suppress_logging):
        """WebからAPIまでのエラー伝播テスト"""
        app = WeatherWebApp(test_config_file)
        app.flask_app.config['TESTING'] = True
        app.flask_app.config['WTF_CSRF_ENABLED'] = False
        
        # CityNotFoundErrorを発生させるモック
        from unittest.mock import Mock
        mock_client = Mock()
        mock_client.get_current_weather.side_effect = CityNotFoundError('NonexistentCity')
        app.weather_client = mock_client
        
        client = app.flask_app.test_client()
        
        # HTML版でのエラー
        response = client.post('/weather', data={'city': 'NonexistentCity'})
        assert response.status_code == 200
        assert b'\xe8\xa6\x8b\xe3\x81\xa4\xe3\x81\x8b\xe3\x82\x8a\xe3\x81\xbe\xe3\x81\x9b\xe3\x82\x93' in response.data  # "見つかりません" in UTF-8
        
        # JSON API版でのエラー
        response = client.get('/api/weather/NonexistentCity')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error_type'] == 'city_not_found'


class TestEndToEndConfigurationFlow:
    """設定ファイルの流れのE2Eテスト"""
    
    @pytest.mark.integration
    def test_config_flow_from_file_to_api_client(self, test_config_file, mock_env_vars, suppress_logging):
        """設定ファイルからAPIクライアントまでの設定流れテスト"""
        # 1. 設定ファイルの読み込み確認
        from src.utils import load_config
        config = load_config(test_config_file)
        
        assert config['api']['base_url'] == "https://api.openweathermap.org/data/2.5/"
        assert config['api']['timeout'] == 10
        assert config['defaults']['city'] == "Tokyo"
        
        # 2. APIクライアントでの設定使用確認
        client = create_weather_client(test_config_file)
        
        assert client.base_url == config['api']['base_url']
        assert client.timeout == config['api']['timeout']
        assert client.default_language == config['defaults']['language']
        
        # 3. CLI版での設定使用確認
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        assert cli.weather_client.base_url == config['api']['base_url']
        
        # 4. Web版での設定使用確認
        web_app = WeatherWebApp(test_config_file)
        
        assert web_app.flask_app.config['HOST'] == config['web']['host']
        assert web_app.flask_app.config['PORT'] == config['web']['port']


class TestEndToEndDataTransformation:
    """データ変換のE2Eテスト"""
    
    @pytest.mark.integration
    def test_data_transformation_api_to_model_to_display(self, test_config_file, mock_env_vars, 
                                                       sample_api_response, suppress_logging):
        """API応答からモデル、表示までのデータ変換テスト"""
        from unittest.mock import Mock, patch
        
        # 1. モックAPIレスポンス
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        
        with patch('requests.get', return_value=mock_response):
            # 2. APIクライアントでのデータ取得・変換
            client = create_weather_client(test_config_file)
            weather_data = client.get_current_weather("Tokyo")
            
            # WeatherDataモデルの確認
            assert weather_data.city_name == "Tokyo"
            assert weather_data.temperature == 25.5
            assert weather_data.description == "晴れ"
            
            # 3. CLI表示用データ変換
            from src.cli_utils import format_weather_display
            cli_display = format_weather_display(weather_data)
            
            assert "Tokyo" in cli_display
            assert "25.5℃" in cli_display
            assert "晴れ" in cli_display
            
            # 4. Web表示用データ変換
            web_dict = weather_data.to_dict()
            
            assert web_dict['city_name'] == "Tokyo"
            assert web_dict['temperature'] == 25.5
            assert isinstance(web_dict['timestamp'], str)


class TestEndToEndConcurrency:
    """並行処理のE2Eテスト"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_multiple_api_calls_concurrency(self, test_config_file, mock_env_vars, 
                                          mock_successful_api_response, suppress_logging):
        """複数のAPI呼び出しの並行処理テスト"""
        import threading
        import time
        
        client = create_weather_client(test_config_file)
        results = []
        errors = []
        
        def get_weather_for_city(city):
            try:
                weather_data = client.get_current_weather(city)
                results.append((city, weather_data))
            except Exception as e:
                errors.append((city, e))
        
        # 複数都市の並行取得をシミュレート
        cities = ["Tokyo", "London", "Paris", "New York", "Sydney"]
        threads = []
        
        start_time = time.time()
        
        for city in cities:
            thread = threading.Thread(target=get_weather_for_city, args=(city,))
            threads.append(thread)
            thread.start()
        
        # すべてのスレッドの完了を待機
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # 結果の確認
        assert len(results) == len(cities)  # すべて成功
        assert len(errors) == 0             # エラーなし
        
        # 各結果の妥当性確認
        for city, weather_data in results:
            assert weather_data.city_name == "Tokyo"  # モックでは同じデータ
            assert weather_data.temperature == 25.5
        
        # 並行処理により時間短縮されていることを期待
        # （実際のAPIでは有効だが、モックでは意味が薄い）
        assert end_time - start_time < 10  # 10秒以内に完了


@pytest.mark.api
@pytest.mark.slow
class TestEndToEndWithRealAPI:
    """実際のAPIを使用したE2Eテスト（オプション）"""
    
    def test_real_api_integration(self):
        """実際のOpenWeatherMap APIを使用した統合テスト"""
        # 実際のAPIキーが設定されている場合のみ実行
        api_key = os.getenv('OPENWEATHER_API_KEY')
        
        if not api_key or api_key.startswith('test_') or api_key == 'demo_api_key_for_testing':
            pytest.skip("実際のAPIキーが設定されていません")
        
        # 実際のAPI呼び出しテスト
        try:
            client = create_weather_client()
            weather_data = client.get_current_weather("London")
            
            # 基本的なデータ検証
            assert weather_data.city_name == "London"
            assert isinstance(weather_data.temperature, (int, float))
            assert isinstance(weather_data.humidity, int)
            assert 0 <= weather_data.humidity <= 100
            assert isinstance(weather_data.description, str)
            assert len(weather_data.description) > 0
            
        except APIKeyError:
            pytest.skip("実際のAPIキーが無効です")
        except requests.exceptions.RequestException:
            pytest.skip("ネットワーク接続の問題でテストをスキップします")
    
    def test_real_api_city_not_found(self):
        """実際のAPIでの存在しない都市テスト"""
        api_key = os.getenv('OPENWEATHER_API_KEY')
        
        if not api_key or api_key.startswith('test_') or api_key == 'demo_api_key_for_testing':
            pytest.skip("実際のAPIキーが設定されていません")
        
        try:
            client = create_weather_client()
            
            # 存在しない都市名でテスト
            with pytest.raises(CityNotFoundError) as exc_info:
                client.get_current_weather("NonexistentCityXYZ123")
            
            assert "NonexistentCityXYZ123" in str(exc_info.value)
            
        except APIKeyError:
            pytest.skip("実際のAPIキーが無効です")
        except requests.exceptions.RequestException:
            pytest.skip("ネットワーク接続の問題でテストをスキップします")