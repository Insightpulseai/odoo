"""CLI entrypoint for Notion Sync service."""

import sys
from datetime import datetime

import click
import structlog
from dotenv import load_dotenv

from .config import Config
from .sync import SyncEngine

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@click.group()
@click.option("--env-file", default=".env", help="Path to .env file")
@click.pass_context
def cli(ctx: click.Context, env_file: str) -> None:
    """Notion Sync - Sync Notion databases to Databricks."""
    load_dotenv(env_file)
    ctx.ensure_object(dict)


@cli.command()
@click.option("--full-sync", is_flag=True, help="Force full sync (ignore watermarks)")
@click.option("--dry-run", is_flag=True, help="Don't write to Databricks")
@click.pass_context
def sync(ctx: click.Context, full_sync: bool, dry_run: bool) -> None:
    """Sync all Notion databases to Databricks."""
    logger.info(
        "Starting Notion sync",
        full_sync=full_sync,
        dry_run=dry_run,
        timestamp=datetime.utcnow().isoformat(),
    )

    try:
        config = Config.from_env()
        config.sync.dry_run = dry_run

        engine = SyncEngine(config)
        summary = engine.sync_all(full_sync=full_sync)

        if summary.success:
            logger.info(
                "Sync completed successfully",
                total_pages=summary.total_pages_synced,
                databases=len(summary.results),
            )
            sys.exit(0)
        else:
            logger.error(
                "Sync completed with errors",
                total_errors=summary.total_errors,
            )
            for result in summary.results:
                if result.errors:
                    logger.error(
                        "Database errors",
                        database=result.database_name,
                        errors=result.errors,
                    )
            sys.exit(1)

    except Exception as e:
        logger.exception("Sync failed", error=str(e))
        sys.exit(1)


@cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check health of Notion and Databricks connections."""
    logger.info("Running health checks")

    try:
        config = Config.from_env()
        engine = SyncEngine(config)

        # Check Notion
        notion_healthy = engine.notion.check_health()
        logger.info("Notion health", healthy=notion_healthy)

        # Check Databricks
        databricks_healthy = engine.databricks.check_health()
        logger.info("Databricks health", healthy=databricks_healthy)

        if notion_healthy and databricks_healthy:
            logger.info("All systems healthy")
            sys.exit(0)
        else:
            logger.error("Some systems unhealthy")
            sys.exit(1)

    except Exception as e:
        logger.exception("Health check failed", error=str(e))
        sys.exit(1)


@cli.command()
@click.argument("database_name")
@click.option("--full-sync", is_flag=True, help="Force full sync")
@click.pass_context
def sync_database(ctx: click.Context, database_name: str, full_sync: bool) -> None:
    """Sync a specific Notion database."""
    logger.info("Starting single database sync", database=database_name)

    try:
        config = Config.from_env()
        engine = SyncEngine(config)

        # Map database name to ID
        db_map = {
            "programs": config.notion.programs_db_id,
            "projects": config.notion.projects_db_id,
            "budget_lines": config.notion.budget_lines_db_id,
            "risks": config.notion.risks_db_id,
        }

        if database_name not in db_map:
            logger.error("Unknown database", name=database_name, valid=list(db_map.keys()))
            sys.exit(1)

        mapping_config = engine.mapping["databases"].get(database_name, {})

        result = engine.sync_database(
            database_id=db_map[database_name],
            database_name=database_name,
            mapping_config=mapping_config,
            full_sync=full_sync,
        )

        if result.success:
            logger.info(
                "Database sync completed",
                pages_synced=result.pages_synced,
                duration=result.duration_seconds,
            )
            sys.exit(0)
        else:
            logger.error("Database sync failed", errors=result.errors)
            sys.exit(1)

    except Exception as e:
        logger.exception("Sync failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    cli()
