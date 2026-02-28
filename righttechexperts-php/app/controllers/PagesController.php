<?php
/**
 * Pages Controller
 * Converts public/views/pages.py — all public page handlers
 */

class PagesController
{
    // ─── Shared query helpers ───────────────────────────────────────

    private static function service_list(?string $service_type = null, ?bool $is_featured = null, ?int $exclude_id = null, ?int $limit = null): array
    {
        $where = [published_clause()];
        $params = [];
        if ($service_type) {
            $where[] = "service_type = ?";
            $params[] = $service_type;
        }
        if ($is_featured !== null) {
            $where[] = "is_featured = ?";
            $params[] = (int) $is_featured;
        }
        if ($exclude_id) {
            $where[] = "id != ?";
            $params[] = $exclude_id;
        }
        $sql = "SELECT * FROM service WHERE " . implode(' AND ', $where) . " ORDER BY sort_order, id";
        if ($limit)
            $sql .= " LIMIT {$limit}";
        $items = db_query($sql, $params);
        // Fallback: if no published items, try non-trashed
        if (empty($items)) {
            $where2 = [not_trashed_clause()];
            $params2 = [];
            if ($service_type) {
                $where2[] = "service_type = ?";
                $params2[] = $service_type;
            }
            if ($is_featured !== null) {
                $where2[] = "is_featured = ?";
                $params2[] = (int) $is_featured;
            }
            if ($exclude_id) {
                $where2[] = "id != ?";
                $params2[] = $exclude_id;
            }
            $sql2 = "SELECT * FROM service WHERE " . implode(' AND ', $where2) . " ORDER BY sort_order, id";
            if ($limit)
                $sql2 .= " LIMIT {$limit}";
            $items = db_query($sql2, $params2);
        }
        // Inject virtual laptop-repair if missing
        $haslaptop = false;
        foreach ($items as $i) {
            if ($i['slug'] === 'laptop-repair') {
                $haslaptop = true;
                break;
            }
        }
        if (!$haslaptop && ($service_type === 'repair' || $service_type === null)) {
            $items[] = [
                'id' => -9001,
                'slug' => 'laptop-repair',
                'title' => 'Laptop Repair',
                'description' => 'Fast laptop diagnostics and repair in Orange County.',
                'icon_class' => 'fa-solid fa-laptop-medical',
                'service_type' => 'repair',
                'is_featured' => 1,
                'sort_order' => 9999,
            ];
        }
        return $items;
    }

    private static function industry_list(?int $limit = null): array
    {
        $sql = "SELECT * FROM industry WHERE " . published_clause() . " ORDER BY sort_order, id";
        if ($limit)
            $sql .= " LIMIT {$limit}";
        $items = db_query($sql);
        if (empty($items)) {
            $sql = "SELECT * FROM industry WHERE " . not_trashed_clause() . " ORDER BY sort_order, id";
            if ($limit)
                $sql .= " LIMIT {$limit}";
            $items = db_query($sql);
        }
        return $items;
    }

    private static function build_home_hero_cards(array $cb, array $all_services): array
    {
        $all_slugs = array_column($all_services, 'slug');
        $detail_or_services = function ($slug) use ($all_slugs) {
            return in_array($slug, $all_slugs) ? "/services/{$slug}" : '/services';
        };

        return [
            ['title' => 'Cloud', 'subtitle' => 'AWS, Azure, and GCP', 'icon' => 'fa-solid fa-cloud', 'color' => 'blue', 'href' => $detail_or_services('cloud-solutions'), 'aria_label' => 'Open Cloud Solutions service page'],
            ['title' => 'Cybersecurity', 'subtitle' => 'Threat Defense', 'icon' => 'fa-solid fa-lock', 'color' => 'purple', 'href' => $detail_or_services('cybersecurity'), 'aria_label' => 'Open Cybersecurity service page'],
            ['title' => 'Software & Web Development', 'subtitle' => 'Full-Stack Solutions', 'icon' => 'fa-solid fa-code', 'color' => 'green', 'href' => $detail_or_services('software-development'), 'aria_label' => 'Open Software & Web Development service page'],
            ['title' => 'Technical Repair', 'subtitle' => 'Certified Technicians', 'icon' => 'fa-solid fa-laptop-medical', 'color' => 'amber', 'href' => '/services#repair', 'aria_label' => 'Open Technical Repair services'],
            ['title' => 'Managed IT Solutions', 'subtitle' => 'Proactive Support', 'icon' => 'fa-solid fa-network-wired', 'color' => 'cyan', 'href' => $detail_or_services('managed-it-services'), 'aria_label' => 'Open Managed IT Solutions service page'],
            ['title' => 'Enterprise Consultancy', 'subtitle' => 'Strategic Advisory', 'icon' => 'fa-solid fa-handshake', 'color' => 'rose', 'href' => $detail_or_services('enterprise-consultancy'), 'aria_label' => 'Open Enterprise Consultancy service page'],
        ];
    }

