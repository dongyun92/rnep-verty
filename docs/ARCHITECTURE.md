# RNEP 시스템 아키텍처

## 1. 시스템 개요

RNEP(Risk and Noise Evaluation Platform)는 UAM 비행 시나리오에 대한 위험도 및 소음 평가를 수행하는 통합 플랫폼입니다.

## 2. 핵심 컴포넌트

### 2.1 시나리오 관리 시스템 (Scenario Management)

#### 기능
- SHP 파일에서 비행경로 임포트
- 비행 시나리오 생성 및 편집
- 웨이포인트별 예상 도착시간(ETA) 자동 계산

#### 주요 클래스
- `FlightPathImporter`: SHP 파일 임포트 및 변환
- `ScenarioEditor`: 시나리오 생성 및 편집
- `ETACalculator`: 웨이포인트별 도착시간 계산

### 2.2 평가 오케스트레이터 (Evaluation Orchestrator)

#### 기능
- 다양한 평가 알고리즘 통합 관리
- 평가 작업 스케줄링 및 실행
- 결과 수집 및 저장

#### 알고리즘 어댑터
- `UNISTGroundRiskAdapter`: UNIST 지상 위험도 평가
- `UNISTAirRiskAdapter`: UNIST 공중 위험도 평가
- `KonkukNoiseAdapter`: 건국대 소음 평가

### 2.3 출력 생성기 (Output Generator)

#### 기능
- 평가 결과를 QGIS 호환 형식으로 변환
- SHP/GeoJSON 파일 생성
- QGIS 스타일 파일(.qml) 자동 생성

## 3. 데이터 흐름

### 3.1 비행경로 임포트
```
사용자 → SHP 파일 업로드 → FlightPathImporter → 좌표계 변환 → DB 저장
```

### 3.2 시나리오 생성
```
사용자 입력 (날짜/시간/기체/경로) → ScenarioEditor → ETA 계산 → 시나리오 저장
```

### 3.3 평가 실행
```
평가 요청 → EvaluationOrchestrator → 데이터 준비 → 알고리즘 실행 → 결과 저장
```

### 3.4 결과 출력
```
평가 결과 → QGISOutputGenerator → 형식 변환 → SHP/GeoJSON 생성 → 다운로드
```

## 4. 기술 스택

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL with PostGIS
- **Cache**: Redis
- **Task Queue**: Celery (선택사항)

### 데이터 처리
- **GIS**: GeoPandas, Shapely, Fiona
- **수치 계산**: NumPy, SciPy
- **데이터 검증**: Pydantic

### API
- **표준**: OpenAPI 3.0
- **인증**: JWT (향후 구현)
- **문서화**: Swagger UI, ReDoc

## 5. 데이터베이스 스키마

### 주요 테이블
- `flight_scenarios`: 비행 시나리오
- `flight_paths`: 비행경로 (SHP 임포트)
- `aircraft`: 기체 정보
- `evaluation_requests`: 평가 요청
- `evaluation_results`: 평가 결과

## 6. 확장성 고려사항

### 6.1 알고리즘 추가
- 플러그인 형태의 어댑터 패턴 사용
- 새로운 알고리즘은 `AlgorithmInterface` 구현

### 6.2 성능 최적화
- Redis 캐싱으로 반복 계산 최소화
- 대용량 처리를 위한 비동기 작업 큐

### 6.3 모니터링
- 평가 작업 상태 실시간 추적
- 시스템 리소스 사용량 모니터링

## 7. 보안 고려사항

- API 엔드포인트 인증/인가
- 입력 데이터 검증 및 소독
- 파일 업로드 크기 및 형식 제한
- 알고리즘 실행 환경 격리