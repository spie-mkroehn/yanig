from typing import Generator
from pydantic import BaseModel
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os
from os.path import join, dirname


class ElevenlabsAudio(BaseModel):
    api_key:str = None
    client:ElevenLabs = None

    def invoke(self, user_input:str):
        self.__init_prerequisites__()
        audio_stream = self.client.text_to_speech.convert_as_stream(
            text=user_input,
            voice_id="7eVMgwCnXydb3CikjV7a", # Lea (German)
            #model_id="eleven_multilingual_v2"
            model_id="eleven_flash_v2.5"
        )
        stream(audio_stream)

    def stream(self, user_input: Generator):
        self.__init_prerequisites__()
        audio_stream = self.client.generate(
            text=user_input,
            voice="Lea",
            #model="eleven_multilingual_v2",
            model="eleven_flash_v2.5",
            stream=True
        )
        stream(audio_stream)       

    def __init_prerequisites__(self):
        if self.api_key is None:
            load_dotenv(join(dirname(__file__), '.env'))
            self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if self.client is None:
            self.client = ElevenLabs(
                api_key=self.api_key,
            )

    # Konfigurationsoptionen für Pydantic
    class Config:
        arbitrary_types_allowed = True
