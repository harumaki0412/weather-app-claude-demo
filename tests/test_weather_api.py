"""
WeatherAPIクラス（weather_api.py）の単体テスト
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.weather_api import WeatherAPI
from src.models import WeatherData
from src.exceptions import (
    CityNotFoundError,
    APIKeyError,
    APIConnectionError,
    APIResponseError
)


class TestWeatherAPIInitialization:
    """WeatherAPI初期化のテスト"""
    
    @pytest.mark.unit
    def test_weather_api_initialization_success(self, test_config_file, mock_env_vars, suppress_logging):
        """正常な初期化テスト"""
        api = WeatherAPI(test_config_file)
        
        assert api.api_key == 'test_api_key_123456789abcdef'
        assert api.base_url == "https://api.openweathermap.org/data/2.5/"
        assert api.timeout == 10
        assert api.units == "metric"
        assert api.default_language == "ja"
    
    @pytest.mark.unit
    def test_weather_api_initialization_missing_config(self, mock_env_vars, suppress_logging):
        """設定ファイルが存在しない場合の初期化テスト"""
        with pytest.raises(FileNotFoundError):
            WeatherAPI("nonexistent_config.yaml")
    
    @pytest.mark.unit
    @patch.dict('os.environ', {}, clear=True)
    def test_weather_api_initialization_missing_api_key(self, test_config_file, suppress_logging):
        """APIキーが設定されていない場合の初期化テスト"""
        with pytest.raises(ValueError) as exc_info:
            WeatherAPI(test_config_file)
        
        assert "環境変数 OPENWEATHER_API_KEY が設定されていません" in str(exc_info.value)


class TestWeatherAPIGetCurrentWeather:
    """get_current_weather メソッドのテスト"""
    
    @pytest.mark.unit
    def test_get_current_weather_success(self, test_config_file, mock_env_vars, 
                                       mock_successful_api_response, sample_api_response, suppress_logging):
        """正常な天気情報取得テスト"""
        api = WeatherAPI(test_config_file)
        weather_data = api.get_current_weather("Tokyo")
        
        # WeatherDataオブジェクトが返されることを確認
        assert isinstance(weather_data, WeatherData)
        assert weather_data.city_name == "Tokyo"
        assert weather_data.country == "JP"
        assert weather_data.temperature == 25.5
        assert weather_data.feels_like == 27.0
        assert weather_data.humidity == 65
        assert weather_data.pressure == 1013
        assert weather_data.description == "晴れ"
        assert weather_data.description_en == "Clear"
        assert weather_data.wind_speed == 3.5
        assert weather_data.wind_direction == 180
        assert weather_data.visibility == 10000
        assert isinstance(weather_data.timestamp, datetime)
    
    @pytest.mark.unit
    def test_get_current_weather_city_not_found(self, test_config_file, mock_env_vars, 
                                               mock_404_api_response, suppress_logging):
        """都市が見つからない場合のテスト"""
        api = WeatherAPI(test_config_file)
        
        with pytest.raises(CityNotFoundError) as exc_info:
            api.get_current_weather("NonexistentCity")
        
        assert exc_info.value.city_name == "NonexistentCity"
        assert "都市 'NonexistentCity' が見つかりません" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_get_current_weather_api_key_error(self, test_config_file, mock_env_vars, 
                                             mock_401_api_response, suppress_logging):
        """APIキーエラーのテスト"""
        api = WeatherAPI(test_config_file)
        
        with pytest.raises(APIKeyError) as exc_info:
            api.get_current_weather("Tokyo")
        
        assert "APIキーが無効です" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_get_current_weather_other_http_error(self, test_config_file, mock_env_vars, 
                                                 mock_requests_get, suppress_logging):
        """その他のHTTPエラーのテスト"""
        # 500 Internal Server Error をモック
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal Server Error"}
        mock_requests_get.return_value = mock_response
        
        api = WeatherAPI(test_config_file)
        
        with pytest.raises(APIResponseError) as exc_info:
            api.get_current_weather("Tokyo")
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    def test_get_current_weather_timeout_error(self, test_config_file, mock_env_vars, 
                                              mock_requests_get, suppress_logging):
        """タイムアウトエラーのテスト"""
        mock_requests_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        api = WeatherAPI(test_config_file)
        
        with pytest.raises(APIConnectionError) as exc_info:
            api.get_current_weather("Tokyo")
        
        assert "APIリクエストがタイムアウトしました" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_get_current_weather_connection_error(self, test_config_file, mock_env_vars, 
                                                 mock_requests_get, suppress_logging):
        """接続エラーのテスト"""
        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        api = WeatherAPI(test_config_file)
        
        with pytest.raises(APIConnectionError) as exc_info:
            api.get_current_weather("Tokyo")
        
        assert "APIサーバーに接続できません" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_get_current_weather_custom_language(self, test_config_file, mock_env_vars, 
                                                mock_successful_api_response, suppress_logging):
        """カスタム言語設定のテスト"""
        api = WeatherAPI(test_config_file)
        weather_data = api.get_current_weather("Tokyo", lang="en")
        
        # WeatherDataオブジェクトが正常に返されることを確認
        assert isinstance(weather_data, WeatherData)
        assert weather_data.city_name == "Tokyo"


class TestWeatherAPIParseWeatherData:
    """_parse_weather_data メソッドのテスト"""
    
    @pytest.mark.unit
    def test_parse_weather_data_success(self, test_config_file, mock_env_vars, 
                                      sample_api_response, suppress_logging):
        """正常なデータ解析テスト"""
        api = WeatherAPI(test_config_file)
        weather_data = api._parse_weather_data(sample_api_response)
        
        assert isinstance(weather_data, WeatherData)
        assert weather_data.city_name == "Tokyo"
        assert weather_data.country == "JP"
        assert weather_data.temperature == 25.5
        assert weather_data.feels_like == 27.0
    
    @pytest.mark.unit
    def test_parse_weather_data_missing_required_field(self, test_config_file, mock_env_vars, suppress_logging):
        """必須フィールドが欠損している場合のテスト"""
        api = WeatherAPI(test_config_file)
        
        # 'name'フィールドが欠損したデータ
        invalid_data = {
            "main": {"temp": 25.0, "feels_like": 26.0, "humidity": 60, "pressure": 1010},
            "weather": [{"description": "test", "main": "Test"}],
            "sys": {"country": "JP"}
            # "name" フィールドが欠損
        }
        
        with pytest.raises(APIResponseError) as exc_info:
            api._parse_weather_data(invalid_data)
        
        assert "API応答データが不完全です" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_parse_weather_data_optional_fields_missing(self, test_config_file, mock_env_vars, suppress_logging):
        """オプショナルフィールドが欠損している場合のテスト"""
        api = WeatherAPI(test_config_file)
        
        # 最小限の必須フィールドのみを含むデータ
        minimal_data = {
            "name": "TestCity",
            "sys": {"country": "TC"},
            "main": {
                "temp": 20.0,
                "feels_like": 21.0,
                "humidity": 50,
                "pressure": 1000
            },
            "weather": [{"description": "test weather", "main": "Test"}]
            # wind, visibility は欠損
        }
        
        weather_data = api._parse_weather_data(minimal_data)
        
        assert weather_data.city_name == "TestCity"
        assert weather_data.country == "TC"
        assert weather_data.wind_speed is None
        assert weather_data.wind_direction is None
        assert weather_data.visibility is None


class TestWeatherAPIValidateApiKey:
    """validate_api_key メソッドのテスト"""
    
    @pytest.mark.unit
    @patch.object(WeatherAPI, 'get_current_weather')
    def test_validate_api_key_success(self, mock_get_weather, test_config_file, mock_env_vars, suppress_logging):
        """APIキー検証成功のテスト"""
        # get_current_weather が正常に動作する場合
        mock_get_weather.return_value = Mock(spec=WeatherData)
        
        api = WeatherAPI(test_config_file)
        result = api.validate_api_key()
        
        assert result is True
        mock_get_weather.assert_called_once_with("London")
    
    @pytest.mark.unit
    @patch.object(WeatherAPI, 'get_current_weather')
    def test_validate_api_key_invalid_key(self, mock_get_weather, test_config_file, mock_env_vars, suppress_logging):
        """APIキー検証失敗のテスト"""
        # get_current_weather がAPIKeyErrorを発生させる場合
        mock_get_weather.side_effect = APIKeyError("Invalid API key")
        
        api = WeatherAPI(test_config_file)
        result = api.validate_api_key()
        
        assert result is False
        mock_get_weather.assert_called_once_with("London")
    
    @pytest.mark.unit
    @patch.object(WeatherAPI, 'get_current_weather')
    def test_validate_api_key_other_exception(self, mock_get_weather, test_config_file, mock_env_vars, suppress_logging):
        """その他の例外の場合のテスト"""
        # get_current_weather が他の例外を発生させる場合（キーは有効と判断）
        mock_get_weather.side_effect = APIConnectionError("Network error")
        
        api = WeatherAPI(test_config_file)
        result = api.validate_api_key()
        
        assert result is True  # APIキー以外のエラーは有効と判断
        mock_get_weather.assert_called_once_with("London")


class TestWeatherAPIRequestParameters:
    """APIリクエストパラメータのテスト"""
    
    @pytest.mark.unit
    def test_request_parameters_construction(self, test_config_file, mock_env_vars, 
                                           mock_requests_get, suppress_logging):
        """リクエストパラメータが正しく構築されることを確認"""
        api = WeatherAPI(test_config_file)
        
        # モックレスポンスを設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Tokyo", "sys": {"country": "JP"},
            "main": {"temp": 25, "feels_like": 26, "humidity": 60, "pressure": 1010},
            "weather": [{"description": "clear", "main": "Clear"}]
        }
        mock_requests_get.return_value = mock_response
        
        # API呼び出し
        api.get_current_weather("Tokyo", lang="en")
        
        # requests.getが正しいパラメータで呼び出されたかを確認
        mock_requests_get.assert_called_once()
        args, kwargs = mock_requests_get.call_args
        
        # URL確認
        expected_url = "https://api.openweathermap.org/data/2.5/weather"
        assert args[0] == expected_url
        
        # パラメータ確認
        params = kwargs['params']
        assert params['q'] == 'Tokyo'
        assert params['appid'] == 'test_api_key_123456789abcdef'
        assert params['units'] == 'metric'
        assert params['lang'] == 'en'
        
        # タイムアウト確認
        assert kwargs['timeout'] == 10


class TestWeatherAPIEdgeCases:
    """エッジケースのテスト"""
    
    @pytest.mark.unit
    def test_empty_city_name(self, test_config_file, mock_env_vars, 
                           mock_requests_get, suppress_logging):
        """空の都市名でのテスト"""
        api = WeatherAPI(test_config_file)
        
        # 空文字列でもAPIリクエストは送信される
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response
        
        with pytest.raises(CityNotFoundError) as exc_info:
            api.get_current_weather("")
        
        assert exc_info.value.city_name == ""
    
    @pytest.mark.unit
    def test_special_characters_in_city_name(self, test_config_file, mock_env_vars, 
                                           mock_successful_api_response, suppress_logging):
        """特殊文字を含む都市名のテスト"""
        api = WeatherAPI(test_config_file)
        
        special_city_names = [
            "São Paulo",
            "Москва",  # Moscow in Cyrillic
            "東京",      # Tokyo in Japanese
            "New York",  # Space in name
            "Zürich"     # Umlaut
        ]
        
        for city_name in special_city_names:
            try:
                # 例外が発生しないことを確認（モックなので実際のレスポンスは同じ）
                weather_data = api.get_current_weather(city_name)
                assert isinstance(weather_data, WeatherData)
            except Exception as e:
                pytest.fail(f"Unexpected exception for city '{city_name}': {e}")
    
    @pytest.mark.unit
    def test_very_long_city_name(self, test_config_file, mock_env_vars, 
                                mock_successful_api_response, suppress_logging):
        """非常に長い都市名のテスト"""
        api = WeatherAPI(test_config_file)
        
        # 200文字の都市名
        long_city_name = "A" * 200
        
        # 例外が発生しないことを確認
        weather_data = api.get_current_weather(long_city_name)
        assert isinstance(weather_data, WeatherData)