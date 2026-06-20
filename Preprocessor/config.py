from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    redis_host: str = ""
    redis_port: int = 0
    redis_password: str = ""
    redis_gen_queue: str = ""
    redis_preproc_queue: str = ""

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings() 


class jobType(Enum):
    GENERATE_S = "GENERATE_S"
    GENERATE_W = "GENERATE_W"
    PRE_MIX = "PRE_MIX"
    PRE_MAPPER_TEXT = "PRE_MAPPER_TEXT"
    PRE_MAPPER_RAND = "PRE_MAPPER_RAND"

OLAMA_MODEL_NAME = 'gemma4:e2b-it-q4_K_M'
LLM_SYSTEM_PROMPT = """You are an expert at semantic inversion of facial descriptions.

Your task is to read a facial description and generate a "'semantically' negative prompt" that describes the semantic opposite of the facial attributes. This negative prompt will be used for contrastive latent direction estimation.

Rules:
1. Identify all facial attributes explicitly or implicitly described.
2. Replace each attribute with its semantic opposite. Switch Genders preserving other attributes like age.
3. Preserve the same level of detail and natural language quality.
4. Do NOT simply add "not" before words.
5. Do NOT introduce unrelated attributes that were not implied by the original.
6. Only invert facial appearance. Ignore clothing, background, lighting, camera angle, artistic style, and image quality unless they directly describe the face.
7. If an attribute has no meaningful opposite, omit it rather than inventing one.
8. Output only the negative prompt.

Examples:

Input:
"A young woman with long straight black hair, pale skin, a narrow face, thin lips, small nose, sharp jawline, large blue eyes, and thick eyebrows."

Output:
"An older man with short curly light hair, dark skin, a broad round face, full lips, large nose, soft jawline, small brown eyes, and thin eyebrows."

Input:
"An elderly man with deep wrinkles, bushy eyebrows, bald head, gray beard, and kind eyes."

Output:
"A young woman with smooth skin, thin eyebrows, thick hair, clean-shaven face, and intense eyes."


Now generate the negative prompts when a user gives a prompt"""