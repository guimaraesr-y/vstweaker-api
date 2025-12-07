import os
import tempfile
from datetime import datetime
from pydub import AudioSegment
from typing import Iterable
from django.core.files import File

# small helper classes (object calisthenics: pequenas classes)
class TrackSetting:
    def __init__(self, path: str, volume_db: float = 0.0, pan: float = 0.0):
        self.path = path
        self.volume_db = float(volume_db)
        self.pan = float(pan)

class MixResult:
    def __init__(self, output_path: str):
        self.output_path = output_path

class MixingService:
    """
    Responsável por ler as faixas, aplicar volume/pan e gerar um .wav mixado.
    Usa pydub/ffmpeg.
    """

    def __init__(self, sample_rate: int = 44100, channels: int = 2, bit_depth: int = 16):
        self.sample_rate = sample_rate
        self.channels = channels
        self.bit_depth = bit_depth

    def _load_audio(self, path: str) -> AudioSegment:
        # pydub detects format by extension; ensure ffmpeg is available.
        audio = AudioSegment.from_file(path)
        # convert to target channels and sample rate for consistent overlay
        audio = audio.set_frame_rate(self.sample_rate)
        audio = audio.set_channels(self.channels)
        return audio

    def _apply_volume_and_pan(self, audio: AudioSegment, volume_db: float, pan: float) -> AudioSegment:
        # apply volume (gain)
        audio = audio.apply_gain(volume_db)
        # pan expects -1.0 .. 1.0
        # pydub.AudioSegment.pan exists and returns a stereo AudioSegment
        if -1.0 <= pan <= 1.0:
            # pan only works for stereo segments; ensure stereo
            if audio.channels == 1:
                audio = AudioSegment.from_mono_audiosegments(audio, audio)
            audio = audio.pan(pan)
        return audio

    def mix(self, track_settings: Iterable[TrackSetting], output_filename: str = None) -> MixResult:
        """
        track_settings: iterable of TrackSetting with file paths and parameters
        returns MixResult with output_path
        """
        temp_dir = tempfile.mkdtemp(prefix="vs_mix_")
        try:
            # load and process tracks
            processed_segments = []
            max_duration_ms = 0

            for ts in track_settings:
                seg = self._load_audio(ts.path)
                seg = self._apply_volume_and_pan(seg, ts.volume_db, ts.pan)
                processed_segments.append(seg)
                if len(seg) > max_duration_ms:
                    max_duration_ms = len(seg)

            # create base silent track with length = max_duration_ms
            base = AudioSegment.silent(duration=max_duration_ms, frame_rate=self.sample_rate).set_channels(self.channels)

            # overlay each processed segment onto base
            output = base
            for seg in processed_segments:
                # overlay aligns starts at 0ms; if you want offsets, extend the model to include offset
                output = output.overlay(seg)

            # export to wav 16-bit PCM by default
            if output_filename is None:
                ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                output_filename = f"mix_{ts}.wav"

            output_path = os.path.join(temp_dir, output_filename)

            # pydub export params: format 'wav', parameters to ensure 16-bit PCM
            output.export(output_path, format="wav", parameters=["-ar", str(self.sample_rate), "-ac", str(self.channels)])

            return MixResult(output_path=output_path)
        finally:
            # do NOT delete here — caller will move file / attach to Django FileField.
            pass
