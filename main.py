from tkinter import *
from tkinter import ttk
import time
import os
import csv
import shutil
import sys
import threading
import configparser

######### Made by Liam Lawes
program_version_number = '0.2.7.250106' + ' - Beta'
###########################

### Default Vars ###
_default_option_string = "-- Select --"
_file_timesheet = 'timesheet.csv'
_file_billers = 'billers.csv'

### INIT Load program in own directory ##
if getattr(sys, 'frozen', False):
    install_location = os.path.dirname(sys.executable) + "\\"
else:
    install_location = os.path.dirname(__file__) + "\\"

os.chdir(install_location)

### Class ###
class TK_Window:
    def __init__(self, xgeo, ygeo, title):
        self.xgeo = xgeo
        self.ygeo = ygeo
        self.title = title

    def spawn_window(self):
        window = Tk()
        screen_width = window.winfo_screenwidth()  # 1920
        screen_height = window.winfo_screenheight() # 1080
        x_offset = screen_width - (self.xgeo*1.1)
        y_offset = screen_height - (self.ygeo*1.3)
        window.attributes('-topmost', True)
        window.geometry(f'{self.xgeo}x{self.ygeo}+{str(int(x_offset))}+{str(int(y_offset))}')
        window.title(self.title)
        window.iconbitmap(install_location+'micon.ico')  # Set icon for application
        wframe = ttk.Frame(window, padding=15)
        wframe.grid()
    
        return window, wframe
    

### GUI SPAWN FUNCTIONS ###
def error_window_spawn(error_title, error_text):
    error_message = TK_Window(400, 100, f'{error_title}')
    error_window, error_frame = error_message.spawn_window()
    ttk.Label(error_frame, text=f"{error_text}").grid(column=0, row=0)
    ttk.Button(error_frame, text="Ok", command=error_window.destroy).grid(column=0, row=1)
    error_window.mainloop()

