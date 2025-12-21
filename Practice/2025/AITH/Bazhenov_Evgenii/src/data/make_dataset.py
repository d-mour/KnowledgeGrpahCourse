"""Module contains scripts to create dataset from raw data."""

import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

logger = logging.getLogger(__name__)


@click.command()
@click.argument("input_filepath", type=click.Path(exists=True))
@click.argument("output_filepath", type=click.Path())
def main(input_filepath, output_filepath):
    """Run data processing scripts.

    Convert raw data from the input file
    path into cleaned data ready for analysis, then save it to the output file
    path.

    Parameters:
    input_filepath (str): Path to the input raw data file.
    output_filepath (str): Path to save the cleaned data file.
    """
    logger.info("making final data set from raw data")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
