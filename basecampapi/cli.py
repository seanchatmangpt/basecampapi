import typer
from .basecamp import Basecamp
from .endpoints.camprife import Campfire
from .endpoints.messageboard import MessageBoard

app = typer.Typer(help="CLI interface for Basecamp API")

@app.command()
def auth(
    account_id: int,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    verification_code: str = None,
):
    """Authenticate with Basecamp and retrieve access token."""
    credentials = {
        "account_id": account_id,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }
    if verification_code:
        typer.echo("Using verification code to obtain refresh token...")
        Basecamp(credentials=credentials, verification_code=verification_code)
    else:
        try:
            Basecamp(credentials=credentials)
        except Exception as exc:
            typer.echo(str(exc))

@app.command()
def campfire_send(
    account_id: int,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    refresh_token: str,
    project_id: int,
    campfire_id: int,
    content: str,
):
    """Send a message to a Campfire chat."""
    credentials = {
        "account_id": account_id,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "refresh_token": refresh_token,
    }
    Basecamp(credentials=credentials)
    campfire = Campfire(project_id=project_id, campfire_id=campfire_id)
    campfire.write(content=content)

@app.command()
def message_create(
    account_id: int,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    refresh_token: str,
    project_id: int,
    message_board_id: int,
    subject: str,
    content: str,
):
    """Create a message on a message board."""
    credentials = {
        "account_id": account_id,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "refresh_token": refresh_token,
    }
    Basecamp(credentials=credentials)
    mb = MessageBoard(project_id=project_id, message_board_id=message_board_id)
    mb.create_message(subject=subject, content=content)

if __name__ == "__main__":
    app()
