#!/usr/bin/env python3
"""
テスト実行スクリプト
包括的なテストスイートを実行するためのユーティリティ
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """コマンドを実行し結果を表示"""
    print(f"\n{'='*60}")
    print(f"実行中: {description}")
    print(f"コマンド: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"エラー: コマンドが失敗しました (終了コード: {e.returncode})")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"エラー: コマンドが見つかりません: {command[0]}")
        return False


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description="Weather App テストスイート実行")
    parser.add_argument('--unit', action='store_true', help='単体テストのみ実行')
    parser.add_argument('--integration', action='store_true', help='統合テストのみ実行')
    parser.add_argument('--web', action='store_true', help='Webテストのみ実行')
    parser.add_argument('--cli', action='store_true', help='CLIテストのみ実行')
    parser.add_argument('--e2e', action='store_true', help='E2Eテストのみ実行')
    parser.add_argument('--api', action='store_true', help='実際のAPIテストも実行')
    parser.add_argument('--coverage', action='store_true', help='カバレッジレポート生成')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細出力')
    parser.add_argument('--file', '-f', help='特定のテストファイルのみ実行')
    parser.add_argument('--function', '-k', help='特定のテスト関数のみ実行')
    
    args = parser.parse_args()
    
    # プロジェクトルートに移動
    project_root = Path(__file__).parent
    print(f"プロジェクトディレクトリ: {project_root}")
    
    # 基本的なpytestコマンド
    base_cmd = ['python', '-m', 'pytest']
    
    # 詳細出力オプション
    if args.verbose:
        base_cmd.extend(['-v', '-s'])
    
    # カバレッジオプション
    if args.coverage:
        base_cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term'])
    
    # 特定のファイル実行
    if args.file:
        base_cmd.append(f"tests/{args.file}")
    
    # 特定の関数実行
    if args.function:
        base_cmd.extend(['-k', args.function])
    
    # テスト種別別実行
    success = True
    
    if args.unit:
        cmd = base_cmd + ['-m', 'unit']
        success &= run_command(cmd, "単体テスト")
    
    elif args.integration:
        cmd = base_cmd + ['-m', 'integration']
        success &= run_command(cmd, "統合テスト")
    
    elif args.web:
        cmd = base_cmd + ['-m', 'web']
        success &= run_command(cmd, "Webテスト")
    
    elif args.cli:
        cmd = base_cmd + ['-m', 'cli']
        success &= run_command(cmd, "CLIテスト")
    
    elif args.e2e:
        cmd = base_cmd + ['-m', 'integration', 'tests/test_end_to_end.py']
        success &= run_command(cmd, "E2Eテスト")
    
    elif args.api:
        cmd = base_cmd + ['-m', 'api']
        success &= run_command(cmd, "実際のAPIテスト")
    
    elif args.file or args.function:
        # 特定ファイル・関数実行
        success &= run_command(base_cmd, f"指定されたテスト")
    
    else:
        # 全テスト実行（段階的）
        test_phases = [
            (base_cmd + ['-m', 'unit'], "🧪 単体テスト"),
            (base_cmd + ['-m', 'integration', '--ignore=tests/test_end_to_end.py'], "🔗 統合テスト"),
            (base_cmd + ['tests/test_end_to_end.py', '-m', 'integration'], "🌐 E2Eテスト"),
        ]
        
        print("📋 包括的テストスイートを実行します")
        print("段階:")
        for i, (_, description) in enumerate(test_phases, 1):
            print(f"  {i}. {description}")
        
        for cmd, description in test_phases:
            if not run_command(cmd, description):
                success = False
                print(f"❌ {description} で失敗しました")
                break
            else:
                print(f"✅ {description} が成功しました")
    
    # 結果サマリー
    print(f"\n{'='*60}")
    if success:
        print("🎉 すべてのテストが成功しました！")
        
        if args.coverage:
            print("\n📊 カバレッジレポートが生成されました:")
            print("  - HTML: htmlcov/index.html")
            print("  - ターミナル: 上記の出力を参照")
        
        print("\n💡 追加オプション:")
        print("  --unit      : 単体テストのみ")
        print("  --integration: 統合テストのみ")
        print("  --web       : Webテストのみ")
        print("  --coverage  : カバレッジレポート生成")
        print("  --api       : 実際のAPIテスト（要APIキー）")
        
        return 0
    else:
        print("❌ テストで失敗があります")
        print("\n🔍 トラブルシューティング:")
        print("  1. 依存関係: pip install -r requirements.txt")
        print("  2. 環境変数: .envファイルの設定確認")
        print("  3. 詳細確認: --verbose オプションを使用")
        return 1


if __name__ == "__main__":
    sys.exit(main())