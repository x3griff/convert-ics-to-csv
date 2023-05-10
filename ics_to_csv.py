import os
import sys
import ics
import csv
import re

def convert_ics_to_string(filename: str) -> str:
    # open the ICS file and write contents to string
    with open(filename, 'r') as calendar_file:
        lines = calendar_file.readlines()
        if lines[0] != "BEGIN:VCALENDAR\n" or lines[len(lines)-1]!="END:VCALENDAR\n":
            raise Exception("This isn't a valid ICS file")
        calendar_string = ''
        for line in lines:
            calendar_string += line
    return calendar_string

def multi_replace(dict, text):
  if text is not None:
    # Create a regular expression from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 
  else:
    return text
  
def make_event_list(calendar_string: str) -> list:
    #uses ics library to turn calendar string into object
    try:
        calendar = ics.Calendar.parse_multiple(calendar_string)
    except ics.grammar.parse.ParseError:
        raise

    # calling with [0] because calendar is a list with a single Calendar object
    events = calendar[0].events 

    # create list where each item will be a line in the csv output
    events_csv_list = [["Date", "Name", "Description"]] 

    # create a dictionary of text to be replaced in fields
    replacement_text = {
        "\n" : " ",
        "  " : " "
    }

    # loop through event set
    # get date of event (in this case, events are all one day so the begin date is enough)
    # get the event name and description
    # replace repeating text in description field 
    for event in events:
        start = event.begin
        date = f"{start.year}-{start.month:02d}-{start.day:02d} {start.hour:02d}:{start.minute:02d}"
        name = event.name
        description = multi_replace(replacement_text, event.description)
        events_csv_list.append([date, name, description])
    return events_csv_list

def convert_list_to_csv(events_csv_list: list, output_name: str,) -> None:
    # write the list to csv output
    with open(output_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(events_csv_list)

if __name__ == "__main__":
    calendar_string = convert_ics_to_string(sys.argv[1])
    event_list = make_event_list(calendar_string)
    base_file_path = os.path.splitext(sys.argv[1])[0]
    convert_list_to_csv(event_list, os.path.splitext(sys.argv[1])[0] + ".csv")




