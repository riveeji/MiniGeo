from minigeo.sql.model_generator import ModelSQLGenerator, sql_generator_from_env


def test_model_sql_generator_reads_sql_from_json_response() -> None:
    class FakeClient:
        def __init__(self):
            self.prompts = []

        def generate(self, prompt: str) -> str:
            self.prompts.append(prompt)
            return '{"sql":"select * from samples"}'

    client = FakeClient()
    generator = ModelSQLGenerator(client)

    assert generator.generate("列出样本") == "select * from samples"
    assert "只返回 JSON 对象" in client.prompts[0]


def test_model_sql_generator_falls_back_to_plain_select_text() -> None:
    class FakeClient:
        def generate(self, prompt: str) -> str:
            return "select * from predictions"

    assert ModelSQLGenerator(FakeClient()).generate("列出预测") == "select * from predictions"


def test_model_sql_generator_extracts_json_after_thinking_block() -> None:
    class FakeClient:
        def generate(self, prompt: str) -> str:
            return (
                "<think>先分析 schema。</think>\n"
                "```json\n"
                '{"sql":"SELECT sample_id FROM samples WHERE region = \'Qinhuangdao\'"}\n'
                "```"
            )

    sql = ModelSQLGenerator(FakeClient()).generate("列出 Qinhuangdao 样本")

    assert sql == "SELECT sample_id FROM samples WHERE region = 'Qinhuangdao'"


def test_model_sql_generator_extracts_select_without_trailing_markdown() -> None:
    class FakeClient:
        def generate(self, prompt: str) -> str:
            return "SQL 如下：\nSELECT * FROM spectra WHERE peak_cm1 > 1000;\n```"

    assert ModelSQLGenerator(FakeClient()).generate("查询峰位") == "SELECT * FROM spectra WHERE peak_cm1 > 1000"


def test_model_sql_generator_falls_back_for_placeholder_sql() -> None:
    class FakeClient:
        def generate(self, prompt: str) -> str:
            return '{"sql":"select ..."}'

    sql = ModelSQLGenerator(FakeClient()).generate("秦皇岛样本中被误判最多的预测矿物是什么？")

    assert "Qinhuangdao" in sql
    assert "select ..." not in sql


def test_sql_generator_from_env_uses_model_when_enabled() -> None:
    def fake_transport(url, headers, payload, timeout):
        return {"choices": [{"message": {"content": '{"sql":"select * from minerals"}'}}]}

    generator = sql_generator_from_env(
        {
            "OPENAI_BASE_URL": "http://localhost:8000/v1",
            "OPENAI_API_KEY": "EMPTY",
            "MINIGEO_SQL_MODEL": "Qwen/Qwen3.5-2B",
            "MINIGEO_SQL_USE_MODEL": "1",
        },
        transport=fake_transport,
    )

    assert generator.generate("列出矿物") == "select * from minerals"


def test_sql_generator_from_env_defaults_to_rule_based() -> None:
    generator = sql_generator_from_env({})

    assert "Qinhuangdao" in generator.generate("秦皇岛样本中被误判最多的预测矿物是什么？")
