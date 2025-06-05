"""
CLI用ユーティリティ関数
ユーザビリティ向上のための表示機能
"""

import sys
import os
from typing import Optional
from datetime import datetime


class Colors:
    """ANSIカラーコード定義"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    @classmethod
    def is_supported(cls) -> bool:
        """カラー出力がサポートされているかチェック"""
        return (
            hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and
            os.environ.get("TERM") != "dumb"
        )


def colored_text(text: str, color: str, bold: bool = False) -> str:
    """
    カラー付きテキストを生成
    
    Args:
        text: 表示テキスト
        color: カラーコード
        bold: 太字にするか
        
    Returns:
        str: カラー付きテキスト（サポートされていない場合は通常テキスト）
    """
    if not Colors.is_supported():
        return text
    
    style = Colors.BOLD if bold else ""
    return f"{style}{color}{text}{Colors.RESET}"


def print_header(title: str) -> None:
    """ヘッダー表示"""
    print()
    print(colored_text("=" * 50, Colors.CYAN, bold=True))
    print(colored_text(f"  {title}", Colors.CYAN, bold=True))
    print(colored_text("=" * 50, Colors.CYAN, bold=True))
    print()


def print_success(message: str) -> None:
    """成功メッセージ表示"""
    print(colored_text(f"✓ {message}", Colors.GREEN, bold=True))


def print_error(message: str) -> None:
    """エラーメッセージ表示"""
    print(colored_text(f"✗ エラー: {message}", Colors.RED, bold=True))


def print_warning(message: str) -> None:
    """警告メッセージ表示"""
    print(colored_text(f"⚠ 警告: {message}", Colors.YELLOW, bold=True))


def print_info(message: str) -> None:
    """情報メッセージ表示"""
    print(colored_text(f"ℹ {message}", Colors.BLUE))


def format_weather_display(weather_data) -> str:
    """
    天気情報を見やすく整形
    
    Args:
        weather_data: WeatherDataオブジェクト
        
    Returns:
        str: 整形された天気情報
    """
    # 天気アイコンのマッピング
    weather_icons = {
        'clear': '☀️',
        'clouds': '☁️',
        'rain': '🌧️',
        'drizzle': '🌦️',
        'thunderstorm': '⛈️',
        'snow': '❄️',
        'mist': '🌫️',
        'fog': '🌫️',
        'haze': '🌫️',
    }
    
    # 天気アイコンを取得
    icon = ""
    for key, emoji in weather_icons.items():
        if key in weather_data.description_en.lower():
            icon = emoji + " "
            break
    
    # 風向きを文字で表現
    wind_direction_text = ""
    if weather_data.wind_direction is not None:
        directions = ['北', '北北東', '北東', '東北東', '東', '東南東', '南東', '南南東',
                     '南', '南南西', '南西', '西南西', '西', '西北西', '北西', '北北西']
        index = round(weather_data.wind_direction / 22.5) % 16
        wind_direction_text = directions[index]
    
    # 表示内容を構築
    lines = []
    lines.append(colored_text(f"📍 都市: {weather_data.city_name}, {weather_data.country}", Colors.CYAN, bold=True))
    lines.append(colored_text(f"{icon}天気: {weather_data.description}", Colors.BLUE, bold=True))
    lines.append("")
    
    # 気温情報
    temp_color = Colors.RED if weather_data.temperature > 25 else Colors.BLUE if weather_data.temperature < 10 else Colors.GREEN
    lines.append(colored_text(f"🌡️  気温: {weather_data.temperature}℃", temp_color, bold=True))
    lines.append(f"   体感温度: {weather_data.feels_like}℃")
    lines.append("")
    
    # その他の情報
    lines.append(f"💧 湿度: {weather_data.humidity}%")
    lines.append(f"🎈 気圧: {weather_data.pressure} hPa")
    
    # 風情報（利用可能な場合）
    if weather_data.wind_speed is not None:
        wind_text = f"💨 風速: {weather_data.wind_speed} m/s"
        if wind_direction_text:
            wind_text += f" ({wind_direction_text})"
        lines.append(wind_text)
    
    # 視程（利用可能な場合）
    if weather_data.visibility is not None:
        lines.append(f"👁️  視程: {weather_data.visibility / 1000:.1f} km")
    
    lines.append("")
    lines.append(colored_text(f"🕐 取得時刻: {weather_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", Colors.MAGENTA))
    
    return "\n".join(lines)


def prompt_city_name(default_city: Optional[str] = None) -> str:
    """
    都市名の入力を促す
    
    Args:
        default_city: デフォルト都市名
        
    Returns:
        str: 入力された都市名
    """
    if default_city:
        prompt = f"都市名を入力してください (デフォルト: {default_city}): "
    else:
        prompt = "都市名を入力してください: "
    
    try:
        city = input(colored_text(prompt, Colors.CYAN)).strip()
        return city if city else default_city
    except KeyboardInterrupt:
        print("\n")
        print_info("操作がキャンセルされました")
        sys.exit(0)
    except EOFError:
        print("\n")
        print_error("入力エラーが発生しました")
        sys.exit(1)


def confirm_action(message: str) -> bool:
    """
    ユーザーに確認を求める
    
    Args:
        message: 確認メッセージ
        
    Returns:
        bool: ユーザーの選択（True/False）
    """
    try:
        response = input(colored_text(f"{message} (y/N): ", Colors.YELLOW)).strip().lower()
        return response in ['y', 'yes', 'はい']
    except (KeyboardInterrupt, EOFError):
        return False