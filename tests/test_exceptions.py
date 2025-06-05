"""
例外クラス（exceptions.py）の単体テスト
"""

import pytest

from src.exceptions import (
    WeatherAPIError,
    CityNotFoundError,
    APIKeyError,
    APIConnectionError,
    APIResponseError
)


class TestWeatherAPIError:
    """WeatherAPIError基底クラスのテスト"""
    
    @pytest.mark.unit
    def test_base_exception_creation(self):
        """基底例外クラスの作成テスト"""
        error = WeatherAPIError("基底エラーメッセージ")
        assert str(error) == "基底エラーメッセージ"
        assert isinstance(error, Exception)
    
    @pytest.mark.unit
    def test_base_exception_without_message(self):
        """メッセージなしの基底例外作成テスト"""
        error = WeatherAPIError()
        assert str(error) == ""


class TestCityNotFoundError:
    """CityNotFoundError例外のテスト"""
    
    @pytest.mark.unit
    def test_city_not_found_error_creation(self):
        """CityNotFoundError作成テスト"""
        city_name = "UnknownCity"
        error = CityNotFoundError(city_name)
        
        assert str(error) == f"都市 '{city_name}' が見つかりません"
        assert error.city_name == city_name
        assert isinstance(error, WeatherAPIError)
        assert isinstance(error, Exception)
    
    @pytest.mark.unit
    def test_city_not_found_error_inheritance(self):
        """継承関係のテスト"""
        error = CityNotFoundError("TestCity")
        assert isinstance(error, WeatherAPIError)
        assert isinstance(error, Exception)
    
    @pytest.mark.unit
    def test_city_not_found_error_with_special_characters(self):
        """特殊文字を含む都市名のテスト"""
        city_name = "São Paulo"
        error = CityNotFoundError(city_name)
        assert error.city_name == city_name
        assert city_name in str(error)
    
    @pytest.mark.unit
    def test_city_not_found_error_with_empty_string(self):
        """空文字の都市名テスト"""
        city_name = ""
        error = CityNotFoundError(city_name)
        assert error.city_name == ""
        assert "都市 '' が見つかりません" == str(error)


class TestAPIKeyError:
    """APIKeyError例外のテスト"""
    
    @pytest.mark.unit
    def test_api_key_error_with_default_message(self):
        """デフォルトメッセージでの作成テスト"""
        error = APIKeyError()
        assert str(error) == "APIキーが無効または未設定です"
        assert isinstance(error, WeatherAPIError)
    
    @pytest.mark.unit
    def test_api_key_error_with_custom_message(self):
        """カスタムメッセージでの作成テスト"""
        custom_message = "カスタムAPIキーエラー"
        error = APIKeyError(custom_message)
        assert str(error) == custom_message
        assert isinstance(error, WeatherAPIError)
    
    @pytest.mark.unit
    def test_api_key_error_inheritance(self):
        """継承関係のテスト"""
        error = APIKeyError()
        assert isinstance(error, WeatherAPIError)
        assert isinstance(error, Exception)


class TestAPIConnectionError:
    """APIConnectionError例外のテスト"""
    
    @pytest.mark.unit
    def test_api_connection_error_with_default_message(self):
        """デフォルトメッセージでの作成テスト"""
        error = APIConnectionError()
        assert str(error) == "APIサーバーに接続できません"
        assert isinstance(error, WeatherAPIError)
    
    @pytest.mark.unit
    def test_api_connection_error_with_custom_message(self):
        """カスタムメッセージでの作成テスト"""
        custom_message = "ネットワークタイムアウトが発生しました"
        error = APIConnectionError(custom_message)
        assert str(error) == custom_message
        assert isinstance(error, WeatherAPIError)
    
    @pytest.mark.unit
    def test_api_connection_error_inheritance(self):
        """継承関係のテスト"""
        error = APIConnectionError()
        assert isinstance(error, WeatherAPIError)
        assert isinstance(error, Exception)


class TestAPIResponseError:
    """APIResponseError例外のテスト"""
    
    @pytest.mark.unit
    def test_api_response_error_with_status_code_only(self):
        """ステータスコードのみでの作成テスト"""
        status_code = 500
        error = APIResponseError(status_code)
        
        assert error.status_code == status_code
        assert str(error) == f"APIエラー (ステータスコード: {status_code})"
        assert isinstance(error, WeatherAPIError)
    
    @pytest.mark.unit
    def test_api_response_error_with_custom_message(self):
        """カスタムメッセージ付きでの作成テスト"""
        status_code = 429
        custom_message = "API使用制限に達しました"
        error = APIResponseError(status_code, custom_message)
        
        assert error.status_code == status_code
        assert str(error) == custom_message
        assert isinstance(error, WeatherAPIError)
    
    @pytest.mark.unit
    def test_api_response_error_inheritance(self):
        """継承関係のテスト"""
        error = APIResponseError(500)
        assert isinstance(error, WeatherAPIError)
        assert isinstance(error, Exception)
    
    @pytest.mark.unit
    def test_api_response_error_common_status_codes(self):
        """一般的なHTTPステータスコードのテスト"""
        test_cases = [
            (400, "Bad Request"),
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not Found"),
            (429, "Too Many Requests"),
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable")
        ]
        
        for status_code, description in test_cases:
            error = APIResponseError(status_code, description)
            assert error.status_code == status_code
            assert str(error) == description


class TestExceptionHierarchy:
    """例外階層全体のテスト"""
    
    @pytest.mark.unit
    def test_all_exceptions_inherit_from_weather_api_error(self):
        """すべての例外がWeatherAPIErrorを継承していることを確認"""
        exceptions_to_test = [
            CityNotFoundError("test"),
            APIKeyError(),
            APIConnectionError(),
            APIResponseError(500)
        ]
        
        for exception in exceptions_to_test:
            assert isinstance(exception, WeatherAPIError)
            assert isinstance(exception, Exception)
    
    @pytest.mark.unit
    def test_exception_catching_hierarchy(self):
        """例外キャッチの階層テスト"""
        # 具体的な例外をWeatherAPIErrorでキャッチできることを確認
        
        # CityNotFoundError
        try:
            raise CityNotFoundError("TestCity")
        except WeatherAPIError as e:
            assert isinstance(e, CityNotFoundError)
            assert isinstance(e, WeatherAPIError)
        
        # APIKeyError
        try:
            raise APIKeyError("Test API key error")
        except WeatherAPIError as e:
            assert isinstance(e, APIKeyError)
            assert isinstance(e, WeatherAPIError)
        
        # APIConnectionError
        try:
            raise APIConnectionError("Test connection error")
        except WeatherAPIError as e:
            assert isinstance(e, APIConnectionError)
            assert isinstance(e, WeatherAPIError)
        
        # APIResponseError
        try:
            raise APIResponseError(500, "Test response error")
        except WeatherAPIError as e:
            assert isinstance(e, APIResponseError)
            assert isinstance(e, WeatherAPIError)
    
    @pytest.mark.unit
    def test_specific_exception_catching(self):
        """特定の例外を直接キャッチできることを確認"""
        
        # CityNotFoundError直接キャッチ
        try:
            raise CityNotFoundError("TestCity")
        except CityNotFoundError as e:
            assert e.city_name == "TestCity"
        
        # APIResponseError直接キャッチ
        try:
            raise APIResponseError(404, "Not found")
        except APIResponseError as e:
            assert e.status_code == 404
            assert str(e) == "Not found"