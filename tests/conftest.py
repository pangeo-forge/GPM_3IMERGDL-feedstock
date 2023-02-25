import pytest
import os
import pathlib
import xarray
import copy
import subprocess
import json
import tempfile
import time

ROOT_DIR = pathlib.Path(__file__).parent.parent
ZARR_STORE_NAME = os.environ.get("ZARR_STORE_NAME", "gpm-3imergdl")



@pytest.fixture(scope="module")
def zarr_store_root() -> str:
    job_name = os.environ.get("JOB_NAME", f"test-{str(int(time.time()))}")

    config = {
        "BaseCommand": {
            "logging_config": {
                "version": 1,
                "formatters": {
                    "simple": {
                        "format": "%(asctime)s %(levelname)s %(message)s"
                    }
                },
                "handlers": {
                    "recipe_parse_debug": {
                        "class": "logging.FileHandler",
                        "level": "DEBUG",
                        "formatter": "simple",
                        "filename": f"{job_name}_parse.debug.log"
                    },
                    "recipe_parse_info": {
                        "class": "logging.FileHandler",
                        "level": "INFO",
                        "formatter": "simple",
                        "filename": f"{job_name}_parse.info.log"
                    },
                    "beam_info_log": {
                        "class": "logging.FileHandler",
                        "level": "INFO",
                        "formatter": "simple",
                        "filename": f"{job_name}_beam.info.log"
                    },
                    "beam_debug_log": {
                        "class": "logging.FileHandler",
                        "level": "DEBUG",
                        "formatter": "simple",
                        "filename": f"{job_name}_beam.debug.log"
                    }
                },
                "loggers": {
                    "pangeo_forge_recipes.parse": {
                        "level": "DEBUG",
                        "handlers": ["recipe_parse_debug", "recipe_parse_info"]
                    },
                    "apache_beam": {
                        "level": "DEBUG",
                        "handlers": ["beam_info_log", "beam_debug_log"]
                    }
                }
            }
        },
        "TargetStorage": {
            "fsspec_class": "fsspec.implementations.local.LocalFileSystem",
            "root_path": f"file://{ROOT_DIR}/storage/output/{job_name}"
        },
        "InputCacheStorage": {
            "fsspec_class": "fsspec.implementations.local.LocalFileSystem",
            "root_path": f"file://{ROOT_DIR}/storage/cache"
        },
        "Bake": {
            "bakery_class":  "pangeo_forge_runner.bakery.local.LocalDirectBakery",
            "job_name": job_name
        }
    }
    with tempfile.NamedTemporaryFile(suffix=".json") as f:
        print(config)
        f.write(json.dumps(config).encode())
        f.flush()
        subprocess.check_call([
            "pangeo-forge-runner",
            "bake",
            "--prune",
            "-f",
            f.name,
            "--repo",
            ROOT_DIR
        ])

        return config["TargetStorage"]["root_path"]



# Not module scoped, as we want to provide a new array for each test
@pytest.fixture
def zarr_store(zarr_store_root: str) -> xarray.Dataset:
    return xarray.open_dataset(
        os.path.join(zarr_store_root, ZARR_STORE_NAME),
        engine="zarr"
    )
    
