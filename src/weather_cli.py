#!/usr/bin/env python3
"""
Weather CLI - 天気情報取得コマンドラインアプリ
ユーザーフレンドリーなインターフェースと包括的なエラーハンドリングを提供
"""

__version__ = "1.0.0"

import sys
import argparse
import logging
from typing import Optional, List
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src import create_weather_client, setup_logging
from src.exceptions import (
    CityNotFoundError,
    APIKeyError,
    APIConnectionError,
    APIResponseError,
    WeatherAPIError
)
from src.cli_utils import (
    print_header,
    print_success,
    print_error,
    print_warning,
    print_info,
    format_weather_display,
    prompt_city_name,
    confirm_action,
    colored_text,
    Colors
)


class WeatherCLI:
    """天気情報CLI アプリケーション"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        CLI初期化
        
        Args:
            config_path: 設定ファイルパス
        """
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.weather_client = None
        
    def initialize_client(self) -> bool:
        """
        天気APIクライアントを初期化
        
        Returns:
            bool: 初期化成功フラグ
        """
        try:
            self.weather_client = create_weather_client(self.config_path)
            return True
        except FileNotFoundError as e:
            print_error(f"設定ファイルが見つかりません: {e}")
            self._show_setup_instructions()
            return False
        except Exception as e:
            print_error(f"初期化エラー: {e}")
            return False
    
    def validate_setup(self) -> bool:
        """
        セットアップの検証（APIキーなど）
        
        Returns:
            bool: セットアップが有効かどうか
        """
        try:
            print_info("APIキーを検証中...")
            if self.weather_client.validate_api_key():
                print_success("APIキーは有効です")
                return True
            else:
                print_error("APIキーが無効です")
                self._show_api_key_instructions()
                return False
        except APIKeyError:
            print_error("APIキーが設定されていません")
            self._show_api_key_instructions()
            return False
        except APIConnectionError:
            print_warning("ネットワーク接続を確認できませんが、処理を続行します")
            return True
        except Exception as e:
            print_error(f"セットアップ検証エラー: {e}")
            return False
    
    def get_weather_for_city(self, city_name: str, show_detailed: bool = False) -> bool:
        """
        指定都市の天気情報を取得・表示
        
        Args:
            city_name: 都市名
            show_detailed: 詳細表示フラグ
            
        Returns:
            bool: 取得成功フラグ
        """
        try:
            print_info(f"'{city_name}' の天気情報を取得中...")
            
            # 天気情報取得
            weather_data = self.weather_client.get_current_weather(city_name)
            
            # 成功メッセージ
            print_success(f"天気情報を取得しました")
            print()
            
            # 天気情報表示
            print(format_weather_display(weather_data))
            
            # 詳細情報表示（オプション）
            if show_detailed:
                self._show_detailed_info(weather_data)
            
            return True
            
        except CityNotFoundError as e:
            print_error(f"都市が見つかりません: {e.city_name}")
            self._suggest_similar_cities(e.city_name)
            return False
            
        except APIKeyError as e:
            print_error(f"APIキーエラー: {e}")
            self._show_api_key_instructions()
            return False
            
        except APIConnectionError as e:
            print_error(f"接続エラー: {e}")
            self._show_connection_troubleshooting()
            return False
            
        except APIResponseError as e:
            print_error(f"API応答エラー: {e}")
            if e.status_code == 429:
                print_warning("API使用制限に達している可能性があります。しばらく待ってから再試行してください。")
            return False
            
        except WeatherAPIError as e:
            print_error(f"天気API例外: {e}")
            return False
            
        except Exception as e:
            print_error(f"予期しないエラー: {e}")
            self.logger.exception("Unexpected error in get_weather_for_city")
            return False
    
    def interactive_mode(self) -> None:
        """対話型モード"""
        print_header("天気情報アプリ - 対話モード")
        print_info("'quit', 'exit', 'q' で終了します")
        print()
        
        # デフォルト都市を設定から取得
        try:
            default_city = self.weather_client.config.get('defaults', {}).get('city', 'Tokyo')
        except:
            default_city = 'Tokyo'
        
        while True:
            try:
                city = prompt_city_name(default_city)
                
                if not city:
                    print_warning("都市名が入力されませんでした")
                    continue
                
                # 終了コマンドチェック
                if city.lower() in ['quit', 'exit', 'q', 'やめる', '終了']:
                    print_info("アプリケーションを終了します")
                    break
                
                # 天気情報取得
                success = self.get_weather_for_city(city)
                
                if success:
                    # 次の操作確認
                    print()
                    if not confirm_action("他の都市の天気も調べますか？"):
                        break
                else:
                    # エラー時の継続確認
                    print()
                    if not confirm_action("続行しますか？"):
                        break
                
                print()  # 改行
                
            except KeyboardInterrupt:
                print("\n")
                print_info("操作がキャンセルされました")
                break
            except EOFError:
                print("\n")
                break
    
    def batch_mode(self, cities: List[str], show_detailed: bool = False) -> None:
        """
        バッチモード（複数都市の一括処理）
        
        Args:
            cities: 都市名リスト
            show_detailed: 詳細表示フラグ
        """
        print_header(f"天気情報一括取得 - {len(cities)}都市")
        
        success_count = 0
        
        for i, city in enumerate(cities, 1):
            print(colored_text(f"\n[{i}/{len(cities)}] ", Colors.CYAN, bold=True) + f"処理中: {city}")
            print("-" * 40)
            
            if self.get_weather_for_city(city, show_detailed):
                success_count += 1
        
        # 結果サマリー
        print()
        print_header("処理結果")
        print_success(f"成功: {success_count}/{len(cities)} 都市")
        if success_count < len(cities):
            print_error(f"失敗: {len(cities) - success_count}/{len(cities)} 都市")
    
    def _show_detailed_info(self, weather_data) -> None:
        """詳細情報の表示"""
        print("\n" + colored_text("🔍 詳細情報", Colors.CYAN, bold=True))
        print("-" * 30)
        print(f"データソース: OpenWeatherMap API")
        print(f"API応答都市名: {weather_data.city_name}")
        print(f"国コード: {weather_data.country}")
        print(f"英語概況: {weather_data.description_en}")
        if weather_data.wind_direction:
            print(f"風向き: {weather_data.wind_direction}°")
    
    def _suggest_similar_cities(self, city_name: str) -> None:
        """類似都市名の提案"""
        # 日本の主要都市（よくある入力ミス対応）
        major_cities = {
            'tokyo': ['Tokyo', '東京'],
            'osaka': ['Osaka', '大阪'],
            'kyoto': ['Kyoto', '京都'],
            'nagoya': ['Nagoya', '名古屋'],
            'sapporo': ['Sapporo', '札幌'],
            'fukuoka': ['Fukuoka', '福岡'],
            'hiroshima': ['Hiroshima', '広島'],
            'sendai': ['Sendai', '仙台']
        }
        
        city_lower = city_name.lower()
        for key, suggestions in major_cities.items():
            if key in city_lower or any(s.lower() in city_lower for s in suggestions):
                print_info(f"もしかして: {', '.join(suggestions)}")
                break
        else:
            print_info("英語での都市名入力を試してください（例: Tokyo, London, New York）")
    
    def _show_setup_instructions(self) -> None:
        """セットアップ手順の表示"""
        print()
        print_info("セットアップが必要です:")
        print("1. pip install -r requirements.txt")
        print("2. cp .env.example .env")
        print("3. .envファイルにOpenWeatherMap APIキーを設定")
        print("4. https://openweathermap.org/api でAPIキーを取得")
    
    def _show_api_key_instructions(self) -> None:
        """APIキー設定手順の表示"""
        print()
        print_info("APIキーの設定手順:")
        print("1. https://openweathermap.org/api でアカウント作成")
        print("2. APIキーを取得")
        print("3. .envファイルのOPENWEATHER_API_KEYに設定")
        print("4. 例: OPENWEATHER_API_KEY=your_api_key_here")
    
    def _show_connection_troubleshooting(self) -> None:
        """接続トラブルシューティング"""
        print()
        print_info("接続トラブルシューティング:")
        print("1. インターネット接続を確認")
        print("2. プロキシ設定を確認")
        print("3. ファイアウォール設定を確認")
        print("4. しばらく時間をおいて再試行")


