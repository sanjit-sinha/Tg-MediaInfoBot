import os.path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]


def token_generator():
    credentials = None
    if not os.path.exists("token.json"):
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)

        credentials = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(credentials.to_json())


if __name__ == "__main__":
    token_generator()
