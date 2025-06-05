# 🌤️ Weather App - 総合天気情報取得アプリケーション

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/Tests-134_passing-brightgreen)](./tests/)
[![Coverage](https://img.shields.io/badge/Coverage-50%25-yellow)](./htmlcov/index.html)
[![License](https://img.shields.io/badge/License-MIT-blue)](./LICENSE)

OpenWeatherMap APIを使用した包括的な天気情報取得アプリケーション。初心者から開発者まで使いやすい設計で、CLI版とWeb版（Flask）の両方をサポートし、充実したテストスイート（134テスト）を備えています。

![Weather App Demo](https://via.placeholder.com/800x400/1e3a8a/ffffff?text=Weather+App+CLI+%26+Web+Interface)

## 🎯 プロジェクト概要

このアプリケーションは、世界中の都市の天気情報を簡単に取得できる総合的なソリューションです。教育目的とプロダクション利用の両方を想定し、モダンなPython開発のベストプラクティスを実装しています。

### 🌟 何ができるアプリか

- **🏙️ 世界中の都市の天気情報取得**: 都市名を指定して現在の天気、気温、湿度、風速などを表示
- **🖥️ マルチインターフェース**: コマンドライン（CLI）とWebブラウザ（Flask）の両方で利用可能
- **🎨 ユーザーフレンドリー**: カラフルな出力、対話型モード、わかりやすいエラーメッセージ
- **🔧 高い拡張性**: モジュラー設計で新機能の追加が容易
- **✅ 品質保証**: 包括的なテストカバレッジによる信頼性の確保
- **📊 開発者支援**: 詳細なログ、設定管理、APIキー検証機能

## 🚀 主要機能一覧

### 📱 CLI版（コマンドライン）
- **単発検索**: `python src/weather_cli.py Tokyo`
- **一括検索**: `python src/weather_cli.py Tokyo London Paris`
- **対話モード**: `python src/weather_cli.py --interactive`
- **詳細表示**: `python src/weather_cli.py Tokyo --detailed`
- **カスタマイズ**: カラー出力制御、ログレベル調整
- **バージョン情報**: `python src/weather_cli.py --version`

### 🌐 Web版（Flaskアプリ）
- **HTML フォーム**: ブラウザから直感的に天気検索
- **JSON API**: プログラムからのアクセス用RESTful API
- **リアルタイム表示**: 美しいWebインターフェース
- **API テスト機能**: 開発者向けのAPI動作確認ページ
- **ヘルスチェック**: アプリケーション状態監視エンドポイント
- **バージョン情報**: `/api/version` エンドポイント

### 🧪 テスト機能
- **134個の包括的テスト**: 単体・統合・E2Eテスト
- **50%コードカバレッジ**: HTMLレポート付き
- **モック対応**: 外部API依存なしでテスト実行
- **CI/CD対応**: 自動テスト実行環境
- **パフォーマンステスト**: 並行処理・負荷テスト

## ⚡ クイックスタート

### 1️⃣ 環境準備
```bash
# リポジトリをクローン
git clone https://github.com/harumaki0412/weather-app-claude-demo.git
cd weather-app-claude-demo

# 仮想環境作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2️⃣ 依存関係インストール
```bash
pip install -r requirements.txt
```

### 3️⃣ APIキー設定
```bash
# 環境変数ファイル作成
cp .env.example .env

# .envファイルを編集してAPIキーを設定
echo "OPENWEATHER_API_KEY=your_api_key_here" >> .env
```

### 4️⃣ 動作確認
```bash
# CLI版で東京の天気を取得
python src/weather_cli.py Tokyo

# Web版を起動（別ターミナルで）
python src/weather_web.py
# ブラウザで http://localhost:5000 にアクセス
```

## 🔑 詳細なセットアップ手順

### OpenWeatherMap APIキーの取得

1. **アカウント作成**
   - [OpenWeatherMap](https://openweathermap.org/api) にアクセス
   - 「Sign Up」でアカウント作成（無料）
   - メール認証を完了

2. **APIキー取得**
   - ダッシュボードの「API keys」タブ
   - デフォルトキーをコピー、または新規作成
   - キーがアクティブになるまで数分待機

3. **環境変数設定**
   ```bash
   # .envファイルに追記
   OPENWEATHER_API_KEY=your_actual_api_key_here
   
   # またはシステム環境変数として設定
   export OPENWEATHER_API_KEY=your_actual_api_key_here
   ```

4. **APIキー動作確認**
   ```bash
   # 専用検証スクリプトで確認
   python verify_api_key.py
   
   # または簡単なテスト
   python debug_api.py
   ```

### Python環境の詳細設定

```bash
# Python 3.8以上を確認
python --version

# 仮想環境作成（推奨方法）
python -m venv weather_app_env
source weather_app_env/bin/activate  # Linux/Mac
# weather_app_env\Scripts\activate  # Windows

# 依存関係の詳細インストール
pip install --upgrade pip
pip install -r requirements.txt

# 開発用依存関係（オプション）
pip install pytest-xdist  # 並列テスト実行
pip install black         # コードフォーマット
pip install flake8        # コード品質チェック
```

## 📁 ファイル構造の完全解説

```
weather-app-claude-demo/
├── 📋 ドキュメント・設定
│   ├── README.md              # このファイル - プロジェクト説明
│   ├── LICENSE                # MITライセンス
│   ├── TEST_SUMMARY.md        # テストスイート詳細ガイド
│   ├── config.yaml            # アプリケーション設定
│   ├── pytest.ini            # pytest設定
│   ├── requirements.txt       # Python依存関係
│   └── .env.example          # 環境変数テンプレート
│
├── 🚀 実行ファイル・ユーティリティ
│   ├── run_tests.py          # 統合テスト実行スクリプト
│   ├── debug_api.py          # API動作確認ツール
│   ├── demo_cli.py           # CLI使用例デモ
│   ├── verify_api_key.py     # APIキー検証ツール
│   ├── test_api.py           # 手動API テスト
│   ├── test_web_*.py         # Web機能テスト
│   ├── weather               # CLI実行用シェルスクリプト
│   └── web                   # Web実行用シェルスクリプト
│
├── 💻 ソースコード (src/)
│   ├── __init__.py           # パッケージ初期化・ファクトリ関数
│   ├── weather_api.py        # OpenWeatherMap API クライアント
│   ├── weather_cli.py        # CLI アプリケーション本体
│   ├── weather_web.py        # Flask Web アプリケーション
│   ├── models.py             # データモデル（WeatherData）
│   ├── exceptions.py         # カスタム例外クラス
│   ├── utils.py              # 設定読み込み・ログ設定
│   └── cli_utils.py          # CLI用ユーティリティ（色付き出力等）
│
├── 🧪 テストスイート (tests/)
│   ├── __init__.py           # テストパッケージ初期化
│   ├── conftest.py           # pytest共通設定・フィクスチャ
│   ├── fixtures/             # テスト用データ・設定
│   │   └── test_config.yaml  # テスト専用設定
│   ├── test_models.py        # データモデル単体テスト
│   ├── test_exceptions.py    # 例外クラステスト  
│   ├── test_utils.py         # ユーティリティ関数テスト
│   ├── test_weather_api.py   # API クライアント単体テスト
│   ├── test_weather_cli_integration.py  # CLI統合テスト
│   ├── test_weather_web_integration.py # Web統合テスト
│   └── test_end_to_end.py    # エンドツーエンドテスト
│
├── 🎨 Webテンプレート (templates/)
│   ├── base.html             # 基本レイアウトテンプレート
│   ├── weather.html          # 天気表示ページ
│   └── api_test.html         # API テスト用ページ
│
├── 📊 静的ファイル (static/)
│   └── css/                  # CSSスタイルシート
│
└── 📈 レポート・キャッシュ
    ├── htmlcov/              # テストカバレッジHTMLレポート
    ├── .pytest_cache/        # pytestキャッシュ
    └── .DS_Store            # macOS システムファイル
```

### 🔍 主要ファイルの役割詳細

#### コアモジュール
- **`src/weather_api.py`**: OpenWeatherMap APIとの通信を担当。HTTPリクエスト、レスポンス解析、エラーハンドリング
- **`src/models.py`**: 天気データの構造化。型安全性とデータ変換を保証
- **`src/exceptions.py`**: アプリケーション固有の例外。適切なエラー分類と処理

#### インターフェース
- **`src/weather_cli.py`**: CLI アプリケーションのメインロジック。引数解析、対話モード、バッチ処理
- **`src/weather_web.py`**: Flask Webアプリケーション。ルーティング、テンプレート、JSON API

#### サポートモジュール  
- **`src/utils.py`**: 設定管理、ログ設定、環境変数処理
- **`src/cli_utils.py`**: CLI表示用ユーティリティ。カラー出力、フォーマット、ユーザー入力

## 🎮 使用方法

### CLI版の具体的使用例

```bash
# 基本的な天気取得
python src/weather_cli.py Tokyo
# 出力例:
# 🌤️  東京, JP の天気情報
# 🌡️  気温: 25.5℃ (体感: 27.0℃)
# 💧 湿度: 65%
# 🌀 気圧: 1013 hPa
# 💨 風速: 3.5 m/s

# 複数都市の一括検索
python src/weather_cli.py Tokyo London "New York"
# 3つの都市の天気を順次表示

# 対話モード
python src/weather_cli.py --interactive
# 対話的に都市名を入力して連続検索

# 詳細情報付き表示  
python src/weather_cli.py Tokyo --detailed
# 視界、風向き、日の出・日の入り時刻も表示

# カスタム設定ファイル使用
python src/weather_cli.py Tokyo --config custom_config.yaml

# ログレベル調整
python src/weather_cli.py Tokyo --verbose

# カラー出力無効化
python src/weather_cli.py Tokyo --no-color

# ヘルプ表示
python src/weather_cli.py --help
```

### Web版の具体的使用例

```bash
# デフォルト設定で起動
python src/weather_web.py
# http://localhost:5000 でアクセス可能

# カスタムポート・ホスト指定
python src/weather_web.py --host 0.0.0.0 --port 8080

# デバッグモード有効
python src/weather_web.py --debug

# 本番環境用設定
python src/weather_web.py --host 0.0.0.0 --port 80
```

#### Web API エンドポイント

```bash
# JSON形式で天気情報取得
curl "http://localhost:5000/api/weather/Tokyo"

# レスポンス例:
{
  "status": "success",
  "data": {
    "city_name": "Tokyo",
    "country": "JP", 
    "temperature": 25.5,
    "humidity": 65,
    "description": "晴れ"
  }
}

# ヘルスチェック
curl "http://localhost:5000/health"

# バージョン情報
curl "http://localhost:5000/api/version"

# エラーハンドリング例
curl "http://localhost:5000/api/weather/NonexistentCity"
# 404エラーとエラー詳細を返却
```

### 設定ファイルのカスタマイズ

```yaml
# config.yaml の例
api:
  base_url: "https://api.openweathermap.org/data/2.5/"
  timeout: 15  # タイムアウト延長
  units: "imperial"  # 華氏温度

defaults:
  city: "London"  # デフォルト都市変更
  language: "en"  # 英語表示

web:
  host: "127.0.0.1"
  port: 8080
  debug: false  # 本番環境設定

logging:
  level: "DEBUG"  # デバッグログ有効
```

## 👩‍💻 開発者向け情報

### テスト実行

```bash
# 全テスト実行
python run_tests.py

# カバレッジレポート付き
python run_tests.py --coverage

# 特定タイプのテスト実行
python run_tests.py --unit      # 単体テストのみ
python run_tests.py --integration  # 統合テストのみ
python run_tests.py --e2e       # E2Eテストのみ

# 特定ファイルのテスト
python run_tests.py --file test_models.py

# 詳細出力
python run_tests.py --verbose

# 並列実行（高速化）
pytest -n auto

# 実際のAPI使用テスト（APIキー必要）
python run_tests.py --api
```

### 開発環境構築

```bash
# 開発用依存関係インストール
pip install pytest-xdist pytest-mock coverage black flake8

# コードフォーマット
black src/ tests/

# コード品質チェック
flake8 src/ tests/

# 型チェック（オプション）
pip install mypy
mypy src/

# pre-commit フック設定（オプション）
pip install pre-commit
pre-commit install
```

### デバッグとトラブルシューティング

```bash
# API接続テスト
python debug_api.py

# APIキー検証
python verify_api_key.py

# 設定ファイル検証
python -c "from src.utils import load_config; print(load_config('config.yaml'))"

# ログファイル確認
tail -f app.log  # ログファイルがある場合

# 依存関係確認
pip list
pip check
```

### 新機能開発ガイドライン

1. **ブランチ戦略**
   ```bash
   git checkout -b feature/新機能名
   ```

2. **テスト駆動開発**
   ```bash
   # テストを先に書く
   # 実装
   # リファクタリング
   ```

3. **コード品質確保**
   ```bash
   # テスト実行
   python run_tests.py
   
   # フォーマット
   black .
   
   # 品質チェック
   flake8 .
   ```

## 🛠️ 技術スタック・設計思想

### 技術スタック

#### バックエンド
- **Python 3.8+**: モダンなPython機能を活用
- **Requests 2.31.0**: HTTP通信ライブラリ
- **Flask 3.0.0**: 軽量Webフレームワーク
- **PyYAML 6.0.1**: 設定ファイル管理
- **python-dotenv 1.0.0**: 環境変数管理

#### テスト・品質管理
- **pytest 7.4.3**: テストフレームワーク
- **pytest-mock 3.12.0**: モック機能
- **pytest-cov 4.1.0**: カバレッジ測定
- **coverage 7.3.2**: カバレッジレポート生成

#### 外部API
- **OpenWeatherMap API**: 天気データソース
- **RESTful API設計**: 標準的なHTTP方式

### 設計思想とアーキテクチャ

#### 1. モジュラー設計
```
分離された責任範囲:
- API通信 (weather_api.py)
- ビジネスロジック (models.py, exceptions.py)  
- ユーザーインターフェース (weather_cli.py, weather_web.py)
- ユーティリティ (utils.py, cli_utils.py)
```

#### 2. 設定外部化
- YAML設定ファイル
- 環境変数サポート
- デフォルト値の提供
- 環境別設定対応

#### 3. 堅牢なエラーハンドリング
```python
# カスタム例外階層
WeatherAPIError
├── CityNotFoundError
├── APIKeyError  
├── APIConnectionError
└── APIResponseError
```

#### 4. テスト戦略
- **単体テスト**: 個別関数・クラス
- **統合テスト**: モジュール間連携
- **E2Eテスト**: 完全なワークフロー
- **モック活用**: 外部依存を排除

#### 5. ユーザビリティ重視
- 直感的なCLIインターフェース
- カラフルな出力
- 対話型モード
- 詳細なエラーメッセージ

### パフォーマンス最適化

- **接続タイムアウト設定**: API応答性確保
- **効率的なデータ変換**: 型安全性とパフォーマンス両立
- **並行処理対応**: 複数都市の同時取得可能
- **キャッシュ戦略**: （将来実装予定）

### セキュリティ考慮事項

- **APIキー保護**: 環境変数による秘匿化
- **入力検証**: SQLインジェクション等の対策
- **XSS対策**: Flaskの自動エスケープ活用
- **ログセキュリティ**: 機密情報のログ出力回避

## 🚧 今後の拡張予定

### Phase 1: 基本機能強化 (短期)
- [ ] **5日間天気予報機能**
  - 詳細な予報データ表示
  - グラフ・チャート形式の可視化
  
- [ ] **お気に入り都市管理**
  - ユーザー設定として保存
  - 一括取得機能
  
- [ ] **気象警報・注意報**
  - 警報情報の取得・表示
  - プッシュ通知機能

### Phase 2: ユーザーエクスペリエンス向上 (中期)
- [ ] **モダンWebUI**
  - React/Vue.js フロントエンド
  - レスポンシブデザイン
  - PWA (Progressive Web App) 対応
  
- [ ] **多言語対応**
  - 国際化 (i18n) 実装
  - 多様な言語での天気情報
  
- [ ] **テーマ・カスタマイズ**
  - ダークモード
  - カラーテーマ選択
  - レイアウト調整

### Phase 3: 高度な機能 (長期)
- [ ] **機械学習予測**
  - 独自の天気予測モデル
  - 履歴データ分析
  
- [ ] **IoTデバイス連携**
  - 温度センサー統合
  - スマートホーム連携
  
- [ ] **APIプラットフォーム化**
  - 開発者向けAPI提供
  - レート制限・認証機能
  - 詳細な使用状況分析

### Phase 4: エンタープライズ機能 (将来)
- [ ] **マルチテナント対応**
  - 組織・チーム管理
  - 権限・ロール管理
  
- [ ] **ビッグデータ処理**
  - 大規模気象データ処理
  - リアルタイムストリーミング
  
- [ ] **クラウドネイティブ**
  - Docker コンテナ化
  - Kubernetes 対応
  - CI/CD パイプライン完全自動化

### 技術的改善項目
- [ ] **パフォーマンス最適化**
  - Redis キャッシュ導入
  - 非同期処理 (asyncio) 対応
  - GraphQL API 提供
  
- [ ] **監視・運用**
  - Prometheus メトリクス
  - Grafana ダッシュボード
  - ヘルスチェック強化
  
- [ ] **セキュリティ強化**
  - OAuth 2.0 認証
  - API レート制限
  - セキュリティスキャン自動化

## 🤝 コントリビューション

プロジェクトへの貢献を歓迎します！

### 開発参加手順
1. Issues で議論・提案
2. Fork & Clone
3. 機能ブランチ作成
4. 実装 & テスト
5. Pull Request 作成

### 開発ガイドライン
- テスト付きで実装
- コードスタイル準拠
- ドキュメント更新
- Conventional Commits

## 📄 ライセンス

MIT License - 詳細は [LICENSE](./LICENSE) ファイルを参照

## 🙋‍♂️ サポート・お問い合わせ

- **Issues**: [GitHub Issues](https://github.com/harumaki0412/weather-app-claude-demo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/harumaki0412/weather-app-claude-demo/discussions)
- **Email**: [プロジェクト専用メール]

---

<div align="center">

**🌟 このプロジェクトが役に立ったら、Star ⭐ をお願いします！**

Made with ❤️ by [harumaki0412](https://github.com/harumaki0412)

🤖 Generated with [Claude Code](https://claude.ai/code)

</div>