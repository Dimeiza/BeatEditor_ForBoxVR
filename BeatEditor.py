import PySimpleGUI as sg

from Music import Music
from BoxVRJson import BoxVRJson
import logging

boxVRJson = BoxVRJson()
music = Music()

edit = False

window = None
segment_table_heading = ['_startBeatIndex','_startTime','_length','_energyLevel','_numBeats','_averageEnergy','_index']
beat_table_heading =    ['_index','_triggerTime','_beatLength','_beatInBar','_magnitude','_bpm']

track_data_label_list = ['trackId','originalFilePath','originalTrackName','originalArtist','duration','firstBeatOffset','bpm']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def updateGUITable():

    for track_data_label in track_data_label_list:
        window[track_data_label].update(boxVRJson.get_track_data_element(track_data_label))

    beat_lists = []
    beat_count = boxVRJson.get_beat_count()
    for beat_index in range(beat_count):

        new_beat_entry = []        
        for i in range(0,len(beat_table_heading)):
            new_beat_entry.append(boxVRJson.get_beat_data_element(beat_index,beat_table_heading[i]))
        
        beat_lists.append(new_beat_entry)

    window['beats'].update(values=beat_lists)

    segment_lists = []
    segment_count = boxVRJson.get_segment_count()
    for segment_index in range(segment_count):

        new_segment_entry = []
        for i in range(0,len(segment_table_heading)):
            new_segment_entry.append(boxVRJson.get_segment_data_element(segment_index,segment_table_heading[i]))
        
        segment_lists.append(new_segment_entry)

    window['segmentList'].update(values=segment_lists)

def adjustFirstBeat():

    first_beat_offset = float(window['firstBeatOffset'].get())

    boxVRJson.adjust_first_beat_offset(first_beat_offset)

def update_json_value(table_name,row,col,value):

    if table_name == 'beats':
        update_target = beat_table_heading[col]
        boxVRJson.update_beat_list_value(update_target,row-1,value)

    elif table_name == 'segmentList':
        update_target = segment_table_heading[col]
        boxVRJson.update_segment_list_value(update_target,row-1,value)

    updateGUITable()

def edit_cell(window, table_name, row, col, justify='left'):

    global textvariable, edit

    def callback(event, row, col, text, key):
        global edit
        widget = event.widget
        if key == 'Return':
            text = widget.get()
            update_json_value(table_name,row,col,text)
        widget.destroy()
        widget.master.destroy()
        values = list(table.item(row, 'values'))
        values[col] = text
        table.item(row, values=values)
        edit = False

    if edit or row <= 0:
        return

    edit = True
    table = window[table_name].Widget
    root = table.master

    text = table.item(row, "values")[col]
    x, y, width, height = table.bbox(row, col)

    frame = sg.tk.Frame(root)
    frame.place(x=x, y=y, anchor="nw", width=width, height=height)
    textvariable = sg.tk.StringVar()
    textvariable.set(text)
    entry = sg.tk.Entry(frame, textvariable=textvariable, justify=justify)
    entry.pack()
    entry.select_range(0, sg.tk.END)
    entry.icursor(sg.tk.END)
    entry.focus_force()
    entry.bind("<Return>", lambda e, r=row, c=col, t=text, k='Return':callback(e, r, c, t, k))
    entry.bind("<Escape>", lambda e, r=row, c=col, t=text, k='Escape':callback(e, r, c, t, k))
    entry.bind("<Leave>", lambda e, r=row, c=col, t=text, k='Leave':callback(e, r, c, t, k))

def beat_callback_gui(beat_index):

    all_row = boxVRJson.get_beat_count()
    window['beats'].update(select_rows=[beat_index])
    scroll_percentage = beat_index/all_row

    window['beats'].set_vscroll_position(scroll_percentage)

    segment_row = boxVRJson.get_segment_number_from_beat_index(beat_index)
    window['segmentList'].update(select_rows=[segment_row])

    all_segment_row = boxVRJson.get_segment_count()

    segment_scroll_percentage = segment_row/all_segment_row - 0.1
    window['segmentList'].set_vscroll_position(segment_scroll_percentage)

    beatInBar = int(boxVRJson.get_beat_data_element(beat_index,'_beatInBar'))
    energyLevel = int(boxVRJson.get_beat_data_segment_element(beat_index,'_energyLevel'))

    window['left_glove'].update(visible=False)
    window['right_glove'].update(visible=False)
    window['ducking_left_glove'].update(visible=False)
    window['ducking_right_glove'].update(visible=False)

    if energyLevel == 0 or energyLevel == 1 or energyLevel == 3:
        if beatInBar == 1:
            window['left_glove'].update(visible=True)
        if beatInBar == 2:
            window['right_glove'].update(visible=True)
        if energyLevel == 3:
            if beatInBar == 3:
                window['ducking_left_glove'].update(visible=True)
            if beatInBar == 4:
                window['ducking_right_glove'].update(visible=True)

    elif energyLevel == 2:
        if beatInBar == 1 or beatInBar == 3:
            window['left_glove'].update(visible=True)
        if beatInBar == 2 or beatInBar == 4:
            window['right_glove'].update(visible=True)

    window['now_energy_level'].update(energyLevel)

