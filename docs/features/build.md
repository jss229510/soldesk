# PC 구성·호환성·부품 교체

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 담당자 |  |

## 1. 개요

사용 용도와 등급에 맞는 추천 구성을 보여주고, 선택 부품의 교체 후보와 전력 호환성을 확인합니다. 교체 후보 계산은 서버에서 수행합니다.

## 2. 화면/사용자 흐름

1. 사용자가 사무·게임·방송·AI 작업 등 용도와 세부 등급을 선택합니다.
2. 추천 견적과 해당 견적의 부품 항목을 조회합니다.
3. 사용자가 교체할 부품 카테고리를 선택합니다.
4. 현재 부품 ID·수량 목록을 서버에 보내 교체 후보를 받습니다.
5. 변경한 구성은 전력 검사 API로 검증합니다.

## 3. 관련 API

- `POST /api/build/replacements`
- `GET /api/estimates/recommended`
- `POST /api/estimates/power-check`
- `GET /api/estimates/{estimateId}/power-check`

## 4. 관련 DB 테이블/엔티티

- `ESTIMATES`
- `ESTIMATE_ITEMS`
- `PARTS`
- `PART_SPECS`

## 5. 담당 코드 위치

- `backend/src/main/java/com/comcheck/comcheck/domain/build/ReplacementCandidateController.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/build/ReplacementCandidateService.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/build/PlatformCompatibilityChecker.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/build/MinimumRequirementChecker.java`
- `frontend/src/pages/BuildPage.jsx`
- `frontend/src/api/estimates.js`
- `frontend/src/components/build/`

## 6. 주의사항 / 미완성 부분 / TODO

- `frontend/src/api/builds.js`의 `/builds/budget`, `/builds/presets` 호출은 목업 흐름입니다.
- 실제 Spring API는 `/api/estimates/recommended`와 `/api/build/replacements`를 사용합니다.
- 호환성 규칙의 지원 범위는 `PART_SPECS.spec_key` 데이터 품질에 의존합니다.
