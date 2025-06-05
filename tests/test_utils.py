"""
ユーティリティ関数（utils.py）の単体テスト
"""

import os
import pytest
import tempfile
import yaml
from unittest.mock import patch, mock_open
from pathlib import Path

from src.utils import (
    load_config,
    load_environment,
    get_api_key,
    setup_logging
)


class TestLoadConfig:
    """load_config関数のテスト"""
    
    @pytest.mark.unit
    def test_load_config_success(self, test_config_file):
        """正常な設定ファイル読み込みテスト"""
        config = load_config(test_config_file)
        
        assert isinstance(config, dict)
        assert 'api' in config
        assert 'defaults' in config
        assert 'web' in config
        assert 'logging' in config
        
        # API設定確認
        assert config['api']['base_url'] == "https://api.openweathermap.org/data/2.5/"
        assert config['api']['timeout'] == 10
        assert config['api']['units'] == "metric"
        
        # デフォルト設定確認
        assert config['defaults']['city'] == "Tokyo"
        assert config['defaults']['language'] == "ja"
    
    @pytest.mark.unit
    def test_load_config_file_not_found(self):
        """存在しないファイルの読み込みテスト"""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_config("nonexistent_config.yaml")
        
        assert "設定ファイル nonexistent_config.yaml が見つかりません" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_load_config_invalid_yaml(self):
        """無効なYAMLファイルの読み込みテスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [unmatched bracket")
            invalid_yaml_file = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_config(invalid_yaml_file)
            
            assert "設定ファイルの読み込みエラー" in str(exc_info.value)
        finally:
            os.unlink(invalid_yaml_file)
    
    @pytest.mark.unit
    def test_load_config_empty_file(self):
        """空のファイルの読み込みテスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            empty_file = f.name
        
        try:
            config = load_config(empty_file)
            assert config is None
        finally:
            os.unlink(empty_file)
    
    @pytest.mark.unit
    def test_load_config_unicode_content(self):
        """Unicode文字を含む設定ファイルの読み込みテスト"""
        config_content = {
            'api': {
                'base_url': 'https://api.example.com/',
                'description': '天気API設定'
            },
            'defaults': {
                'city': '東京',
                'message': 'こんにちは世界'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_content, f, allow_unicode=True)
            unicode_file = f.name
        
        try:
            config = load_config(unicode_file)
            assert config['defaults']['city'] == '東京'
            assert config['defaults']['message'] == 'こんにちは世界'
        finally:
            os.unlink(unicode_file)


class TestLoadEnvironment:
    """load_environment関数のテスト"""
    
    @pytest.mark.unit
    @patch('src.utils.load_dotenv')
    def test_load_environment_calls_load_dotenv(self, mock_load_dotenv):
        """load_dotenvが呼び出されることを確認"""
        load_environment()
        mock_load_dotenv.assert_called_once()
    
    @pytest.mark.unit
    def test_load_environment_no_exception(self):
        """例外が発生しないことを確認"""
        # 実際にload_dotenvを呼び出しても例外が発生しないことを確認
        try:
            load_environment()
        except Exception as e:
            pytest.fail(f"load_environment() raised an exception: {e}")


class TestGetApiKey:
    """get_api_key関数のテスト"""
    
    @pytest.mark.unit
    def test_get_api_key_success(self, mock_env_vars):
        """APIキーが正常に取得できるテスト"""
        api_key = get_api_key()
        assert api_key == 'test_api_key_123456789abcdef'
    
    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_not_set(self):
        """APIキーが設定されていない場合のテスト"""
        with pytest.raises(ValueError) as exc_info:
            get_api_key()
        
        assert "環境変数 OPENWEATHER_API_KEY が設定されていません" in str(exc_info.value)
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': ''})
    def test_get_api_key_empty_string(self):
        """APIキーが空文字の場合のテスト"""
        with pytest.raises(ValueError) as exc_info:
            get_api_key()
        
        assert "環境変数 OPENWEATHER_API_KEY が設定されていません" in str(exc_info.value)
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': '   '})
    def test_get_api_key_whitespace_only(self):
        """APIキーが空白のみの場合のテスト"""
        # 現在の実装では空白もそのまま返される
        api_key = get_api_key()
        assert api_key == '   '


class TestSetupLogging:
    """setup_logging関数のテスト"""
    
    @pytest.mark.unit
    @patch('src.utils.logging.basicConfig')
    def test_setup_logging_default_parameters(self, mock_basic_config):
        """デフォルトパラメータでのログ設定テスト"""
        setup_logging()
        
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args
        
        # レベルがINFOであることを確認
        assert call_args[1]['level'] == 20  # logging.INFO = 20
        
        # フォーマットがデフォルトであることを確認
        assert "%(asctime)s - %(name)s - %(levelname)s - %(message)s" in call_args[1]['format']
        
        # ハンドラーが設定されていることを確認
        assert 'handlers' in call_args[1]
    
    @pytest.mark.unit
    @patch('src.utils.logging.basicConfig')
    def test_setup_logging_custom_level(self, mock_basic_config):
        """カスタムレベルでのログ設定テスト"""
        setup_logging("DEBUG")
        
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args
        
        # レベルがDEBUGであることを確認
        assert call_args[1]['level'] == 10  # logging.DEBUG = 10
    
    @pytest.mark.unit
    @patch('src.utils.logging.basicConfig')
    def test_setup_logging_custom_format(self, mock_basic_config):
        """カスタムフォーマットでのログ設定テスト"""
        custom_format = "%(levelname)s: %(message)s"
        setup_logging("INFO", custom_format)
        
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args
        
        assert call_args[1]['format'] == custom_format
    
    @pytest.mark.unit
    @patch('src.utils.logging.basicConfig')
    def test_setup_logging_invalid_level(self, mock_basic_config):
        """無効なログレベルでの設定テスト"""
        # getattr(logging, 'INVALID_LEVEL'.upper()) は AttributeError を発生させる
        with pytest.raises(AttributeError):
            setup_logging("INVALID_LEVEL")
    
    @pytest.mark.unit
    @patch('src.utils.logging.basicConfig')
    def test_setup_logging_case_insensitive_level(self, mock_basic_config):
        """大文字小文字を区別しないレベル設定テスト"""
        test_levels = ["debug", "INFO", "Warning", "ERROR", "critical"]
        expected_numeric_levels = [10, 20, 30, 40, 50]
        
        for level_str, expected_numeric in zip(test_levels, expected_numeric_levels):
            mock_basic_config.reset_mock()
            setup_logging(level_str)
            
            call_args = mock_basic_config.call_args
            assert call_args[1]['level'] == expected_numeric


class TestUtilsIntegration:
    """ユーティリティ関数の統合テスト"""
    
    @pytest.mark.unit
    def test_config_and_env_integration(self, test_config_file, mock_env_vars):
        """設定ファイルと環境変数の統合テスト"""
        # 環境変数を読み込み
        load_environment()
        
        # 設定ファイルを読み込み
        config = load_config(test_config_file)
        
        # APIキーを取得
        api_key = get_api_key()
        
        # すべてが正常に動作することを確認
        assert isinstance(config, dict)
        assert api_key == 'test_api_key_123456789abcdef'
        assert config['api']['base_url'] == "https://api.openweathermap.org/data/2.5/"
    
    @pytest.mark.unit
    @patch('src.utils.logging.basicConfig')
    def test_logging_setup_with_config(self, mock_basic_config, test_config_file):
        """設定ファイルからのログ設定テスト"""
        config = load_config(test_config_file)
        logging_config = config.get('logging', {})
        
        level = logging_config.get('level', 'INFO')
        format_str = logging_config.get('format')
        
        setup_logging(level, format_str)
        
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args
        
        # ERROR レベル（50）が設定されていることを確認
        assert call_args[1]['level'] == 40  # logging.ERROR = 40
        assert call_args[1]['format'] == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"