def create_parser() -> argparse.ArgumentParser:
    """コマンドライン引数パーサーを作成"""
    parser = argparse.ArgumentParser(
        description="天気情報取得CLIアプリケーション",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s                     # 対話モード
  %(prog)s Tokyo               # Tokyo の天気を取得
  %(prog)s Tokyo London        # 複数都市の天気を一括取得
  %(prog)s --interactive       # 対話モードを明示的に開始
  %(prog)s Tokyo --detailed    # 詳細情報付きで表示
        """
    )
    
    parser.add_argument(
        'cities',
        nargs='*',
        help='都市名（複数指定可能）'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='対話モードで実行'
    )
    
    parser.add_argument(
        '-d', '--detailed',
        action='store_true',
        help='詳細情報を表示'
    )
    
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='設定ファイルパス（デフォルト: config.yaml）'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='詳細ログを表示'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='カラー出力を無効化'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
        help='バージョン情報を表示'
    )
    
    return parser


def main() -> int:
    """メイン実行関数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # ログレベル設定
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    # カラー出力設定
    if args.no_color:
        Colors.is_supported = lambda: False
    
    # CLI アプリケーション初期化
    cli = WeatherCLI(args.config)
    
    # クライアント初期化
    if not cli.initialize_client():
        return 1
    
    # セットアップ検証
    if not cli.validate_setup():
        return 1
    
    try:
        # 実行モード判定
        if args.interactive or not args.cities:
            # 対話モード
            cli.interactive_mode()
        else:
            # バッチモード
            cli.batch_mode(args.cities, args.detailed)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n")
        print_info("操作がキャンセルされました")
        return 130  # SIGINT
    except Exception as e:
        print_error(f"予期しないエラー: {e}")
        logging.getLogger(__name__).exception("Unexpected error in main")
        return 1


if __name__ == "__main__":
    sys.exit(main())