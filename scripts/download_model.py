"""One-time online setup: initialize Mirage so its engine and weights are cached locally."""
import os
os.environ["CACTUS_TELEMETRY"] = "0"


def main():
    print("Initializing Cactus Mirage. The first run may download engine files and model weights.")
    print("This is the only setup step expected to require internet access.")
    import cactus

    vision = cactus.Mirage()
    print("Mirage initialized successfully.")
    print("Model cache is ready. Run scripts/smoke_test.py to test local image inference.")
    del vision


if __name__ == "__main__":
    main()
