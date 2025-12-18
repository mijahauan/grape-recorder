
import os
import shutil
import tempfile
import logging
from pathlib import Path
from dataclasses import dataclass
from grape_recorder.cli import cleanup_handler

logging.basicConfig(level=logging.INFO)

@dataclass
class MockTask:
    dataset_path: str
    metadata: dict

def test_cleanup():
    # Setup temp environment
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        date_str = "20251218"
        channel = "WWV_10_MHz"
        
        # 1. Create decimated product
        decimated_dir = root / "products" / channel / "decimated"
        decimated_dir.mkdir(parents=True)
        bin_file = decimated_dir / f"{date_str}.bin"
        json_file = decimated_dir / f"{date_str}.json"
        bin_file.write_text("dummy binary data")
        json_file.write_text("{}")
        
        print(f"Created binary: {bin_file}")
        
        # 2. Create Digital RF structure
        # upload/20251218/CALL_GRID/REC@ID/OBS.../
        obs_dir = root / "upload" / date_str / "TEST_GRID" / "REC@1" / "OBS2025-12-18T00-00"
        obs_dir.mkdir(parents=True)
        
        # Add some DRF files
        (obs_dir / "ch0").mkdir()
        (obs_dir / "ch0" / "drf_properties.h5").write_text("metadata")
        (obs_dir / "metadata").mkdir()
        (obs_dir / "metadata" / "data.h5").write_text("metadata")
        
        # Add .upload_complete to simulate success token (should be preserved)
        token_file = obs_dir / ".upload_complete"
        token_file.write_text("complete")
        
        print(f"Created DRF dataset: {obs_dir}")
        
        # 3. Create Task
        task = MockTask(
            dataset_path=str(obs_dir),
            metadata={'date': '2025-12-18'} # CLI passes dash format usually
        )
        
        # 4. Run Cleanup
        print("Running cleanup_handler...")
        cleanup_handler(task)
        
        # 5. Verify Results
        
        # Check DRF files deleted
        assert not (obs_dir / "ch0").exists(), "ch0 dir should be gone or empty"
        assert not (obs_dir / "metadata").exists(), "metadata dir should be gone"
        assert token_file.exists(), "Token file .upload_complete MUST exist"
        print("✓ DRF cleanup verified")
        
        # Check Decimated files deleted
        assert not bin_file.exists(), f"Decimated bin file {bin_file} should be deleted"
        assert not json_file.exists(), f"Decimated json file {json_file} should be deleted"
        print("✓ Decimated file cleanup verified")
        
        # Check unrelated files preserved (optional)
        
if __name__ == "__main__":
    try:
        test_cleanup()
        print("\nSUCCESS: Cleanup logic verified!")
    except AssertionError as e:
        print(f"\nFAILURE: {e}")
        exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        exit(1)
