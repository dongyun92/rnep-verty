# RNEP 데이터 모델 설계

## 1. 핵심 엔티티

### 1.1 FlightScenario (비행 시나리오)

비행 시나리오는 날짜, 시간, 기체, 경로를 조합한 하나의 평가 단위입니다.

```python
{
    "id": "uuid",
    "name": "string",
    "description": "string",
    "flight_date": "date",           # 비행 날짜
    "departure_time": "time",        # 출발 시간
    "aircraft_type": "string",       # 기체 ID
    "flight_path_id": "uuid",        # 비행경로 ID
    "waypoints_with_eta": [          # 계산된 도착시간
        {
            "waypoint_id": "string",
            "position": {
                "lat": "float",
                "lon": "float", 
                "alt": "float"
            },
            "estimated_arrival_time": "datetime",
            "speed": "float"
        }
    ],
    "created_at": "datetime",
    "updated_at": "datetime",
    "status": "enum[draft, ready, evaluating, completed]"
}
```

### 1.2 FlightPath (비행경로)

SHP 파일에서 임포트된 비행경로 정보입니다.

```python
{
    "id": "uuid",
    "name": "string",
    "source_file": "string",         # 원본 SHP 파일명
    "geometry": "LineString",        # GeoJSON 형식
    "waypoints": [
        {
            "id": "string",
            "sequence": "int",       # 순서
            "position": {
                "lat": "float",
                "lon": "float",
                "alt": "float"
            },
            "distance_from_previous": "float"  # 이전 지점과의 거리(km)
        }
    ],
    "total_distance": "float",       # 총 거리(km)
    "imported_at": "datetime"
}
```

### 1.3 Aircraft (기체 정보)

UAM 기체의 성능 및 특성 정보입니다.

```python
{
    "id": "string",
    "name": "string",
    "manufacturer": "string",
    "cruise_speed": "float",         # 순항 속도 (km/h)
    "max_speed": "float",            # 최대 속도 (km/h)
    "climb_rate": "float",           # 상승률 (m/min)
    "descent_rate": "float",         # 하강률 (m/min)
    "max_altitude": "float",         # 최대 고도 (m)
    "range": "float",                # 항속거리 (km)
    "noise_profile": {               # 소음 프로파일
        "takeoff": "float",
        "cruise": "float",
        "landing": "float"
    },
    "risk_parameters": {             # 위험도 파라미터
        "mtow": "float",             # 최대이륙중량
        "rotor_diameter": "float",
        "failure_rate": "float"
    }
}
```

### 1.4 EvaluationRequest (평가 요청)

시나리오에 대한 평가 요청 정보입니다.

```python
{
    "id": "uuid",
    "scenario_id": "uuid",
    "evaluation_types": ["ground_risk", "air_risk", "noise"],
    "requested_at": "datetime",
    "requested_by": "string",
    "status": "enum[pending, processing, completed, failed]",
    "progress": "int",               # 진행률 (0-100)
    "results": {
        "ground_risk": {
            "result_id": "uuid",
            "file_path": "string",
            "completed_at": "datetime"
        },
        "air_risk": {
            "result_id": "uuid",
            "file_path": "string",
            "completed_at": "datetime"
        },
        "noise": {
            "result_id": "uuid",
            "file_path": "string",
            "completed_at": "datetime"
        }
    },
    "error_message": "string"        # 실패 시 에러 메시지
}
```

### 1.5 EvaluationResult (평가 결과)

각 평가 유형별 결과 데이터입니다.

```python
{
    "id": "uuid",
    "evaluation_request_id": "uuid",
    "evaluation_type": "enum[ground_risk, air_risk, noise]",
    "algorithm_version": "string",
    "input_data": {},                # 입력 데이터 스냅샷
    "output_data": {                 # 결과 데이터
        "summary": {
            "max_value": "float",
            "min_value": "float",
            "mean_value": "float",
            "affected_area": "float"
        },
        "file_outputs": [            # 생성된 파일들
            {
                "type": "string",    # "shapefile", "geojson", "raster"
                "path": "string",
                "size": "int"
            }
        ]
    },
    "metadata": {
        "processing_time": "float",  # 처리 시간(초)
        "memory_usage": "float"      # 메모리 사용량(MB)
    },
    "created_at": "datetime"
}
```

## 2. 데이터베이스 스키마

### 2.1 PostgreSQL 테이블 정의

```sql
-- 비행 시나리오
CREATE TABLE flight_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    flight_date DATE NOT NULL,
    departure_time TIME NOT NULL,
    aircraft_type VARCHAR(50) NOT NULL,
    flight_path_id UUID NOT NULL,
    waypoints_with_eta JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flight_path_id) REFERENCES flight_paths(id),
    FOREIGN KEY (aircraft_type) REFERENCES aircraft(id)
);

-- 비행경로
CREATE TABLE flight_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    source_file VARCHAR(500),
    geometry GEOMETRY(LineString, 4326) NOT NULL,
    waypoints JSONB NOT NULL,
    total_distance FLOAT NOT NULL,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 기체 정보
CREATE TABLE aircraft (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255),
    cruise_speed FLOAT NOT NULL,
    max_speed FLOAT NOT NULL,
    climb_rate FLOAT NOT NULL,
    descent_rate FLOAT NOT NULL,
    max_altitude FLOAT,
    range FLOAT,
    noise_profile JSONB,
    risk_parameters JSONB
);

-- 평가 요청
CREATE TABLE evaluation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL,
    evaluation_types TEXT[] NOT NULL,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    requested_by VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    progress INT DEFAULT 0,
    results JSONB,
    error_message TEXT,
    FOREIGN KEY (scenario_id) REFERENCES flight_scenarios(id)
);

-- 평가 결과
CREATE TABLE evaluation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_request_id UUID NOT NULL,
    evaluation_type VARCHAR(20) NOT NULL,
    algorithm_version VARCHAR(50),
    input_data JSONB,
    output_data JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_request_id) REFERENCES evaluation_requests(id)
);
```

### 2.2 인덱스

```sql
-- 성능 최적화를 위한 인덱스
CREATE INDEX idx_scenarios_status ON flight_scenarios(status);
CREATE INDEX idx_scenarios_flight_date ON flight_scenarios(flight_date);
CREATE INDEX idx_paths_geometry ON flight_paths USING GIST(geometry);
CREATE INDEX idx_requests_status ON evaluation_requests(status);
CREATE INDEX idx_requests_scenario ON evaluation_requests(scenario_id);
CREATE INDEX idx_results_request ON evaluation_results(evaluation_request_id);
```

## 3. 데이터 검증 규칙

### 3.1 비행 시나리오
- 비행 날짜는 현재 날짜 이후여야 함
- 출발 시간은 00:00-23:59 범위
- 기체와 비행경로는 반드시 존재해야 함

### 3.2 비행경로
- 최소 2개 이상의 웨이포인트 필요
- 좌표는 WGS84 (EPSG:4326) 기준
- 고도는 0-5000m 범위

### 3.3 평가 요청
- 최소 1개 이상의 평가 유형 선택
- 시나리오는 'ready' 상태여야 함

## 4. 데이터 관계도

```
Aircraft ──┐
           ├──> FlightScenario ──> EvaluationRequest ──> EvaluationResult
FlightPath ┘
```