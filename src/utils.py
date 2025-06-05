"""
ユーティリティ関数
設定ファイルの読み込み、ログ設定、共通処理など
"""

import yaml
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """設定ファイルを読み込み"""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"設定ファイル {config_path} が見つかりません")
    except yaml.YAMLError as e:
        raise ValueError(f"設定ファイルの読み込みエラー: {e}")


def load_environment() -> None:
    """環境変数を読み込み"""
    load_dotenv()


def get_api_key() -> str:
    """OpenWeatherMap APIキーを取得"""
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        raise ValueError("環境変数 OPENWEATHER_API_KEY が設定されていません")
    return api_key


def setup_logging(level: str = "INFO", format_str: str = None) -> None:
    """ログ設定を初期化"""
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        handlers=[logging.StreamHandler()]
    )