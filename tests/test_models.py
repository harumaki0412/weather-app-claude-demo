"""
モデルクラス（models.py）の単体テスト
"""

import pytest
from datetime import datetime

from src.models import WeatherData


class TestWeatherData:
    """WeatherDataクラスのテスト"""
    
    @pytest.mark.unit
    def test_weather_data_creation(self, sample_weather_data):
        """WeatherDataオブジェクトの作成テスト"""
        assert sample_weather_data.city_name == "Tokyo"
        assert sample_weather_data.country == "JP"
        assert sample_weather_data.temperature == 25.5
        assert sample_weather_data.feels_like == 27.0
        assert sample_weather_data.humidity == 65
        assert sample_weather_data.pressure == 1013
        assert sample_weather_data.description == "晴れ"
        assert sample_weather_data.description_en == "Clear"
        assert sample_weather_data.wind_speed == 3.5
        assert sample_weather_data.wind_direction == 180
        assert sample_weather_data.visibility == 10000
        assert isinstance(sample_weather_data.timestamp, datetime)
    
    @pytest.mark.unit
    def test_weather_data_str_representation(self, sample_weather_data):
        """文字列表現のテスト"""
        str_repr = str(sample_weather_data)
        
        assert "Tokyo, JP" in str_repr
        assert "晴れ" in str_repr
        assert "25.5℃" in str_repr
        assert "27.0℃" in str_repr
        assert "65%" in str_repr
        assert "1013 hPa" in str_repr
    
    @pytest.mark.unit
    def test_weather_data_to_dict(self, sample_weather_data):
        """辞書変換のテスト"""
        data_dict = sample_weather_data.to_dict()
        
        # 必須フィールドの確認
        assert data_dict['city_name'] == "Tokyo"
        assert data_dict['country'] == "JP"
        assert data_dict['temperature'] == 25.5
        assert data_dict['feels_like'] == 27.0
        assert data_dict['humidity'] == 65
        assert data_dict['pressure'] == 1013
        assert data_dict['description'] == "晴れ"
        assert data_dict['description_en'] == "Clear"
        assert data_dict['wind_speed'] == 3.5
        assert data_dict['wind_direction'] == 180
        assert data_dict['visibility'] == 10000
        
        # timestampがISO形式の文字列になっていることを確認
        assert isinstance(data_dict['timestamp'], str)
        assert 'T' in data_dict['timestamp']  # ISO形式のマーカー
    
    @pytest.mark.unit
    def test_weather_data_with_none_values(self):
        """オプショナルフィールドがNoneの場合のテスト"""
        weather_data = WeatherData(
            city_name="TestCity",
            country="TC",
            temperature=20.0,
            feels_like=21.0,
            humidity=50,
            pressure=1000,
            description="テスト天気",
            description_en="Test Weather",
            wind_speed=None,
            wind_direction=None,
            visibility=None,
            timestamp=datetime.now()
        )
        
        assert weather_data.wind_speed is None
        assert weather_data.wind_direction is None
        assert weather_data.visibility is None
        
        # 辞書変換でもNoneが保持されることを確認
        data_dict = weather_data.to_dict()
        assert data_dict['wind_speed'] is None
        assert data_dict['wind_direction'] is None
        assert data_dict['visibility'] is None
    
    @pytest.mark.unit
    def test_weather_data_immutability(self, sample_weather_data):
        """データクラスの不変性テスト（dataclassのfrozen=Falseのため変更可能）"""
        original_temp = sample_weather_data.temperature
        sample_weather_data.temperature = 30.0
        assert sample_weather_data.temperature == 30.0
        assert sample_weather_data.temperature != original_temp
    
    @pytest.mark.unit
    def test_weather_data_equality(self):
        """WeatherDataオブジェクトの等価性テスト"""
        timestamp = datetime.now()
        
        weather1 = WeatherData(
            city_name="Tokyo",
            country="JP",
            temperature=25.0,
            feels_like=26.0,
            humidity=60,
            pressure=1010,
            description="晴れ",
            description_en="Clear",
            wind_speed=2.0,
            wind_direction=90,
            visibility=10000,
            timestamp=timestamp
        )
        
        weather2 = WeatherData(
            city_name="Tokyo",
            country="JP",
            temperature=25.0,
            feels_like=26.0,
            humidity=60,
            pressure=1010,
            description="晴れ",
            description_en="Clear",
            wind_speed=2.0,
            wind_direction=90,
            visibility=10000,
            timestamp=timestamp
        )
        
        assert weather1 == weather2
    
    @pytest.mark.unit
    def test_weather_data_inequality(self, sample_weather_data):
        """WeatherDataオブジェクトの不等価性テスト"""
        different_weather = WeatherData(
            city_name="Osaka",  # 異なる都市名
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
            timestamp=sample_weather_data.timestamp
        )
        
        assert sample_weather_data != different_weather
    
    @pytest.mark.unit
    def test_weather_data_temperature_precision(self):
        """温度の精度テスト"""
        weather_data = WeatherData(
            city_name="TestCity",
            country="TC",
            temperature=25.123456,
            feels_like=26.987654,
            humidity=65,
            pressure=1013,
            description="テスト",
            description_en="Test",
            wind_speed=3.5,
            wind_direction=180,
            visibility=10000,
            timestamp=datetime.now()
        )
        
        # 小数点以下の精度が保持されることを確認
        assert weather_data.temperature == 25.123456
        assert weather_data.feels_like == 26.987654