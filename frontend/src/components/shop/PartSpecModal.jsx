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
    cpu_clock: '최대 클럭',
    cpu_L2: 'L2 캐시',
    cpu_L3: 'L3 캐시',
    DDR: '메모리 규격',
};

const formatSpecKey = (specKey) => (
    SPEC_LABELS[specKey] ?? specKey.replaceAll('_', ' ')
);

/** 선택한 부품의 실제 DB 스펙을 보여 주는 모달 */
export const PartSpecModal = ({ part, open, onClose }) => {
  // 모달이 열렸고 부품이 선택된 경우에만 스펙 API를 요청한다.
    const { specs, loading, error } = usePartSpecs(open ? part?.id : null);

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
            {!loading && !error && specs.length > 0 && (
            <div className="flex flex-wrap gap-2">
                {specs.slice(0, 3).map((spec) => (
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

            {!loading && !error && specs.length === 0 && (
            <StateBox status="empty" title="등록된 상세 스펙이 없습니다" />
            )}

            {!loading && !error && specs.length > 0 && (
            <dl className="divide-y divide-gray-700 overflow-hidden rounded-lg border border-gray-700 bg-gray-800">
                {specs.map((spec) => (
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
