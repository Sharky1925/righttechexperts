from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


@dataclass(frozen=True)
class ColumnInfo:
    name: str
    decl_type: str
    notnull: bool
    pk: bool


def _sqlite_affinity(decl_type: str) -> str:
    value = (decl_type or '').upper()
    if 'INT' in value:
        return 'INTEGER'
    if any(token in value for token in ('CHAR', 'CLOB', 'TEXT')):
        return 'TEXT'
    if 'BLOB' in value or value == '':
        return 'BLOB'
    if any(token in value for token in ('REAL', 'FLOA', 'DOUB')):
        return 'REAL'
    return 'NUMERIC'


def _expected_affinities(field) -> set[str]:
    if getattr(field, 'many_to_one', False):
        # SQLite FK columns are typically INTEGER but can appear as NUMERIC.
        return {'INTEGER', 'NUMERIC'}

    internal = field.get_internal_type()

    if internal in {
        'AutoField',
        'BigAutoField',
        'SmallAutoField',
        'IntegerField',
        'BigIntegerField',
        'SmallIntegerField',
        'PositiveIntegerField',
        'PositiveSmallIntegerField',
    }:
        return {'INTEGER', 'NUMERIC'}

    if internal in {'BooleanField'}:
        return {'INTEGER', 'NUMERIC'}

    if internal in {
        'CharField',
        'TextField',
        'SlugField',
        'EmailField',
        'URLField',
        'UUIDField',
        'GenericIPAddressField',
        'FileField',
        'ImageField',
        'JSONField',
    }:
        return {'TEXT', 'NUMERIC'}

    if internal in {'FloatField'}:
        return {'REAL', 'NUMERIC'}

    if internal in {
        'DecimalField',
        'DateField',
        'DateTimeField',
        'TimeField',
        'DurationField',
    }:
        return {'NUMERIC', 'TEXT'}

    return {'NUMERIC', 'TEXT', 'INTEGER', 'REAL'}


def _load_table_columns(conn: sqlite3.Connection, table_name: str) -> dict[str, ColumnInfo]:
    rows = conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
    cols: dict[str, ColumnInfo] = {}
    for _, name, decl_type, notnull, _default, pk in rows:
        cols[name] = ColumnInfo(
            name=name,
            decl_type=decl_type or '',
            notnull=bool(notnull),
            pk=bool(pk),
        )
    return cols


class Command(BaseCommand):
    help = 'Compare Django model column definitions against a Flask SQLite schema.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-db',
            default='/Users/umutdemirkapu/mylauncher/app/site.db',
            help='Path to the Flask SQLite database file.',
        )
        parser.add_argument(
            '--apps',
            nargs='*',
            default=['public', 'admin_panel', 'acp'],
            help='App labels to include in parity checks.',
        )
        parser.add_argument(
            '--strict',
            action='store_true',
            help='Exit non-zero on any mismatch or warning.',
        )
        parser.add_argument(
            '--require-tables',
            action='store_true',
            help='Treat missing model tables as failures instead of warnings.',
        )

    def handle(self, *args, **options):
        source_db = Path(options['source_db']).expanduser().resolve()
        include_apps: set[str] = set(options['apps'])
        strict: bool = options['strict']
        require_tables: bool = options['require_tables']

        if not source_db.exists():
            raise CommandError(f'Source DB not found: {source_db}')

        conn = sqlite3.connect(source_db)
        try:
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                ).fetchall()
            }

            failures: list[str] = []
            warnings: list[str] = []
            checked = 0

            for model in apps.get_models():
                if model._meta.app_label not in include_apps:
                    continue
                if model._meta.auto_created:
                    continue

                table_name = model._meta.db_table
                checked += 1

                if table_name not in tables:
                    msg = f'[{model._meta.label}] missing table in source DB: {table_name}'
                    if require_tables:
                        failures.append(msg)
                    else:
                        warnings.append(msg)
                    continue

                db_cols = _load_table_columns(conn, table_name)
                model_fields = [f for f in model._meta.local_fields if getattr(f, 'column', None)]
                model_colnames = {f.column for f in model_fields}
                db_colnames = set(db_cols.keys())

                missing = sorted(model_colnames - db_colnames)
                extra = sorted(db_colnames - model_colnames)
                if missing:
                    failures.append(f'[{model._meta.label}] missing columns in DB: {", ".join(missing)}')
                if extra:
                    warnings.append(f'[{model._meta.label}] extra DB columns not in model: {", ".join(extra)}')

                for field in model_fields:
                    col = field.column
                    info = db_cols.get(col)
                    if not info:
                        continue

                    if field.primary_key and not info.pk:
                        failures.append(f'[{model._meta.label}.{col}] expected primary key but DB pk=0')

                    if not field.primary_key:
                        # Only treat DB stricter-than-model nullability as failure.
                        # DB looser-than-model is common in legacy SQLite schemas and is a warning.
                        if field.null and info.notnull:
                            failures.append(
                                f'[{model._meta.label}.{col}] model allows NULL but DB is NOT NULL'
                            )
                        elif (not field.null) and (not info.notnull):
                            warnings.append(
                                f'[{model._meta.label}.{col}] model NOT NULL but DB allows NULL'
                            )

                    actual_aff = _sqlite_affinity(info.decl_type)
                    allowed_aff = _expected_affinities(field)
                    if actual_aff not in allowed_aff:
                        warnings.append(
                            f'[{model._meta.label}.{col}] type affinity mismatch '
                            f'(model={"|".join(sorted(allowed_aff))}, db={actual_aff}, decl="{info.decl_type}")'
                        )

            if failures:
                self.stdout.write(self.style.ERROR('Schema parity failures:'))
                for item in failures:
                    self.stdout.write(f'  - {item}')
            else:
                self.stdout.write(self.style.SUCCESS('No blocking parity failures found.'))

            if warnings:
                self.stdout.write(self.style.WARNING('Schema parity warnings:'))
                for item in warnings:
                    self.stdout.write(f'  - {item}')

            self.stdout.write(f'Checked models: {checked}')
            self.stdout.write(f'Failures: {len(failures)}')
            self.stdout.write(f'Warnings: {len(warnings)}')

            if strict and (failures or warnings):
                raise CommandError('Strict parity check failed.')
        finally:
            conn.close()
