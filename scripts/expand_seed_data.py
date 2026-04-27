import argparse
from pathlib import Path

from minigeo.benchmark import load_benchmark
from minigeo.jsonl import write_jsonl
from minigeo.rag.corpus import load_corpus

BENCH_PATH = Path("data/benchmark/minigeo_bench.jsonl")
CORPUS_PATH = Path("data/processed/rag_corpus.jsonl")
SOURCE_PATH = Path("data/processed/source_manifest.jsonl")

SOURCE_MANIFEST = [
    {
        "source_id": "src_pubchem_quartz",
        "name": "PubChem Quartz",
        "url": "https://pubchem.ncbi.nlm.nih.gov/compound/Quartz",
        "use": "Mineral occurrence, silica/quartz metadata, and source traceability.",
        "license_note": "Use as source metadata; do not redistribute scraped page text.",
    },
    {
        "source_id": "src_pubchem_feldspar",
        "name": "PubChem Feldspar",
        "url": "https://pubchem.ncbi.nlm.nih.gov/compound/Feldspar",
        "use": "Feldspar group and aluminum silicate metadata.",
        "license_note": "Use as source metadata; do not redistribute scraped page text.",
    },
    {
        "source_id": "src_pubchem_calcite",
        "name": "PubChem Calcite",
        "url": "https://pubchem.ncbi.nlm.nih.gov/compound/Calcite",
        "use": "Calcite mineral formula and Raman reference metadata.",
        "license_note": "Use as source metadata; do not redistribute scraped page text.",
    },
    {
        "source_id": "src_pubchem_hematite",
        "name": "PubChem Hematite",
        "url": "https://pubchem.ncbi.nlm.nih.gov/compound/Hematite-_Fe2O3",
        "use": "Hematite iron oxide formula metadata.",
        "license_note": "Use as source metadata; do not redistribute scraped page text.",
    },
    {
        "source_id": "src_ntrs_feldspar_raman",
        "name": "NASA NTRS feldspar Raman characterization",
        "url": "https://ntrs.nasa.gov/citations/20030111413",
        "use": "Feldspar Raman spectroscopy and planetary exploration context.",
        "license_note": "Use as bibliographic/source metadata.",
    },
    {
        "source_id": "src_pmc_quartz_raman",
        "name": "PMC quartz Raman orientation study",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4770934/",
        "use": "Quartz Raman mode around 461 cm-1 and spectroscopy context.",
        "license_note": "Use as open-access source metadata with citation.",
    },
    {
        "source_id": "src_pubchem_dolomite",
        "name": "PubChem Dolomite",
        "url": "https://pubchem.ncbi.nlm.nih.gov/compound/Dolomite",
        "use": "Dolomite carbonate mineral formula metadata.",
        "license_note": "Use as source metadata; do not redistribute scraped page text.",
    },
    {
        "source_id": "src_pubchem_anorthite",
        "name": "PubChem Anorthite",
        "url": "https://pubchem.ncbi.nlm.nih.gov/compound/Anorthite",
        "use": "Anorthite feldspar composition metadata.",
        "license_note": "Use as source metadata; do not redistribute scraped page text.",
    },
]

