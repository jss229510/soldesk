/**
 * 견적의 호환성을 검사한다. 화면에 "모든 부품이 호환됩니다" 배너로 노출.
 * 규칙은 mock 수준이지만 실제 API 응답이 들어와도 형태는 그대로 쓸 수 있다.
 */

const need = (items, category) => items.find((i) => i.category === category)?.part;

export const checkCompatibility = (items = []) => {
  const issues = [];
  const cpu = need(items, 'cpu');
  const board = need(items, 'mainboard');
  const ram = need(items, 'ram');
  const gpu = need(items, 'gpu');
  const psu = need(items, 'psu');
  const cooler = need(items, 'cooler');
  const pcCase = need(items, 'case');

  if (cpu && board && cpu.attrs.socket !== board.attrs.socket) {
    issues.push({
      level: 'error',
      message: `CPU 소켓(${cpu.attrs.socket})과 메인보드 소켓(${board.attrs.socket})이 다릅니다.`,
    });
  }

  if (ram && board && ram.attrs.memoryType !== board.attrs.memoryType) {
    issues.push({
      level: 'error',
      message: `메인보드는 ${board.attrs.memoryType}만 지원합니다. 램을 교체하세요.`,
    });
  }

  if (cooler && cpu && cooler.attrs.maxTdp < cpu.attrs.tdp) {
    issues.push({
      level: 'warn',
      message: `쿨러 허용 발열(${cooler.attrs.maxTdp}W)이 CPU TDP(${cpu.attrs.tdp}W)보다 낮습니다.`,
    });
  }

  if (cooler && cpu && !cooler.attrs.sockets?.includes(cpu.attrs.socket)) {
    issues.push({
      level: 'error',
      message: `쿨러가 ${cpu.attrs.socket} 소켓을 지원하지 않습니다.`,
    });
  }

  const draw = (cpu?.attrs.tdp ?? 0) + (gpu?.attrs.tdp ?? 0) + 150;
  if (psu && draw > psu.attrs.watt * 0.85) {
    issues.push({
      level: 'warn',
      message: `예상 소비전력 ${draw}W 기준으로 ${psu.attrs.watt}W 파워는 여유가 부족합니다.`,
    });
  }

  if (pcCase && board && !pcCase.attrs.formFactors?.includes(board.attrs.formFactor)) {
    issues.push({
      level: 'error',
      message: `케이스가 ${board.attrs.formFactor} 보드를 수용하지 못합니다.`,
    });
  }

  if (pcCase && gpu && gpu.attrs.length > pcCase.attrs.maxGpuLength) {
    issues.push({
      level: 'error',
      message: `그래픽카드 길이 ${gpu.attrs.length}mm 가 케이스 한계(${pcCase.attrs.maxGpuLength}mm)를 넘습니다.`,
    });
  }

  return {
    ok: issues.length === 0,
    hasError: issues.some((i) => i.level === 'error'),
    issues,
    estimatedWatt: draw,
  };
};
