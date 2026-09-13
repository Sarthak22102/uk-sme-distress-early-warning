"""Boundaries for untrusted public data and credential-bearing HTTP requests."""
import re
import urllib.request
from datetime import date
from pathlib import Path


def require(condition, message='Validation failed'):
    """Unlike assert, release checks remain active under python -O."""
    if not condition:
        raise ValueError(message)


class RejectRedirects(urllib.request.HTTPRedirectHandler):
    """Never forward credentials, or downgrade HTTPS, following a redirect."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('HTTP redirects are disabled for source downloads and API requests')


def source_opener():
    return urllib.request.build_opener(RejectRedirects())


def snapshot_date(value):
    require(bool(re.fullmatch(r'\d{4}-\d{2}-01', value)), 'Snapshot must be YYYY-MM-01')
    return date.fromisoformat(value)


def source_path(root, name, snapshot):
    snapshot_date(snapshot)
    pattern = rf'BasicCompanyData-{re.escape(snapshot)}-part[1-9]\d*_[1-9]\d*\.zip'
    require(bool(re.fullmatch(pattern, name)), 'Invalid source partition filename')
    root = Path(root).resolve()
    path = root / name
    require(not path.is_symlink(), 'Source partition must not be a symlink')
    require(path.resolve().parent == root, 'Source partition escapes raw directory')
    return path


def check_archive(archive):
    """Bound disk/CPU exposure before CRC verification or decompression."""
    members = archive.infolist()
    require(0 < len(members) <= 20, 'Unexpected ZIP member count')
    total = 0
    for member in members:
        require(not member.is_dir() and member.filename.lower().endswith('.csv'), 'Unexpected ZIP member')
        total += member.file_size
        require(member.file_size <= 2 * 1024**3, 'ZIP member exceeds size limit')
        require(member.file_size / max(member.compress_size, 1) <= 100, 'Suspicious ZIP compression ratio')
    require(total <= 3 * 1024**3, 'ZIP expanded size exceeds limit')


def safe_cell(value):
    """Escape spreadsheet formula prefixes in presentation exports, not source data."""
    if not isinstance(value, str) or not value:
        return value
    stripped = value.lstrip()
    if value[0] in '\t\r\n' or (stripped and stripped[0] in '=+-@＝＋－＠'):
        return "'" + value
    return value


def safe_frame(frame):
    result = frame.copy()
    for column in result.select_dtypes(include=['object', 'string']).columns:
        result[column] = result[column].map(safe_cell)
    return result


def sql_identifier(value):
    """Only simple internal SQL identifiers are accepted; values use parameters."""
    require(bool(re.fullmatch(r'[a-z_][a-z0-9_]*', value)), 'Invalid SQL identifier')
    return '"' + value + '"'
