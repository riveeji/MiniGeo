from pathlib import Path
import json
from typing import Any


def load_sft_rows(path: Path, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
        if len(rows) >= limit:
            break
    return rows


def format_sft_example(row: dict[str, Any]) -> str:
    instruction = str(row["instruction"])
    input_text = str(row["input"])
    output = str(row["output"])
    return (
        "System: 你是 MiniGeo，回答必须简短、可引用、基于证据。\n"
        f"User: {instruction}\n\n输入：{input_text}\n"
        f"Assistant: {output}"
    )


def build_smoke_plan(
    config: dict[str, Any],
    sample_size: int,
    max_steps: int,
    output_dir: str,
) -> dict[str, Any]:
    model = config["model"]
    training = config["training"]
    data = config["data"]
    return {
        "base_model": model["base_model"],
        "train_path": data["train_path"],
        "output_dir": output_dir or model["output_dir"],
        "sample_size": sample_size,
        "max_steps": max_steps,
        "lora_rank": int(training.get("lora_rank", 16)),
        "lora_alpha": int(training.get("lora_alpha", 32)),
        "lora_dropout": float(training.get("lora_dropout", 0.05)),
        "learning_rate": float(training.get("learning_rate", 0.0002)),
    }


def run_qlora_smoke(plan: dict[str, Any]) -> None:
    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from torch.utils.data import Dataset
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        DataCollatorForLanguageModeling,
        Trainer,
        TrainingArguments,
    )

    rows = load_sft_rows(Path(plan["train_path"]), limit=int(plan["sample_size"]))
    texts = [format_sft_example(row) for row in rows]
    tokenizer = AutoTokenizer.from_pretrained(plan["base_model"], trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    class SmokeDataset(Dataset):
        def __len__(self) -> int:
            return len(texts)

        def __getitem__(self, index: int) -> dict[str, Any]:
            return tokenizer(texts[index], truncation=True, max_length=512)

    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        plan["base_model"],
        quantization_config=quantization,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(
        model,
        LoraConfig(
            r=int(plan["lora_rank"]),
            lora_alpha=int(plan["lora_alpha"]),
            lora_dropout=float(plan["lora_dropout"]),
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        ),
    )
    model.print_trainable_parameters()
    args = TrainingArguments(
        output_dir=plan["output_dir"],
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        max_steps=int(plan["max_steps"]),
        learning_rate=float(plan["learning_rate"]),
        bf16=True,
        logging_steps=1,
        save_steps=int(plan["max_steps"]),
        save_total_limit=1,
        report_to=[],
        optim="paged_adamw_8bit",
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=SmokeDataset(),
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    )
    trainer.train()
    adapter_dir = Path(plan["output_dir"]) / "adapter"
    model.save_pretrained(adapter_dir)
    tokenizer.save_pretrained(adapter_dir)
    print(f"wrote={adapter_dir}")
