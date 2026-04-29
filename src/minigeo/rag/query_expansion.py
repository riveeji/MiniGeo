from minigeo.rag.tokenizer import tokenize

MINERAL_EXPANSIONS = {
    "石英": ["石英", "硅酸盐", "二氧化硅", "sio2"],
    "长石": ["长石", "铝硅酸盐", "框架", "火成岩", "变质岩"],
    "方解石": ["方解石", "碳酸盐", "硅酸盐"],
    "赤铁矿": ["赤铁矿", "铁氧化物", "fe2o3"],
    "白云石": ["白云石", "钙镁", "碳酸盐", "camg"],
    "石膏": ["石膏", "含水", "硫酸盐", "caso4"],
    "磁铁矿": ["磁铁矿", "铁氧化物", "磁性", "fe3o4"],
    "黄铁矿": ["黄铁矿", "硫化物", "fes2", "金属光泽"],
    "橄榄石": ["橄榄石", "镁铁", "硅酸盐", "基性", "超基性岩"],
    "白云母": ["白云母", "层状", "硅酸盐", "片状", "解理"],
    "高岭石": ["高岭石", "黏土", "层状", "硅酸盐"],
    "钙长石": ["钙长石", "斜长石", "长石族", "caal2si2o8"],
}

SPECTROSCOPY_EXPANSIONS = {
    "长石": ["框架", "振动", "弱峰", "噪声", "混淆", "光谱"],
    "石英": ["拉曼", "464", "峰", "光谱"],
    "方解石": ["碳酸根", "1085", "峰", "光谱"],
    "赤铁矿": ["铁氧化物", "光谱", "峰"],
}


def expand_query_tokens(query: str) -> list[str]:
    text = query.lower()
    expanded: list[str] = []
    if "failure case" in text or "failure analysis" in text:
        expanded.extend(["失败", "案例", "分析", "失败案例", "检索", "生成", "验证", "误判", "sql", "错误"])
    if "证据来源" in query or "无证据结论" in query or "证据引用" in query:
        expanded.extend(["证据", "来源", "可信", "回答", "可追踪"])
    for mineral, terms in MINERAL_EXPANSIONS.items():
        if mineral in query:
            expanded.extend(terms)
            if any(word in query for word in ["光谱", "谱", "峰", "混淆", "性质"]):
                expanded.extend(SPECTROSCOPY_EXPANSIONS.get(mineral, []))
    tokens: list[str] = []
    for term in expanded:
        tokens.extend(tokenize(term))
    return tokens
