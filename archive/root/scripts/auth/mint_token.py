#!/usr/bin/env python3
"""
JWT Token Minter for InsightPulse AI Platform
Generates HS256 JWT tokens for service-to-service authentication

Usage:
    # Mint token for specific service
    python3 scripts/auth/mint_token.py --sub "svc:docflow" --scope "ocr:read,ai:call,mcp:invoke"

    # Mint token with custom expiry (default: 1 hour)
    python3 scripts/auth/mint_token.py --sub "svc:analytics" --exp 3600

    # Mint token using environment variables
    AUTH_JWT_HS256_SECRET='...' AUTH_JWT_ISSUER='...' AUTH_JWT_AUDIENCE='...' python3 scripts/auth/mint_token.py
"""
import os
import sys
import time
import argparse
from pathlib import Path

try:
    import jwt
except ImportError:
    print("Error: PyJWT not installed. Installing...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pyjwt"])
    import jwt

def load_env_from_file(env_file: Path):
    """Load environment variables from .env file"""
    if not env_file.exists():
        return

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                if key not in os.environ:
                    os.environ[key] = value

def mint_token(
    secret: str,
    issuer: str,
    audience: str,
    subject: str,
    scope: list[str],
    expires_in: int = 3600
) -> str:
    """
    Mint a JWT token for service-to-service authentication

    Args:
        secret: HS256 secret key
        issuer: Token issuer (e.g., "https://auth.insightpulseai.com")
        audience: Token audience (e.g., "ipai-platform")
        subject: Service identifier (e.g., "svc:docflow")
        scope: List of permissions (e.g., ["ocr:read", "ai:call"])
        expires_in: Token expiration in seconds (default: 3600 = 1 hour)

    Returns:
        JWT token string
    """
    now = int(time.time())
    payload = {
        "iss": issuer,
        "aud": audience,
        "iat": now,
        "exp": now + expires_in,
        "sub": subject,
        "scope": scope,
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def verify_token(token: str, secret: str, issuer: str, audience: str) -> dict:
    """
    Verify and decode a JWT token

    Args:
        token: JWT token string
        secret: HS256 secret key
        issuer: Expected token issuer
        audience: Expected token audience

    Returns:
        Decoded payload dictionary

    Raises:
        jwt.InvalidTokenError: If token is invalid
    """
    return jwt.decode(
        token,
        secret,
        algorithms=["HS256"],
        issuer=issuer,
        audience=audience,
        options={"require": ["exp", "iss", "aud", "sub"]}
    )

def main():
    parser = argparse.ArgumentParser(
        description="Mint JWT tokens for InsightPulse AI service-to-service auth"
    )
    parser.add_argument(
        "--sub",
        default="svc:default",
        help="Service subject (default: svc:default)"
    )
    parser.add_argument(
        "--scope",
        default="ocr:read,ai:call,mcp:invoke",
        help="Comma-separated scope list (default: ocr:read,ai:call,mcp:invoke)"
    )
    parser.add_argument(
        "--exp",
        type=int,
        default=3600,
        help="Token expiration in seconds (default: 3600)"
    )
    parser.add_argument(
        "--verify",
        metavar="TOKEN",
        help="Verify and decode existing token instead of minting"
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(__file__).parent.parent.parent / ".env.platform.local",
        help="Path to .env file for loading secrets"
    )

    args = parser.parse_args()

    # Load environment from file if exists
    load_env_from_file(args.env_file)

    # Get required environment variables
    secret = os.environ.get("AUTH_JWT_HS256_SECRET")
    issuer = os.environ.get("AUTH_JWT_ISSUER", "https://auth.insightpulseai.com")
    audience = os.environ.get("AUTH_JWT_AUDIENCE", "ipai-platform")

    if not secret:
        print("Error: AUTH_JWT_HS256_SECRET not set", file=sys.stderr)
        print("Set it in environment or .env.platform.local", file=sys.stderr)
        sys.exit(1)

    if args.verify:
        # Verify mode
        try:
            payload = verify_token(args.verify, secret, issuer, audience)
            print("✅ Token valid")
            print(f"   Issuer: {payload['iss']}")
            print(f"   Audience: {payload['aud']}")
            print(f"   Subject: {payload['sub']}")
            print(f"   Scope: {payload.get('scope', [])}")
            print(f"   Issued: {time.ctime(payload['iat'])}")
            print(f"   Expires: {time.ctime(payload['exp'])}")
            expires_in = payload['exp'] - int(time.time())
            if expires_in > 0:
                print(f"   Valid for: {expires_in}s ({expires_in // 60}m)")
            else:
                print(f"   ⚠️  Expired {-expires_in}s ago")
        except jwt.InvalidTokenError as e:
            print(f"❌ Token invalid: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Mint mode
        scope = [s.strip() for s in args.scope.split(',') if s.strip()]
        token = mint_token(secret, issuer, audience, args.sub, scope, args.exp)

        print("✅ JWT token minted")
        print(f"   Subject: {args.sub}")
        print(f"   Scope: {', '.join(scope)}")
        print(f"   Expires: {args.exp}s ({args.exp // 60}m)")
        print()
        print("Token:")
        print(token)
        print()
        print("Usage:")
        print(f"  curl -H 'Authorization: Bearer {token}' https://api.example.com")

if __name__ == "__main__":
    main()
