import asyncio
import contextlib
import os
import platform
import signal
import sys
from os import environ

from dotenv import load_dotenv

from spark import logger

bot = ...
log = logger.root_logger


def _cleanup_loop(loop: asyncio.AbstractEventLoop) -> None:
    try:
        tasks = {t for t in asyncio.all_tasks(loop=loop) if not t.done()}

        if not tasks:
            log.debug("No tasks to cleanup")
            return

        log.debug("Cleaning up after %d tasks", len(tasks))
        for task in tasks:
            task.cancel()

        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        log.debug("All tasks finished cancelling.")

        for task in tasks:
            if task.cancelled():
                continue
            if task.exception() is not None:
                loop.call_exception_handler(
                    {
                        "message": "Unhandled exception during shutdown.",
                        "exception": task.exception(),
                        "task": task,
                    }
                )
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        log.debug("Closing the event loop")
        loop.close()


def main():
    load_dotenv()

    if platform.system() == "Linux":
        with contextlib.suppress(ImportError):
            # noinspection PyUnresolvedReferences
            import uvloop

            uvloop.install()

    loop = asyncio.new_event_loop()
    exit_code = 0

    with contextlib.suppress(NotImplementedError):
        loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
        loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())

    async def runner():
        nonlocal exit_code
        try:
            exit_code = await bootstrap()
        finally:
            if bot is not ... and not bot.is_closed():
                await bot.close()

    def stop_loop_on_completion(_):
        loop.stop()

    future = asyncio.ensure_future(runner(), loop=loop)
    future.add_done_callback(stop_loop_on_completion)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        log.info("Received Ctrl+C interrupt, attempting to shut down as gracefully as possible")
    finally:
        try:
            if (exc := future.exception()) and not isinstance(exc, KeyboardInterrupt | SystemExit):
                log.critical("Main bot loop encountered an unhandled exception", exc_info=exc)
        except Exception as e:
            # For whatever reason, we can't simply 'except CancelledError | InvalidStateError'
            # to suppress these, as they don't inherit from BaseException? Not sure what's
            # going on there, but whatever.
            if not isinstance(e, asyncio.CancelledError | asyncio.InvalidStateError):
                log.critical("Encountered an unhandled exception", exc_info=e)
        future.remove_done_callback(stop_loop_on_completion)
        log.info("Performing shutdown cleanup")
        _cleanup_loop(loop)

    sys.exit(exit_code)


async def bootstrap() -> int:
    global bot
    import discord
    from discord import Intents

    from spark.bot import Spark, ExitCode
    # from spark.db import setup as setup_db
    from spark.events import setup_events
    from spark.help import SparkHelpCommand

    log.info("Setting up...")
    log.info("----------------------------------------------")

    discord.VoiceClient.warn_nacl = False
    bot = Spark(
        intents=Intents(
            message_content=True,  # basic bot functionality
            guilds=True,  # basic bot functionality
            messages=True,  # basic bot functionality
            members=True,  # basic bot functionality
        ),
        help_command=SparkHelpCommand(),
        max_messages=1250,
    )
    # await setup_db()
    setup_events(bot)

    log.info("Logging into discord as Spark...")
    log.info(f"discord.py API version: {discord.__version__}")
    log.info(f"Python version: {platform.python_version()}")
    log.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    log.info("----------------------------------------------")

    try:
        await bot.start(environ["SPARK_TOKEN"])
    except discord.LoginFailure:
        log.critical("Failed to login to Discord; is your token valid?")
        exit_code = ExitCode.CONFIG_ERROR
    except discord.PrivilegedIntentsRequired:
        log.critical(
            "You must enable the Members and Message Content privileged intents in the "
            "Discord Developer dashboard for Spark to function."
        )
        exit_code = ExitCode.CONFIG_ERROR
    except Exception as e:
        log.critical("Main bot loop encountered an unhandled exception", exc_info=e)
        log.critical("Attempting to die as gracefully as possible")
        exit_code = ExitCode.FATAL_ERROR
    else:
        # noinspection PyProtectedMember
        exit_code = bot._exit_code

    return exit_code


if __name__ == "__main__":
    main()