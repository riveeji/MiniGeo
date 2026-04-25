from pathlib import Path
from typing import Any


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def _load_yaml_subset(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if indent == 0:
            key, _, value = line.partition(":")
            current_key = key.strip()
            data[current_key] = _parse_scalar(value) if value.strip() else {}
            continue
        if current_key is None:
            raise ValueError(f"Invalid YAML subset line: {raw_line}")
        if line.startswith("- "):
            if not isinstance(data[current_key], list):
                data[current_key] = []
            data[current_key].append(_parse_scalar(line[2:]))
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"Invalid YAML subset line: {raw_line}")
        if not isinstance(data[current_key], dict):
            raise ValueError(f"Cannot add mapping under list section: {current_key}")
        data[current_key][key.strip()] = _parse_scalar(value)
    return data


def load_lora_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        return _load_yaml_subset(text)
    loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise ValueError(f"Config must be a mapping: {path}")
    return loaded


def _section(config: dict[str, Any], name: str) -> dict[str, Any]:
    section = config.get(name)
    return section if isinstance(section, dict) else {}


def validate_lora_config(config: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    model = _section(config, "model")
    training = _section(config, "training")
    data = _section(config, "data")

    if not model.get("base_model"):
        errors.append("model.base_model 不能为空")
    if not model.get("output_dir"):
        errors.append("model.output_dir 不能为空")
    if training.get("method") != "qlora":
        errors.append("training.method 必须是 qlora")
    if training.get("quantization") != "4bit":
        errors.append("training.quantization 必须是 4bit")
    if not isinstance(training.get("lora_rank"), int) or training.get("lora_rank") <= 0:
        errors.append("training.lora_rank 必须是正整数")

    for key in ["train_path", "eval_path"]:
        value = data.get(key)
        if not value:
            errors.append(f"data.{key} 不能为空")
            continue
        path = root / str(value)
        if not path.exists():
            errors.append(f"data.{key} 不存在：{value}")
    return errors
