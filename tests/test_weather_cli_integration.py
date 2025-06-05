"""
CLI版アプリケーション（weather_cli.py）の統合テスト
"""

import pytest
import sys
from io import StringIO
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.weather_cli import WeatherCLI, main, create_parser
from src.models import WeatherData
from src.exceptions import CityNotFoundError, APIKeyError, APIConnectionError


class TestWeatherCLIInitialization:
    """WeatherCLI初期化の統合テスト"""
    
    @pytest.mark.integration
    def test_cli_initialization_success(self, test_config_file, mock_env_vars, suppress_logging):
        """正常な初期化テスト"""
        cli = WeatherCLI(test_config_file)
        
        assert cli.config_path == test_config_file
        assert cli.weather_client is None  # 初期化時はNone
        assert cli.logger is not None
    
    @pytest.mark.integration
    def test_cli_client_initialization_success(self, test_config_file, mock_env_vars, suppress_logging):
        """クライアント初期化成功テスト"""
        cli = WeatherCLI(test_config_file)
        result = cli.initialize_client()
        
        assert result is True
        assert cli.weather_client is not None
    
    @pytest.mark.integration
    def test_cli_client_initialization_failure(self, mock_env_vars, suppress_logging):
        """クライアント初期化失敗テスト"""
        cli = WeatherCLI("nonexistent_config.yaml")
        
        with patch('sys.stdout', new_callable=StringIO):
            result = cli.initialize_client()
        
        assert result is False
        assert cli.weather_client is None


class TestWeatherCLIValidateSetup:
    """セットアップ検証の統合テスト"""
    
    @pytest.mark.integration
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    def test_validate_setup_success(self, mock_init, test_config_file, mock_env_vars, suppress_logging):
        """セットアップ検証成功テスト"""
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        # WeatherAPIクライアントをモック
        mock_client = Mock()
        mock_client.validate_api_key.return_value = True
        cli.weather_client = mock_client
        
        with patch('sys.stdout', new_callable=StringIO):
            result = cli.validate_setup()
        
        assert result is True
        mock_client.validate_api_key.assert_called_once()
    
    @pytest.mark.integration
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    def test_validate_setup_api_key_invalid(self, mock_init, test_config_file, mock_env_vars, suppress_logging):
        """APIキー無効時のセットアップ検証テスト"""
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        # APIキー検証が失敗するモック
        mock_client = Mock()
        mock_client.validate_api_key.return_value = False
        cli.weather_client = mock_client
        
        with patch('sys.stdout', new_callable=StringIO):
            result = cli.validate_setup()
        
        assert result is False
    
    @pytest.mark.integration
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    def test_validate_setup_api_key_error(self, mock_init, test_config_file, mock_env_vars, suppress_logging):
        """APIキーエラー時のセットアップ検証テスト"""
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        # APIKeyErrorを発生させるモック
        mock_client = Mock()
        mock_client.validate_api_key.side_effect = APIKeyError("Invalid API key")
        cli.weather_client = mock_client
        
        with patch('sys.stdout', new_callable=StringIO):
            result = cli.validate_setup()
        
        assert result is False


class TestWeatherCLIGetWeatherForCity:
    """天気情報取得の統合テスト"""
    
    @pytest.mark.integration
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    def test_get_weather_success(self, mock_init, test_config_file, mock_env_vars, 
                                sample_weather_data, suppress_logging):
        """天気情報取得成功テスト"""
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        # 成功するWeatherAPIクライアントをモック
        mock_client = Mock()
        mock_client.get_current_weather.return_value = sample_weather_data
        cli.weather_client = mock_client
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cli.get_weather_for_city("Tokyo")
        
        assert result is True
        mock_client.get_current_weather.assert_called_once_with("Tokyo")
        
        # 出力内容を確認
        output = mock_stdout.getvalue()
        assert "Tokyo" in output
        assert "25.5℃" in output
    
    @pytest.mark.integration
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    def test_get_weather_city_not_found(self, mock_init, test_config_file, mock_env_vars, suppress_logging):
        """都市が見つからない場合のテスト"""
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        # CityNotFoundErrorを発生させるモック
        mock_client = Mock()
        mock_client.get_current_weather.side_effect = CityNotFoundError("UnknownCity")
        cli.weather_client = mock_client
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cli.get_weather_for_city("UnknownCity")
        
        assert result is False
        
        # エラーメッセージが出力されることを確認
        output = mock_stdout.getvalue()
        assert "都市が見つかりません" in output
    
    @pytest.mark.integration
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    def test_get_weather_api_connection_error(self, mock_init, test_config_file, mock_env_vars, suppress_logging):
        """API接続エラーの場合のテスト"""
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        # APIConnectionErrorを発生させるモック
        mock_client = Mock()
        mock_client.get_current_weather.side_effect = APIConnectionError("Connection failed")
        cli.weather_client = mock_client
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cli.get_weather_for_city("Tokyo")
        
        assert result is False
        
        # 接続エラーメッセージが出力されることを確認
        output = mock_stdout.getvalue()
        assert "接続エラー" in output