# -- MAIN WINDOW FUNCTION --
def main_window_spawn(_file_target, _timeslot_target, text_message):

    # Function to execute timeslot update
    def update_bill():

        # Extra inbedded function for window detroyer
        def destroy_all():
            try: 
                main_window.destroy()
                confirm_window.destroy()

            except Exception: 
                pass
        #

        answer_one = billing_choice_one.get()
        answer_two = billing_choice_two.get()
        answer_notes = billing_note.get()

        # Ensure default option has not been submitted.
        if answer_one == _default_option_string or answer_two == _default_option_string:
            error_window_spawn("ERROR", "Please select a billing option.")
            return


        if csv_writer(_file_target, _timeslot_target, answer_one, answer_two, answer_notes):
            # Check that default option has been chosen.
            confirm_message = TK_Window(500, 100, 'Billing Confirmed')
            confirm_window, confirm_frame = confirm_message.spawn_window()
            ttk.Label(confirm_frame, text=f"BILLING COMPLETE - You billed {answer_two} for {answer_one} successfully.").grid(column=0, row=0)
            ttk.Button(confirm_frame, text="Ok", command=destroy_all).grid(column=0, row=1)
            confirm_window.mainloop()

        else:
            error_window_spawn(f"Error", "Error writing timeslot.")
        #

    def update_timeslot():

        def execute_update():

            def destroy_all():
                try: 
                    uts_confirm_window.destroy()
                    update_ts_window.destroy()

                except Exception: 
                    pass

            update_ts_time = update_ts_choice.get()
            answer_one = billing_choice_one.get()
            answer_two = billing_choice_two.get()
            answer_notes = billing_note.get()

            for row in current_schedule_cells: 
                if row['_time'] in update_ts_time:
                    _timeslot_target = row['_time']

            try:
                if csv_writer(_file_target, _timeslot_target, answer_one, answer_two, answer_notes):
                # Check that default option has been chosen.
                    uts_confirm_message = TK_Window(500, 150, 'Billing Confirmed')
                    uts_confirm_window, uts_confirm_frame = uts_confirm_message.spawn_window()
                    ttk.Label(uts_confirm_frame, text=f"Timeslot has been updated successfully!").grid(column=0, row=0)
                    ttk.Button(uts_confirm_frame, text="Ok", command=destroy_all).grid(column=0, row=1)
                    uts_confirm_window.mainloop()

                else:
                    error_window_spawn('Error', 'Unable to write timeslot.')

            except UnboundLocalError: 
                error_window_spawn('Error', 'You need to choose a Timeslot to update.')
        
        current_schedule_cells = csv_reader(_file_target)

        update_ts_message = TK_Window(600, 175, 'Update Timeslot')
        update_ts_window, update_ts_frame = update_ts_message.spawn_window()

        # Making Options for update timeslot func
        update_ts_options = [_default_option_string]
        update_ts_choice = StringVar(update_ts_window)

        billing_choice_one = StringVar(update_ts_window)
        billing_choice_two = StringVar(update_ts_window)
        billing_note = StringVar(update_ts_window)
        billing_choice_one.set(bco_options[0])         # Default value
        billing_choice_two.set(bct_options[0])  

        for row in current_schedule_cells: 
            if len(row['_billing_one']) >= 1:
                update_ts_options.append(row['_time']+" - "+row['_billing_one'] + " - "+ row['_notes'])

        ## Update Timeslot Window LAYOUT
        ttk.Label(update_ts_frame, text=f"Choose a Timeslot from today to update!").grid(column=0, row=0)
        ttk.Label(update_ts_frame, text=f"Timeslots: ").grid(column=0, row=1)
        ttk.OptionMenu(update_ts_frame, update_ts_choice, *update_ts_options).grid(column=1, row=1)
        ttk.Label(update_ts_frame, text="").grid(column=0, row=2)
        ttk.OptionMenu(update_ts_frame, billing_choice_one, *bco_options).grid(column=0, row=3)
        ttk.OptionMenu(update_ts_frame, billing_choice_two, *bct_options).grid(column=1, row=3)
        ttk.Label(update_ts_frame, text=f"Notes  --> ").grid(column=0, row=4)
        ttk.Entry(update_ts_frame, textvariable=billing_note).grid(column=1, row=4)
        ttk.Button(update_ts_frame, text="Update Time", command=execute_update).grid(column=0, row=5)
        ttk.Button(update_ts_frame, text="Exit", command=update_ts_window.destroy).grid(column=1, row=5)

        update_ts_window.mainloop()

    # Calculate total hours worked so far 
    total_hours_worked = calc_work_time(_file_target)

    ### Main Window Function Start/Spawn
    main_message = TK_Window(600, 225, 'Account A Bill')
    main_window, main_frame = main_message.spawn_window()  
    
    ## Main Windows options load
    bco_options = [_default_option_string] # Billing choice options one list.
    bct_options = [_default_option_string] # Billing choice options two list.
    billing_choice_one = StringVar(main_window)
    billing_choice_two = StringVar(main_window)
    billing_note = StringVar(main_window)

    current_schedule_cells = csv_reader(_file_target)
    for row in current_schedule_cells:
        if row['_time'] in _timeslot_target:
            last_slot = row
            place = last_slot['row_no']
            the_last_row_recorded = place - 1
    
    for row in current_schedule_cells:
        if row['row_no'] == the_last_row_recorded and len(row['_billing_one']) >= 1:
            bco_options = [row['_billing_one']] # Billing choice options one list.
            bct_options = [row['_billing_two']] # Billing choice options two list.
            billing_choice_one.set(row['_billing_one'])
            billing_choice_two.set(row['_billing_two'])
        else:
            billing_choice_one.set(bco_options[0])         # Default value
            billing_choice_two.set(bct_options[0])         # Default value

    bc_cells = csv_reader(_file_billers)
    for row in bc_cells:
        if row['ï»¿Catergory_one'] != None: 
            bco_options.append(row['ï»¿Catergory_one'])
        if row['Catergory_two'] != None and len(row['Catergory_two']) > 0:
            bct_options.append(row['Catergory_two'])
    
    ## Main Window LAYOUT
    ttk.Label(main_frame , text=text_message).grid(column=0, row=0)
    ttk.Label(main_frame , text=' ').grid(column=0, row=1)
    ttk.OptionMenu(main_frame , billing_choice_one, *bco_options).grid(column=0, row=2)
    ttk.OptionMenu(main_frame , billing_choice_two, *bct_options).grid(column=1, row=2)
    ttk.Label(main_frame, text=' ').grid(column=0, row=3)
    ttk.Label(main_frame, text='Notes  --> ').grid(column=0, row=4)
    ttk.Entry(main_frame, textvariable=billing_note).grid(column=1, row=4) 
    ttk.Button(main_frame , text="Submit", command=update_bill).grid(column=0, row=6)
    ttk.Button(main_frame , text="Quit", command=main_window.destroy).grid(column=1, row=6)
    ttk.Label(main_frame, text=" ").grid(column=0, row=7)
    ttk.Label(main_frame, text=" ").grid(column=0, row=8)
    ttk.Label(main_frame, text=f"Hours you have billed today:       {total_hours_worked[0]} /hrs").grid(column=0, row=9)
    ttk.Button(main_frame , text="Update a Previous Timeslot", command=update_timeslot).grid(column=0, row=10)
    
    main_window.mainloop()

