#!/usr/bin/env python3
"""
Main script to run the Snowflake to Azure AI Search pipeline.

This script orchestrates the extraction, embedding, and indexing process.
"""

import sys
import argparse
from pathlib import Path

# Add src directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import Config
from src.utils.logging_config import setup_logging, get_logger
from src.orchestration.pipeline import Pipeline


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Snowflake to Azure AI Search pipeline"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to config YAML file",
        default=None
    )

    parser.add_argument(
        "--env",
        type=str,
        help="Path to .env file",
        default=None
    )

    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Run in incremental mode (only process new/updated records)"
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Run in full mode (process all records)"
    )

    parser.add_argument(
        "--recreate-index",
        action="store_true",
        help="Recreate the search index before indexing"
    )

    parser.add_argument(
        "--reset-checkpoint",
        action="store_true",
        help="Reset checkpoint to force full reprocessing"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level"
    )

    parser.add_argument(
        "--json-logs",
        action="store_true",
        help="Output logs in JSON format"
    )

    return parser.parse_args()


def main():
    """Main entry point for the pipeline."""
    args = parse_args()

    # Setup logging
    setup_logging(log_level=args.log_level, json_logs=args.json_logs)
    logger = get_logger(__name__)

    logger.info(
        "Starting pipeline execution",
        incremental=args.incremental,
        full=args.full,
        recreate_index=args.recreate_index
    )

    try:
        # Load configuration
        config = Config(config_path=args.config, env_path=args.env)

        # Initialize pipeline
        pipeline = Pipeline(config)

        # Reset checkpoint if requested
        if args.reset_checkpoint:
            logger.info("Resetting checkpoint")
            pipeline.reset_checkpoint()

        # Determine incremental mode
        incremental = None
        if args.incremental:
            incremental = True
        elif args.full:
            incremental = False

        # Run pipeline
        stats = pipeline.run(
            incremental=incremental,
            recreate_index=args.recreate_index
        )

        # Display results
        logger.info("Pipeline execution completed successfully", stats=stats)

        print("\n" + "=" * 50)
        print("Pipeline Execution Summary")
        print("=" * 50)
        print(f"Rows extracted: {stats['rows_extracted']}")
        print(f"Rows embedded: {stats['rows_embedded']}")
        print(f"Rows indexed: {stats['rows_indexed']}")
        if 'total_documents_in_index' in stats:
            print(f"Total documents in index: {stats['total_documents_in_index']}")
        print(f"Duration: {stats['duration_seconds']:.2f} seconds")
        print("=" * 50)
        print("\nPipeline completed successfully!")

        sys.exit(0)

    except Exception as e:
        logger.error("Pipeline execution failed", error=str(e), exc_info=True)
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
