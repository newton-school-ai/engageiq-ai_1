"""Supervisor agent - orchestrates the engagement monitoring pipeline."""


def run_pipeline(
    mode: str = "student", duration: int = 60, input_source: str = "webcam"
):
    """Run the full engagement monitoring pipeline.

    Args:
        mode: User mode - "student" or "teacher".
        duration: Session duration in seconds.
        input_source: Input source - "webcam", file path, or RTSP URL.
    """
    # TODO: Implement LangGraph pipeline
    raise NotImplementedError("Supervisor pipeline not yet implemented")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EngageIQ AI Supervisor Agent")
    parser.add_argument("--mode", default="student", choices=["student", "teacher"])
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--input", default="webcam", dest="input_source")
    args = parser.parse_args()
    run_pipeline(args.mode, args.duration, args.input_source)