### OPERATIONAL FUNCTIONS
# csv_reader() - created dictonary list from csv file.
def csv_reader(the_csv):
    read_list = []
    row_count = 0
    with open(the_csv, newline='') as cfile:
        reader = csv.DictReader(cfile)
        for row in reader:

            ## Adding extra error catch for adding 0 to time before 10am in timesheet csv
            if '_time' in row:
                if len(row['_time']) <= 4:
                    row['_time'] = '0' + row['_time']
            else:
                pass
            ##

            row_count += 1
            row["row_no"] = row_count
            read_list.append(row)
        return read_list

# Function built for updating specific csv cells 
def csv_writer(the_csv, the_time_value, new_biller1_value, new_biller2_value, new_notes_value):
    rows = []
    executed = False
        # Read existing rows
    with open(the_csv, newline='') as cfile:
        reader = csv.DictReader(cfile)
        for row in reader:

            ## Adding extra error catch for adding 0 to time before 10am in timesheet csv
            if '_time' in row:
                if len(row['_time']) <= 4:
                    row['_time'] = '0' + row['_time']
            else:
                pass
            ##
            
            if the_time_value == row['_time']:
                row['_billing_one'] = new_biller1_value
                row['_billing_two'] = new_biller2_value
                row['_notes'] = new_notes_value
                executed = True
            rows.append(row)

    # Writes back to file   
    with open(the_csv, 'w', newline='') as cfile:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(cfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


    return executed

# Function to assit get_rounded_time() function.
def round_down(x, base=15):
    return base * (x // base)

# Fucntion to round time to nearest 15 min interval
def get_rounded_time():
    read_hour = int(time.strftime("%H"))
    read_minute = int(time.strftime("%M"))

    # Round down the minutes to the nearest 15
    rounded_minute = round_down(read_minute)

    if rounded_minute == 0:
        if read_minute < 15:
            rounded_hour = read_hour  # Keep the same hour
        else:
            rounded_hour = (read_hour - 1) % 24  # Decrement hour and wrap around if necessary
    else:
        rounded_hour = read_hour

    return f"{rounded_hour:02}:{rounded_minute:02}"

# Function to check and create csv timesheet files in the timesheet directory
def check_or_make_schedule():
    # Checks 'timesheet' folder is created or creates one.
    timesheet_directory = f"{install_location}"+"timesheets\\"
    try:
        os.chdir(timesheet_directory)
    except FileNotFoundError:
        os.mkdir("timesheets")
        try:
            os.chdir(timesheet_directory)
        except Exception:
            return

    # Defines lists, date and time vars for function
    the_template = install_location + _file_timesheet
    the_year = time.strftime("%Y")
    the_month = time.strftime("%m")
    directory_list = []
    directory_scan = os.listdir()
    _file_todays_schedule = f'AAB_Minutes_{time.strftime("%d-%m-%Y")}.csv'

    # Enumerates all folders in 'timesheet' folder
   
    for directory in directory_scan:
        if os.path.isdir(directory):
            directory_list.append(directory)
    

    # Checks there is atleast one folder
    list_check = len(directory_list)
    if list_check <= 0:
        print(f"ERROR: No {the_year} directories found in scan.")
        #os.system(f'mkdir {the_month}-{the_year}')
    
    # Completes file creation
    for directory in directory_list:
        if directory == f"{the_month}-{the_year}":
            target_location = timesheet_directory + f"{directory}\\" + _file_timesheet
            os.chdir(timesheet_directory + f"{directory}\\")
            returned_location = timesheet_directory + f"{directory}\\" + _file_todays_schedule  # Returning value out of function for use.
            try:
                shutil.copy(the_template, target_location)
                os.rename(_file_timesheet, _file_todays_schedule)         
            except FileExistsError:
                os.remove(_file_timesheet)
                pass
    
    os.chdir(install_location)
    try:
        return returned_location
    
    except UnboundLocalError: 
        print(f"ERROR: This error is most likely cause by not having folder for the current month in you 'timesheets' folder.")
        print(f'SYSTEM: All directories have been automatically created.')
        new_month = f"{timesheet_directory}"+f"{the_month}-{the_year}"
        os.mkdir(new_month)
        returned_location = check_or_make_schedule()
        #print("SYSTEM: New directory automatically created, please restart program.")
        return returned_location

# Function to check start time and amend any missing timeslots
def find_missing_slot(target_file): 
    rounded_time = get_rounded_time()
    starting_time_guess_list = []
    current_timesheet_cells = csv_reader(target_file)

    for row in current_timesheet_cells:
        if len(row['_billing_one']) >= 1:
            starting_time_guess_list.append(row)

    if len(starting_time_guess_list) <= 0:
        return
    
    for row in current_timesheet_cells:
        if row['_time'] in rounded_time:
            current_timeslot_row_number = int(row['row_no']) + 1
        
    # Error catch if there is no missed time
    try:
        start_time_row = starting_time_guess_list[0]
        start_time_row_number = int(start_time_row['row_no'])

    except IndexError:
        pass
    
    missing_rows = [] 

    for row in current_timesheet_cells: 
         # billing_one has no data    and    ro no. is high than start time row no.   and    row no. is less then current row no.
        if len(row['_billing_one']) <= 0 and int(row['row_no']) >= start_time_row_number and int(row['row_no']) < current_timeslot_row_number:
            missing_rows.append(row)

    return missing_rows

def calc_work_time(target_file):
    total_hour_count = 0
    current_timesheet_cells = csv_reader(target_file)
    work_slots = []
    break_slots = []

    # Build list and calculate work hours.
    for row in current_timesheet_cells:
        if len(row['_billing_one']) >= 1:
            work_slots.append(row)
            if 'On Break' not in row['_billing_one']:
                total_hour_count += 1
            elif 'On Break' in row['_billing_one']:
                break_slots.append(row)

    try:
        start_time_slot = work_slots[0]
        start_time = start_time_slot['_time']
        start_time_row = start_time_slot['row_no']

        last_slot = work_slots[-1]

    except IndexError:
        start_time = None
        

    try:
        break_start_slot = break_slots[0]
        break_start = break_start_slot['_time']

        break_last_slot = break_slots[-1]

    except IndexError:
        break_start = None
        
    try:
        if last_slot is not None:
            working_hours = float(GBVAR_working_hours)
            remaining_work_slots = working_hours/0.25
            finish_time_row = (start_time_row + remaining_work_slots) + len(break_slots)

            for row in current_timesheet_cells:
                if finish_time_row == row['row_no']:
                    finish_time = row['_time']

        else:
            pass

    except UnboundLocalError:
        last_slot = None
        finish_time = None

    if len(break_slots) >= 1:
        for row in current_timesheet_cells:
            if break_last_slot['_time'] in row['_time']:
                break_finish_row_number = int(row['row_no']) + 1

        for row in current_timesheet_cells:
            if break_finish_row_number == row['row_no']:
                break_finish = row['_time']
    else:
        break_finish = None

    total_hours = ((total_hour_count * 15) / 60)
    
    return total_hours, start_time, finish_time, break_start, break_finish

def calc_biller_time(target_file, biller, key):
    current_timesheet_cells = csv_reader(target_file)
    counter = 0

    for row in current_timesheet_cells:
        if biller == row[key]:
            counter += 1

    total_time =  ((counter * 15) / 60)
    
    return total_time

def get_totals(target_file, totals_date):
    
    class Catergory:
        def __init__(self, name, list, key, counter):
            self.name = name
            self.list = list
            self.key = key
            self.counter = counter
            
    cat_one = Catergory('one', [], 'ï»¿Catergory_one', 0)
    cat_two = Catergory('two', [], 'Catergory_two', 0)
    
    billers_csv = csv_reader(_file_billers)

    for row in billers_csv: # not amendedin cat_one.list with only 'Standard Billing' 
        cat_one.list.append(row[cat_one.key])
    
    for row in billers_csv:
        cat_two.list.append(row[cat_two.key])

    total_hours_worked, start_time, end_time, break_start_time, break_end_time = calc_work_time(target_file)

    totals_message = TK_Window(600, 275, f'Working Totals for {totals_date}')
    totals_window, totals_frame = totals_message.spawn_window()
    
    for cat_one_biller in cat_one.list:
        if len(cat_one_biller) >= 1:
            biller_time = calc_biller_time(target_file, cat_one_biller, '_billing_one') 
            ttk.Label(totals_frame, text=f"{cat_one_biller}:       {biller_time}  /hrs").grid(column=0, row=cat_one.counter)
            cat_one.counter += 1
        
    for cat_two_biller in cat_two.list:
        if len(cat_two_biller) >= 1:
            biller_time = calc_biller_time(target_file, cat_two_biller, '_billing_two')
            ttk.Label(totals_frame, text=f"{cat_two_biller}:       {biller_time}  /hrs").grid(column=1, row=cat_two.counter)
            cat_two.counter += 1

    ttk.Label(totals_frame, text=f" ").grid(column=0, row=(cat_one.counter + 1))
    ttk.Label(totals_frame, text=f"Total hours you have billed:       {total_hours_worked} /hrs").grid(column=0, row=(cat_one.counter + 2))
    ttk.Label(totals_frame, text=f" ").grid(column=0, row=(cat_one.counter + 3))
    ttk.Label(totals_frame, text=f"Starting Time: {start_time}").grid(column=0, row=(cat_one.counter + 4))
    ttk.Label(totals_frame, text=f"Finishing Time: {end_time}").grid(column=0, row=(cat_one.counter + 5))
    ttk.Label(totals_frame, text=f"Break Start: {break_start_time}").grid(column=1, row=(cat_one.counter + 4))
    ttk.Label(totals_frame, text=f"Break Finish: {break_end_time}").grid(column=1, row=(cat_one.counter + 5))
    ttk.Label(totals_frame, text=f" ").grid(column=0, row=(cat_one.counter + 6))
    ttk.Button(totals_frame, text="Ok", command=totals_window.destroy).grid(column=0, row=(cat_one.counter + 7))

    totals_window.mainloop()

def find_work_times():

    def spawn_times():

        # Data input check
        the_day = day_entry.get().strip()
        the_month = month_entry.get().strip()
        the_year = year_entry.get().strip()

        if the_day >= '32' or the_day <= '0' or len(the_day) >= 3 or len(the_day) <= 0: 
            error_window_spawn('Error', 'Please select a day between 1 - 31.')
            return

        if the_month >= '13' or the_month <= '0' or len(the_month) >= 3 or len(the_month) <= 0:
            error_window_spawn('Error', 'Please select a month between 1 - 12.')
            return

        if len(the_year) != 4:
            error_window_spawn('Error', 'Please input just 4 digits for the year.')
            return

        # file
        totals_date = f'{the_day}-{the_month}-{the_year}'
        search_location = install_location + 'timesheets\\' + f'{the_month}-{the_year}\\'
        try:
            os.chdir(search_location)

        except FileNotFoundError:
            error_window_spawn('Error', f'Could not find the month folder: {the_month}-{the_year}')
            return

        
        for file in os.listdir():
            if totals_date in file:
                the_target = search_location+file
                
        os.chdir(install_location)

        try:
            get_totals(the_target, totals_date)
        except UnboundLocalError:
            error_window_spawn('Error', f'There is no file with the date: {totals_date}')
        
    worktimes_message = TK_Window(450, 150, 'Find Past Totals')
    worktimes_window, worktimes_frame = worktimes_message.spawn_window()

    day_entry = StringVar(worktimes_window)
    month_entry = StringVar(worktimes_window)
    year_entry = StringVar(worktimes_window)

    ttk.Label(worktimes_frame, text=f"Enter Day:").grid(column=0, row=1)
    ttk.Label(worktimes_frame, text=f"Enter Month:").grid(column=1, row=1)
    ttk.Label(worktimes_frame, text=f"Enter Year:").grid(column=2, row=1)
    
    ttk.Entry(worktimes_frame, textvariable=day_entry).grid(column=0, row=2)
    ttk.Entry(worktimes_frame, textvariable=month_entry).grid(column=1, row=2)
    ttk.Entry(worktimes_frame, textvariable=year_entry).grid(column=2, row=2)

    
    ttk.Button(worktimes_frame, text="Find", command=spawn_times).grid(column=0, row=3)
    ttk.Button(worktimes_frame, text="Close", command=worktimes_window.destroy).grid(column=1, row=3)
    worktimes_window.mainloop()

def config_ini():
    def create_config():
        try:
            os.remove(cfg_file)
        except FileNotFoundError:
            pass
        os.system(f'echo > {cfg_file}')
        with open(cfg_file, 'w') as new_cfg:
            config[SECTION] = default_cfg_content
            config.write(new_cfg)
            print('New Configuration has been successfully created.')
            new_cfg.close()

    def read_config():
        with open(cfg_file, 'r') as config_choices:
            config.read(cfg_file)
            if config.has_section(SECTION) and config.has_option(SECTION, WH_KEY):
                print('Configuration loaded successfully.')
                global GBVAR_working_hours
                GBVAR_working_hours = config[SECTION][WH_KEY]

            else:
                print('Error reading configuration, attempting to return configuration to default.')
                config_choices.close()
                create_config()
                read_config()

    config = configparser.ConfigParser()
    SECTION = 'CONFIG'
    WH_KEY = 'working hours'
    cfg_file = 'cfg.ini'

    default_cfg_content = {
        f'{WH_KEY}':'7',
    }

    try:
        with open(cfg_file):
            pass
    except FileNotFoundError: 
        create_config()
    
    read_config()

### MAIN THREAD FUNCTIONS
def auto_pop(target_file):
    while True:
        current_time = time.strftime("%H:%M")
        rounded_time = get_rounded_time() 

        # Run check to see if current timeslot is populated.
        if current_time == rounded_time:  
            current_timesheet_cells = csv_reader(target_file)
            for row in current_timesheet_cells:
                if row['_time'] == rounded_time:
                    current_timeslot = row
                    if len(current_timeslot['_billing_one']) >= 1:
                        pass    

                    else:
                        msg_text=f"Please submit billing for timeslot starting from {rounded_time}."
                        main_window_spawn(target_file, rounded_time, msg_text)

        # If populated, additional check below to ensure a previous timeslot has not been missed in the day.
        missing_rows = find_missing_slot(target_file)
        
        try:
            if len(missing_rows) >= 1:
                for row in missing_rows:
                    missing_time_slot = row['_time']
                    msg_text = f'Timeslot Missed! Please submit billing for timeslot starting from {missing_time_slot}.'
                    main_window_spawn(target_file, missing_time_slot, msg_text)
                    
        except TypeError:
            pass

        # Wait before checking again
        time.sleep(5)

def command_line(target_file): 
    while True:
        user_input = input('Command: ').strip()
        if user_input.lower() in ['help', '?']:
            print("""\n--- Help Menu ---
'update'        - To update a timeslot.
'totals'        - To calculate todays daily totals.
'find'          - To find daily totals for another date.
'time'          - To check the current timeslot.
'config'        - To open configuration file.
'h' / 'help'    - for Help.
'clear' / 'cls' - to clear data in Terminal.
'exit' / 'quit' - to Exit the program.  
------------------\n""")

        elif user_input.lower() in ['exit', 'quit']:
            input_confirm = input('Are you sure you want to quit (y/n): ')
            if input_confirm.lower() in ['yes', 'y']:
                print('Program is shutting down...')
                time.sleep(0.5)
                quit()
            else:
                print('Type "yes" after exit command to shutdown program.')
                pass

        elif user_input.lower() in ['cls', 'clear']:
            os.system('cls')
            print("AAB Start Success - Type 'exit' to stop this program.")
            print('Version: ' + program_version_number)

        elif user_input.lower() in ['update']:
            rounded_time = get_rounded_time()
            msg_text = f'Update the last timeslot starting from {rounded_time}.'
            main_window_spawn(target_file, rounded_time, msg_text)

        elif user_input.lower() in ['totals']:
            the_date = time.strftime("%d/%m/%Y")
            get_totals(target_file, the_date)

        elif user_input.lower() in ['time']:
            rounded_time = get_rounded_time()
            error_window_spawn('Current Timeslot Check', f'The current timeslot is: {rounded_time}')
        
        elif user_input.lower() in ['find', 'pasttotals']:
            find_work_times()

        elif user_input.lower() in ['config', 'cfg']:
            os.system('start cfg.ini')
            print('\nPlease remember to restart the program after updating the config file.\n')

        else: 
            print('Please type "help" for options.')
  
## End of functions 


### Program Loop ###
if __name__ in "__main__":
    target_file = check_or_make_schedule()
    config_ini()
    print("AAB Start Program Success - Type 'exit' to stop this program.")
    print('Version: ' + program_version_number)

    #### DEVELOPMENT
    main_thread = threading.Thread(target=auto_pop, args=(target_file,)) #, args=(target_file))
    main_thread.daemon = True
    main_thread.start()
    command_line(target_file)
    #### 
    

##########
## DEV NOTES 
##########
# * Add configuration file for managing directories. 
# * Finish cmd line threading



    

    
        