def gui_callback_function(playtime):
    window['PlayTime'].update(playtime)

def build_GUI():

    global window
    global beat_table_heading
    global segment_table_heading

    track_basic_information_group = [
        [sg.Text("beatfile:"),sg.Input(key='_loaded_beat_file',enable_events=True,readonly=True),sg.Input(key='_save_target_beat_file',enable_events=True, visible=False)],
        [sg.Text("trackId:"),sg.Text("",key='trackId')],
        [sg.Text("originalFilePath:"),sg.Text(key='originalFilePath')] ,
        [sg.Text("originalTrackName:"),sg.Text(key='originalTrackName')]   ,
        [sg.Text("originalArtist:"),sg.Text(key='originalArtist')]   ,
        [sg.Text("firstBeatOffset:"),sg.Text(key='firstBeatOffset'),sg.Text("duration:"),sg.Text(key='duration'),sg.Text("bpm"),sg.Text(key='bpm')],
    ]

    track_control_group = [
        [sg.FileBrowse('load',target='_loaded_beat_file', file_types = (('BoxVR beat Files', '*.trackdata.txt'),)), sg.Button('play'),sg.Button('pause'),sg.Button('stop'),sg.FileSaveAs('save',target='_save_target_beat_file',file_types =  (('BoxVR beat Files', '*.trackdata.txt'),))],
    ]

    music_playpos_group = [
        [sg.Text('Position:'),sg.Text('',size=(20,1),key='PlayTime')],
        [sg.Text('BoxVR music start delay:'),sg.Text('',key='delay_time')],
    ]

    track_group = [
        [sg.Frame('',track_basic_information_group)],
        [sg.Frame('',track_control_group),sg.Frame('',music_playpos_group)]
    ]

    segment_width=[]
    for segment_label in segment_table_heading:
        segment_width.append(len(segment_label) + 3)

    segment_restructure_group = [
        [sg.Button('restruct with 16 beats',key='reconstruct_segment'),sg.Text('_averageEnergy(calories per beat):'),sg.Input('1.0',key='average_energy',size=(5,1)),sg.Text('_energyLevel:'),sg.Input('0',key='setEnergyLevel',size=(5,1))]
    ]


    segment_group = [
        [sg.Table([[]],headings=segment_table_heading,vertical_scroll_only=False,col_widths=segment_width,key='segmentList',auto_size_columns=False,enable_click_events=True)],
        [sg.Button('insert'),sg.Button('remove'),sg.Frame('restructure segment',segment_restructure_group)]    
    ]

    beat_width=[]
    for beat_label in beat_table_heading:
        segment_width.append(len(beat_label) + 3)

    all_beat_control_group = [
        [sg.Button('flat beatLength',key='flat_beat_length'),sg.Input('',key='beat_length_for_all',size=(20,1))]
    ]

    selected_beat_control_group = [
        [sg.Button('insert beat',key='insert_beat'),sg.Button('remove beat',key='remove_beat')],
        [sg.Button('double beatLength',key='double_beatlength'),sg.Button('half beatLength',key='half_beatlength')],
    ]

    first_beat_control_group = [
        [sg.Button('move next triggerTime',key='forward_first_beat_to_next'),sg.Button('back with own beatLength',key='back_first_beat_with_own_beatLength')],
    ]

    beat_control_group = [
        [sg.Frame('first beat',first_beat_control_group)],
        [sg.Frame('selected beat',selected_beat_control_group)],
        [sg.Frame('all baets',all_beat_control_group)],
    ]

    beat_group = [
        [sg.Table([[]],headings=beat_table_heading,vertical_scroll_only=False,col_widths=beat_width,key='beats',auto_size_columns=False,enable_click_events=True),sg.Frame('',beat_control_group)],
    ]

    ducking_left_glove_group = [[sg.Image(key='ducking_left_glove',source='res/ducking_left_glove.png',visible=False)]]
    ducking_right_glove_group = [[sg.Image(key='ducking_right_glove',source='res/ducking_right_glove.png',visible=False)]]

    left_glove_group = [[sg.Image(key='left_glove',source='res/left_glove.png',visible=False)]]
    right_glove_group = [[sg.Image(key='right_glove',source='res/right_glove.png',visible=False)]]

    glove_icon_group = [
        [sg.Frame('',ducking_left_glove_group,size=(64,64)),sg.Frame('',ducking_right_glove_group,size=(64,64))],
        [sg.Frame('',left_glove_group,size=(64,64)),sg.Frame('',right_glove_group,size=(64,64))],
        [sg.Text("energyLevel"),sg.Text(key='now_energy_level')],
    ]


    layout = [  [sg.Frame('track',track_group),sg.Frame('beat indication',glove_icon_group)],
                [sg.Frame('segment',segment_group)],
                [sg.Frame('beat',beat_group)],
            ]
    window = sg.Window('BeatEditor for BoxVR',layout,resizable=True)

