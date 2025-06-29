# RNEP-VERTY 프로젝트 컨텍스트

## 프로젝트 개요
RNEP(Risk and Noise Evaluation Platform) - UAM(도심항공교통) 위험도 및 소음 평가 플랫폼

## 주요 기능
1. SHP 파일을 통한 비행경로 임포트
2. 비행 시나리오 편집 (날짜, 시간, 기체, 경로 선택)
3. 웨이포인트별 ETA(예상도착시간) 계산
4. 평가 알고리즘 연동 (위험도: UNIST, 소음: 건국대)
5. QGIS 호환 결과 출력

## 기술 스택
- Python 3.9+
- FastAPI (비동기 REST API)
- PostgreSQL + PostGIS (공간 데이터)
- SQLAlchemy + Alembic (ORM, 마이그레이션)
- Pydantic (데이터 검증)
- Redis (캐싱)
- Docker

## 개발 현황
### 완료된 작업
- ✅ 프로젝트 기본 구조 생성 (Issue #1)
- ✅ 데이터베이스 스키마 구현 (Issue #3)
  - SQLAlchemy 모델 정의
  - Alembic 마이그레이션 설정
  - PostGIS 공간 데이터 지원

### 진행 예정
1. **FastAPI 기본 설정 (Issue #11)** ← 다음 작업
2. SHP 파일 임포터 구현 (Issue #5)
3. 시나리오 관리 모듈 개발 (Issue #4)
4. ETA 계산기 구현 (Issue #6)
5. 시나리오 관리 API 구현 (Issue #12)

## 중요 설계 결정사항
1. **3D 시각화 제외** - 개발하지 않음
2. **위험도 맵 생성** - 인터페이스만 구현 (추후 개발)
3. **보고서 생성** - 인터페이스만 구현 (추후 개발)
4. **평가 알고리즘** - 외부 기관 제공 예정, 인터페이스만 정의

## 프로젝트 구조
```
rnep-verty/
├── rnep/               # 메인 애플리케이션
│   ├── api/           # FastAPI 엔드포인트
│   ├── config/        # 설정 관리
│   ├── database/      # DB 모델 및 연결
│   ├── edio/          # SHP 임포터, 시나리오 관리
│   ├── evaluation/    # 평가 알고리즘 인터페이스
│   └── output/        # 결과 출력 (QGIS 호환)
├── docs/              # 설계 문서
├── scripts/           # 유틸리티 스크립트
├── tests/             # 테스트 코드
└── data/              # 샘플 데이터
```

## 데이터베이스 접속 정보
- Host: localhost
- Port: 5432
- Database: rnep_db
- User: rnep_user
- Password: rnep_password

## 개발 환경 실행
```bash
# Docker 컨테이너 실행
docker-compose up -d

# 데이터베이스 초기화
python scripts/init_db.py

# API 서버 실행 (추후)
uvicorn rnep.api.main:app --reload
```

## 테스트 명령어
```bash
# 린트 실행
ruff check .

# 타입 체크
mypy rnep/

# 테스트 실행
pytest
```

## GitHub Issues
모든 개발 작업은 GitHub Issues로 관리됨:
- https://github.com/yourusername/rnep-verty/issues

## 참고 문서
- SRR 문서: /Users/dykim/Documents/1-1/SRR/기관/(250527)UAM1-1_SRR_건국대 수정_최종본.pdf
- 아키텍처: docs/ARCHITECTURE.md
- 데이터 모델: docs/DATA_MODEL.md
- API 명세: docs/API.md
- 워크플로우: docs/WORKFLOW.md