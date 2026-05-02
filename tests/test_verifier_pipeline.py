from minigeo.verifier.claim_extractor import LocalClaimExtractor, ModelClaimExtractor
from minigeo.verifier.evidence_matcher import EvidenceMatcher
from minigeo.verifier.support_classifier import HeuristicSupportClassifier, ModelSupportClassifier
from minigeo.verifier.verifier import MiniGeoVerifier


class FakeClient:
    def __init__(self, response: str):
        self.response = response
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


def test_local_claim_extractor_splits_chinese_sentences() -> None:
    claims = LocalClaimExtractor().extract("石英主要成分是二氧化硅。方解石是碳酸盐矿物！")

    assert claims == ["石英主要成分是二氧化硅", "方解石是碳酸盐矿物"]


def test_local_claim_extractor_drops_standalone_modal_fragment_when_other_claims_exist() -> None:
    claims = LocalClaimExtractor().extract("能。石英的 464 cm-1 峰和方解石 1085 cm-1 带可用于区分两者。")

    assert claims == ["石英的 464 cm-1 峰和方解石 1085 cm-1 带可用于区分两者"]


def test_model_claim_extractor_reads_json_list() -> None:
    client = FakeClient('["石英是二氧化硅", "石英有 464 cm-1 拉曼峰"]')

    claims = ModelClaimExtractor(client).extract("石英是二氧化硅，并有 464 cm-1 拉曼峰。")

    assert claims == ["石英是二氧化硅", "石英有 464 cm-1 拉曼峰"]
    assert "抽取" in client.prompts[0]


def test_evidence_matcher_returns_best_chunk_ids() -> None:
    chunks = [
        {"chunk_id": "quartz", "text": "石英的主要化学成分是二氧化硅 SiO2。"},
        {"chunk_id": "calcite", "text": "方解石是碳酸盐矿物。"},
    ]

    matches = EvidenceMatcher().match("石英主要成分是二氧化硅", chunks, top_k=1)

    assert matches[0]["chunk_id"] == "quartz"
    assert matches[0]["match_score"] > 0


def test_heuristic_support_classifier_marks_supported_and_insufficient() -> None:
    classifier = HeuristicSupportClassifier(min_score=0.2)

    supported = classifier.classify("石英主要成分是二氧化硅", [{"chunk_id": "q", "match_score": 0.8}])
    insufficient = classifier.classify("石英主要成分是二氧化硅", [])

    assert supported.status == "supported"
    assert supported.evidence == ["q"]
    assert insufficient.status == "insufficient"


def test_model_support_classifier_reads_json_object() -> None:
    client = FakeClient('{"status":"contradicted","evidence":["doc_a"],"confidence":0.7}')
    classifier = ModelSupportClassifier(client)

    result = classifier.classify("石英是碳酸盐矿物", [{"chunk_id": "doc_a", "text": "石英是硅酸盐矿物。"}])

    assert result.status == "contradicted"
    assert result.evidence == ["doc_a"]
    assert result.confidence == 0.7
    assert "判断 claim 是否被证据支持" in client.prompts[0]


def test_minigeo_verifier_produces_partial_report() -> None:
    chunks = [
        {"chunk_id": "quartz", "text": "石英的主要化学成分是二氧化硅 SiO2。"},
    ]

    report = MiniGeoVerifier().verify("石英主要成分是二氧化硅。方解石是碳酸盐矿物。", chunks)

    assert report["verdict"] == "partially_supported"
    assert report["claims"][0]["status"] == "supported"
    assert report["claims"][1]["status"] == "insufficient"
