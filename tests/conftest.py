"""
pytest設定ファイル
テスト用の共通フィクスチャとユーティリティを提供
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models import WeatherData
from src.exceptions import *


@pytest.fixture(scope="session")
def project_root_path():
    """プロジェクトルートパスを提供"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_config_dir(project_root_path):
    """テスト用設定ディレクトリを作成"""
    test_dir = project_root_path / "tests" / "fixtures"
    test_dir.mkdir(exist_ok=True)
    return test_dir


@pytest.fixture
def sample_weather_data():
    """サンプル天気データを提供"""
    return WeatherData(
        city_name="Tokyo",
        country="JP",
        temperature=25.5,
        feels_like=27.0,
        humidity=65,
        pressure=1013,
        description="晴れ",
        description_en="Clear",
        wind_speed=3.5,
        wind_direction=180,
        visibility=10000,
        timestamp=datetime(2025, 6, 5, 12, 0, 0)
    )


@pytest.fixture
def sample_api_response():
    """OpenWeatherMap APIのサンプルレスポンス"""
    return {
        "coord": {"lon": 139.6917, "lat": 35.6895},
        "weather": [
            {
                "id": 800,
                "main": "Clear",
                "description": "晴れ",
                "icon": "01d"
            }
        ],
        "base": "stations",
        "main": {
            "temp": 25.5,
            "feels_like": 27.0,
            "temp_min": 24.0,
            "temp_max": 27.0,
            "pressure": 1013,
            "humidity": 65
        },
        "visibility": 10000,
        "wind": {
            "speed": 3.5,
            "deg": 180
        },
        "clouds": {"all": 0},
        "dt": 1749095343,
        "sys": {
            "type": 2,
            "id": 268395,
            "country": "JP",
            "sunrise": 1749065152,
            "sunset": 1749117228
        },
        "timezone": 32400,
        "id": 1850144,
        "name": "Tokyo",
        "cod": 200
    }


@pytest.fixture
def mock_api_response_404():
    """404エラーのAPIレスポンス"""
    return {
        "cod": "404",
        "message": "city not found"
    }


@pytest.fixture
def test_config_file(test_config_dir):
    """テスト用設定ファイルを作成"""
    config_content = """
api:
  base_url: "https://api.openweathermap.org/data/2.5/"
  timeout: 10
  units: "metric"

defaults:
  city: "Tokyo"
  language: "ja"

web:
  host: "127.0.0.1"
  port: 5000
  debug: true

logging:
  level: "ERROR"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
"""
    config_file = test_config_dir / "test_config.yaml"
    config_file.write_text(config_content.strip())
    return str(config_file)


@pytest.fixture
def mock_env_vars():
    """テスト用環境変数を設定"""
    with patch.dict(os.environ, {
        'OPENWEATHER_API_KEY': 'test_api_key_123456789abcdef',
        'FLASK_ENV': 'testing',
        'FLASK_DEBUG': 'False'
    }):
        yield


@pytest.fixture
def mock_requests_get():
    """requests.getをモック化"""
    with patch('requests.get') as mock_get:
        yield mock_get


@pytest.fixture
def mock_successful_api_response(mock_requests_get, sample_api_response):
    """成功するAPI呼び出しをモック化"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_api_response
    mock_requests_get.return_value = mock_response
    return mock_response


@pytest.fixture
def mock_404_api_response(mock_requests_get, mock_api_response_404):
    """404エラーのAPI呼び出しをモック化"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = mock_api_response_404
    mock_requests_get.return_value = mock_response
    return mock_response


@pytest.fixture
def mock_401_api_response(mock_requests_get):
    """401エラー（APIキーエラー）をモック化"""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "cod": 401,
        "message": "Invalid API key"
    }
    mock_requests_get.return_value = mock_response
    return mock_response


@pytest.fixture
def temp_env_file():
    """一時的な.envファイルを作成"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("OPENWEATHER_API_KEY=test_key_12345\n")
        f.write("FLASK_DEBUG=True\n")
        temp_file = f.name
    
    yield temp_file
    
    # クリーンアップ
    os.unlink(temp_file)


@pytest.fixture
def suppress_logging():
    """テスト中のログ出力を抑制"""
    import logging
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


# カスタムアサーション関数
def assert_weather_data_equal(actual: WeatherData, expected: WeatherData):
    """WeatherDataオブジェクトの比較"""
    assert actual.city_name == expected.city_name
    assert actual.country == expected.country
    assert actual.temperature == expected.temperature
    assert actual.feels_like == expected.feels_like
    assert actual.humidity == expected.humidity
    assert actual.pressure == expected.pressure
    assert actual.description == expected.description
    assert actual.description_en == expected.description_en


# テストユーティリティ関数
def create_mock_weather_api():
    """モック化されたWeatherAPIインスタンスを作成"""
    from src.weather_api import WeatherAPI
    mock_api = Mock(spec=WeatherAPI)
    return mock_api


def create_test_flask_app():
    """テスト用Flaskアプリケーションを作成"""
    from src.weather_web import WeatherWebApp
    app = WeatherWebApp()
    app.flask_app.config['TESTING'] = True
    app.flask_app.config['WTF_CSRF_ENABLED'] = False
    return app