"""
カスタム例外クラス
APIエラーやアプリケーション固有のエラーを定義
"""


class WeatherAPIError(Exception):
    """天気API関連の基底例外クラス"""
    pass


class CityNotFoundError(WeatherAPIError):
    """指定された都市が見つからない場合の例外"""
    def __init__(self, city_name: str):
        self.city_name = city_name
        super().__init__(f"都市 '{city_name}' が見つかりません")


class APIKeyError(WeatherAPIError):
    """APIキーが無効または未設定の場合の例外"""
    def __init__(self, message: str = "APIキーが無効または未設定です"):
        super().__init__(message)


class APIConnectionError(WeatherAPIError):
    """API接続エラーの例外"""
    def __init__(self, message: str = "APIサーバーに接続できません"):
        super().__init__(message)


class APIResponseError(WeatherAPIError):
    """API応答エラーの例外"""
    def __init__(self, status_code: int, message: str = None):
        self.status_code = status_code
        error_msg = message or f"APIエラー (ステータスコード: {status_code})"
        super().__init__(error_msg)