# Strava Activities Renamer :running:

## Description :framed_picture:

**Strava Activities Renamer** is a `Python 3` script for dumping all Strava activities to file, in `CSV` format, and (after editing the available property fields, that are listed in the table below) printing or updating them automatically.

| Property     | Possible Actions       | 
|--------------|------------------------|
| Name         | print or remote update |
| Description  | remote empty           |
| Workout Type | print                  |

## Setup :wrench:

1. **clone** this repository
2. **install** `Python 3` dependencies: `pip3 install -r requirements.txt`
3. **create** a new Strava application, from the "*My API Application*" tab from *Settings*
4. **get** the client ID (referred to as `CLIENT_ID`) and secret (referred to as `CLIENT_SECRET`), from the same Strava page

## Usage :toolbox:

1. **generate** a new authorization URL

```
./strava_activities_renamer.py get-code --client-id CLIENT_ID
[+] Authorization URL is: https://www.strava.com/oauth/authorize?client_id=CLIENT_ID&redirect_uri=http%3A%2F%2Flocalhost%2Fget_the_code_parameter&approval_prompt=auto&response_type=code&scope=read%2Cread_all%2Cprofile%3Aread_all%2Cprofile%3Awrite%2Cactivity%3Aread%2Cactivity%3Aread_all%2Cactivity%3Awrite
```

2. **access** the generated URL in the browser and, after giving permissions, get the `code` parameter from the redirect URL that will be referred to as `CODE`
3. **generate** a permanent token

```
./strava_activities_renamer.py get-token --client-id CLIENT_ID --client-secret CLIENT_SECRET --code CODE
[+] A new permanent token was generated, with the following details:
    - access token: ACCESS_TOKEN
    - refresh access token: REFRESH_ACCESS_TOKEN
    - expired at: EXPIRED_AT
```

4. *check the validity of the token (optional)*

```
./strava_activities_renamer.py check-token-validity --client-id CLIENT_ID --client-secret CLIENT_SECRET --refresh-access-token REFRESH_ACCESS_TOKEN --expires-at EXPIRED_AT
[+] Access token is still valid!
```

5. **dump** all activities to file

```
./strava_activities_renamer.py get-activities --access-token ACCESS_TOKEN --output-file OUTPUT_FILENAME
[+] Number of saved activities: ACTIVITIES_COUNT

cat OUTPUT_FILENAME | head -n 1
ID,Name,Distance,Type,Workout type,Start date,Was manually added,Is private,Gear ID,Description
```

6. **copy** the output file: `cp OUTPUT_FILENAME COPIED_FILENAME`
7. **edit** the activities in the copy with a `CSV` editor
8. **print** or **update** the changes

```
./strava_activities_renamer.py update-activities --access-token ACCESS_TOKEN --original-file OUTPUT_FILENAME --modified-file COPIED_FILENAME --only-print
[+] Name changes are:
        - for activity with ID ACTIVITY_ID (https://www.strava.com/activities/ACTIVITY_ID), from 'ORIGINAL_NAME' to 'MODIFIED_NAME'
[+] Type changes are:
        - for activity with ID ACTIVITY_ID (https://www.strava.com/activities/ACTIVITY_ID), from ORIGINAL_ACTIVITY_TYPE to MODIFIED_ACTIVITY_TYPE
```

## Resources :books:

| Name          | Description                                                      | Link                                                   | 
|---------------|------------------------------------------------------------------|--------------------------------------------------------|
| **stravalib** | `Python 3` module for interacting with Strava API                | [Github repository](https://github.com/hozn/stravalib) |
| **click**     | `Python 3` module for creating command line interfaces           | [website](https://click.palletsprojects.com/en/7.x/)   |
| **tqdm**      | `Python 3` module for creating progress bars in the command line | [Github repository](https://github.com/tqdm/tqdm)      |