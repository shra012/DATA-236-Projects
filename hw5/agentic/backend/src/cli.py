import typer

from .database import SessionLocal
from .models import Conversation, Message

app = typer.Typer(help="CLI tools for Agentic chat backend")


@app.command()
def list_conversations(user_id: str):
    db = SessionLocal()
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(
            Conversation.updated_at.desc(), 
            Conversation.created_at.desc()
        ).all()
    finally:
        db.close()

    if not conversations:
        typer.echo("No conversations yet.")
        return

    for convo in conversations:
        title = convo.title or "(untitled)"
        when = convo.updated_at or convo.created_at
        typer.echo(f"#{convo.id} – {title} – {when:%Y-%m-%d %H:%M:%S}")


@app.command()
def list_users():
    db = SessionLocal()
    try:
        users = db.query(Conversation.user_id).distinct().order_by(Conversation.user_id).all()

        if not users:
            typer.echo("No users found.")
            return

        typer.echo("Users with conversations:")
        for user in users:
            user_id = user[0]
            count = db.query(Conversation).filter(Conversation.user_id == user_id).count()
            typer.echo(f"  {user_id} ({count} conversation(s))")
    finally:
        db.close()


@app.command()
def show_messages(conversation_id: int):
    db = SessionLocal()
    try:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.id.asc()).all()
    finally:
        db.close()

    if not messages:
        typer.echo("No messages for that conversation.")
        return

    for msg in messages:
        typer.echo(f"[{msg.role.value}] {msg.content}")


@app.command()
def clear_conversations(
    user_id: str = typer.Option(None, help="User ID to clear. If not provided, clears all."),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    db = SessionLocal()
    try:
        if user_id:
            conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
            target = f"user '{user_id}'"
        else:
            conversations = db.query(Conversation).all()
            target = "all users"

        if not conversations:
            typer.echo(f"No conversations found for {target}.")
            return


        count = len(conversations)

        if not confirm and not typer.confirm(f"Delete {count} conversation(s) for {target}?"):
            typer.echo("Cancelled.")
            return

        if user_id:
            db.query(Conversation).filter(Conversation.user_id == user_id).delete()
        else:
            db.query(Conversation).delete()

        db.commit()
        typer.echo(f"Deleted {count} conversation(s).")
    finally:
        db.close()


if __name__ == "__main__":
    app()