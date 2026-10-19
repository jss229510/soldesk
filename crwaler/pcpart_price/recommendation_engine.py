"""정제된 6개 부품 후보에서 용도별 조건과 호환성을 판정하는 순수 로직."""
from recommendation_profiles import USE_CASE_RULES


GPU_PSU_FALLBACK_WATT = {'보급': 500, '중급': 650, '고급': 750, '최상급': 850}


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def spec_map(spec_rows):
    """한 부품의 PART_SPECS 행을 {spec_key: spec_value}로 바꾼다."""
    return {row['spec_key']: row['spec_value'] for row in spec_rows}


def supports_ddr(ram_type, board_ram_type):
    ram_types = {item.strip().upper() for item in str(ram_type or '').split(',')}
    board_types = {item.strip().upper() for item in str(board_ram_type or '').split(',')}
    return bool(ram_types & board_types)


def required_psu_watt(gpu_specs, rule):
    recommended = number(gpu_specs.get('recommended_psu_watt'))
    if recommended is not None:
        return max(recommended, rule['psu_min_watt'])
    return max(GPU_PSU_FALLBACK_WATT.get(gpu_specs.get('performance_tier'), 0), rule['psu_min_watt'])


def compatible_bundle(use_case, cpu, ram, mainboard, ssd, psu, gpu=None):
    """부품별 spec map을 받아 추천 가능 여부와 실패 사유를 반환한다."""
    rule = USE_CASE_RULES[use_case]
    reasons = []

    if number(cpu.get('cpu_core')) is None or number(cpu['cpu_core']) < rule['cpu_min_cores']:
        reasons.append('CPU 코어 수 부족')
    if rule.get('cpu_min_threads') and (number(cpu.get('thread')) is None or number(cpu['thread']) < rule['cpu_min_threads']):
        reasons.append('CPU 스레드 수 부족')
    if cpu.get('cpu_socket') != mainboard.get('cpu_socket'):
        reasons.append('CPU-메인보드 소켓 불일치')
    if not supports_ddr(ram.get('ram_type'), mainboard.get('ram_type')):
        reasons.append('RAM-메인보드 DDR 불일치')
    if number(ram.get('capacity_gb')) is None or number(ram['capacity_gb']) < rule['ram_min_gb']:
        reasons.append('RAM 용량 부족')
    if number(ssd.get('storage_gb')) is None or number(ssd['storage_gb']) < rule['ssd_min_gb']:
        reasons.append('SSD 용량 부족')
    if number(mainboard.get('m2_slots')) is None or number(mainboard['m2_slots']) < rule['mainboard_min_m2_slots']:
        reasons.append('메인보드 M.2 슬롯 부족')
    if rule.get('mainboard_min_ram_slots') and (number(mainboard.get('ram_socket')) is None or number(mainboard['ram_socket']) < rule['mainboard_min_ram_slots']):
        reasons.append('메인보드 RAM 슬롯 부족')

    if rule['requires_discrete_gpu'] and gpu is None:
        reasons.append('외장 GPU 필요')
    if gpu is not None:
        allowed_tiers = rule.get('allowed_gpu_tiers')
        if allowed_tiers and gpu.get('performance_tier') not in allowed_tiers:
            reasons.append('GPU 성능 등급 부족')
        required_watt = required_psu_watt(gpu, rule)
    else:
        required_watt = rule['psu_min_watt']
    if number(psu.get('wattage')) is None or number(psu['wattage']) < required_watt:
        reasons.append('PSU 정격출력 부족')

    return {'compatible': not reasons, 'reasons': reasons, 'required_psu_watt': required_watt}
