"""
Create or update a Cognito user when onboarding generates credentials,
so the user can sign in on the Dashboard with the same User ID and Password.

You do NOT need to merge DynamoDB and Cognito. Just set COGNITO_USER_POOL_ID
in the backend .env to your pool's ID (e.g. kyc-yv → get ID from User pool overview).
The backend creates the user in Cognito when it generates the credentials in chat.
Use the same User Pool ID as the frontend (VITE_COGNITO_USER_POOL_ID).
"""
from typing import Optional

import boto3
from ai_sahayak.config.settings import settings


def ensure_cognito_user(username: str, password: str, *, name: Optional[str] = None) -> bool:
    """
    Ensure a user exists in the configured Cognito User Pool with the given password.
    If user exists, set their password; if not, create user and set permanent password.
    Optional name is stored as Cognito "name" attribute so the Dashboard can show "Namaste, {name}!".
    Returns True on success.
    """
    pool_id = (settings.COGNITO_USER_POOL_ID or "").strip()
    if not pool_id:
        print("Cognito: COGNITO_USER_POOL_ID not set in .env — no user created. Add it to link chat credentials to Dashboard login.")
        return False

    # Cognito username: alphanumeric and _.- only; normalize for consistency
    safe_username = "".join(c for c in str(username) if c.isalnum() or c in "_.-") or username

    # Attributes: phone (for 10-digit), and name (for Dashboard greeting)
    user_attrs = []
    if len(safe_username) == 10 and safe_username.isdigit():
        user_attrs.append({"Name": "phone_number", "Value": f"+91{safe_username}"})
    if name and (name := str(name).strip()):
        user_attrs.append({"Name": "name", "Value": name[:99]})

    try:
        client = boto3.client(
            "cognito-idp",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
        )
        try:
            create_kw: dict = {
                "UserPoolId": pool_id,
                "Username": safe_username,
                "TemporaryPassword": password,
                "MessageAction": "SUPPRESS",
            }
            if user_attrs:
                create_kw["UserAttributes"] = user_attrs
            client.admin_create_user(**create_kw)
            print(f"Cognito: user '{safe_username}' created in pool {pool_id}. Check Cognito → User pools → your pool → Users.")
        except client.exceptions.UsernameExistsException:
            print(f"Cognito: user '{safe_username}' already exists, updating password.")
            name_attrs = [a for a in user_attrs if a["Name"] == "name"]
            if name_attrs:
                try:
                    client.admin_update_user_attributes(
                        UserPoolId=pool_id,
                        Username=safe_username,
                        UserAttributes=name_attrs,
                    )
                except Exception:
                    pass
        except Exception:
            raise

        client.admin_set_user_password(
            UserPoolId=pool_id,
            Username=safe_username,
            Password=password,
            Permanent=True,
        )
        return True
    except Exception as e:
        import traceback
        err_msg = str(e).lower()
        if "access denied" in err_msg or "not authorized" in err_msg:
            print("Cognito: IAM credentials need cognito-idp:AdminCreateUser and AdminSetUserPassword on this user pool.")
        print(f"Cognito ensure user failed for '{safe_username}': {e}")
        traceback.print_exc()
        return False
