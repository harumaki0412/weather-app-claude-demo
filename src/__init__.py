"""
Weather App - OpenWeatherMap API連携天気情報取得アプリ
CLI版とWeb版の両方をサポートします。
"""

__version__ = "1.0.0"
__author__ = "Weather App Team"

from .weather_api import WeatherAPI
from .models import WeatherData
from .exceptions import (
    WeatherAPIError,
    CityNotFoundError,
    APIKeyError,
    APIConnectionError,
    APIResponseError
)
from .utils import load_environment, setup_logging


def create_weather_client(config_path: str = "config.yaml") -> WeatherAPI:
    """
    天気APIクライアントを作成するファクトリ関数
    
    Args:
        config_path: 設定ファイルのパス
        
    Returns:
        WeatherAPI: 初期化済みのAPIクライアント
    """
    load_environment()
    return WeatherAPI(config_path)