# ============================================
# Ultra-Fast Biomedical Fine-Tune (2025 Best Practice)
# Works on 1xA100 80GB
# ============================================
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments, AutoTokenizer, BitsAndBytesConfig, AutoProcessor
from transformers import Glm4vForConditionalGeneration
from peft import LoraConfig, get_peft_model, PeftModel
import os

# ============================================
# 1. Config
# ============================================
max_seq_length = 4096
dtype = torch.bfloat16

# ============================================
# 2. Load Model + Tokenizer with 4-bit Quantization
# ============================================
model_name = "zai-org/GLM-4.6V-Flash"

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=dtype,
)

processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
tokenizer = processor.tokenizer

model = Glm4vForConditionalGeneration.from_pretrained(
    model_name,
    quantization_config=quantization_config,
    device_map="auto",
    torch_dtype=dtype,
    trust_remote_code=True,
)

print("✓ Model loaded successfully")

# ============================================
# Apply LoRA Adapters
# ============================================
lora_config = LoraConfig(
    r=64,
    lora_alpha=64,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

print("✓ LoRA adapters configured")

# ============================================
# Prepare High-Quality Biomedical Dataset
# ============================================
dataset = load_dataset("TsinghuaC3I/UltraMedical", split="train")
dataset = dataset.shuffle(seed=42)

print(f"✓ Loaded {len(dataset)} training examples")

# ============================================
# Format Data for SFT
# ============================================
def formatting_prompts_func(examples):
    texts = []
    for conversation in examples["conversations"]:
        text = tokenizer.apply_chat_template(conversation, tokenize=False) + tokenizer.eos_token
        texts.append(text)
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True, remove_columns=dataset.column_names)
dataset = dataset.train_test_split(test_size=0.1, seed=42)

print("✓ Dataset formatted for training")

# ============================================
# Configure and Run Training
# ============================================
training_args = TrainingArguments(
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=16,
    num_train_epochs=1,  # Reduced to 1 due to larger dataset size
    warmup_steps=200,
    learning_rate=5e-5,
    bf16=True,
    logging_steps=10,
    eval_steps=100,
    save_steps=200,
    optim="adamw_torch_fused",
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    seed=3407,
    output_dir="glm_biomed_outputs",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    evaluation_strategy="steps",
    gradient_checkpointing=True,
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=4,
    packing=False,
    args=training_args,
)

print("✓ Training configured")
print("Starting training... (this will take several days on a single A100; adjust epochs or subsample if needed)")

trainer_stats = trainer.train()

print("✓ Training completed!")

# ============================================
# Save LoRA Weights
# ============================================
model.save_pretrained("glm_biomed_lora")
tokenizer.save_pretrained("glm_biomed_lora")
print("✓ LoRA weights saved to: glm_biomed_lora/")

# ============================================
# Save Merged Full Model
# ============================================
model = model.merge_and_unload()
model.save_pretrained("glm_biomed_merged")
tokenizer.save_pretrained("glm_biomed_merged")
print("✓ Merged model saved to: glm_biomed_merged/")

# ============================================
# Test Inference
# ============================================
test_prompt = [
    {"role": "user", "content": "Answer this biomedical question accurately based on medical knowledge: What are the primary considerations when selecting biomaterials for cardiovascular implants?"}
]

inputs = tokenizer.apply_chat_template(test_prompt, return_tensors="pt").to("cuda")

outputs = model.generate(
    inputs,
    max_new_tokens=256,
    temperature=0.3,
    do_sample=True,
    top_p=0.9
)

print("\n" + "="*50)
print("INFERENCE TEST:")
print("="*50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
print("\n✓ All done! Model ready for use.")
