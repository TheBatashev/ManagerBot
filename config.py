from dotenv import load_dotenv
import os
from hashlib import sha256


load_dotenv()



class Settings :
    def __init__(self):

        self.BOT_TOKEN = os.getenv('BOT_TOKEN')
        
        self.REDIS_HOST = os.getenv('REDIS_HOST')
        self.REDIS_PORT = int(os.getenv('REDIS_PORT'))
        self.REDIS_EXPIRE = int(os.getenv('REDIS_EXPIRE'))

        self.EMOJIS = ['🟦','🟨','🟪','🟩','🟥','🟧','🟫','⬜️','⬛️']


    def __repr__(self):
        pass

    
settings = Settings()