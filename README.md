# Google Calendar Avaliability

This script reads data from your Google Calendar and generates a list of your availabilities in a format suitable for email use. The script also copies the generated list to your clipboard.


### Example Output:

```
    Monday 7/10 09:00 AM - 10:00 AM
    Tuesday 7/11 09:00 AM - 03:00 PM 04:00 PM - 05:00 PM
    Wednesday 7/12 09:00 AM - 01:00 PM 02:00 PM - 05:00 PM
    Thursday 7/13 09:00 AM - 02:00 PM 03:00 PM - 05:00 PM
    Friday 7/14 09:00 AM - 05:00 PM
```


## Authors

- [@patrickwmurph](https://github.com/patrickwmurph)


## API

To run this script, you need to create a Google Calendar API. Follow the steps below:

1. Enable the API
2. Configure the OAuth consent screen
3. Authorize credentials for a desktop application

For detailed instructions, refer to the link[link](https://developers.google.com/calendar/api/quickstart/python).

Once you have downloaded the credentials.json file, place it in the **tokens** directory. 


## Installing libraries :

Install the required google client libraries using the following command: 

```
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

The following libraries are also required:

 - subprocess
 - re
 - datetime
 - os.path
 - calendar

 
## Documentation

To run the script, use the following command:

```
python3 email-avaliability
```

The first time you run the script, it will prompt you to authorize access. If you are signed in to multiple accounts, you will be asked to choose one. After running the script, a web token called *tokens.json* will be generated in the **tokens** directory.

Authorization will not be necessary for future runs of the script once the token is generated.

When running the script, you will be prompted to enter a start and end date for the availabilities you want to generate. The date format should be as follows:

- YYYY-MM-DD

After running the script, your availabilities will be displayed, and they will be automatically copied to your clipboard for easy pasting into an email.



