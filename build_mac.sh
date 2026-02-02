#!/bin/bash
# Mac용 로컬 빌드: .app 번들로 출력.
# 영문 경로(/tmp/ImageMergerBuild)에서 빌드 후 dist/ 를 프로젝트로 복사.

set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="/tmp/ImageMergerBuild"

echo "프로젝트: $PROJECT_DIR"
echo "빌드 경로: $BUILD_DIR (영문 경로에서 빌드)"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# 필요한 파일만 복사 (.venv, dist, build, .git 제외). ImageMerger.spec 포함
rsync -a --exclude='.venv' --exclude='venv' --exclude='dist' --exclude='build' \
  --exclude='.git' --exclude='__pycache__' --exclude='main.spec' --exclude='.DS_Store' \
  "$PROJECT_DIR/" "$BUILD_DIR/"

cd "$BUILD_DIR"
echo "가상환경 생성 및 의존성 설치..."
python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt

echo "PyInstaller로 Mac .app 번들 빌드 중 (ImageMerger.spec 사용)..."
.venv/bin/pyinstaller --noconfirm ImageMerger.spec --distpath dist --workpath build

echo "dist/ 를 프로젝트로 복사 (.app 번들만 유지)..."
mkdir -p "$PROJECT_DIR/dist"
rm -rf "$PROJECT_DIR/dist/"*
# .app 번들만 복사 (PyInstaller가 ImageMerger 폴더도 만들면 제외)
for f in "$BUILD_DIR/dist/"*; do
  case "$(basename "$f")" in
    ImageMerger.app) cp -R "$f" "$PROJECT_DIR/dist/" ;;
    ImageMerger)     ;;  # 폴더는 복사하지 않음
    *)               cp -R "$f" "$PROJECT_DIR/dist/" ;;
  esac
done

echo "완료. 응용 프로그램: $PROJECT_DIR/dist/ImageMerger.app"
ls -la "$PROJECT_DIR/dist/"