    // ─── Page handlers ──────────────────────────────────────────────

    public static function index(): void
    {
        $pro_services = normalize_icon_items(
            self::service_list('professional', true),
            'fa-solid fa-gear'
        );
        if (empty($pro_services)) {
            $pro_services = normalize_icon_items(
                self::service_list('professional'),
                'fa-solid fa-gear'
            );
        }

        $repair_services = normalize_icon_items(
            self::service_list('repair', true),
            'fa-solid fa-wrench'
        );
        if (empty($repair_services)) {
            $repair_services = normalize_icon_items(
                self::service_list('repair'),
                'fa-solid fa-wrench'
            );
        }

        $all_services = self::service_list();
        $testimonials = db_query(
            "SELECT * FROM testimonial WHERE is_featured = 1 AND " . not_trashed_clause() . " ORDER BY id"
        );
        $cb = get_page_content('home');
        $hero_cards = self::build_home_hero_cards($cb, $all_services);

        render_with_layout('index', [
            'pro_services' => $pro_services,
            'repair_services' => $repair_services,
            'testimonials' => $testimonials,
            'hero_cards' => $hero_cards,
            'cb' => $cb,
        ]);
    }

    public static function about(): void
    {
        $team = db_query(
            "SELECT * FROM team_member WHERE " . not_trashed_clause() . " ORDER BY sort_order, id"
        );
        render_with_layout('about', [
            'team' => $team,
            'cb' => get_page_content('about'),
        ]);
    }

    public static function services(): void
    {
        $pro_services = normalize_icon_items(
            self::service_list('professional'),
            'fa-solid fa-gear'
        );
        $repair_services = normalize_icon_items(
            self::service_list('repair'),
            'fa-solid fa-wrench'
        );
        $cb = get_page_content('services');

        render_with_layout('services', [
            'pro_services' => $pro_services,
            'repair_services' => $repair_services,
            'active_type' => $_GET['type'] ?? '',
            'cb' => $cb,
        ]);
    }

    public static function services_it_track(): void
    {
        header('Location: /services?type=professional', true, 301);
        exit;
    }

    public static function services_repair_track(): void
    {
        header('Location: /services#repair', true, 301);
        exit;
    }

    public static function service_detail(string $slug): void
    {
        $service = db_query_one(
            "SELECT * FROM service WHERE slug = ? AND " . published_clause(),
            [$slug]
        );
        if (!$service) {
            $service = db_query_one(
                "SELECT * FROM service WHERE slug = ? AND " . not_trashed_clause(),
                [$slug]
            );
        }
        // Virtual laptop-repair
        if (!$service && $slug === 'laptop-repair') {
            $service = [
                'id' => -9001,
                'slug' => 'laptop-repair',
                'title' => 'Laptop Repair',
                'description' => 'Fast laptop diagnostics and repair in Orange County.',
                'icon_class' => 'fa-solid fa-laptop-medical',
                'service_type' => 'repair',
                'is_featured' => 1,
                'profile_json' => null,
            ];
        }
        if (!$service) {
            http_response_code(404);
            self::not_found();
            return;
        }

        $service['icon_class'] = normalize_icon_class($service['icon_class'] ?? '', 'fa-solid fa-gear');

        $related_services = normalize_icon_items(
            self::service_list($service['service_type'] ?? null, null, (int) ($service['id'] ?? 0), 6),
            'fa-solid fa-gear'
        );
        $featured_industries = normalize_icon_items(
            self::industry_list(6),
            'fa-solid fa-building'
        );

        render_with_layout('service_detail', [
            'slug' => $slug,
            'service' => $service,
            'related_services' => $related_services,
            'featured_industries' => $featured_industries,
        ]);
    }

    public static function blog(): void
    {
        $page = max(1, min((int) ($_GET['page'] ?? 1), 1000));
        $category_slug = trim(substr($_GET['category'] ?? '', 0, 120));
        $search = trim(substr($_GET['q'] ?? '', 0, 120));
        $per_page = 6;

        $where = [published_clause()];
        $params = [];
        if ($category_slug) {
            $cat = db_query_one("SELECT id FROM category WHERE slug = ?", [$category_slug]);
            if ($cat) {
                $where[] = "category_id = ?";
                $params[] = $cat['id'];
            }
        }
        if ($search) {
            $where[] = "title LIKE ?";
            $params[] = "%{$search}%";
        }

        $total = (int) db_query_one(
            "SELECT COUNT(*) as cnt FROM post WHERE " . implode(' AND ', $where),
            $params
        )['cnt'];
        $pages = max(1, (int) ceil($total / $per_page));
        $page = min($page, $pages);
        $offset = ($page - 1) * $per_page;

        $posts = db_query(
            "SELECT * FROM post WHERE " . implode(' AND ', $where) . " ORDER BY created_at DESC, id DESC LIMIT {$per_page} OFFSET {$offset}",
            $params
        );
        $categories = db_query("SELECT id, name, slug FROM category ORDER BY name, id");

        render_with_layout('blog', [
            'posts' => $posts,
            'page' => $page,
            'total_pages' => $pages,
            'total' => $total,
            'categories' => $categories,
            'current_category' => $category_slug,
            'search' => $search,
        ]);
    }

