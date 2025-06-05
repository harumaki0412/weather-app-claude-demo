# Weather App - Claude Code Demo

OpenWeatherMap APIを使用した天気情報取得アプリです。CLI版とWeb版（Flask）の両方をサポートしています。

## 機能

- 都市名を入力して現在の天気情報を表示
- 気温、湿度、天気概況の表示
- エラーハンドリング（存在しない都市名など）
- CLI版とWeb版の両方をサポート

## セットアップ

1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

2. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集してOpenWeatherMap APIキーを設定
```

3. OpenWeatherMap APIキーの取得
[OpenWeatherMap](https://openweathermap.org/api)でアカウントを作成し、APIキーを取得してください。

## 使用方法

### CLI版
```bash
python src/weather_cli.py [都市名]
```

### Web版
```bash
python src/weather_web.py
```

その後、ブラウザで http://localhost:5000 にアクセス

## テスト実行

```bash
pytest tests/
```

## プロジェクト構造

```
weather-app-claude-demo/
├── src/                    # ソースコード
│   ├── weather_api.py      # OpenWeatherMap API連携
│   ├── weather_cli.py      # CLI版実装
│   ├── weather_web.py      # Flask Web版実装
│   └── utils.py           # 共通ユーティリティ
├── tests/                  # テストコード
├── templates/             # Flask テンプレート
├── config.yaml           # 設定ファイル
└── requirements.txt      # Python依存関係
```
