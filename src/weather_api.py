"""
OpenWeatherMap API連携クラス
天気情報の取得とデータ変換を行う
"""

import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from .models import WeatherData
from .exceptions import (
    CityNotFoundError, 
    APIKeyError, 
    APIConnectionError, 
    APIResponseError
)
from .utils import load_config, get_api_key


class WeatherAPI:
    """OpenWeatherMap API連携クラス"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初期化
        
        Args:
            config_path: 設定ファイルのパス
        """
        self.logger = logging.getLogger(__name__)
        self.config = load_config(config_path)
        self.api_key = get_api_key()
        
        # API設定の取得
        api_config = self.config.get('api', {})
        self.base_url = api_config.get('base_url', 'https://api.openweathermap.org/data/2.5')
        self.timeout = api_config.get('timeout', 10)
        self.units = api_config.get('units', 'metric')
        
        # デフォルト設定
        defaults = self.config.get('defaults', {})
        self.default_language = defaults.get('language', 'ja')
        
        self.logger.info("WeatherAPI初期化完了")
    
    def get_current_weather(self, city_name: str, lang: str = None) -> WeatherData:
        """
        指定都市の現在の天気情報を取得
        
        Args:
            city_name: 都市名
            lang: 言語設定（デフォルト: ja）
            
        Returns:
            WeatherData: 天気情報データ
            
        Raises:
            CityNotFoundError: 都市が見つからない場合
            APIKeyError: APIキーエラー
            APIConnectionError: 接続エラー
            APIResponseError: その他のAPIエラー
        """
        if lang is None:
            lang = self.default_language
            
        self.logger.info(f"天気情報取得開始: {city_name}")
        
        # APIパラメータの設定
        params = {
            'q': city_name,
            'appid': self.api_key,
            'units': self.units,
            'lang': lang
        }
        
        # API URL の構築
        url = urljoin(self.base_url, 'weather')
        
        try:
            # API リクエスト実行
            response = requests.get(url, params=params, timeout=self.timeout)
            self.logger.debug(f"API応答ステータス: {response.status_code}")
            
            # ステータスコード別のエラーハンドリング
            if response.status_code == 404:
                raise CityNotFoundError(city_name)
            elif response.status_code == 401:
                raise APIKeyError("APIキーが無効です")
            elif response.status_code != 200:
                raise APIResponseError(response.status_code)
            
            # JSON データの解析
            data = response.json()
            weather_data = self._parse_weather_data(data)
            
            self.logger.info(f"天気情報取得成功: {city_name}")
            return weather_data
            
        except requests.exceptions.Timeout:
            self.logger.error(f"APIタイムアウト: {city_name}")
            raise APIConnectionError("APIリクエストがタイムアウトしました")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"API接続エラー: {city_name}")
            raise APIConnectionError("APIサーバーに接続できません")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"APIリクエストエラー: {e}")
            raise APIConnectionError(f"APIリクエストエラー: {e}")
    
    def _parse_weather_data(self, data: Dict[str, Any]) -> WeatherData:
        """
        API応答データをWeatherDataオブジェクトに変換
        
        Args:
            data: OpenWeatherMap APIの応答データ
            
        Returns:
            WeatherData: 構造化された天気データ
        """
        try:
            # 基本情報
            city_name = data['name']
            country = data['sys']['country']
            
            # 気温・体感温度
            main = data['main']
            temperature = round(main['temp'], 1)
            feels_like = round(main['feels_like'], 1)
            humidity = main['humidity']
            pressure = main['pressure']
            
            # 天気概況
            weather = data['weather'][0]
            description = weather['description']
            description_en = weather['main']
            
            # 風情報（オプショナル）
            wind = data.get('wind', {})
            wind_speed = wind.get('speed')
            wind_direction = wind.get('deg')
            
            # 視程（オプショナル）
            visibility = data.get('visibility')
            
            # タイムスタンプ
            timestamp = datetime.now()
            
            return WeatherData(
                city_name=city_name,
                country=country,
                temperature=temperature,
                feels_like=feels_like,
                humidity=humidity,
                pressure=pressure,
                description=description,
                description_en=description_en,
                wind_speed=wind_speed,
                wind_direction=wind_direction,
                visibility=visibility,
                timestamp=timestamp
            )
            
        except KeyError as e:
            self.logger.error(f"API応答データの解析エラー: {e}")
            raise APIResponseError(200, f"API応答データが不完全です: {e}")
    
    def validate_api_key(self) -> bool:
        """
        APIキーの有効性を検証
        
        Returns:
            bool: APIキーが有効かどうか
        """
        try:
            # 軽量なAPIリクエストでキーを検証
            self.get_current_weather("London")
            return True
        except APIKeyError:
            return False
        except Exception:
            # その他のエラーの場合、キー自体は有効と判断
            return True