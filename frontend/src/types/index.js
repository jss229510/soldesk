/**
 * JSX 프로젝트라 타입은 JSDoc typedef 로 관리한다.
 * 에디터에서 자동완성이 동작하고, 나중에 TS 로 옮길 때 그대로 옮겨 쓸 수 있다.
 *
 * @typedef {'cpu'|'gpu'|'psu'|'ram'|'ssd'|'mainboard'|'cooler'|'case'} CategoryId
 *
 * @typedef {Object} Category
 * @property {CategoryId} id
 * @property {string} label     상단 탭에 노출되는 짧은 이름
 * @property {string} title     카테고리 페이지 큰 제목
 * @property {string} icon
 * @property {string} accent    CSS 변수 문자열
 * @property {string[]} keywords
 *
 * @typedef {Object} Part
 * @property {string} id
 * @property {CategoryId} category
 * @property {string} brand
 * @property {string} name
 * @property {string[]} specs          카드에 칩으로 노출되는 스펙 3개 내외
 * @property {number} rating           0~5
 * @property {number} reviewCount
 * @property {number} price            현재가(원)
 * @property {number|null} listPrice   정가(원). 없으면 할인 표기 생략
 * @property {number} stock
 * @property {number} trendRate        최근 12개월 변동률(%) — 음수면 하락
 * @property {'베스트'|'특가'|'신제품'|'가성비'|null} badge
 * @property {number} popularity       인기순 정렬 기준
 * @property {string} releasedAt       ISO date, 최신순 정렬 기준
 * @property {Object} attrs            호환성 판정에 쓰는 속성 (socket, memory, tdp 등)
 * @property {string|null} image
 *
 * @typedef {Object} PricePoint
 * @property {string} month   'YYYY-MM'
 * @property {number} price
 *
 * @typedef {Object} PriceHistory
 * @property {string} partId
 * @property {PricePoint[]} points
 * @property {number} yearAgoPrice
 * @property {number} lowestPrice
 * @property {number} changeRate
 * @property {number} changeAmount
 *
 * @typedef {Object} BuildItem
 * @property {CategoryId} category
 * @property {Part} part
 *
 * @typedef {Object} Build
 * @property {BuildItem[]} items
 * @property {number} total
 * @property {number} budget
 */
export {};
