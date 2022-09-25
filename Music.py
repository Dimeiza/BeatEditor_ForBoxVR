from cgitb import enable
import PySimpleGUI as sg
import pyaudio
import wave
import threading
import logging

from BoxVRJson import BoxVRJson

class Music:

	boxVRJson = None
	wf_sound = None
	wf_music = None
	wf_sound_punch_air = None

	music_stream = None
	sound_stream = None

	current_time = 0
	paused_time = 0

	flag_playing_sound = False
	beat_callback_function = None
	gui_callback_function = None

	musicPlayThread = None
	logger = None

	delay = 0
	sound= None

	beat_callback_thread = None

	def __init__(self):
		self.logger = logging.getLogger(__name__)

		self.wf_sound = wave.open('./res/hit.wav',"rb")
		self.wf_sound_punch_air = wave.open('./res/punchair.wav',"rb")
		self.sound_data = self.wf_sound.readframes(self.wf_sound.getnframes())
		self.punch_air_sound_data = self.wf_sound_punch_air.readframes(self.wf_sound_punch_air.getnframes())

	def set_boxVR_Json(self,boxVRJson):
		self.boxVRJson = boxVRJson

	def set_current_time(self,current_time):
		self.current_time = current_time

	def set_flag_playing_sound(self,flag_playing_sound):
		self.flag_playing_sound = flag_playing_sound

	def music_callback(self,in_data, frame_count, time_info, status):

		if self.flag_playing_sound == False:
			return (bytes(0),pyaudio.paAbort)
		else:
			data = self.wf_music.readframes(frame_count)
			return (data, pyaudio.paContinue)

	def open_music_file(self,music_file_path):
		self.logger.debug(music_file_path)

		self.close_music_file()
		self.wf_music = wave.open(music_file_path, "rb")

		bpm = float(self.boxVRJson.get_track_data_element('bpm'))
		avg_beat_time = 1.0 /bpm * 60

		# set delay based on bpm(it seems 8 beats delay between trigger time and actual impact in box vr)
		self.delay = avg_beat_time * 8.0

	def close_music_file(self):
		if self.wf_music != None:
			self.wf_music.close()
			self.wf_music = None

	def set_beat_callback(self,beat_callback_function):
		self.beat_callback_function = beat_callback_function

	def set_gui_callback(self,gui_callback_function):
		self.gui_callback_function = gui_callback_function

	def set_paused_time(self,paused_time):
		self.paused_time = paused_time

	def pause(self):
		if self.flag_playing_sound == True:
			self.flag_playing_sound = False
			self.paused_time = self.current_time
			# self.musicPlayThread.join()

	def stop(self):
		if self.flag_playing_sound == True:
			self.flag_playing_sound = False
			self.paused_time = 0
			# self.musicPlayThread.join()

	def start(self):
		if self.flag_playing_sound == False:
			self.musicPlayThread = threading.Thread(target=self.play,args=(self.paused_time,))
			self.musicPlayThread.daemon = True
			self.musicPlayThread.start()

	def get_delay(self):
		return self.delay

	def beat_action(self,sound_data,beat_index):
		self.sound_stream.write(sound_data)
		self.beat_callback_function(beat_index)

	def play(self,start_time):

		self.flag_playing_sound = True
		beat_index = 0
		self.current_time = start_time
		self.logger.debug(self.current_time)

		print(self.delay)
		self.wf_music.setpos(int(self.current_time * self.wf_music.getframerate()))
		beat_index = int(self.boxVRJson.get_next_beat_index(self.current_time))

		p = pyaudio.PyAudio()
		self.music_stream = p.open(format=p.get_format_from_width(self.wf_music.getsampwidth()), channels=self.wf_music.getnchannels(), rate=self.wf_music.getframerate(), output=True,stream_callback=self.music_callback)
		self.sound_stream = p.open(format=p.get_format_from_width(self.wf_sound.getsampwidth()), channels=self.wf_sound.getnchannels(), rate=self.wf_sound.getframerate(), output=True)

		next_beat_trigger_time = float(self.boxVRJson.get_beat_data_element(beat_index,'_triggerTime'))

		self.music_stream.start_stream()

		next_beat_energy_level = 4
		beat_index_mod = 0

		audio_thread = None
		while self.music_stream.is_active():
		
			next_beat_trigger_time = float(self.boxVRJson.get_beat_data_element(beat_index,'_triggerTime'))
			next_beat_energy_level = int(self.boxVRJson.get_beat_data_segment_element(beat_index,'_energyLevel'))

			self.current_time = self.wf_music.tell() / self.wf_music.getframerate()
			self.gui_callback_function(self.current_time - self.delay)

			if self.current_time > next_beat_trigger_time + self.delay:
				self.logger.debug("beat! index:{},current_time:{},trigger_time:{},energy_level:{}".format(beat_index,self.current_time,next_beat_trigger_time,next_beat_energy_level))
				beat_index_mod = beat_index % 4
				if next_beat_energy_level == 2:
					audio_thread = threading.Thread(target=self.beat_action,args=(self.sound_data,beat_index,))
					audio_thread.start()
				elif (next_beat_energy_level == 0 or next_beat_energy_level == 1 or next_beat_energy_level == 3) and (beat_index_mod == 0 or beat_index_mod == 1):
					audio_thread = threading.Thread(target=self.beat_action,args=(self.sound_data,beat_index,))
					audio_thread.start()
				elif (next_beat_energy_level == 3) and (beat_index_mod == 2 or beat_index_mod == 3):
					audio_thread = threading.Thread(target=self.beat_action,args=(self.punch_air_sound_data,beat_index,))
					audio_thread.start()
				else:
					self.beat_callback_function(beat_index)
				
				beat_index = beat_index + 1

		# stop stream (6)
		self.music_stream.stop_stream()
		self.music_stream.close()

