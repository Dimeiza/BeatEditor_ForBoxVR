import json
import logging

class BoxVRJson:

    beat_data = {}
    track_data = {}
    NEW_SEGMENT_AVERAGE_ENERGY = 1.5

    logger = None
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # load JSON
    def loadboxVRJSON(self,filepath):

        with open(filepath,encoding="utf-8") as f:
            self.track_data = json.load(f)

        self.beat_data = json.loads(self.track_data['beatStrucureJSON'])
          
    # save JSON
    def saveboxVRJSON(self,filepath):
        output_json_file = open(filepath, mode="w", encoding="utf-8")

        self.track_data['beatStrucureJSON'] = json.dumps(self.beat_data)
        json.dump(self.track_data, output_json_file)
        output_json_file.close()


    # methods for track data
    def get_track_data_element(self,json_key_str):
        if json_key_str == 'trackId':
            return self.track_data['trackId'][json_key_str]
        else:
            return self.track_data[json_key_str]

    # methods for beat list

    def get_beat_data_element(self,beat_index,json_key_str):
        return self.beat_data['_beatList']['_beats'][beat_index][json_key_str]    

    def get_beat_count(self):
        return len(self.beat_data['_beatList']['_beats'])

    def multiply_selected_beat_length(self,beat_index,multiplier):

        self.beat_data['_beatList']['_beats'][beat_index]['_beatLength'] = float(self.beat_data['_beatList']['_beats'][beat_index]['_beatLength'] ) * multiplier

        self.adjust_beat_list()
        self.adjust_segment_list()
        self.write_segment_list_to_beat_list()

    def get_sum_of_beat_length(self,start_index,num_beats):

        sum_of_beat_length =0
        for beat in self.beat_data['_beatList']['_beats']:
            if start_index <= beat['_index'] and beat['_index'] < start_index + num_beats:
                sum_of_beat_length = sum_of_beat_length + beat['_beatLength']
        
        return sum_of_beat_length

    def get_calc_average_beat_length(self):

        beat_length_sum = 0
        for beat in self.beat_data['_beatList']['_beats']:
            beat_length_sum = beat_length_sum + float(beat['_beatLength'])
        
        return (beat_length_sum / len(self.beat_data['_beatList']['_beats']))

    def get_beat_data_segment_element(self,beat_index,json_key_str):
        return self.beat_data['_beatList']['_beats'][beat_index]['_segment'][json_key_str]    

    def remove_beat_from_beat_list(self,beat_index):

        index = self.beat_data['_beatList']['_beats'][beat_index]['_index']
        length = self.beat_data['_beatList']['_beats'][beat_index]['_beatLength']

        del self.beat_data['_beatList']['_beats'][beat_index]

        self.beat_data['_beatList']['_beats'][beat_index]['_index'] = index
        self.beat_data['_beatList']['_beats'][beat_index]['_beatLength'] = length + float(self.beat_data['_beatList']['_beats'][beat_index]['_beatLength'])

        self.adjust_beat_list()
        self.adjust_segment_list()
        self.write_segment_list_to_beat_list()

    def insert_beat_from_beat_list(self,beat_index):
        new_beat = {}
        new_beat['_index'] = int(self.beat_data['_beatList']['_beats'][beat_index]['_index'])
        new_beat['_beatInBar'] = int(self.beat_data['_beatList']['_beats'][beat_index]['_beatInBar'])
        new_beat['_magnitude'] = float(self.beat_data['_beatList']['_beats'][beat_index]['_magnitude'])
        new_beat['_triggerTime'] = float(self.beat_data['_beatList']['_beats'][beat_index]['_triggerTime'])
        new_beat['_beatLength'] = float(self.beat_data['_beatList']['_beats'][beat_index]['_beatLength']) / 2.0 
        new_beat['_bpm'] = float(self.beat_data['_beatList']['_beats'][beat_index]['_bpm'])
        new_beat['_isLastBeat'] = float(self.beat_data['_beatList']['_beats'][beat_index]['_isLastBeat'])

        # adjust triggerTime
        self.beat_data['_beatList']['_beats'][beat_index]['_triggerTime'] = float(self.beat_data['_beatList']['_beats'][beat_index]['_triggerTime']) + new_beat['_beatLength']

        # adjust beatLength
        self.beat_data['_beatList']['_beats'][beat_index]['_beatLength'] = float(self.beat_data['_beatList']['_beats'][beat_index]['_beatLength']) / 2.0 

        for i in range(beat_index,len(self.beat_data['_beatList']['_beats'])):
            # adjust index
            self.beat_data['_beatList']['_beats'][i]['_index'] = int( self.beat_data['_beatList']['_beats'][i]['_index']) + 1

        self.beat_data['_beatList']['_beats'].append(new_beat)

        self.adjust_beat_list()
        self.write_segment_list_to_beat_list()

    def update_beat_list_value(self,json_key_str,beat_index,value):
        self.beat_data['_beatList']['_beats'][beat_index][json_key_str] = value
        self.logger.debug(self.beat_data['_beatList']['_beats'][beat_index])
    
        self.adjust_beat_list()
        self.adjust_segment_list()
        self.write_segment_list_to_beat_list()

    def forward_first_beat_to_next_beat_timing(self):

        self.beat_data['_beatList']['_beats'][0]['_triggerTime'] = self.beat_data['_beatList']['_beats'][1]['_triggerTime']

        self.adjust_beat_list()
        self.adjust_segment_list()
        self.write_segment_list_to_beat_list()

    def back_first_beat_with_own_beatLength(self):

        first_beat_candidate_trigger_time = self.beat_data['_beatList']['_beats'][0]['_triggerTime'] -self.beat_data['_beatList']['_beats'][0]['_beatLength']

        # if first_beat_candidate_trigger_time > 0:
        self.beat_data['_beatList']['_beats'][0]['_triggerTime'] = first_beat_candidate_trigger_time

        self.adjust_beat_list()
        self.adjust_segment_list()
        self.write_segment_list_to_beat_list()


    def get_next_beat_index(self,current_time):

        for beat in self.beat_data['_beatList']['_beats']:
            if float(beat['_triggerTime']) > current_time:
                return beat['_index']

    def adjust_beat_list(self):

        self.beat_data['_beatList']['_beats'] = sorted(self.beat_data['_beatList']['_beats'],key= lambda x: int(x['_index']))
        for i in range(0,len(self.beat_data['_beatList']['_beats'])-1):
            self.logger.debug(self.beat_data['_beatList']['_beats'][i])

            # adjust triggertime
            trigger_time = float(self.beat_data['_beatList']['_beats'][i]['_triggerTime'])
            beat_length = float(self.beat_data['_beatList']['_beats'][i]['_beatLength'])
            next_trigger_time = self.beat_data['_beatList']['_beats'][i+1]['_triggerTime']

            if next_trigger_time != trigger_time + beat_length:
                self.beat_data['_beatList']['_beats'][i+1]['_triggerTime'] = trigger_time + beat_length

            # adjust beatInBar
            next_beat_in_bar = int( self.beat_data['_beatList']['_beats'][i]['_beatInBar']) + 1
            if next_beat_in_bar == 5:
                next_beat_in_bar = 1
            self.beat_data['_beatList']['_beats'][i+ 1]['_beatInBar'] = next_beat_in_bar

            # adjust indes
            next_index = int( self.beat_data['_beatList']['_beats'][i]['_index']) + 1
            self.beat_data['_beatList']['_beats'][i+ 1]['_index'] = next_index

    def flat_all_beat_length(self,beat_length_for_all):
        for beat in self.beat_data['_beatList']['_beats']:
            beat['_beatLength'] = beat_length_for_all

        self.adjust_beat_list()
        self.adjust_segment_list()
        self.write_segment_list_to_beat_list()

    # methods for segment list
    def get_segment_data_element(self,segment_index,json_key_str):
        return self.beat_data['_segmentList']['_segments'][segment_index][json_key_str]    

    def get_segment_count(self):
        return len(self.beat_data['_segmentList']['_segments'])

    def reconstructSegment(self,segment_num_beat,average_energy,energy_level):

        self.beat_data['_segmentList']['_segments'].clear()

        for beat in self.beat_data['_beatList']['_beats']:
            new_segment = {}
            if (beat['_index'] ) % segment_num_beat == 0:          
                new_segment['_startTime'] = float(beat['_triggerTime'])
                new_segment['_startBeatIndex'] = int(beat['_index'])
                new_segment['_numBeats'] = segment_num_beat
                new_segment['_length'] = self.get_sum_of_beat_length(int(beat['_index']),segment_num_beat)
                new_segment['_averageEnergy'] = average_energy
                new_segment['_index'] = 0
                new_segment['_energyLevel'] = energy_level
                self.logger.debug("index={},new segment:{}".format(beat['_index'],new_segment))

                self.beat_data['_segmentList']['_segments'].append(new_segment)

        self.logger.debug(self.beat_data['_segmentList']['_segments'])
        self.write_segment_list_to_beat_list()


    def get_segment_number_from_beat_index(self,beat_index):

        segment_index = 0
        for segment in self.beat_data['_segmentList']['_segments']:
            if int(segment['_startBeatIndex']) <= beat_index and beat_index < int(segment['_startBeatIndex']) + int(segment['_numBeats']):
                return segment_index
            
            segment_index = segment_index +1

        # if not found in segment_list
        return -1

    def update_segment_list_value(self,json_key_str,segment_index,value):

        self.beat_data['_segmentList']['_segments'][segment_index][json_key_str] = value

        self.adjust_segment_list()
        self.write_segment_list_to_beat_list()   

    def insert_segment_to_segment_list(self,segment_index):
        new_segment = {}
        new_segment['_startTime'] = float( self.beat_data['_segmentList']['_segments'][segment_index]['_startTime'])
        new_segment['_startBeatIndex'] = int( self.beat_data['_segmentList']['_segments'][segment_index]['_startBeatIndex'])
        new_segment['_numBeats'] = 1
        new_segment['_length'] = 1
        new_segment['_averageEnergy'] = self.NEW_SEGMENT_AVERAGE_ENERGY
        new_segment['_index'] = 0
        new_segment['_energyLevel'] = 0

        self.beat_data['_segmentList']['_segments'][segment_index]['_startTime'] = int(self.beat_data['_segmentList']['_segments'][segment_index]['_startTime']) + int(new_segment['_length'])
        self.beat_data['_segmentList']['_segments'][segment_index]['_startBeatIndex'] = int(self.beat_data['_segmentList']['_segments'][segment_index]['_startBeatIndex']) + int(new_segment['_numBeats'])
        self.beat_data['_segmentList']['_segments'][segment_index]['_numBeats'] = int(self.beat_data['_segmentList']['_segments'][segment_index]['_numBeats']) - int(new_segment['_numBeats'])

        self.beat_data['_segmentList']['_segments'].append(new_segment)

        self.adjust_segment_list()
        self.write_segment_list_to_beat_list()

    def remove_segment_from_segment_list(self,segment_index):
        num_beats = self.beat_data['_segmentList']['_segments'][segment_index]['_numBeats']
        length = self.beat_data['_segmentList']['_segments'][segment_index]['_length']

        del self.beat_data['_segmentList']['_segments'][segment_index]

        self.beat_data['_segmentList']['_segments'][segment_index]['_numBeats'] = num_beats + int(self.beat_data['_segmentList']['_segments'][segment_index]['_numBeats'])
        self.beat_data['_segmentList']['_segments'][segment_index]['_length'] = length + float(self.beat_data['_segmentList']['_segments'][segment_index]['_length'])

        self.adjust_segment_list()
        self.write_segment_list_to_beat_list()

    def write_segment_list_to_beat_list(self):

        for beat in self.beat_data['_beatList']['_beats']:
            segment_number = self.get_segment_number_from_beat_index(beat['_index'])
            if segment_number != -1:
                beat['_segment'] = self.beat_data['_segmentList']['_segments'][segment_number]
            else:
                self.logger.debug('error')

    def adjust_segment_list(self):

        self.beat_data['_segmentList']['_segments'] = sorted(self.beat_data['_segmentList']['_segments'],key= lambda x: int(x['_startBeatIndex']))

        for i in range(0,len(self.beat_data['_segmentList']['_segments'])-1):
            self.logger.debug(self.beat_data['_segmentList']['_segments'][i])

            # adjust start beat index
            start_beat_index = int(self.beat_data['_segmentList']['_segments'][i]['_startBeatIndex'])
            next_start_beat_index =  int(self.beat_data['_segmentList']['_segments'][i+1]['_startBeatIndex'])
            beat_num = int(self.beat_data['_segmentList']['_segments'][i]['_numBeats'])

            if start_beat_index + beat_num != next_start_beat_index:
                self.beat_data['_segmentList']['_segments'][i+1]['_startBeatIndex'] = start_beat_index + beat_num

            # adjust start time with beat list
            start_time =float(self.beat_data['_beatList']['_beats'][start_beat_index]['_triggerTime']) 
            length = self.get_sum_of_beat_length(start_beat_index,beat_num)
            
            self.beat_data['_segmentList']['_segments'][i]['_startTime'] = start_time
            self.beat_data['_segmentList']['_segments'][i]['_length'] = length