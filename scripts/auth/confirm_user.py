#!/usr/bin/env python3
"""
Confirm Supabase User

Admin script to confirm an unconfirmed user's email in Supabase Auth.
This is a one-time admin fix for users stuck in "unconfirmed" state.

Usage:
    python scripts/auth/confirm_user.py --email user@example.com [--dry-run]

Required environment variables:
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY
"""

import argparse
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def confirm_user(email: str, dry_run: bool = False) -> bool:
    """Confirm a user's email via Supabase Admin API."""
    try:
        from supabase import create_client
    except ImportError:
        logger.error("supabase-py not installed. Run: pip install supabase")
        return False

    supabase_url = os.environ.get('SUPABASE_URL')
    service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not service_key:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        return False

    client = create_client(supabase_url, service_key)

    # List users to find the target
    logger.info(f"Looking up user: {email}")

    try:
        # Use admin API to list users
        users_response = client.auth.admin.list_users()
        users = users_response.users if hasattr(users_response, 'users') else []

        target_user = None
        for user in users:
            if user.email == email:
                target_user = user
                break

        if not target_user:
            logger.error(f"User not found: {email}")
            return False

        logger.info(f"Found user: id={target_user.id}, confirmed={target_user.email_confirmed_at is not None}")

        if target_user.email_confirmed_at:
            logger.info(f"User {email} is already confirmed (confirmed at: {target_user.email_confirmed_at})")
            return True

        if dry_run:
            logger.info(f"[DRY-RUN] Would confirm user: {email}")
            return True

        # Update user to confirm email
        logger.info(f"Confirming user: {email}")
        client.auth.admin.update_user_by_id(
            target_user.id,
            {"email_confirm": True}
        )

        logger.info(f"Successfully confirmed user: {email}")
        return True

    except Exception as e:
        logger.error(f"Error confirming user: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Confirm Supabase user email')
    parser.add_argument('--email', '-e', required=True, help='Email address to confirm')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Show what would be done')

    args = parser.parse_args()

    success = confirm_user(args.email, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