EXTRA_CORPUS = [
    ("doc_dolomite#chunk_001", "doc_dolomite", "白云石是钙镁碳酸盐矿物，常用化学式为 CaMg(CO3)2。", "PubChem Dolomite", "https://pubchem.ncbi.nlm.nih.gov/compound/Dolomite", "concept", "dolomite"),
    ("doc_dolomite#chunk_002", "doc_dolomite", "白云石与方解石同属碳酸盐体系，但含有镁，反应和谱学解释需要区分。", "MiniGeo curated mineral notes", "https://example.org/minigeo/dolomite", "mineral_property", "dolomite"),
    ("doc_gypsum#chunk_001", "doc_gypsum", "石膏是含水硫酸盐矿物，常用化学式为 CaSO4·2H2O。", "MiniGeo curated mineral notes", "https://example.org/minigeo/gypsum", "concept", "gypsum"),
    ("doc_gypsum#chunk_002", "doc_gypsum", "石膏硬度较低，不能仅凭浅色外观与方解石或石英区分。", "MiniGeo curated mineral notes", "https://example.org/minigeo/gypsum-property", "mineral_property", "gypsum"),
    ("doc_magnetite#chunk_001", "doc_magnetite", "磁铁矿是铁氧化物矿物，常用化学式为 Fe3O4。", "MiniGeo curated mineral notes", "https://example.org/minigeo/magnetite", "concept", "magnetite"),
    ("doc_magnetite#chunk_002", "doc_magnetite", "磁性可以辅助区分磁铁矿和赤铁矿，但最终结论仍应结合结构或光谱证据。", "MiniGeo curated mineral notes", "https://example.org/minigeo/magnetite-property", "mineral_property", "magnetite"),
    ("doc_pyrite#chunk_001", "doc_pyrite", "黄铁矿是硫化物矿物，常用化学式为 FeS2。", "MiniGeo curated mineral notes", "https://example.org/minigeo/pyrite", "concept", "pyrite"),
    ("doc_pyrite#chunk_002", "doc_pyrite", "黄铁矿的金属光泽不能单独证明其为金或氧化物，需要结合硬度、条痕和成分证据。", "MiniGeo curated mineral notes", "https://example.org/minigeo/pyrite-property", "mineral_property", "pyrite"),
    ("doc_olivine#chunk_001", "doc_olivine", "橄榄石是一类镁铁硅酸盐矿物，常见于基性和超基性岩。", "MiniGeo curated mineral notes", "https://example.org/minigeo/olivine", "concept", "olivine"),
    ("doc_olivine#chunk_002", "doc_olivine", "橄榄石与辉石都可出现在镁铁质岩石中，分类时需要结合晶体结构和谱学证据。", "MiniGeo curated mineral notes", "https://example.org/minigeo/olivine-property", "mineral_property", "olivine"),
    ("doc_muscovite#chunk_001", "doc_muscovite", "白云母是层状硅酸盐矿物，常具有片状解理。", "MiniGeo curated mineral notes", "https://example.org/minigeo/muscovite", "concept", "muscovite"),
    ("doc_muscovite#chunk_002", "doc_muscovite", "片状解理可以辅助识别白云母，但可信回答仍需要证据来源。", "MiniGeo curated mineral notes", "https://example.org/minigeo/muscovite-property", "mineral_property", "muscovite"),
    ("doc_kaolinite#chunk_001", "doc_kaolinite", "高岭石是黏土矿物，属于层状硅酸盐体系。", "MiniGeo curated mineral notes", "https://example.org/minigeo/kaolinite", "concept", "kaolinite"),
    ("doc_kaolinite#chunk_002", "doc_kaolinite", "高岭石和白云母都属于层状硅酸盐相关体系，但粒度、结构和应用场景不同。", "MiniGeo curated mineral notes", "https://example.org/minigeo/kaolinite-property", "mineral_property", "kaolinite"),
    ("doc_anorthite#chunk_001", "doc_anorthite", "钙长石是斜长石端元之一，化学组成可表示为 CaAl2Si2O8。", "PubChem Anorthite", "https://pubchem.ncbi.nlm.nih.gov/compound/Anorthite", "concept", "anorthite"),
    ("doc_anorthite#chunk_002", "doc_anorthite", "钙长石属于长石族，回答时应避免把它误归为碳酸盐矿物。", "MiniGeo curated mineral notes", "https://example.org/minigeo/anorthite-property", "mineral_property", "anorthite"),
    ("doc_spectroscopy#chunk_004", "doc_spectroscopy", "Raman 光谱适合识别矿物相，但峰位可能受晶向、压力、温度和仪器设置影响。", "PMC quartz Raman orientation study", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4770934/", "spectroscopy", ""),
    ("doc_spectroscopy#chunk_005", "doc_spectroscopy", "行星探测中的 Raman 系统可用于识别矿物及其不同组成，尤其适合现场矿物表征。", "NASA NTRS feldspar Raman characterization", "https://ntrs.nasa.gov/citations/20030111413", "spectroscopy", ""),
    ("doc_system#chunk_011", "doc_system", "SQL 题需要记录预期查询意图和预期结果条件，而不是只保存自然语言答案。", "MiniGeo system design notes", "https://example.org/minigeo/sql-eval", "system", ""),
    ("doc_system#chunk_012", "doc_system", "扩展 benchmark 时应保持题型分布，避免只增加容易的概念题。", "MiniGeo system design notes", "https://example.org/minigeo/benchmark-balance", "system", ""),
]

MINERAL_FACTS = [
    {"name": "quartz", "zh": "石英", "class": "硅酸盐", "formula": "SiO2", "evidence": ["doc_quartz#chunk_001"], "spectra": ["doc_quartz#chunk_002"]},
    {"name": "feldspar", "zh": "长石", "class": "铝硅酸盐框架", "formula": "含 K、Na 或 Ca 的铝硅酸盐", "evidence": ["doc_feldspar#chunk_001"], "spectra": ["doc_feldspar#chunk_002"]},
    {"name": "calcite", "zh": "方解石", "class": "碳酸盐", "formula": "CaCO3", "evidence": ["doc_calcite#chunk_001"], "spectra": ["doc_calcite#chunk_002"]},
    {"name": "hematite", "zh": "赤铁矿", "class": "铁氧化物", "formula": "Fe2O3", "evidence": ["doc_hematite#chunk_001"], "spectra": ["doc_hematite#chunk_002"]},
    {"name": "dolomite", "zh": "白云石", "class": "碳酸盐", "formula": "CaMg(CO3)2", "evidence": ["doc_dolomite#chunk_001"], "spectra": ["doc_dolomite#chunk_002"]},
    {"name": "gypsum", "zh": "石膏", "class": "含水硫酸盐", "formula": "CaSO4·2H2O", "evidence": ["doc_gypsum#chunk_001"], "spectra": ["doc_gypsum#chunk_002"]},
    {"name": "magnetite", "zh": "磁铁矿", "class": "铁氧化物", "formula": "Fe3O4", "evidence": ["doc_magnetite#chunk_001"], "spectra": ["doc_magnetite#chunk_002"]},
    {"name": "pyrite", "zh": "黄铁矿", "class": "硫化物", "formula": "FeS2", "evidence": ["doc_pyrite#chunk_001"], "spectra": ["doc_pyrite#chunk_002"]},
    {"name": "olivine", "zh": "橄榄石", "class": "镁铁硅酸盐", "formula": "镁铁硅酸盐", "evidence": ["doc_olivine#chunk_001"], "spectra": ["doc_olivine#chunk_002"]},
    {"name": "muscovite", "zh": "白云母", "class": "层状硅酸盐", "formula": "含钾铝的层状硅酸盐", "evidence": ["doc_muscovite#chunk_001"], "spectra": ["doc_muscovite#chunk_002"]},
    {"name": "kaolinite", "zh": "高岭石", "class": "层状硅酸盐", "formula": "铝硅酸盐黏土矿物", "evidence": ["doc_kaolinite#chunk_001"], "spectra": ["doc_kaolinite#chunk_002"]},
    {"name": "anorthite", "zh": "钙长石", "class": "长石族硅酸盐", "formula": "CaAl2Si2O8", "evidence": ["doc_anorthite#chunk_001"], "spectra": ["doc_anorthite#chunk_002"]},
]


def item(idx: int, question: str, answer: str, type_: str, evidence: list[str], difficulty: str = "easy", answerable: bool = True, requires_sql: bool = False, expected_sql_intent=None, expected_result=None) -> dict:
    return {
        "id": f"minigeo_{idx:03d}",
        "question": question,
        "answer": answer,
        "type": type_,
        "difficulty": difficulty,
        "answerable": answerable,
        "requires_sql": requires_sql,
        "evidence": evidence,
        "expected_sql_intent": expected_sql_intent,
        "expected_result": expected_result,
    }


def make_extra_items(start: int, count: int = 200) -> list[dict]:
    rows: list[dict] = []
    idx = start

    for fact in MINERAL_FACTS:
        rows.append(item(idx, f"{fact['zh']}属于哪类矿物？", f"{fact['zh']}属于{fact['class']}矿物。", "concept", fact["evidence"])); idx += 1
        rows.append(item(idx, f"{fact['zh']}的常用组成或化学式是什么？", f"{fact['zh']}的常用组成或化学式是 {fact['formula']}。", "mineral_property", fact["evidence"])); idx += 1
        rows.append(item(idx, f"识别{fact['zh']}时为什么需要证据来源？", f"因为 MiniGeo 需要用可追踪证据支持关于{fact['zh']}的结论。", "evidence", fact["evidence"], "medium")); idx += 1

    for fact in MINERAL_FACTS:
        rows.append(item(idx, f"如果问题声称{fact['zh']}是碳酸盐矿物，但证据显示其属于{fact['class']}，系统应如何回答？", f"系统应指出前提可能错误，并依据证据说明{fact['zh']}属于{fact['class']}矿物。", "false_premise", fact["evidence"], "medium")); idx += 1

    missing_samples = ["PX-101", "MOON-204", "MICA-777", "DIAMOND-404", "MARS-CLAY-9", "OLV-UNKNOWN", "SPECTRA-X0", "QHD-999"]
    for sample_id in missing_samples:
        rows.append(item(idx, f"当前资料库能否确定样本 {sample_id} 的矿物类别？", f"不能。当前资料库没有样本 {sample_id} 的充分证据，系统应说明证据不足。", "unanswerable", [], "medium", False)); idx += 1

    sql_prompts = [
        ("查询 Qinhuangdao 地区每种预测矿物的错误次数。", "按地区过滤样本并按 predicted_mineral 聚合错误预测。", {"group_by": "predicted_mineral"}),
        ("找出每个地区的错误样本数量。", "连接 samples 和 predictions，按 region 统计 is_correct=0 的记录。", {"group_by": "region"}),
        ("列出 Qinhuangdao 中所有预测错误的 sample_id。", "连接 samples 和 predictions 并筛选 region 与 is_correct。", {"fields": ["sample_id"]}),
        ("查询每个真实矿物被误判成什么矿物。", "按 true_mineral 和 predicted_mineral 聚合错误预测。", {"group_by": ["true_mineral", "predicted_mineral"]}),
        ("统计 spectra 表中每个样本的峰位数量。", "按 sample_id 聚合 spectra 记录。", {"table": "spectra"}),
        ("查询具有 460 到 470 cm-1 峰位的样本。", "在 spectra 表中筛选 peak_cm1 范围。", {"peak_range": [460, 470]}),
        ("查询 Qinhuangdao 错误样本对应的光谱备注。", "连接 samples、predictions、spectra 并筛选错误预测。", {"join": ["samples", "predictions", "spectra"]}),
        ("统计预测正确率。", "用 predictions 表中 is_correct 计算平均正确率。", {"metric": "accuracy"}),
        ("查询真实矿物为 quartz 的错误预测。", "筛选 true_mineral=quartz 且 is_correct=0。", {"true_mineral": "quartz"}),
        ("查询预测为 feldspar 的样本来自哪些地区。", "连接 samples 和 predictions 并筛选 predicted_mineral。", {"predicted_mineral": "feldspar"}),
        ("查询数据库中有哪些表参与 Agent 分析。", "读取 schema 或列出 samples、predictions、spectra。", {"tables": ["samples", "predictions", "spectra"]}),
        ("查询每个矿物类别的关键光谱特征。", "读取 minerals 表的 mineral_class 和 key_spectral_feature。", {"table": "minerals"}),
        ("查询峰位大于 1000 cm-1 的光谱记录。", "筛选 spectra.peak_cm1 > 1000。", {"condition": "peak_cm1 > 1000"}),
        ("统计 Qinhuangdao 地区样本总数。", "按 samples.region 过滤并计数。", {"region": "Qinhuangdao"}),
        ("查询每个预测矿物的正确和错误数量。", "按 predicted_mineral 与 is_correct 聚合。", {"group_by": ["predicted_mineral", "is_correct"]}),
        ("查询错误预测最多的真实矿物。", "筛选错误预测并按 true_mineral 聚合排序。", {"group_by": "true_mineral"}),
        ("查询每个 sample_id 的真实矿物、预测矿物和峰位。", "连接 samples、predictions、spectra。", {"join": ["samples", "predictions", "spectra"]}),
        ("查询没有光谱记录的样本。", "samples 左连接 spectra 并筛选缺失 spectrum_id。", {"join": "left"}),
        ("查询 Qinhuangdao 中被预测为 quartz 的错误样本。", "筛选 region、predicted_mineral 和 is_correct。", {"predicted_mineral": "quartz"}),
        ("根据错误信息修复把 predicted 写成 prediction 的 SQL。", "使用 schema 将错误列名修复为 predicted_mineral。", {"repair": "column_name"}),
        ("根据 schema 修复缺少 join 条件的 SQL。", "使用 sample_id 连接 samples 和 predictions。", {"repair": "join_condition"}),
        ("查询 Agent 最终报告应返回哪些结构化字段。", "最终报告应包含 SQL、证据、验证结果和限制说明。", {"fields": ["sql", "evidence", "verification", "limitations"]}),
    ]
    for prompt, intent, expected in sql_prompts:
        rows.append(item(idx, prompt, intent, "sql", [], "medium", True, True, intent, expected)); idx += 1

    multi_hop_pairs = [
        ("石英", "长石", ["doc_quartz#chunk_002", "doc_feldspar#chunk_002"]),
        ("方解石", "白云石", ["doc_calcite#chunk_001", "doc_dolomite#chunk_001"]),
        ("赤铁矿", "磁铁矿", ["doc_hematite#chunk_001", "doc_magnetite#chunk_001"]),
        ("白云母", "高岭石", ["doc_muscovite#chunk_001", "doc_kaolinite#chunk_001"]),
        ("黄铁矿", "赤铁矿", ["doc_pyrite#chunk_001", "doc_hematite#chunk_001"]),
        ("橄榄石", "长石", ["doc_olivine#chunk_001", "doc_feldspar#chunk_001"]),
    ]
    for left, right, evidence in multi_hop_pairs:
        rows.append(item(idx, f"比较{left}和{right}时为什么需要多条证据？", f"因为需要分别确认{left}和{right}的类别或光谱特征，再进行可靠对比。", "multi_hop", evidence, "medium")); idx += 1

    while len(rows) < count:
        fact = MINERAL_FACTS[len(rows) % len(MINERAL_FACTS)]
        mode = len(rows) % 8
        if mode == 0:
            rows.append(item(idx, f"当前资料库是否能证明样本 UNKNOWN-{idx} 是{fact['zh']}？", f"不能。当前资料库没有 UNKNOWN-{idx} 的充分证据，系统应拒答。", "unanswerable", [], "medium", False))
        elif mode == 1:
            rows.append(item(idx, f"如果问题声称{fact['zh']}一定属于碳酸盐矿物，MiniGeo 应如何处理？", f"MiniGeo 应检查证据并指出该前提需要验证；若证据显示{fact['zh']}属于{fact['class']}，应纠正错误前提。", "false_premise", fact["evidence"], "medium"))
        elif mode == 2:
            rows.append(item(idx, f"查询数据库中真实矿物为 {fact['name']} 的错误预测数量。", f"筛选 true_mineral={fact['name']} 且 is_correct=0，并统计错误数量。", "sql", [], "medium", True, True, f"count incorrect predictions where true_mineral={fact['name']}", {"true_mineral": fact["name"], "is_correct": 0}))
        elif mode == 3:
            rows.append(item(idx, f"{fact['zh']}的证据引用应包含哪些 chunk？", f"回答{fact['zh']}基础问题时应优先引用 {', '.join(fact['evidence'])}。", "evidence", fact["evidence"], "easy"))
        elif mode == 4:
            rows.append(item(idx, f"为什么不能只凭外观判断{fact['zh']}？", f"因为外观信息可能混淆，关于{fact['zh']}的可靠判断需要成分、性质或光谱证据。", "mineral_property", fact["evidence"] + fact["spectra"], "medium"))
        elif mode == 5:
            rows.append(item(idx, f"{fact['zh']}相关光谱或性质证据在回答中有什么作用？", f"它用于把关于{fact['zh']}的结论限制在可追踪证据范围内，避免无依据推断。", "spectroscopy", fact["spectra"], "medium"))
        elif mode == 6:
            other = MINERAL_FACTS[(len(rows) + 3) % len(MINERAL_FACTS)]
            rows.append(item(idx, f"比较{fact['zh']}和{other['zh']}类别时需要哪些证据？", f"需要分别引用{fact['zh']}和{other['zh']}的类别证据，再进行对比。", "multi_hop", fact["evidence"] + other["evidence"], "medium"))
        else:
            rows.append(item(idx, f"MiniGeo 如何避免在回答{fact['zh']}问题时产生无证据结论？", f"MiniGeo 应检索{fact['zh']}相关证据，证据不足时拒答或说明限制。", "evidence", fact["evidence"], "medium"))
        idx += 1

    return rows[:count]


def main() -> None:
    parser = argparse.ArgumentParser(description="Expand deterministic MiniGeo seed benchmark and corpus.")
    parser.add_argument("--target-items", type=int, default=300)
    args = parser.parse_args()

    bench = load_benchmark(BENCH_PATH)
    corpus = load_corpus(CORPUS_PATH)

    existing_chunks = {row["chunk_id"] for row in corpus}
    for chunk_id, doc_id, text, source, url, topic, mineral in EXTRA_CORPUS:
        if chunk_id not in existing_chunks:
            corpus.append(
                {
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "text": text,
                    "source": source,
                    "url": url,
                    "page": None,
                    "topic": topic,
                    "mineral": mineral,
                    "license": "source_metadata_only",
                }
            )

    if len(bench) < args.target_items:
        existing_ids = {row["id"] for row in bench}
        next_idx = max(int(row["id"].split("_")[1]) for row in bench) + 1
        needed = args.target_items - len(bench)
        extra = [row for row in make_extra_items(next_idx, needed) if row["id"] not in existing_ids]
        bench.extend(extra[:needed])

    write_jsonl(CORPUS_PATH, corpus)
    write_jsonl(BENCH_PATH, bench)
    write_jsonl(SOURCE_PATH, SOURCE_MANIFEST)
    print(f"benchmark_items={len(bench)}")
    print(f"corpus_chunks={len(corpus)}")
    print(f"sources={len(SOURCE_MANIFEST)}")


if __name__ == "__main__":
    main()
