# make this file last since this is where you actually use the database and tables

import typer # allows us to make CLI commands
from app.database import create_db_and_tables, get_session, drop_all # carry over the database functions we made in database.py
from app.models import User # carry over the User table we made in models.py
from fastapi import Depends # handles some ugly dependency injection for us
from sqlmodel import select # allows us to run select queries on the database
from sqlalchemy.exc import IntegrityError # allows us to catch database errors (like when we try to create a user with a username that already exists)

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username: str):
    with get_session() as db:  # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first() # Run a query to find the user with the given username
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command()
def get_all_users():
    with get_session() as db: # Get a connection to the database
        all_users = db.exec(select(User)).all() # Run a query to get all users
        if not all_users:
            print("No users found")
            return
        else:
            for user in all_users:
                print(user)

@cli.command()
def change_email(username: str, new_email:str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first() # Run a query to find the user with the given username
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email # Update the user's email
        db.add(user) # Tell the database about this change
        db.commit() # Tell the database to persist this change
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command()
def create_user(username: str, email:str, password: str):
    with get_session() as db:
        new_user = User(username, email, password) 
        try:
            db.add(new_user)
            db.commit()
        except IntegrityError as e:
            db.rollback() # If there was an error, we need to rollback the transaction so we can try again
            print(f"Error: A user with the username '{username}' already exists.")
            return
        else:
            print(new_user)
            

@cli.command()
def delete_user(username: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first() # Run a query to find the user with the given username
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f"Deleted user {username}")


if __name__ == "__main__":
    cli()