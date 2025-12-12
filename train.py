# ============================================
# Ultra-Fast Biomedical Fine-Tune with Unsloth (2025 Best Practice)
# Works on 1xA100 80GB or 2x4090/3090
# ============================================
import torch
from unsloth import FastLanguageModel
from datasets import load_dataset, concatenate_datasets
from trl import SFTTrainer
from transformers import TrainingArguments
import os

# ============================================
# 1. Config
# ============================================
max_seq_length = 4096 # Changed max_seq_length
dtype = torch.bfloat16
load_in_4bit = True

# ============================================
# 2. Load Model + Tokenizer with Flash Attention
# ============================================
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="meta-llama/Llama-2-7b-hf", # Changed model name to Llama-2-7b
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
    device_map="auto",
    trust_remote_code=True,
)

model=FastLanguageModel.get_peft_model(
    model,
    r=64,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=64,
    lora_dropout=0.05
    bia="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
    use_rslora=True,
    loftq_config=None,
)

print("✓ Model & LoRA ready")

print("✓ Model loaded successfully")

# ============================================
# Prepare Biomedical Datasets
# ============================================
pubmedqa = load_dataset("pubmed_qa", "pqa_labeled", split="train")
medmcqa = load_dataset("openlifescienceai/medmcqa", split="train[:10000]")
dataset = concatenate_datasets([pubmedqa, medmcqa])
dataset = dataset.shuffle(seed=42)

print(f"✓ Loaded {len(dataset)} training examples")

# ============================================
# Format Data for Biomedical SFT
# ============================================
alpaca_prompt = """Below is an instruction that describes a biomedical task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

def formatting_prompts_func(examples):
    instructions = []
    inputs = []
    outputs = []

    for i in range(len(examples['question'])):
        question = examples['question'][i] if 'question' in examples else examples['query'][i]
        answer = examples['answer'][i] if 'answer' in examples else examples['cop'][i]

        instructions.append("Answer this biomedical question accurately based on medical knowledge.")
        inputs.append(question)
        outputs.append(str(answer))

    texts = []
    for instruction, input_text, output_text in zip(instructions, inputs, outputs):
        text = alpaca_prompt.format(instruction, input_text, output_text) + tokenizer.eos_token
        texts.append(text)

    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True, remove_columns=dataset.column_names)
dataset = dataset.train_test_split(test_size=0.1, seed=42)

print("✓ Dataset formatted for training")

# ============================================
# Apply QLoRA Adapters
# ============================================
model = FastLanguageModel.get_peft_model(
    model,
    r=64,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj",
                    "w1", "w2", "w3"], # Reverted target modules
    lora_alpha=64,
    lora_dropout=0.05,
    bias="all",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
    use_rslora=True,
)

print("✓ LoRA adapters configured")

# ============================================
# Configure and Run Training
# ============================================
training_args = TrainingArguments(
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=16,
    num_train_epochs=5,
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
    output_dir="llama2_biomed_outputs", # Changed output directory
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    evaluation_strategy="steps", # Reverted eval_strategy
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
    args=training_args, # Pass the TrainingArguments object
)

print("✓ Training configured")
print("Starting training... (this will take 6-10 hours)")

trainer_stats = trainer.train()

print("✓ Training completed!")

# ============================================
# Save LoRA Weights
# ============================================
model.save_pretrained("llama2_biomed_lora") # Changed save directory
tokenizer.save_pretrained("llama2_biomed_lora") # Changed save directory
print("✓ LoRA weights saved to: llama2_biomed_lora/")

# ============================================
# Save Merged Full Model
# ============================================
model.save_pretrained_merged(
    "llama2_biomed_merged", # Changed save directory
    tokenizer,
    save_method="merged_16bit"
)
print("✓ Merged model saved to: llama2_biomed_merged/")

# ============================================
# Test Inference
# ============================================
FastLanguageModel.for_inference(model)

test_prompt = """Below is an instruction that describes a biomedical task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
Answer this biomedical question accurately based on medical knowledge.

### Input:
What are the primary considerations when selecting biomaterials for cardiovascular implants?

### Response:
"""

inputs = tokenizer([test_prompt], return_tensors="pt").to("cuda")
outputs = model.generate(
    **inputs,
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
