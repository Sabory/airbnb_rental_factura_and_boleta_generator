import confuse
from dotenv import load_dotenv

load_dotenv()

config = confuse.Configuration("app", __name__)
config.set_file("./config.yml", base_for_paths=True)
config.set_env()
