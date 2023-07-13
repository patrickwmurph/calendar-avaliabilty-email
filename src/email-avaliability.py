from __future__ import print_function

import subprocess
import re
import datetime
import os.path
import calendar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def main():
    output = ''  # Variable to store the output
    
    creds = None
    if os.path.exists('../tokens/token.json'):
        creds = Credentials.from_authorized_user_file('../tokens/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('../tokens/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('../tokens/token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('calendar', 'v3', credentials=creds)

        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")

        time_min = datetime.datetime.strptime(start_date, "%Y-%m-%d").isoformat() + 'Z'
        time_max = datetime.datetime.strptime(end_date, "%Y-%m-%d").isoformat() + 'Z'
        print(f"Getting availability from {start_date} to {end_date}\n")

        events_result = service.events().list(calendarId='primary', timeMin=time_min,
                                              timeMax=time_max, maxResults=10,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        all_dates = set()
        current_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        while current_date <= datetime.datetime.strptime(end_date, "%Y-%m-%d"):
            all_dates.add(current_date.strftime("%Y-%m-%d"))
            current_date += datetime.timedelta(days=1)

        availability = []
        for date in all_dates:
            # Convert date to day of the week and month/day format
            dt = datetime.datetime.strptime(date, "%Y-%m-%d")
            day_of_week = calendar.day_name[dt.weekday()]
            month_day = dt.strftime("%-m/%-d")
            
            # Check if there are events for the day
            found_event = False
            event_end_times = []  # List to store the end times of events
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                event_date = start.split('T')[0]
                if event_date == date:
                    found_event = True
                    event_end_time = event['end'].get('dateTime', event['end'].get('date')).split('T')[1][:5]
                    event_end_times.append(event_end_time)
            
            # Output available time blocks
            if found_event:
                if event_end_times:
                    event_end_times.sort()
                    start_time = "09:00"
                    available_times = []
                    for end_time in event_end_times:
                        if start_time != end_time and start_time < end_time:
                            available_times.append(f"{start_time} - {end_time}")
                        start_time = end_time
                    if start_time < "17:00":
                        available_times.append(f"{start_time} - 17:00")
                    
                    # Exclude busy time slots within the available times
                    if len(available_times) > 1:
                        busy_times = []
                        for event in events:
                            start = event['start'].get('dateTime', event['start'].get('date'))
                            event_date = start.split('T')[0]
                            if event_date == date:
                                busy_start_time = start.split('T')[1][:5]
                                busy_end_time = event['end'].get('dateTime', event['end'].get('date')).split('T')[1][:5]
                                busy_times.append((busy_start_time, busy_end_time))
                        
                        trimmed_available_times = []
                        for time_slot in available_times:
                            slot_start_time = time_slot.split(' - ')[0]
                            slot_end_time = time_slot.split(' - ')[1]
                            for busy_slot in busy_times:
                                busy_start_time = busy_slot[0]
                                busy_end_time = busy_slot[1]
                                if busy_start_time < slot_end_time and busy_end_time > slot_start_time:
                                    if slot_start_time < busy_start_time:
                                        trimmed_available_times.append(f"{slot_start_time} - {busy_start_time}")
                                    if slot_end_time > busy_end_time:
                                        slot_start_time = busy_end_time
                            if slot_start_time < slot_end_time:
                                trimmed_available_times.append(f"{slot_start_time} - {slot_end_time}")
                        
                        available_times = trimmed_available_times
                    
                    availability.append((day_of_week, month_day, available_times))
            else:
                availability.append((day_of_week, month_day, ["9:00 - 17:00"]))
        
        # Sort availability by day
        availability.sort(key=lambda x: datetime.datetime.strptime(x[1], "%m/%d"))
        
        # Generate the formatted output with AM/PM format
        for day, date, times in availability:
            formatted_times = []
            for time_slot in times:
                start_time, end_time = time_slot.split(' - ')
                start_time = datetime.datetime.strptime(start_time, "%H:%M").strftime("%I:%M %p")
                end_time = datetime.datetime.strptime(end_time, "%H:%M").strftime("%I:%M %p")
                formatted_times.append(f"{start_time} - {end_time}")
            output += f"{day} {date} " + ', '.join(formatted_times) + '\n'

    except HttpError as error:
        output += 'An error occurred: %s\n' % error
    
    lines = output.split('\n')
    updated_lines = []

    for line in lines:
        if line.strip() != '':
            parts = line.split(',')
            updated_parts = []
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    updated_parts.append(part.strip())
            updated_line = ', '.join(updated_parts)
            updated_lines.append(updated_line)

    updated_availability = '\n'.join(updated_lines)
    
    lines = updated_availability.split('\n')
    start_times = []
    result = []
    for line in lines:
        start_times.clear()
        
        dotw_date = re.findall('\w+\s\d+/\d+', line)
        intervals = re.findall('\d{2}:\d{2}\s\w{2}\s-\s\d{2}:\d{2}\s\w{2}', line)
        
        for interval in intervals :
            duplicate_index = None
            start_time = re.findall('(\S+\s\S+)\s-\s(\S+\s\S+)', interval)[0][0]
            if start_time not in start_times :
                start_times.append(start_time)
                continue
            elif start_time in start_times :
                duplicate_index = start_times.index(start_time) + 1
                intervals.pop(duplicate_index)
        dotw_date.extend(intervals)
        result.append(' '.join(dotw_date))
    availability_output = '\n'.join(result)
    print(availability_output)
    subprocess.run("pbcopy", text=True, input=availability_output)
    
if __name__ == '__main__':
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    main()
