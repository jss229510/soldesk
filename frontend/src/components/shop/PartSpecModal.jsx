import { Button, Chip, Modal, StateBox, Thumbnail } from '../common';
import { usePartSpecs } from '../../hooks/usePartSpecs';
import { formatPrice } from '../../utils/format';

// DB의 cpu_brand 같은 스펙 키를 화면에서 읽기 쉽게 표시한다.
const SPEC_LABELS = {
    cpu_brand: '제조사',
    cpu_socket: '소켓',
    tdp_watt: '소비 전력 (TDP)',
    cpu_core: '코어 수',
    thread: '스레드 수',
    cpu_thread: '스레드 수',
    cpu_clock: '최대 클럭',
    cpu_clock_boost: '부스트 클럭',
    cpu_L2: 'L2 캐시',
    cpu_L3: 'L3 캐시',
    DDR: '메모리 규격',
    ddr_support: '지원 메모리 규격',
    integrated_graphics: '내장 그래픽',
    chipset: '칩셋',
    length_mm: '길이',
    performance_tier: '성능 등급',
    recommended_psu_watt: '권장 파워 용량',
    vram_gb: '그래픽 메모리 용량',
    vram_type: '그래픽 메모리 규격',
    form_factor: '폼팩터',
    m2_slots: 'M.2 슬롯 수',
    max_ram_capacity_gb: '최대 메모리 용량',
    nvme_supported: 'NVMe 지원',
    ram_socket: '메모리 슬롯',
    ram_type: '메모리 규격',
    atx_version: 'ATX 버전',
    efficiency_rating: '에너지 효율 등급',
    fan_size: '팬 크기',
    modular_type: '모듈러 방식',
    pcie_connector: 'PCIe 보조전원 커넥터',
    wattage: '정격 출력',
    capacity_gb: '용량',
    module_count: '모듈 수',
    speed_mhz: '동작 속도',
    interface: '인터페이스',
    nand_type: 'NAND 종류',
    read_speed_mbs: '순차 읽기 속도',
    storage_gb: '저장 용량',
    tbw: 'TBW',
    write_speed_mbs: '순차 쓰기 속도',
};

// 추천 알고리즘이 사용하는 내부 판정값은 상세 화면에 노출하지 않는다.
const HIDDEN_SPEC_KEYS = new Set(['has_igpu', 'cpu_level']);

const formatSpecKey = (specKey) => (
    SPEC_LABELS[specKey] ?? specKey.replaceAll('_', ' ')
);

/** 선택한 부품의 실제 DB 스펙을 보여 주는 모달 */
export const PartSpecModal = ({ part, open, onClose }) => {
  // 모달이 열렸고 부품이 선택된 경우에만 스펙 API를 요청한다.
    const { specs, loading, error } = usePartSpecs(open ? part?.id : null);
    const displaySpecs = specs.filter((spec) => !HIDDEN_SPEC_KEYS.has(spec.specKey));

  // 선택한 부품이 없으면 모달 자체를 만들지 않는다.
    if (!part) return null;

    return (
    <Modal open={open} onClose={onClose} labelledBy="part-spec-title">
        <div className="grid grid-cols-1 lg:min-h-[31rem] lg:grid-cols-2">
        {/* 기존 시세 모달의 왼쪽 상품 정보 영역을 실제 Part API 데이터로 재사용한다. */}
          <div className="flex flex-col justify-center gap-4 border-b border-gray-700 p-7 lg:border-b-0 lg:border-r">
            <Thumbnail
              part={part}
              className="h-52 !aspect-auto"
              imageClassName="object-contain"
            />

            <div>
            <p className="font-mono text-xs text-cyan-400">{part.brand}</p>
            <h2 id="part-spec-title" className="text-lg font-bold">
                {part.name}
            </h2>
            </div>

          {/* 핵심 스펙 세 개는 기존 목업 화면처럼 Chip으로 빠르게 보여 준다. */}
            {!loading && !error && displaySpecs.length > 0 && (
            <div className="flex flex-wrap gap-2">
                {displaySpecs.slice(0, 3).map((spec) => (
                <Chip key={spec.specId}>
                    {spec.specValue}{spec.specUnit ? ` ${spec.specUnit}` : ''}
                </Chip>
                ))}
            </div>
            )}

            <strong className="text-2xl font-extrabold">
            {formatPrice(part.price)}
            </strong>

            <Button
            variant="outline"
            block
            style={{ border: '1px solid var(--line-strong)' }}
            onClick={onClose}
            >
            닫기
            </Button>
        </div>

        {/* 가격 이력 대신, 현재 완성된 PartSpec API의 전체 스펙을 표시한다. */}
        <div className="p-7 lg:p-8">
            <p className="font-mono text-sm text-gray-500">상세 스펙</p>
            <h3 className="mb-4 mt-1 text-xl font-bold">제품 사양</h3>

            {loading && (
            <StateBox status="loading" title="상세 스펙을 불러오는 중입니다" />
            )}

            {error && (
            <StateBox
                status="error"
                title="상세 스펙을 불러오지 못했습니다"
                description="잠시 후 다시 시도해 주세요."
            />
            )}

            {!loading && !error && displaySpecs.length === 0 && (
            <StateBox status="empty" title="등록된 상세 스펙이 없습니다" />
            )}

            {!loading && !error && displaySpecs.length > 0 && (
            <dl className="divide-y divide-gray-700 overflow-hidden rounded-lg border border-gray-700 bg-gray-800">
                {displaySpecs.map((spec) => (
                <div
                    key={spec.specId}
                    className="grid grid-cols-2 gap-4 px-5 py-3"
                >
                    <dt className="font-mono text-sm text-gray-400">
                    {formatSpecKey(spec.specKey)}
                    </dt>
                    <dd className="text-right font-semibold">
                    {spec.specValue}
                    {spec.specUnit ? ` ${spec.specUnit}` : ''}
                    </dd>
                </div>
                ))}
            </dl>
            )}
        </div>
        </div>
    </Modal>
    );
};

export default PartSpecModal;
