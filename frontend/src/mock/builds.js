import { PARTS_BY_ID } from './parts';

/** 예산 구간별 추천 구성. key 는 예산 상한(원). */
const BUDGET_RECIPES = {
  600000: ['cpu-ryzen5-5600', 'mb-asrock-b550m-pro4', 'ram-kingston-fury-ddr4', 'ssd-hynix-p41-1tb', 'psu-seasonic-gx650', 'cooler-thermalright-pa', 'case-bequiet-pb500dx'],
  1000000: ['cpu-ryzen5-5600', 'gpu-rx7800xt-sapphire', 'mb-asrock-b550m-pro4', 'ram-kingston-fury-ddr4', 'ssd-hynix-p41-1tb', 'psu-seasonic-gx650', 'cooler-thermalright-pa', 'case-bequiet-pb500dx'],
  1500000: ['cpu-ryzen5-5600', 'gpu-rx7800xt-sapphire', 'mb-asrock-b550m-pro4', 'ram-kingston-fury-ddr4', 'ssd-hynix-p41-1tb', 'psu-seasonic-gx650', 'cooler-thermalright-pa', 'case-bequiet-pb500dx'],
  2000000: ['cpu-ryzen7-7800x3d', 'gpu-rtx4070tis-msi', 'mb-gigabyte-b650-aorus', 'ram-crucial-pro-ddr5', 'ssd-wd-sn850x-1tb', 'psu-seasonic-gx650', 'cooler-thermalright-pa', 'case-bequiet-pb500dx'],
  3000000: ['cpu-ryzen7-7800x3d', 'gpu-rtx5080-gigabyte', 'mb-gigabyte-b650-aorus', 'ram-gskill-z5-ddr5', 'ssd-samsung-990pro-2tb', 'psu-bequiet-dp13-850', 'cooler-nzxt-kraken-360', 'case-lianli-o11-evo'],
  5000000: ['cpu-ryzen9-9950x', 'gpu-rtx5090-rog', 'mb-gigabyte-b650-aorus', 'ram-gskill-z5-ddr5', 'ssd-samsung-990pro-2tb', 'psu-corsair-hx1500i', 'cooler-nzxt-kraken-360', 'case-lianli-o11-evo'],
};

/** 용도별 추천 구성. */
const USAGE_RECIPES = {
  'highend-gaming': BUDGET_RECIPES[5000000],
  'mid-gaming': BUDGET_RECIPES[2000000],
  creator: BUDGET_RECIPES[3000000],
  office: BUDGET_RECIPES[1500000],
  streaming: ['cpu-i9-14900ks', 'gpu-rtx4070tis-msi', 'mb-msi-z790-tomahawk', 'ram-gskill-z5-ddr5', 'ssd-samsung-990pro-2tb', 'psu-bequiet-dp13-850', 'cooler-nzxt-kraken-360', 'case-fractal-torrent'],
};

const toItems = (ids) =>
  ids.map((id) => PARTS_BY_ID[id]).filter(Boolean).map((part) => ({ category: part.category, part }));

/** 예산에 가장 가까운(초과하지 않는) 레시피를 고른다. */
export const buildForBudget = (budget) => {
  const tiers = Object.keys(BUDGET_RECIPES)
    .map(Number)
    .sort((a, b) => a - b);
  const tier = tiers.filter((t) => t <= budget).pop() ?? tiers[0];
  return toItems(BUDGET_RECIPES[tier]);
};

export const buildForUsage = (usageId) => toItems(USAGE_RECIPES[usageId] ?? USAGE_RECIPES.office);
