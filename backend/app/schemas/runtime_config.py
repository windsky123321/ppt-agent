from pydantic import BaseModel


class RuntimeModelConfig(BaseModel):
    llm_provider: str = "mock"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-5.5"
    fallback_llm_model: str = "gpt-4.1-mini"
    vision_provider: str = "mock"
    vision_base_url: str = "https://api.openai.com/v1"
    vision_api_key: str = ""
    vision_model: str = "gpt-4.1-mini"
    enable_vision: bool = True
    enable_critic: bool = True
    enable_repair: bool = True
    max_repair_loops: int = 2
    reasoning_effort: str = "low"
    verbosity: str = "low"
    temperature: float = 0.2
    patch_mode: bool = True
    revision_max_output_tokens: int = 1200
    normal_max_output_tokens: int = 4000
    output_dir: str = "storage/decks"


class RuntimeModelConfigView(BaseModel):
    llm_provider: str
    llm_base_url: str
    llm_api_key_masked: str
    llm_model: str
    fallback_llm_model: str
    vision_provider: str
    vision_base_url: str
    vision_api_key_masked: str
    vision_model: str
    enable_vision: bool
    enable_critic: bool
    enable_repair: bool
    max_repair_loops: int
    reasoning_effort: str
    verbosity: str
    temperature: float
    patch_mode: bool
    revision_max_output_tokens: int
    normal_max_output_tokens: int
    output_dir: str


class ModelTestResponse(BaseModel):
    success: bool
    message: str
    llm_ok: bool = False
    vision_ok: bool = False
