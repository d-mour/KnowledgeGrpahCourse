"""Module contains functions to download data from a source."""

import click
import logging
from dotenv import find_dotenv, load_dotenv

logger = logging.getLogger(__name__)


@click.command()
@click.argument("output_folder_path", type=click.Path())
def main(output_folder_path):
    """
    Download data from a specific source and saves it locally.

    Parameters:
    output_folder_path (str): Path to the output folder
    where the downloaded file will be saved.
    """
    logger.info("Downloading data...")

    logger.info("Data downloaded successfully.")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
