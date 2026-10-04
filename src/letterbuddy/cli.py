"""
Letter Buddy – CLI entry point.

Commands:
  letterbuddy read <image|pdf>   – OCR a letter and print results
  letterbuddy explain <image|pdf> – Full pipeline: OCR → extract → understand → card
  letterbuddy serve              – Start the web UI
  letterbuddy setup              – Check/install dependencies
"""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="letterbuddy",
        description="Letter Buddy: Offline letter reader and explainer",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # read command
    read_parser = subparsers.add_parser("read", help="OCR a letter image or PDF")
    read_parser.add_argument("file", help="Path to image (JPG/PNG) or PDF")
    read_parser.add_argument("--lang", help="OCR language override (e.g. 'eng+tel')")

    # explain command
    explain_parser = subparsers.add_parser("explain", help="Full pipeline: read → explain → card")
    explain_parser.add_argument("file", help="Path to image (JPG/PNG) or PDF")
    explain_parser.add_argument("--lang", help="OCR language override")
    explain_parser.add_argument("--speak", action="store_true", help="Read the card aloud")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start the web UI")
    serve_parser.add_argument("--host", default=None, help="Bind host (default: from config)")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    serve_parser.add_argument("--lan", action="store_true", help="Enable LAN access (requires PIN)")
    serve_parser.add_argument("--pin", help="PIN for LAN access")

    # setup command
    subparsers.add_parser("setup", help="Check dependencies and GPU tier")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Enable netguard for offline mode
    from letterbuddy.netguard import auto_enable
    auto_enable()

    if args.command == "read":
        _cmd_read(args)
    elif args.command == "explain":
        _cmd_explain(args)
    elif args.command == "serve":
        _cmd_serve(args)
    elif args.command == "setup":
        _cmd_setup()


def _cmd_read(args: argparse.Namespace) -> None:
    """OCR a letter and print text + confidence."""
    from letterbuddy.config import cfg
    from letterbuddy.ocr import ocr_images
    from letterbuddy.preprocess import preprocess_file

    lang = args.lang or cfg.ocr.langs
    images = preprocess_file(args.file)
    result = ocr_images(images, lang=lang)

    if result.needs_retake:
        print(f"\n⚠️  {result.retake_reason}")
        print(f"   Confidence: {result.mean_confidence:.0f}%")
    else:
        print(f"\n✅ OCR complete (confidence: {result.mean_confidence:.0f}%)")

    print("\n--- OCR Text ---")
    print(result.full_text)


def _cmd_explain(args: argparse.Namespace) -> None:
    """Full pipeline: OCR → extract → understand → card."""
    print("⏳ explain command — implementation coming in Phase 3+")


def _cmd_serve(args: argparse.Namespace) -> None:
    """Start the web UI server."""
    print("⏳ serve command — implementation coming in Phase 6")


def _cmd_setup() -> None:
    """Check dependencies and GPU tier."""
    from letterbuddy.config import cfg
    print(f"GPU: {cfg.gpu.name} ({cfg.gpu.vram_mb} MB) — Tier {cfg.gpu.tier}")
    print(f"LLM: {cfg.llm.primary}")
    print(f"OCR: {cfg.ocr.engine} ({cfg.ocr.langs})")
    print(f"TTS: {cfg.tts.engine} ({cfg.tts.voice})")
    print(f"Target language: {cfg.language.target_name}")


if __name__ == "__main__":
    main()
