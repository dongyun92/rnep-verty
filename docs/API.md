# RNEP API 명세서

## 기본 정보

- **Base URL**: `http://localhost:8000/api`
- **API Version**: v1
- **Content-Type**: `application/json`

## 인증

현재는 인증이 구현되지 않았으나, 향후 JWT 기반 인증이 추가될 예정입니다.

## API 엔드포인트

### 1. 비행경로 관리

#### 1.1 SHP 파일 임포트

비행경로를 SHP 파일에서 임포트합니다.

```
POST /api/flight-paths/import
```

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: SHP 파일 (필수)
  - `name`: 비행경로 이름 (선택)

**Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "강남-판교 노선",
    "total_distance": 25.3,
    "waypoint_count": 15,
    "imported_at": "2024-01-20T10:30:00Z"
}
```

#### 1.2 비행경로 목록 조회

```
GET /api/flight-paths
```

**Query Parameters:**
- `page`: 페이지 번호 (기본값: 1)
- `size`: 페이지 크기 (기본값: 20)
- `search`: 검색어

**Response:**
```json
{
    "items": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "강남-판교 노선",
            "total_distance": 25.3,
            "waypoint_count": 15,
            "imported_at": "2024-01-20T10:30:00Z"
        }
    ],
    "total": 50,
    "page": 1,
    "size": 20
}
```

#### 1.3 비행경로 상세 조회

```
GET /api/flight-paths/{id}
```

**Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "강남-판교 노선",
    "source_file": "gangnam_pangyo_route.shp",
    "geometry": {
        "type": "LineString",
        "coordinates": [[127.0276, 37.4979], [127.1111, 37.3899]]
    },
    "waypoints": [
        {
            "id": "WP001",
            "sequence": 1,
            "position": {
                "lat": 37.4979,
                "lon": 127.0276,
                "alt": 150
            },
            "distance_from_previous": 0
        }
    ],
    "total_distance": 25.3,
    "imported_at": "2024-01-20T10:30:00Z"
}
```

### 2. 시나리오 관리

#### 2.1 시나리오 생성

```
POST /api/scenarios
```

**Request Body:**
```json
{
    "name": "강남-판교 오전 운항",
    "description": "평일 오전 출근 시간대 운항",
    "flight_date": "2024-02-01",
    "departure_time": "08:30:00",
    "aircraft_type": "JOBY_S4",
    "flight_path_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "강남-판교 오전 운항",
    "status": "draft",
    "waypoints_with_eta": [
        {
            "waypoint_id": "WP001",
            "position": {"lat": 37.4979, "lon": 127.0276, "alt": 150},
            "estimated_arrival_time": "2024-02-01T08:30:00Z",
            "speed": 0
        },
        {
            "waypoint_id": "WP002",
            "position": {"lat": 37.4879, "lon": 127.0376, "alt": 300},
            "estimated_arrival_time": "2024-02-01T08:32:15Z",
            "speed": 120
        }
    ],
    "created_at": "2024-01-20T10:35:00Z"
}
```

#### 2.2 시나리오 목록 조회

```
GET /api/scenarios
```

**Query Parameters:**
- `page`: 페이지 번호
- `size`: 페이지 크기
- `status`: 상태 필터 (draft, ready, evaluating, completed)
- `flight_date_from`: 비행날짜 시작
- `flight_date_to`: 비행날짜 종료

#### 2.3 시나리오 수정

```
PUT /api/scenarios/{id}
```

**Request Body:**
```json
{
    "name": "수정된 시나리오 이름",
    "departure_time": "09:00:00"
}
```

#### 2.4 시나리오 삭제

```
DELETE /api/scenarios/{id}
```

### 3. 평가 실행

#### 3.1 평가 요청

```
POST /api/evaluations
```

**Request Body:**
```json
{
    "scenario_id": "660e8400-e29b-41d4-a716-446655440001",
    "evaluation_types": ["ground_risk", "air_risk", "noise"]
}
```

**Response:**
```json
{
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "scenario_id": "660e8400-e29b-41d4-a716-446655440001",
    "status": "processing",
    "progress": 0,
    "requested_at": "2024-01-20T10:40:00Z"
}
```

#### 3.2 평가 상태 조회

```
GET /api/evaluations/{id}
```

**Response:**
```json
{
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "scenario_id": "660e8400-e29b-41d4-a716-446655440001",
    "status": "completed",
    "progress": 100,
    "results": {
        "ground_risk": {
            "result_id": "880e8400-e29b-41d4-a716-446655440003",
            "file_path": "/outputs/ground_risk_880e8400.shp",
            "completed_at": "2024-01-20T10:45:00Z"
        },
        "air_risk": {
            "result_id": "990e8400-e29b-41d4-a716-446655440004",
            "file_path": "/outputs/air_risk_990e8400.shp",
            "completed_at": "2024-01-20T10:46:00Z"
        },
        "noise": {
            "result_id": "aa0e8400-e29b-41d4-a716-446655440005",
            "file_path": "/outputs/noise_contours_aa0e8400.shp",
            "completed_at": "2024-01-20T10:47:00Z"
        }
    }
}
```

#### 3.3 평가 결과 다운로드

```
GET /api/evaluations/{id}/results/{type}
```

**Parameters:**
- `id`: 평가 요청 ID
- `type`: 평가 유형 (ground_risk, air_risk, noise)

**Response:**
- Content-Type: `application/zip`
- 평가 결과 파일들이 압축된 ZIP 파일

### 4. 기체 정보

#### 4.1 기체 목록 조회

```
GET /api/aircraft
```

**Response:**
```json
{
    "items": [
        {
            "id": "JOBY_S4",
            "name": "Joby S4",
            "manufacturer": "Joby Aviation",
            "cruise_speed": 200,
            "max_speed": 322,
            "range": 241
        }
    ]
}
```

#### 4.2 기체 상세 조회

```
GET /api/aircraft/{id}
```

**Response:**
```json
{
    "id": "JOBY_S4",
    "name": "Joby S4",
    "manufacturer": "Joby Aviation",
    "cruise_speed": 200,
    "max_speed": 322,
    "climb_rate": 500,
    "descent_rate": 300,
    "max_altitude": 3000,
    "range": 241,
    "noise_profile": {
        "takeoff": 65,
        "cruise": 55,
        "landing": 62
    },
    "risk_parameters": {
        "mtow": 2177,
        "rotor_diameter": 10,
        "failure_rate": 0.00001
    }
}
```

## 에러 응답

모든 에러는 다음 형식으로 반환됩니다:

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "요청 데이터가 올바르지 않습니다.",
        "details": {
            "field": "departure_time",
            "reason": "시간 형식이 올바르지 않습니다."
        }
    }
}
```

### 에러 코드

- `VALIDATION_ERROR`: 입력 데이터 검증 실패
- `NOT_FOUND`: 리소스를 찾을 수 없음
- `CONFLICT`: 리소스 충돌
- `INTERNAL_ERROR`: 서버 내부 오류

## 상태 코드

- `200 OK`: 성공
- `201 Created`: 리소스 생성 성공
- `400 Bad Request`: 잘못된 요청
- `404 Not Found`: 리소스 없음
- `409 Conflict`: 충돌
- `500 Internal Server Error`: 서버 오류