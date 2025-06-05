#!/usr/bin/env python3
"""
CLI デモンストレーション用スクリプト
CLIの各機能をテストします（実際のAPI呼び出しは行いません）
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.cli_utils import *
from src.models import WeatherData
from datetime import datetime


def demo_cli_features():
    """CLI機能のデモンストレーション"""
    
    # ヘッダー表示
    print_header("CLI ユーザビリティ機能デモ")
    
    # 各種メッセージ表示
    print_success("API接続成功メッセージ")
    print_error("都市が見つからないエラー")
    print_warning("ネットワーク接続警告")
    print_info("情報メッセージ")
    
    print()
    
    # カラー表示テスト
    print("📊 カラー表示テスト:")
    for color_name, color_code in [
        ("RED", Colors.RED),
        ("GREEN", Colors.GREEN),
        ("BLUE", Colors.BLUE),
        ("YELLOW", Colors.YELLOW),
        ("CYAN", Colors.CYAN),
        ("MAGENTA", Colors.MAGENTA)
    ]:
        print(f"  {colored_text(color_name, color_code, bold=True)} - 通常テキスト")
    
    print()
    
    # サンプル天気データを作成してフォーマットテスト
    print_header("天気情報表示フォーマットテスト")
    
    sample_weather = WeatherData(
        city_name="東京",
        country="JP",
        temperature=22.5,
        feels_like=25.1,
        humidity=65,
        pressure=1013,
        description="曇りがち",
        description_en="Clouds",
        wind_speed=3.2,
        wind_direction=180,
        visibility=10000,
        timestamp=datetime.now()
    )
    
    print(format_weather_display(sample_weather))
    
    print()
    print_header("対話機能テスト")
    print("実際の対話機能:")
    print("- prompt_city_name() - 都市名入力")
    print("- confirm_action() - はい/いいえ確認")
    print("- KeyboardInterrupt対応")
    print("- 入力検証とデフォルト値")
    
    print()
    print_success("CLI デモンストレーション完了")


if __name__ == "__main__":
    demo_cli_features()