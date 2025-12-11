import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.yaml"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_project_base_url(project_name: str, env: str = None) -> str:
    """
    Trả về base_url cho project + env.
    Ví dụ: project_name="duckduckgo", env="dev"
    """
    config = load_config()
    if env is None:
        env = config.get("env", "dev")

    try:
        return config["projects"][project_name][env]["base_url"]
    except KeyError as exc:
        raise KeyError(
            f"Không tìm thấy base_url cho project='{project_name}', env='{env}'"
        ) from exc
