from openai import OpenAI
from pydub import AudioSegment
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Optional
import os, dotenv

dotenv.load_dotenv()
client = OpenAI()

def text_to_speech(
    text: str,
    output_dir: str,
    identifier: str
) -> Optional[str]:
    """
    Generate audio file from the given text, return the file name.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=0,
    )
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    text_chunks = text_splitter.split_text(text=text)
    audio_files = []
    try:
        for i, chunk in enumerate(text_chunks):
            audio_file = os.path.join(temp_dir, f"{identifier}_part_{i}.mp3")
            with client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="nova",
                input=chunk
            ) as response:
                response.stream_to_file(audio_file)
            audio_files.append(audio_file)
        final_audio_file = merge_audio_files(audio_files, output_dir, identifier)
        return final_audio_file
    except Exception:
        return None
    finally:
        for file in audio_files:
            os.remove(file)

def merge_audio_files(files: list, output_dir: str, identifier: str) -> str:
    combined_audio = AudioSegment.empty()
    for file in files:
        audio = AudioSegment.from_file(file)
        combined_audio += audio
    file_name = f"{identifier}.mp3"
    output_path = os.path.join(output_dir, file_name)
    combined_audio.export(output_path, format="mp3")
    return file_name