#!/bin/bash

# Initialize Alembic migrations
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
