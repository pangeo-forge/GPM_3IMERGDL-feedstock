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
ZARR_STORE_NAME = "gpm-3imergdl"

base_config = {
    "TargetStorage": {
        "fsspec_class": "fsspec.implementations.local.LocalFileSystem",
    },
    "InputCacheStorage": {
        "fsspec_class": "fsspec.implementations.local.LocalFileSystem",
        "root_path": f"file://{ROOT_DIR}/storage/cache"
    },
    "Bake": {
        "bakery_class":  "pangeo_forge_runner.bakery.local.LocalDirectBakery"
    }
}


@pytest.fixture(scope="module")
def zarr_store_root() -> str:
    job_name = f"test-{str(int(time.time()))}"
    config = copy.deepcopy(base_config)
    config["Bake"]["job_name"] = job_name
    config["TargetStorage"]["root_path"]= f"file://{ROOT_DIR}/storage/output/{job_name}"
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
    
