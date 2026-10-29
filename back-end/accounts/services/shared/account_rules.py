from accounts.models import AccountStatus, Ban, Role, UserRoleBridge


def normalize_email(email):
    return email.strip(" ").lower()


def is_identity_banned(email_normalized, now):
    return Ban.objects.active(now).for_identity(email_normalized).exists()


def is_account_usable(user, now):
    return (
        not user.is_deleted
        and user.account_status == AccountStatus.ACTIVE
        and not Ban.objects.active(now).for_account(user).exists()
    )


def has_active_role(user):
    return user.role_bridges.active().exists()


def assign_role(user, role_code):
    user.role_bridges.update(is_active=False)
    bridge, _ = UserRoleBridge.objects.get_or_create(
        user=user, role=Role.objects.get(code=role_code)
    )
    bridge.is_active = True
    bridge.save()
