import asyncio
import secrets

from .utils import helpers, logger, config, MarzneshinClient
from .models import ServiceCreate, AdminCreate, AdminUpdate
from collections import defaultdict


async def main():
    logger.info("🚀 Starting Marzneshin Migration Import process...")
    admins, users_by_admin = helpers.parse_marzban_data()
    services_by_admin = defaultdict(list)

    async with MarzneshinClient() as api:
        logger.info("Checking admin sudo access...")
        sudo_check = await api.login(
            config.MARZNESHIN_USERNAME, config.MARZNESHIN_PASSWORD
        )
        if not sudo_check or not sudo_check.is_sudo:
            logger.error("Admin access is not valid! Need sudo privileges.")
            return

        logger.info("Checking available inbounds...")
        inbounds = await api.get_inbounds()
        if not inbounds:
            logger.error(
                "No inbounds found! Please add at least one inbound before migration."
            )
            return

        logger.info(f"Starting admin migration process for {len(admins)} admins...")
        for admin in admins:
            success = False
            for attempt in range(3):
                logger.info(
                    f"Processing admin: {admin.username} (Attempt {attempt + 1}/3)"
                )

                try:
                    logger.info(f"Creating service for {admin.username}...")
                    service = await api.create_service(
                        ServiceCreate(
                            name=f"{admin.username}{secrets.token_hex(2)}",
                            inbound_ids=[inbounds.items[0].id],
                        )
                    )
                    if not service:
                        logger.error(f"Failed to create service for '{admin.username}'")
                        continue

                    logger.info("Service created successfully")

                    check_admin = await api.get_admin(admin.username)

                    if not check_admin:
                        logger.info(f"Creating new admin account: {admin.username}")
                        admin_account = await api.create_admin(
                            AdminCreate(
                                username=admin.username,
                                password=f"{admin.username}{admin.username}",
                                service_ids=[service.id],
                            )
                        )
                    else:
                        if check_admin.is_sudo:
                            logger.error(f"Cannot modify sudo admin: {admin.username}")
                            break

                        logger.info(f"Updating existing admin: {admin.username}")
                        admin_account = await api.update_admin(
                            AdminUpdate(
                                username=admin.username,
                                password=f"{admin.username}{admin.username}",
                                service_ids=[service.id],
                            )
                        )

                    if not admin_account:
                        logger.error(
                            f"Failed to create/update admin account: {admin.username}"
                        )
                        continue

                    services_by_admin[admin_account.username] = service.id
                    logger.info(f"Successfully processed admin: {admin.username}")
                    success = True
                    break

                except Exception as e:
                    logger.error(
                        f"Error processing admin {admin.username} (Attempt {attempt + 1}/3): {str(e)}"
                    )
                    if attempt < 2:
                        logger.info(f"Retrying admin {admin.username}...")
                        continue

            if not success:
                logger.error(
                    f"Failed to process admin {admin.username} after 3 attempts"
                )

        logger.info("Starting user migration process...")
        for admin, users in users_by_admin.items():
            if admin not in services_by_admin:
                logger.error(
                    f"Skipping users for admin {admin} due to failed admin creation"
                )
                continue

            logger.info(f"Processing users for admin: {admin} ({len(users)} users)")

            async with MarzneshinClient() as api:
                logger.info(f"Logging in as admin: {admin}")
                check_login = await api.login(admin, f"{admin}{admin}")
                if not check_login:
                    logger.error(f"Failed to login as admin: {admin}")
                    continue

                admin_service = services_by_admin.get(admin)

                for user in users:
                    logger.info(f"Processing user: {user.username}")

                    try:
                        new_user = helpers.parse_marz_user(user, admin_service)
                        logger.debug(f"Data for {user.username}: {new_user.dict()}")
                        created_user = await api.create_user(new_user)
                        if not created_user:
                            logger.error(f"Failed to create user: {user.username}")
                            continue

                        logger.info(f"Successfully created user: {user.username}")

                    except Exception as e:
                        logger.error(f"Error creating user {user.username}: {str(e)}")
                        continue

    logger.info("Migration Import process completed!")


if __name__ == "__main__":
    helpers.make_exceptions_list("marzban.json")
    asyncio.run(main())
