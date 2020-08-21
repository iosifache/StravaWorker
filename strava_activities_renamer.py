#!/usr/bin/env python3

from stravalib.client import Client
import click
from tqdm import trange
import csv
import sys
import time

def compose_activity_url(activity_id: int) -> str:

    """Compose activity URL"""

    return "https://www.strava.com/activities/" + str(activity_id)

def stringify_run_type(run_type_id: int) -> str:

    """Stringify a run type via ID"""

    types_switch = {
        0: "None",
        1: "Race",
        2: "Long Run",
        3: "Workout"
    }

    return types_switch.get(run_type_id, "")

@click.group()
def cli() -> None:

    """Tool for dumping Strava activities to file, in CVS format, and (after editing) updating them automatically"""

@click.command()
@click.option("--client-id", type = int, prompt = "[?] Client ID is", help = "Client ID")
def get_code(client_id: int) -> None:

    """Build an authorization URL"""

    client = Client()
    url = client.authorization_url(client_id = client_id, redirect_uri="http://localhost/get_the_code_parameter", scope=["read", "read_all", "profile:read_all", "profile:write", "activity:read","activity:read_all", "activity:write"])

    print("[+] Authorization URL is: {}".format(url))

@click.command()
@click.option("--client-id", type = int, prompt = "[?] Client ID is", help = "Client ID")
@click.option("--client-secret", type = str, prompt = "[?] Client secret is", help = "Client secret")
@click.option("--code", type = str, prompt = "[?] Code is", help = "Previously generated temporary code")
def get_token(client_id, client_secret, code):

    """Exchange a temporary code for a permanent token"""

    client = Client()
    response = client.exchange_code_for_token(client_id = client_id, client_secret = client_secret, code = code)

    print("[+] A new permanent token was generated, with the following details:\n\t- access token: {}\n\t- refresh access token: {}\n\t- expireS at: {}".format(response["access_token"], response["refresh_token"], response["expires_at"]))

@click.command()
@click.option("--client-id", type = int, prompt = "[?] Client ID is", help = "Client ID")
@click.option("--client-secret", type = str, prompt = "[?] Client secret is", help = "Client secret")
@click.option("--refresh-access-token", type = str, prompt = "[?] Refresh access token is", help = "Refresh access token")
@click.option("--expires-at", type = int, prompt = "[?] Expiration UNIX time is", help = "Expires at UNIX time")
def check_token_validity(client_id, client_secret, refresh_access_token, expires_at):

    """Check the validity of a permanent token and, if needed, request a new one"""

    client = Client()

    if time.time() <= expires_at:

        print("[+] The access token is still valid!")

    else:

        refresh_response = client.refresh_access_token(client_id = client_id, client_secret = client_secret, refresh_token = refresh_access_token)

        print("[!] The access token expired. A new access token was generated, with the following details:\n\t- access token: {}\n\t- refresh access token: {}\n\t- expireS at: {}".format(refresh_response["access_token"], refresh_response["refresh_token"], refresh_response["expires_at"]))

@click.command()
@click.option("--access-token", type = str, prompt = "[?] Access token is", help = "Access token")
@click.option("--output-file", type = click.File("w"), prompt = "[?] Output file is", help = "Output file where activities will be dumped in CSV format")
def get_activities(access_token, output_file):
    
    """Retrieving all user activities and output them in CSV format"""

    client = Client()
    client.access_token = access_token

    filewriter = csv.writer(output_file, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(["ID", "Name", "Distance", "Type", "Workout type", "Start date", "Was manually added", "Is private", "Gear ID", "Description"])

    activities_count = 0
    for activity in client.get_activities():

        filewriter.writerow([activity.id, activity.name, activity.distance, activity.type, activity.workout_type, activity.start_date, activity.manual, activity.private, activity.gear_id, activity.description])

        activities_count += 1

    print("[+] Number of saved activities: {}".format(activities_count))

@click.command()
@click.option("--access-token", type = str, prompt = "[?] Access token is", help = "Help")
@click.option("--original-file", type = click.File("r"), prompt = "[?] Original CSV file is", help = "Original CSV file")
@click.option("--modified-file", type = click.File("r"), prompt = "[?] Modified CSV file is", help = "CSV file with modified activities")
@click.option("--only-print", is_flag = True, help = "Only print the differences, without updating the remote activities")
@click.option("--empty-descriptions", is_flag = True, help = "Empty the descriptions of the activities")
def update_activities(access_token, original_file, modified_file, only_print, empty_descriptions):

    """Update all activities that are different between two CSV files or only print the differences"""

    saved_stderr = sys.stderr
    sys.stderr = open(".stravalib", "w")

    client = Client()
    client.access_token = access_token

    old_csv_reader = csv.DictReader(original_file)
    new_csv_reader = csv.DictReader(modified_file)

    name_changes = []
    type_changes = []
    for new_row in new_csv_reader:

        old_row = next(row for row in old_csv_reader if row["ID"] == new_row["ID"])

        id = new_row["ID"]
        type = old_row["Type"]
        new_name = new_row["Name"]
        new_type = new_row["Workout type"]
        old_name = old_row["Name"]
        old_type = old_row["Workout type"]
        
        if (old_name != new_name):
            name_changes.append((id, old_name, new_name))
        if (old_type != new_type):
            type_changes.append((id, int(old_type), int(new_type)))

    if (not only_print):

        for i in trange(len(name_changes), file = sys.stdout):

            activity_change = name_changes[i]

            if (empty_descriptions):
                client.update_activity(activity_change[0], name = activity_change[2], description = "")
            else:
                client.update_activity(activity_change[0], name = activity_change[2])

            if (i % 100 == 99):

                time.sleep(15 * 60)

    else:
        
        print("[+] Name changes are:")
        for change in name_changes:

            id = change[0]
            url = compose_activity_url(id)

            print("\t- for activity with ID {} ({}), from '{}' to '{}'".format(id, url, change[1], change[2]))

    print("[+] Type changes are:")
    for change in type_changes:

        id = change[0]
        url = compose_activity_url(id)
        if (type == "Run"):
            old_type_string = stringify_run_type(change[1])
            new_type_string = stringify_run_type(change[2])
        else:
            old_type_string = change[1]
            new_type_string = change[2]

        print("\t- for activity with ID {} ({}), from {} to {}".format(id, url, old_type_string, new_type_string))

    sys.stderr = saved_stderr

if __name__ == "__main__":

    cli.add_command(get_code)
    cli.add_command(get_token)
    cli.add_command(check_token_validity)
    cli.add_command(get_activities)
    cli.add_command(update_activities)

    cli()