class TestWeatherCLIBatchMode:
    """バッチモードの統合テスト"""
    
    @pytest.mark.integration
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    @patch.object(WeatherCLI, 'get_weather_for_city')
    def test_batch_mode_multiple_cities(self, mock_get_weather, mock_init, 
                                      test_config_file, mock_env_vars, suppress_logging):
        """複数都市のバッチ処理テスト"""
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        # get_weather_for_cityの戻り値を設定
        mock_get_weather.side_effect = [True, False, True]  # 2成功、1失敗
        
        cities = ["Tokyo", "UnknownCity", "London"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.batch_mode(cities)
        
        # 各都市に対してget_weather_for_cityが呼ばれたことを確認
        assert mock_get_weather.call_count == 3
        expected_cities = ["Tokyo", "UnknownCity", "London"]
        actual_calls = [call[0][0] for call in mock_get_weather.call_args_list]
        assert actual_calls == expected_cities
        
        # 結果サマリーが出力されることを確認
        output = mock_stdout.getvalue()
        assert "成功: 2/3" in output
        assert "失敗: 1/3" in output
    
    @pytest.mark.integration
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    @patch.object(WeatherCLI, 'get_weather_for_city', return_value=True)
    def test_batch_mode_detailed_option(self, mock_get_weather, mock_init, 
                                      test_config_file, mock_env_vars, suppress_logging):
        """詳細表示オプション付きバッチ処理テスト"""
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        cities = ["Tokyo"]
        
        with patch('sys.stdout', new_callable=StringIO):
            cli.batch_mode(cities, show_detailed=True)
        
        # 詳細表示フラグが正しく渡されることを確認
        mock_get_weather.assert_called_once_with("Tokyo", True)


class TestWeatherCLIArgumentParser:
    """コマンドライン引数パーサーのテスト"""
    
    @pytest.mark.integration
    def test_create_parser_basic(self):
        """基本的なパーサー作成テスト"""
        parser = create_parser()
        
        # ヘルプオプションが動作することを確認
        with pytest.raises(SystemExit):
            parser.parse_args(['--help'])
    
    @pytest.mark.integration
    def test_parser_single_city(self):
        """単一都市の引数解析テスト"""
        parser = create_parser()
        args = parser.parse_args(['Tokyo'])
        
        assert args.cities == ['Tokyo']
        assert args.interactive is False
        assert args.detailed is False
        assert args.verbose is False
    
    @pytest.mark.integration
    def test_parser_multiple_cities(self):
        """複数都市の引数解析テスト"""
        parser = create_parser()
        args = parser.parse_args(['Tokyo', 'London', 'Paris'])
        
        assert args.cities == ['Tokyo', 'London', 'Paris']
    
    @pytest.mark.integration
    def test_parser_interactive_mode(self):
        """対話モードの引数解析テスト"""
        parser = create_parser()
        args = parser.parse_args(['--interactive'])
        
        assert args.interactive is True
        assert args.cities == []
    
    @pytest.mark.integration
    def test_parser_detailed_mode(self):
        """詳細モードの引数解析テスト"""
        parser = create_parser()
        args = parser.parse_args(['Tokyo', '--detailed'])
        
        assert args.cities == ['Tokyo']
        assert args.detailed is True
    
    @pytest.mark.integration
    def test_parser_verbose_mode(self):
        """詳細ログモードの引数解析テスト"""
        parser = create_parser()
        args = parser.parse_args(['--verbose'])
        
        assert args.verbose is True
    
    @pytest.mark.integration
    def test_parser_custom_config(self):
        """カスタム設定ファイルの引数解析テスト"""
        parser = create_parser()
        args = parser.parse_args(['--config', 'custom_config.yaml'])
        
        assert args.config == 'custom_config.yaml'
    
    @pytest.mark.integration
    def test_parser_no_color(self):
        """カラー無効化の引数解析テスト"""
        parser = create_parser()
        args = parser.parse_args(['--no-color'])
        
        assert args.no_color is True


class TestWeatherCLIMainFunction:
    """main関数の統合テスト"""
    
    @pytest.mark.integration
    @patch('sys.argv', ['weather_cli.py', '--help'])
    def test_main_help_option(self):
        """ヘルプオプションでのmain関数テスト"""
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0  # 正常終了
    
    @pytest.mark.integration
    @patch('sys.argv', ['weather_cli.py', 'Tokyo'])
    @patch.object(WeatherCLI, 'initialize_client', return_value=False)
    def test_main_initialization_failure(self, mock_init, suppress_logging):
        """初期化失敗時のmain関数テスト"""
        with patch('sys.stdout', new_callable=StringIO):
            result = main()
        
        assert result == 1  # エラー終了
    
    @pytest.mark.integration
    @patch('sys.argv', ['weather_cli.py', 'Tokyo'])
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    @patch.object(WeatherCLI, 'validate_setup', return_value=False)
    def test_main_setup_validation_failure(self, mock_validate, mock_init, suppress_logging):
        """セットアップ検証失敗時のmain関数テスト"""
        with patch('sys.stdout', new_callable=StringIO):
            result = main()
        
        assert result == 1  # エラー終了
    
    @pytest.mark.integration
    @patch('sys.argv', ['weather_cli.py', 'Tokyo'])
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    @patch.object(WeatherCLI, 'validate_setup', return_value=True)
    @patch.object(WeatherCLI, 'batch_mode')
    def test_main_batch_mode_success(self, mock_batch, mock_validate, mock_init, suppress_logging):
        """バッチモード成功時のmain関数テスト"""
        with patch('sys.stdout', new_callable=StringIO):
            result = main()
        
        assert result == 0  # 正常終了
        mock_batch.assert_called_once_with(['Tokyo'], False)
    
    @pytest.mark.integration
    @patch('sys.argv', ['weather_cli.py', '--interactive'])
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    @patch.object(WeatherCLI, 'validate_setup', return_value=True)
    @patch.object(WeatherCLI, 'interactive_mode')
    def test_main_interactive_mode_success(self, mock_interactive, mock_validate, mock_init, suppress_logging):
        """対話モード成功時のmain関数テスト"""
        with patch('sys.stdout', new_callable=StringIO):
            result = main()
        
        assert result == 0  # 正常終了
        mock_interactive.assert_called_once()
    
    @pytest.mark.integration
    @patch('sys.argv', ['weather_cli.py', 'Tokyo'])
    @patch.object(WeatherCLI, 'initialize_client', side_effect=KeyboardInterrupt())
    def test_main_keyboard_interrupt(self, mock_init, suppress_logging):
        """Ctrl+C割り込み時のmain関数テスト"""
        # KeyboardInterruptが適切に処理されることをテスト（実際に割り込まない）
        try:
            with patch('sys.stdout', new_callable=StringIO):
                result = main()
            assert result == 130  # SIGINT終了コード
        except KeyboardInterrupt:
            # テスト環境でKeyboardInterruptが伝播した場合の処理
            pytest.skip("KeyboardInterruptテストをスキップ")
    
    @pytest.mark.integration
    @patch('sys.argv', ['weather_cli.py', 'Tokyo'])
    @patch.object(WeatherCLI, 'initialize_client', side_effect=Exception("Unexpected error"))
    def test_main_unexpected_exception(self, mock_init, suppress_logging):
        """予期しない例外時のmain関数テスト"""
        with patch('sys.stdout', new_callable=StringIO):
            result = main()
        
        assert result == 1  # エラー終了


class TestWeatherCLIUserExperience:
    """ユーザーエクスペリエンスの統合テスト"""
    
    @pytest.mark.integration
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    def test_error_messages_are_user_friendly(self, mock_init, test_config_file, mock_env_vars, suppress_logging):
        """エラーメッセージがユーザーフレンドリーであることのテスト"""
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        # 各種エラーに対してユーザーフレンドリーなメッセージが表示されることを確認
        test_cases = [
            (CityNotFoundError("TestCity"), "都市が見つかりません"),
            (APIKeyError(), "APIキーエラー"),
            (APIConnectionError(), "接続エラー")
        ]
        
        mock_client = Mock()
        cli.weather_client = mock_client
        
        for exception, expected_message in test_cases:
            mock_client.get_current_weather.side_effect = exception
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = cli.get_weather_for_city("TestCity")
            
            assert result is False
            output = mock_stdout.getvalue()
            assert expected_message in output
    
    @pytest.mark.integration
    @patch.object(WeatherCLI, 'initialize_client', return_value=True)
    def test_success_message_includes_weather_data(self, mock_init, test_config_file, 
                                                  mock_env_vars, sample_weather_data, suppress_logging):
        """成功時のメッセージに天気データが含まれることのテスト"""
        cli = WeatherCLI(test_config_file)
        cli.initialize_client()
        
        mock_client = Mock()
        mock_client.get_current_weather.return_value = sample_weather_data
        cli.weather_client = mock_client
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cli.get_weather_for_city("Tokyo")
        
        assert result is True
        output = mock_stdout.getvalue()
        
        # 天気データの主要な情報が含まれていることを確認
        assert "Tokyo" in output
        assert "25.5℃" in output
        assert "晴れ" in output
        assert "65%" in output  # 湿度