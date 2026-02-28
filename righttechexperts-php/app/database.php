<?php
/**
 * Database Layer — PDO wrapper
 * Replaces Django ORM queries with direct PDO.
 */

function db(): PDO
{
    static $pdo = null;
    if ($pdo === null) {
        $pdo = new PDO(DB_DSN, DB_USER, DB_PASS, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]);
        if (DB_DRIVER === 'sqlite') {
            $pdo->exec('PRAGMA journal_mode=WAL');
        }
    }
    return $pdo;
}

// ─── Query helpers ──────────────────────────────────────────────────────

function db_query(string $sql, array $params = []): array
{
    $stmt = db()->prepare($sql);
    $stmt->execute($params);
    return $stmt->fetchAll();
}

function db_query_one(string $sql, array $params = []): ?array
{
    $stmt = db()->prepare($sql);
    $stmt->execute($params);
    $row = $stmt->fetch();
    return $row ?: null;
}

function db_execute(string $sql, array $params = []): int
{
    $stmt = db()->prepare($sql);
    $stmt->execute($params);
    return $stmt->rowCount();
}

function db_insert(string $table, array $data): string
{
    $cols = implode(', ', array_keys($data));
    $places = implode(', ', array_fill(0, count($data), '?'));
    $sql = "INSERT INTO {$table} ({$cols}) VALUES ({$places})";
    $stmt = db()->prepare($sql);
    $stmt->execute(array_values($data));
    return db()->lastInsertId();
}

// ─── Active / Published query fragments ─────────────────────────────────

function not_trashed_clause(string $col = 'is_trashed'): string
{
    return "({$col} = 0 OR {$col} IS NULL)";
}

function published_clause(): string
{
    return "workflow_status = 'published' AND " . not_trashed_clause();
}

// ─── Site Settings ──────────────────────────────────────────────────────

function get_site_settings(): array
{
    static $cache = null;
    if ($cache !== null)
        return $cache;

    $settings = DEFAULT_SITE_SETTINGS;
    try {
        $rows = db_query("SELECT key, value FROM site_setting");
        foreach ($rows as $row) {
            $settings[$row['key']] = $row['value'];
        }
    } catch (Exception $e) {
        // Use defaults silently
    }
    $cache = $settings;
    return $settings;
}

// ─── Content Blocks ─────────────────────────────────────────────────────

function get_page_content(string $page): array
{
    $rows = db_query("SELECT section, content FROM content_block WHERE page = ?", [$page]);
    $result = [];
    foreach ($rows as $row) {
        $decoded = json_decode($row['content'], true);
        $result[$row['section']] = is_array($decoded) ? $decoded : [];
    }
    return $result;
}

// ─── Navigation queries ─────────────────────────────────────────────────

function get_nav_services(string $type): array
{
    $sql = "SELECT id, slug, title, description, icon_class
            FROM service
            WHERE service_type = ? AND " . published_clause() . "
            ORDER BY sort_order, id";
    $items = db_query($sql, [$type]);

    // Fallback: if no published, get all non-trashed of that type
    if (empty($items)) {
        $sql = "SELECT id, slug, title, description, icon_class
                FROM service
                WHERE service_type = ? AND " . not_trashed_clause() . "
                ORDER BY sort_order, id";
        $items = db_query($sql, [$type]);
    }
    return $items;
}

function get_nav_industries(): array
{
    $sql = "SELECT id, slug, title, description, icon_class
            FROM industry
            WHERE " . published_clause() . "
            ORDER BY sort_order, id";
    $items = db_query($sql);
    if (empty($items)) {
        $sql = "SELECT id, slug, title, description, icon_class
                FROM industry
                WHERE " . not_trashed_clause() . "
                ORDER BY sort_order, id";
        $items = db_query($sql);
    }
    return $items;
}
