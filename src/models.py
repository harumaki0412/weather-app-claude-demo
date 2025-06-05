"""
天気データモデル
APIレスポンスを構造化したデータクラス
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class WeatherData:
    """天気情報を格納するデータクラス"""
    city_name: str                    # 都市名
    country: str                      # 国名
    temperature: float                # 気温（℃）
    feels_like: float                # 体感温度（℃）
    humidity: int                     # 湿度（%）
    pressure: int                     # 気圧（hPa）
    description: str                  # 天気概況（日本語）
    description_en: str               # 天気概況（英語）
    wind_speed: Optional[float]       # 風速（m/s）
    wind_direction: Optional[int]     # 風向（度）
    visibility: Optional[int]         # 視程（メートル）
    timestamp: datetime               # データ取得時刻
    
    def __str__(self) -> str:
        """天気情報の文字列表現"""
        return (
            f"都市: {self.city_name}, {self.country}\n"
            f"天気: {self.description}\n"
            f"気温: {self.temperature}℃ (体感温度: {self.feels_like}℃)\n"
            f"湿度: {self.humidity}%\n"
            f"気圧: {self.pressure} hPa"
        )
    
    def to_dict(self) -> dict:
        """辞書形式での出力（Web版で使用）"""
        return {
            'city_name': self.city_name,
            'country': self.country,
            'temperature': self.temperature,
            'feels_like': self.feels_like,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'description': self.description,
            'description_en': self.description_en,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'visibility': self.visibility,
            'timestamp': self.timestamp.isoformat()
        }