    public static function post(string $slug): void
    {
        $post = db_query_one(
            "SELECT * FROM post WHERE slug = ? AND " . published_clause(),
            [$slug]
        );
        if (!$post) {
            http_response_code(404);
            self::not_found();
            return;
        }

        $recent_posts = db_query(
            "SELECT * FROM post WHERE id != ? AND " . published_clause() . " ORDER BY created_at DESC, id DESC LIMIT 3",
            [$post['id']]
        );

        render_with_layout('post', [
            'post' => $post,
            'recent_posts' => $recent_posts,
        ]);
    }

    public static function industries(): void
    {
        $all_industries = normalize_icon_items(
            self::industry_list(),
            'fa-solid fa-building'
        );
        $cb = get_page_content('industries');

        render_with_layout('industries', [
            'industries' => $all_industries,
            'cb' => $cb,
        ]);
    }

    public static function industry_detail(string $slug): void
    {
        $industry = db_query_one(
            "SELECT * FROM industry WHERE slug = ? AND " . published_clause(),
            [$slug]
        );
        if (!$industry) {
            $industry = db_query_one(
                "SELECT * FROM industry WHERE slug = ? AND " . not_trashed_clause(),
                [$slug]
            );
        }
        if (!$industry) {
            http_response_code(404);
            self::not_found();
            return;
        }

        $industry['icon_class'] = normalize_icon_class($industry['icon_class'] ?? '', 'fa-solid fa-building');

        $services = normalize_icon_items(
            self::service_list(null, true, null, 6),
            'fa-solid fa-gear'
        );
        if (empty($services)) {
            $services = normalize_icon_items(
                self::service_list(null, null, null, 6),
                'fa-solid fa-gear'
            );
        }

        $other_industries = normalize_icon_items(
            array_filter(self::industry_list(), fn($i) => $i['slug'] !== $slug),
            'fa-solid fa-building'
        );

        // Parse challenges/solutions/stats
        $hero_desc = trim($industry['hero_description'] ?? $industry['description'] ?? '');
        $challenges = trim($industry['challenges'] ?? 'Downtime pressure|Security and compliance requirements|Scalability constraints');
        $solutions = trim($industry['solutions'] ?? 'Proactive monitoring and escalation|Security-first architecture and controls|Roadmap-based technology modernization');
        $stats = trim($industry['stats'] ?? 'Response SLA:24/7|Coverage:Orange County|Support Model:Onsite + Remote|Focus:Security + Uptime');

        render_with_layout('industry_detail', [
            'slug' => $slug,
            'industry' => $industry,
            'hero_description' => $hero_desc,
            'challenges' => $challenges,
            'solutions' => $solutions,
            'stats' => $stats,
            'services' => $services,
            'other_industries' => $other_industries,
        ]);
    }

    public static function contact(): void
    {
        render_with_layout('contact', []);
    }

    public static function request_quote(): void
    {
        render_with_layout('request_quote', []);
    }

    public static function request_quote_personal(): void
    {
        render_with_layout('request_quote_personal', []);
    }

    public static function remote_support(): void
    {
        render_with_layout('remote_support', []);
    }

    public static function ticket_search(): void
    {
        $ticket_number = trim($_GET['ticket_number'] ?? '');
        $ticket = null;
        $events = [];
        if ($ticket_number) {
            $sanitized = preg_replace('/[^A-Z0-9\-]/', '', strtoupper($ticket_number));
            $ticket = db_query_one("SELECT * FROM support_ticket WHERE ticket_number = ?", [$sanitized]);
            if ($ticket) {
                $events = db_query(
                    "SELECT * FROM support_ticket_event WHERE ticket_id = ? ORDER BY created_at DESC",
                    [$ticket['id']]
                );
            }
        }
        render_with_layout('ticket_search', [
            'ticket_number' => $ticket_number,
            'ticket' => $ticket,
            'events' => $events,
        ]);
    }

    public static function cms_page(string $slug): void
    {
        $page = db_query_one("SELECT * FROM cms_page WHERE slug = ? AND is_published = 1", [$slug]);
        if (!$page) {
            http_response_code(404);
            self::not_found();
            return;
        }
        render_with_layout('cms_page', ['page' => $page]);
    }

    public static function cms_article(string $article_id): void
    {
        $article = db_query_one("SELECT * FROM cms_article WHERE id = ? AND is_published = 1", [(int) $article_id]);
        if (!$article) {
            http_response_code(404);
            self::not_found();
            return;
        }
        render_with_layout('cms_article', ['article' => $article]);
    }

    public static function not_found(): void
    {
        render_with_layout('errors/404', [
            'page_title' => 'Page Not Found | Right On Repair',
        ]);
    }
}
