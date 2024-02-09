"""
Preprocessing helper signifies helper class which provides necessary supporting methods used in AMD service.
"""
from app import tf
import io
from pydub import AudioSegment
import numpy as np
from app.business_rule_exception import ShortAudioLengthException

SAMPLING_RATE = 16000


class PreProcessingPipeLine:
    """
    Preprocessing pipeline class contains audio preprocessing methods used in prediction of the AMD model
    """

    async def pre_process(self, file):
        """
        The method generates tensor of input file and returns tensor list.
        The method also raises exception if it fails to process the audio

        Parameter:
            file: Input Audio file.

        Return:
            tensor: Tensor generated from input audio
        """
        ds = await self.__generate_tensor(file)
        iterator = iter(ds)
        tensor = iterator.get_next()
        return await self.__audio_to_fft(tensor), round(self.audio_length, 2)

    async def __to_dataset(self, audios):
        """The method constructs a dataset of audios"""
        ds = tf.data.Dataset.from_tensor_slices(audios)
        audio_ds = self.__decode_audio(ds)
        return tf.data.Dataset.zip((audio_ds,))

    def __decode_audio(self, audio):
        """The method reads and decodes an audio file and returns it"""
        io_bytes = io.BytesIO([x for x in audio.take(1).as_numpy_iterator()][0])
        raw_audio = AudioSegment.from_file(io_bytes, format="raw", codec='mulaw', frame_rate=8000, channels=1,
                                           sample_width=1)
        # sound = raw_audio.set_frame_rate(16000)
        channel_sounds = raw_audio.split_to_mono()
        samples = [s.get_array_of_samples() for s in channel_sounds]

        fp_arr = np.array(samples).T.astype(np.float32)
        fp_arr /= np.iinfo(samples[0].typecode).max
        if len(fp_arr) < 16000:
            raise ShortAudioLengthException()
        self.audio_length = len(fp_arr)/8000
        two_sec_slice = fp_arr[:16000]
        two_sec_slice = np.concatenate((two_sec_slice, np.zeros((16000 - len(two_sec_slice), 1))), axis=0)
        two_sec_slice_tf = tf.convert_to_tensor(two_sec_slice)
        return tf.data.Dataset.from_tensor_slices([two_sec_slice_tf])

    async def __audio_to_fft(self, audio):
        """The method converts audio to fast fourier transform (FFT) and returns it"""
        audio = tf.squeeze(audio, axis=-1)
        fft = tf.signal.fft(
            tf.cast(tf.complex(real=audio, imag=tf.zeros_like(audio)), tf.complex64)
        )
        fft = tf.expand_dims(fft, axis=-1)
        return tf.math.abs(fft[:, : (audio.shape[1] // 2), :])

    async def __generate_tensor(self, audio):
        """The method converts audio file to a Tensor Object"""
        audios = [audio]
        test_ds = await self.__to_dataset(audios)
        return test_ds
