# ============================================
# FULL WORKING CHAT INTERFACE
# ======================t======================
from unsloth import FastLanguageModel
import torch

# 1. Load your model from Hugging Face
your_username = "ttennant"  # CHANGE THIS to your HF username
model_name = "qwen2.5-7b-medical-lora"  # Your model name

print("Loading model from Hugging Face...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=f"{your_username}/{model_name}",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# Set to inference mode
FastLanguageModel.for_inference(model)
print("✓ Model loaded and ready!\n")

# 2. Define REAL chat function (not placeholder)
def chat(question):
    """Actually generates responses from your fine-tuned model"""
    prompt = f"""<|im_start|>system
You are a helpful medical assistant specialized in biomedical engineering.<|im_end|>
<|im_start|>user
{question}<|im_end|>
<|im_start|>assistant
"""

    # Tokenize and send to GPU
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")

    # Generate response from model
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.3,
        do_sample=True,
        top_p=0.9,
        use_cache=True,
    )

    # Decode the response
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract just the assistant's answer
    if "<|im_start|>assistant" in full_response:
        assistant_response = full_response.split("<|im_start|>assistant")[-1].strip()
        # Remove any trailing tokens
        assistant_response = assistant_response.replace("<|im_end|>", "").strip()
    else:
        assistant_response = full_response

    return assistant_response

# 3. Test with a real medical question first
print("="*60)
print("TESTING MODEL")
print("="*60)
test_question = "What are the stages of wound healing?"
print(f"Test Question: {test_question}\n")
test_answer = chat(test_question)
print(f"Model Answer: {test_answer}\n")

# 4. Start interactive chat
print("="*60)
print("CHAT WITH YOUR BIOMEDICAL AI MODEL")
print("="*60)
print("Type your questions below. Type 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ['quit', 'exit', 'q']:
        print("Goodbye!")
        break

    if question.strip():
        print("\nAI: ", end="")
        response = chat(question)
        print(response)
        print("\n" + "-"*60 + "\n")
