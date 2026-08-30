@classmethod
async def register_user(cls, user_in: UserCreate) -> UserResponse:
    email_clean = user_in.email.strip().lower()

    existing = await cls.get_user_by_email(email_clean)
    if existing:
        raise AppException(
            code="EMAIL_ALREADY_REGISTERED",
            message="An account with this email already exists.",
            status_code=400,
        )

    user_id = str(uuid.uuid4())
    hashed_pwd = hash_password(user_in.password)
    now = utc_now()

    user_doc = {
        "_id": user_id,
        "name": user_in.name.strip(),
        "email": email_clean,
        "password_hash": hashed_pwd,
        "role": user_in.role.value,
        "created_at": now,
        "updated_at": now,
        "last_login": None,
    }

    if db_manager.is_connected and db_manager.users is not None:
        await db_manager.users.insert_one(user_doc)
    else:
        _memory_users[email_clean] = user_doc

    return UserResponse(
        id=user_id,
        name=user_doc["name"],
        email=user_doc["email"],
        role=UserRole(user_doc["role"]),
        created_at=user_doc["created_at"],
        updated_at=user_doc["updated_at"],
        last_login=None,
    )