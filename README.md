# Image Merger (이미지 합성)

**Repository**: [git@github.com:geonokwon/Image_Merger.git](https://github.com/geonokwon/Image_Merger)

PyQt5 GUI로 이미지·PDF를 드래그 앤 드롭해서 하나의 이미지로 합쳐 저장하는 프로그램입니다.

## 기능

- **드래그 앤 드롭**: 창에 이미지 파일을 끌어다 놓으면 목록에 추가
- **파일 추가**: "파일 추가..." 버튼으로 이미지 선택
- **합치기 방향**: 세로(위→아래) 또는 가로(왼쪽→오른쪽)
- **간격**: 이미지 사이 픽셀 간격 설정
- **저장**: PNG 또는 JPEG로 저장

## 실행 방법

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 테스트

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## 응용 프로그램 빌드

### Mac (로컬 빌드)

맥용은 로컬에서 `build_mac.sh`로 빌드해 `dist/`에 응용 프로그램(.app)을 만듭니다.

```bash
./build_mac.sh
# 완료 후: dist/ImageMerger.app
```

프로젝트 경로에 한글이 있으면 PyInstaller가 실패할 수 있어, 스크립트는 영문 경로(`/tmp/ImageMergerBuild`)에서 빌드한 뒤 `dist/`를 프로젝트로 복사합니다.

### Windows (GitHub Actions)

`main` 또는 `master`에 push하거나, Actions 탭에서 **Build Application (Windows)** 워크플로를 수동 실행하면 **Windows용 .exe**가 빌드됩니다.

```bash
git push origin main
```

빌드 완료 후 **Actions → 해당 run → Artifacts**에서 **ImageMerger-Windows**를 받으면 `ImageMerger.exe`가 포함됩니다.

## 구조

- `main.py` — 앱 진입점
- `src/main_window.py` — 메인 윈도우 UI
- `src/image_list_widget.py` — 드래그 앤 드롭 이미지 목록
- `src/image_merger.py` — 이미지 합치기 로직 (Pillow)
- `tests/test_image_merger.py` — image_merger 단위 테스트

## 요구 사항

- Python 3.9+
- PyQt5
- Pillow