def GUI_event_loop():

    table_beat_list_col = 0
    table_segment_list_col = 0
    current_time = 0

    while True:
        event, values = window.read()
        if event is None:
            break
        if event == sg.WINDOW_CLOSED or event == 'exit':
            break
        if event == '_loaded_beat_file':      
            music.stop()
            table_beat_list_col = 0
            table_segment_list_col = 0
            current_time = 0
            boxVRJson.loadboxVRJSON(values['_loaded_beat_file'])
            updateGUITable()
            music_file_path =window['originalFilePath'].get()
            music.set_boxVR_Json(boxVRJson)

            music.open_music_file(music_file_path)
            window['delay_time'].update(music.get_delay())

            window['beat_length_for_all'].update(boxVRJson.get_calc_average_beat_length())

        if event == 'play':
            music.stop()
            music.set_beat_callback(beat_callback_gui)
            music.set_gui_callback(gui_callback_function)
            if table_segment_list_col != 0:
                current_time = boxVRJson.get_segment_data_element(table_segment_list_col,'_startTime')
                music.set_paused_time(current_time)
            music.start()
        if event == 'pause':
            music.pause()
        if event == 'stop':
            music.stop()
        if event == '_save_target_beat_file':
            boxVRJson.saveboxVRJSON(values['_save_target_beat_file'])
        if event == 'reconstruct_segment':
            average_energy = float(window['average_energy'].get())
            energy_level = int(window['setEnergyLevel'].get())
            boxVRJson.reconstructSegment(16,average_energy,energy_level)
            updateGUITable()
        if event == 'remove':
            boxVRJson.remove_segment_from_segment_list(table_segment_list_col)
            updateGUITable()
        if event == 'insert':
            boxVRJson.insert_segment_to_segment_list(table_segment_list_col)
            updateGUITable()
        if event == 'remove_beat':
            boxVRJson.remove_beat_from_beat_list(table_beat_list_col)
            updateGUITable()

        if event == 'insert_beat':
            boxVRJson.insert_beat_from_beat_list(table_beat_list_col)
            updateGUITable()
        if event == 'double_beatlength':
            boxVRJson.multiply_selected_beat_length(table_beat_list_col,2.0)
            updateGUITable()
        if event == 'half_beatlength':
            boxVRJson.multiply_selected_beat_length(table_beat_list_col,0.5)
            updateGUITable()
        if event == 'forward_first_beat_to_next':
            boxVRJson.forward_first_beat_to_next_beat_timing()
            updateGUITable()

        if event == 'back_first_beat_with_own_beatLength':
            boxVRJson.back_first_beat_with_own_beatLength()
            updateGUITable()

        if event == 'flat_beat_length':
            beat_length_for_all = float(window['beat_length_for_all'].get())
            boxVRJson.flat_all_beat_length(beat_length_for_all)
            updateGUITable()

        elif isinstance(event, tuple):

            row, col = event[2]
            logging.debug("table:{},row:{},column:{}".format(event[0],row,col))

            if event[0] == 'segmentList' and type(row) == int and type(col) == int:
                table_segment_list_col = row
                edit_cell(window, event[0], row+1, col, justify='right')
            elif event[0] == 'beats' and type(row) == int and type(col) == int:
                table_beat_list_col = row
                edit_cell(window, event[0], row+1, col, justify='right')

def main():
    build_GUI()
    GUI_event_loop()
    window.close()

if __name__ == "__main__":
    main()
