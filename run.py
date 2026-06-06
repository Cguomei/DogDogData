"""
测试运行器 — 统一入口
取代 Test/ 下的 10 个独立脚本。

用法:
    python run.py                  # 默认：unit + api（过滤 slow/e2e/performance）
    python run.py --type all       # 全部测试
    python run.py --type e2e       # 仅端到端测试
    python run.py --p0             # 仅 P0 冒烟
    python run.py --cov            # 带覆盖率
    python run.py -m "not charts"  # 自定义 marker 过滤
    python run.py --html           # 生成 HTML 报告
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPORT_DIR = Path("Test/reports")
PYTEST = [sys.executable, "-m", "pytest"]


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def run(args: argparse.Namespace) -> int:
    cmd = PYTEST.copy()

    # ── Test type ──────────────────────────────────────────────
    type_map = {
        "unit": ["Test/test_*.py"],
        "api": ["Test/api_tests/"],
        "ui": ["Test/ui_tests/"],
        "e2e": ["Test/e2e_tests/"],
        "store": ["Test/test_store.py"],
        "qa": ["Test/qa_test.py"],
    }

    if args.type == "p0":
        cmd.extend(["-m", "p0"])
    elif args.type == "all":
        cmd.extend(["-m", ""])
    elif args.type in type_map:
        cmd.extend(type_map[args.type])
    else:
        print(f"Unknown type: {args.type}")
        return 1

    # ── Marker override ────────────────────────────────────────
    if args.m:
        cmd.extend(["-m", args.m])

    # ── Coverage ───────────────────────────────────────────────
    if args.cov or args.cov_fail:
        cmd.append("--cov=.")
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        cov_report = REPORT_DIR / f"coverage_{timestamp()}"
        cmd.extend(["--cov-report=html:" + str(cov_report)])
        cmd.append("--cov-report=term-missing")
        if args.cov_fail:
            cmd.append(f"--cov-fail-under={args.cov_fail}")

    # ── HTML report ────────────────────────────────────────────
    if args.html:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        html_report = REPORT_DIR / f"report_{timestamp()}.html"
        cmd.extend([f"--html={html_report}", "--self-contained-html"])

    # ── Verbosity ──────────────────────────────────────────────
    if args.quiet:
        cmd.append("-q")
    elif args.verbose:
        cmd.append("-vv")

    # ── Passthrough args (everything after --) ────────────────
    if args.passthrough:
        cmd.extend(args.passthrough)

    print("─" * 60)
    print(f"  python run.py --type {args.type}")
    print(f"  {' '.join(str(c) for c in cmd)}")
    print("─" * 60)

    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="DogDogData 测试运行器",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--type",
        default="unit",
        choices=["unit", "api", "ui", "e2e", "store", "qa", "p0", "all"],
        help="测试类型（默认: unit）",
    )
    parser.add_argument("-m", help="覆盖 pytest marker 过滤")
    parser.add_argument("--cov", action="store_true", help="启用覆盖率")
    parser.add_argument(
        "--cov-fail", type=int, default=0, help="覆盖率门槛（0=不检查）"
    )
    parser.add_argument("--html", action="store_true", help="生成 HTML 报告")
    parser.add_argument("-q", "--quiet", action="store_true", help="简洁输出")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument(
        "passthrough",
        nargs=argparse.REMAINDER,
        help="传递给 pytest 的其他参数（在 -- 之后）",
    )

    args = parser.parse_args()

    # Strip leading "--" from passthrough
    if args.passthrough and args.passthrough[0] == "--":
        args.passthrough = args.passthrough[1:]

    sys.exit(run(args))


if __name__ == "__main__":
    main()
