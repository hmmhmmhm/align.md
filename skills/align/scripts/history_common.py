"""Shared reporting for optional, user-selected history collection."""
import json
import math
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def date_value(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def estimate(characters, rate=None):
    """Planning assumptions, not a promise about any model's throughput."""
    if rate is not None and (not math.isfinite(rate) or rate <= 0):
        raise ValueError('Analysis throughput must be positive')
    low, high = (rate * .5, rate * 1.5) if rate else (5000, 20000)
    return {'minutes': [round(characters / high, 1), round(characters / low, 1)],
            'basis': 'user-supplied measured rate, +/-50%' if rate else
                     'unmeasured planning assumption: 5,000-20,000 characters/minute',
            'excludes': 'user response time, adoption verification and context expansion'}


def output_path(value):
    path = Path(value).expanduser().absolute()
    if path.is_symlink():
        raise ValueError('Output must not be a symlink')
    path = path.resolve()
    # Evidence is private working material, never an automatic repository artifact.
    for parent in [path.parent, *path.parents]:
        if (parent / '.git').exists():
            raise ValueError('Choose an output outside Git work trees')
    if path.is_symlink():
        raise ValueError('Output must not be a symlink')
    return path


def save(path, report):
    path = output_path(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.align-history-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def summary(report):
    return {key: value for key, value in report.items()
            if key not in ('items', 'records', 'selection')}
