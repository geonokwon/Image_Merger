#!/bin/bash
# Mac용 로컬 빌드: 한글 경로에서도 PyInstaller가 실패하지 않도록
# 영문 경로(/tmp/ImageMergerBuild)에서 빌드 후 dist/ 를 프로젝트로 복사합니다.

set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="/tmp/ImageMergerBuild"

echo "프로젝트: $PROJECT_DIR"
echo "빌드 경로: $BUILD_DIR (영문 경로에서 빌드)"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# 필요한 파일만 복사 (.venv, dist, build, .git 제외)
rsync -a --exclude='.venv' --exclude='venv' --exclude='dist' --exclude='build' \
  --exclude='.git' --exclude='__pycache__' --exclude='*.spec' --exclude='.DS_Store' \
  "$PROJECT_DIR/" "$BUILD_DIR/"

cd "$BUILD_DIR"
echo "가상환경 생성 및 의존성 설치..."
python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt

echo "PyInstaller로 Mac 앱 빌드 중..."
.venv/bin/pyinstaller --noconfirm --windowed --name ImageMerger \
  --distpath dist --workpath build --specpath . \
  main.py

echo "dist/ 를 프로젝트로 복사..."
mkdir -p "$PROJECT_DIR/dist"
cp -R "$BUILD_DIR/dist/"* "$PROJECT_DIR/dist/"

echo "완료. 응용 프로그램: $PROJECT_DIR/dist/ImageMerger.app"
ls -la "$PROJECT_DIR/dist/"
