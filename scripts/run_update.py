import logging

from mining_intel.pipeline import run_all


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_all()


if __name__ == "__main__":
    main()
