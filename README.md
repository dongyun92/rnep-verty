# RNEP-VERTY (Risk and Noise Evaluation Platform)

UAM(Urban Air Mobility) 운항을 위한 위험도 및 소음 평가 통합 플랫폼

## 프로젝트 개요

RNEP(Risk and Noise Evaluation Platform)는 UAM 비행 시나리오에 대한 종합적인 안전성 및 환경 영향 평가를 수행하는 플랫폼입니다. 버티(Verty)가 개발하는 이 시스템은 다양한 연구기관의 평가 알고리즘을 통합하여 QGIS 기반의 시각화를 지원합니다.

### 주요 기능

- **비행 시나리오 관리**: SHP 파일 기반 비행경로 임포트 및 시나리오 편집
- **평가 알고리즘 통합**: UNIST(위험도), 건국대(소음) 등 외부 알고리즘 연동 (인터페이스 정의 완료, 실제 연동은 추후 진행)
- **QGIS 호환 출력**: 평가 결과를 QGIS에서 시각화 가능한 형식으로 출력

### 개발 현황

#### 진행 중
- 프로젝트 기본 구조 설정
- 시나리오 관리 시스템 개발
- SHP 파일 임포터 구현
- FastAPI 기반 REST API 개발

#### 예정
- 알고리즘 어댑터 구현 (외부 기관 알고리즘 제공 시)
- Mock 알고리즘 구현 (테스트용, 필요시)

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         External Systems                         │
├─────────────────┬──────────────────┬───────────────────────────┤
│   QGIS Plugin   │  UNIST Algorithms│   Konkuk Algorithms      │
│   (SHP Files)   │  (Risk Assessment)│   (Noise Assessment)     │
└────────┬────────┴─────────┬────────┴────────┬──────────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RNEP Platform Core                          │
├─────────────────────────────────────────────────────────────────┤
│  • Scenario Management System                                    │
│  • Evaluation Orchestrator                                       │
│  • Output Generator (QGIS Compatible)                           │
└─────────────────────────────────────────────────────────────────┘
```

## 설치 가이드

### 요구사항

- Python 3.9+
- PostgreSQL 12+ (with PostGIS)
- Redis 6+

### 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/dongyun92/rnep-verty.git
cd rnep-verty
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 설정 입력
```

5. 데이터베이스 초기화
```bash
python manage.py init-db
```

6. 개발 서버 실행
```bash
uvicorn rnep.api.main:app --reload
```

## 개발 환경

Docker를 사용한 개발 환경 설정:

```bash
docker-compose up -d
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
rnep-verty/
├── rnep/               # 메인 애플리케이션
│   ├── scenario/       # 시나리오 관리
│   ├── evaluation/     # 평가 관리
│   ├── output/         # 출력 생성
│   └── api/           # REST API
├── docs/              # 문서
├── tests/             # 테스트
└── data/              # 데이터 디렉토리
```

## 기여 방법

1. 이슈를 먼저 생성하여 작업 내용을 명시
2. 기능 브랜치 생성: `git checkout -b feature/issue-number`
3. 변경사항 커밋: `git commit -m "feat: 기능 설명"`
4. 브랜치 푸시: `git push origin feature/issue-number`
5. Pull Request 생성

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 연락처

- 프로젝트 관리자: 버티(Verty)
- 이메일: [연락처 이메일]
- GitHub Issues: https://github.com/dongyun92/rnep-verty/issues