# mixer/services/mixing_service.py
import os
import tempfile
from datetime import datetime
from pydub import AudioSegment


class TrackSetting:
    def __init__(self, file_path, volume_db=0.0, pan=0.0):
        self.file_path = file_path
        self.volume_db = volume_db
        self.pan = pan


class MixResult:
    def __init__(self, output_path):
        self.output_path = output_path


class MixingService:

    def mix(self, track_settings, sample_rate=44100, channels=2):
        processed = []
        longest = 0

        for ts in track_settings:
            audio = AudioSegment.from_file(ts.file_path)
            audio = audio.set_frame_rate(sample_rate).set_channels(channels)

            audio = audio.apply_gain(ts.volume_db)

            if channels == 2:
                audio = audio.pan(ts.pan)

            processed.append(audio)
            longest = max(longest, len(audio))

        base = AudioSegment.silent(duration=longest, frame_rate=sample_rate).set_channels(channels)
        final = base

        for seg in processed:
            final = final.overlay(seg)

        temp_dir = tempfile.mkdtemp(prefix="mix_")
        filename = f"mix_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.wav"
        output_path = os.path.join(temp_dir, filename)

        final.export(output_path, format="wav")

        return MixResult(output_path)
