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

## 응용 프로그램 빌드 (GitHub Actions)

이 저장소를 `main` 또는 `master` 브랜치에 push하거나, GitHub Actions 탭에서 **Build Application** 워크플로를 수동 실행하면 **macOS용 .app**과 **Windows용 .exe**가 각각 빌드됩니다.

```bash
git remote add origin git@github.com:geonokwon/Image_Merger.git
git push -u origin main
```

| 플랫폼 | Artifact | 결과물 |
|--------|----------|--------|
| Windows | `ImageMerger-Windows` | `ImageMerger.exe` (단일 실행 파일) |
| macOS | `ImageMerger-macOS` | `ImageMerger.app` (앱 번들, 다운로드 후 압축 해제) |

빌드 완료 후 **Actions → 해당 run → Artifacts**에서 다운로드해 사용하면 됩니다.

**로컬에서 맥 빌드 시**: 프로젝트 경로에 한글 등 비영문 문자가 있으면 PyInstaller가 Qt 플러그인 경로를 찾지 못해 실패할 수 있습니다. 영문 경로(예: `~/Projects/Image_Merger`)로 복사한 뒤 빌드하거나, GitHub Actions로 빌드하는 것을 권장합니다.

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
