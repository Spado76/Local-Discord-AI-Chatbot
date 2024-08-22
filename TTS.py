import os
import torch
import numpy as np
from scipy.io.wavfile import write
from pydub import AudioSegment
from gtts import gTTS

# https://github.com/snakers4/silero-models#text-to-speech
def silero_tts(tts, language, model, speaker, output_path):
    device = torch.device('cpu')
    torch.set_num_threads(4)
    local_file = 'model.pt'

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(f'https://models.silero.ai/models/tts/{language}/{model}.pt',
                                    local_file)  

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    example_text = "i'm fine thank you and you?"
    sample_rate = 48000

    audio = model.apply_tts(text=tts,
                            speaker=speaker,
                            sample_rate=sample_rate)
    
    audio_numpy = audio.cpu().numpy()

    wav_path = "output.wav"
    write(wav_path, sample_rate, audio_numpy)

    sound = AudioSegment.from_wav(wav_path)
    sound.export(output_path, format="mp3")

    os.remove(wav_path)
    
def google_tts(text, language='en', output_file='output.mp3'):
    # Create a gTTS object with the text you want to turn into sound
    tts = gTTS(text=text, lang=language)

    # Save TTS to audio file
    tts.save(output_file)

if __name__ == "__main__":
    silero_tts("Hello, how are you", "en", "v3_en", "en_21", "output.mp3")
