<?php
/**
 * Pages Controller
 * Converts public/views/pages.py — all public page handlers
 */

// ─── Rich content data per industry ────────────────────────────────────
const INDUSTRY_CONTENT_DETAILS = [
    'healthcare-clinics' => [
        'challenge_descriptions' => [
            'Downtime during intake and charting' => 'System failures during patient check-in slow workflows and frustrate staff, causing delays in care delivery.',
            'Shared workstations with weak controls' => 'Multiple users sharing a single login create audit gaps and increase the risk of unauthorized access to PHI.',
            'Aging clinical endpoints' => 'Outdated desktops and peripherals lead to slow performance, security vulnerabilities, and incompatibility with modern EHR platforms.',
            'EHR vendor complexity' => 'Coordinating updates, integrations, and troubleshooting across EHR vendors requires specialized IT knowledge.',
            'HIPAA security pressure' => 'Clinics must meet strict compliance standards for data encryption, access logs, and breach notification protocols.',
        ],
        'solution_descriptions' => [
            'Role-based access and MFA' => 'Enforce least-privilege access with multi-factor authentication to protect patient data at every login.',
            'Endpoint hardening and patching' => 'Automated patching and security baselines keep clinical devices compliant and protected against known threats.',
            'EHR workflow support' => 'Dedicated support for EHR systems including vendor coordination, update management, and performance optimization.',
            'Backup and recovery planning' => 'HIPAA-compliant backup strategies with regular recovery testing ensure business continuity after any incident.',
            'Documented escalation playbooks' => 'Pre-built response procedures so staff know exactly what to do during critical IT issues.',
        ],
        'seo_keywords' => 'healthcare IT support, HIPAA compliant IT, medical office technology, EHR support, clinic IT services, Orange County healthcare IT',
        'seo_description' => 'HIPAA-compliant managed IT services for healthcare clinics in Orange County. Secure EHR support, endpoint protection, and 24/7 monitoring for medical practices.',
    ],
    'law-firms' => [
        'challenge_descriptions' => [
            'Case document bottlenecks' => 'Slow document retrieval and version conflicts waste billable hours and increase risk of filing errors.',
            'Risky file sharing practices' => 'Attorneys sharing sensitive case files via personal email or unencrypted drives create confidentiality breaches.',
            'Unmanaged remote access' => 'Lawyers working remotely without secured VPN or endpoint controls expose client data to interception.',
            'Weak backup visibility' => 'Without verified backups, a ransomware attack or hardware failure could mean permanent loss of case files.',
            'Phishing exposure' => 'Legal staff are prime phishing targets due to time pressure and high-value client information they handle.',
        ],
        'solution_descriptions' => [
            'Access-controlled document workflows' => 'Secure document management with role-based permissions and audit trails for every file interaction.',
            'Endpoint and identity hardening' => 'Advanced endpoint protection and identity verification to prevent unauthorized access to client data.',
            'Secure remote collaboration' => 'Encrypted VPN, secure file sharing, and compliant video conferencing for remote legal work.',
            'Backup validation and continuity' => 'Regular backup testing and disaster recovery drills to ensure case files are always recoverable.',
            'Priority deadline support' => 'Expedited IT support aligned with court deadlines and filing schedules to prevent costly delays.',
        ],
        'seo_keywords' => 'law firm IT support, legal technology services, legal document management, Orange County law firm IT',
        'seo_description' => 'Secure IT solutions for law firms in Orange County. Confidential document management, endpoint protection, and priority support aligned with court deadlines.',
    ],
    'construction-field-services' => [
        'challenge_descriptions' => [
            'Field device failures' => 'Tablets, phones, and ruggedized devices break down in harsh jobsite conditions, halting daily reports and communication.',
            'Unstable office-jobsite connectivity' => 'Poor network links between the main office and remote jobsites create delays in project management and file access.',
            'Inconsistent mobile security' => 'Field workers using personal devices without security policies expose project data to theft and malware.',
            'Shared credentials' => 'Teams sharing one login across multiple devices eliminates accountability and makes breach investigation impossible.',
            'Slow incident response' => 'When a device or system fails on a jobsite, delayed IT response causes idle crews and missed milestones.',
        ],
        'solution_descriptions' => [
            'Mobile device standardization' => 'Uniform device configurations with remote management ensure every field worker has secure, reliable tools.',
            'Cloud collaboration hardening' => 'Secure cloud-based project management, file sharing, and communication tools accessible from any jobsite.',
            'Secure onboarding and offboarding' => 'Automated provisioning and de-provisioning of field worker accounts to prevent unauthorized access after turnover.',
            'Priority field support' => 'Rapid remote and onsite IT support prioritized for time-sensitive construction operations.',
            'Diagnostics and lifecycle planning' => 'Proactive device health monitoring and replacement scheduling to prevent unexpected equipment failures.',
        ],
        'seo_keywords' => 'construction IT support, field services technology, jobsite IT solutions, Orange County construction IT',
        'seo_description' => 'Reliable IT support for construction and field service companies in Orange County. Mobile device management, secure cloud access, and rapid onsite support.',
    ],
    'manufacturing' => [
        'challenge_descriptions' => [
            'Production-impacting outages' => 'Unplanned IT downtime stops production lines, causing costly delays and missed delivery commitments.',
            'Aging infrastructure' => 'Legacy systems and outdated network equipment create bottlenecks and increase vulnerability to cyberattacks.',
            'Mixed legacy and modern systems' => 'Integrating older industrial control systems with modern cloud platforms introduces compatibility and security risks.',
            'Patch risk on live operations' => 'Applying security patches during production hours risks system crashes and unexpected behavior on critical equipment.',
            'Weak recovery testing' => 'Without regular disaster recovery drills, manufacturers cannot guarantee they can restore operations after a breach.',
        ],
        'solution_descriptions' => [
            'Proactive monitoring with safe maintenance windows' => 'Continuous monitoring with scheduled maintenance during planned downtime to minimize production disruption.',
            'Endpoint and identity hardening' => 'Secure authentication and endpoint controls to protect both office workstations and production floor systems.',
            'Backup and recovery validation' => 'Regular backup testing with documented recovery procedures to verify data can be restored under real conditions.',
            'Vendor coordination for ERP and tooling' => 'Managing vendor relationships and updates for ERP systems, SCADA, and specialized manufacturing software.',
            'Monthly health reporting' => 'Detailed monthly reports on system health, security posture, and recommended actions for continuous improvement.',
        ],
        'seo_keywords' => 'manufacturing IT support, production IT services, industrial cybersecurity, Orange County manufacturing IT',
        'seo_description' => 'Managed IT services for manufacturers in Orange County. Minimize downtime, secure industrial systems, and maintain production continuity with proactive support.',
    ],
    'retail-ecommerce' => [
        'challenge_descriptions' => [
            'POS outages during peak periods' => 'Point-of-sale failures during high-traffic periods directly impact revenue and customer satisfaction.',
            'Store connectivity inconsistencies' => 'Unreliable Wi-Fi and network connections across store locations create checkout delays and inventory sync issues.',
            'Payment endpoint risk' => 'Payment terminals and card readers that lack security updates are prime targets for data theft and skimming attacks.',
            'Checkout device failures' => 'Broken scanners, receipt printers, and card readers disrupt checkout flow and increase customer wait times.',
            'Multi-location visibility gaps' => 'Without centralized monitoring, issues at one store location may go undetected for hours or days.',
        ],
        'solution_descriptions' => [
            'POS and network stabilization' => 'Redundant network configurations and proactive POS monitoring to ensure uninterrupted checkout operations.',
            'Endpoint security controls' => 'Hardened payment terminals and workstations with encryption, patching, and real-time threat detection.',
            'Store operations cloud workflows' => 'Cloud-based inventory, scheduling, and reporting tools accessible from any store location securely.',
            'Vendor escalation management' => 'Single point of contact for all technology vendor issues, from POS providers to payment processors.',
            'Backup and incident planning' => 'Retail-specific disaster recovery and incident response plans to minimize downtime and data loss.',
        ],
        'seo_keywords' => 'retail IT support, eCommerce IT services, POS system support, Orange County retail IT',
        'seo_description' => 'IT support for retail and eCommerce businesses in Orange County. POS system management, payment security, and multi-location technology support.',
    ],
    'professional-services' => [
        'challenge_descriptions' => [
            'Tool sprawl and workflow friction' => 'Too many disconnected tools slow productivity and create data silos that make collaboration difficult.',
            'Manual onboarding and permissions' => 'Setting up new employees manually wastes IT hours and introduces security gaps from inconsistent permissions.',
            'Weak client-data safeguards' => 'Client-facing firms handling sensitive financial or business data need stronger encryption and access controls.',
            'Slow systems reducing billable output' => 'Laggy workstations and unreliable software directly reduce the hours professionals can bill to clients.',
            'Reactive support cycles' => 'Waiting until something breaks to call IT creates unpredictable costs and extended downtime.',
        ],
        'solution_descriptions' => [
            'Cloud collaboration standardization' => 'Unified cloud platforms for document sharing, communication, and project management to eliminate tool sprawl.',
            'Automated user lifecycle controls' => 'Automated onboarding and offboarding with predefined role-based permissions for security and efficiency.',
            'Endpoint and account hardening' => 'Advanced endpoint security and account protection including MFA, conditional access, and encryption.',
            'Proactive device support' => 'Continuous monitoring and maintenance of workstations to prevent performance issues before they impact productivity.',
            'Workflow automation opportunities' => 'Identify and implement automations for repetitive tasks like reporting, invoicing, and data entry.',
        ],
        'seo_keywords' => 'professional services IT, accounting firm IT support, consulting firm technology, Orange County professional IT',
        'seo_description' => 'Scalable IT support for professional services firms in Orange County. Cloud collaboration, automated onboarding, and proactive device management.',
    ],
    'nonprofits' => [
        'challenge_descriptions' => [
            'Limited internal IT capacity' => 'Most nonprofits lack dedicated IT staff, leaving technology decisions to people already stretched thin.',
            'Aging mixed devices' => 'Donated and outdated devices running different operating systems create support headaches and security risks.',
            'Donor-data security risk' => 'Donor information, payment details, and personal records require protection that many nonprofits are not equipped to provide.',
            'Volunteer access complexity' => 'Granting temporary access to volunteers while maintaining security boundaries is operationally challenging.',
            'Backup uncertainty' => 'Without verified backup processes, a hardware failure could mean losing years of organizational data.',
        ],
        'solution_descriptions' => [
            'Right-sized managed coverage' => 'Managed IT services scaled to nonprofit budgets — no unnecessary features, just what your team actually needs.',
            'Secure cloud identity and collaboration' => 'Cloud-based identity management and collaboration tools with nonprofit licensing discounts where available.',
            'Device standardization' => 'Consistent device configurations and software deployments to reduce support complexity and improve security.',
            'Recovery readiness testing' => 'Regular backup verification and recovery drills to ensure your data is always recoverable.',
            'Strategic IT planning' => 'Technology roadmaps aligned with your mission and grant cycles to maximize impact per dollar spent.',
        ],
        'seo_keywords' => 'nonprofit IT support, NGO technology services, nonprofit cybersecurity, Orange County nonprofit IT',
        'seo_description' => 'Mission-focused IT support for nonprofits in Orange County. Budget-conscious managed services, donor data protection, and strategic technology planning.',
    ],
    'real-estate-property-management' => [
        'challenge_descriptions' => [
            'Mobile device issues for agents' => 'Real estate agents depend on smartphones and tablets for showings, closings, and client communication — downtime costs deals.',
            'Fragmented file sharing' => 'Contracts, disclosures, and inspection reports scattered across personal drives and email threads create version confusion.',
            'Transaction-time support delays' => 'IT issues during a closing or contract signing can delay transactions and damage client relationships.',
            'Weak account security' => 'Email account compromises in real estate are increasingly common, leading to wire fraud and data exposure.',
            'Onboarding/offboarding gaps' => 'High agent turnover means credentials are frequently left active, creating unauthorized access risks.',
        ],
        'solution_descriptions' => [
            'Secure cloud document workflows' => 'Centralized document management with version control, e-signatures, and secure sharing for transaction files.',
            'Mobile and office device management' => 'Unified management of agent smartphones, tablets, and office workstations for consistent security and performance.',
            'Identity protection and phishing controls' => 'Email security with advanced phishing protection to prevent wire fraud and business email compromise.',
            'Repeatable user lifecycle management' => 'Standardized onboarding and offboarding checklists with automated account provisioning and deactivation.',
            'Priority troubleshooting support' => 'Fast-track IT support prioritized for time-sensitive real estate transactions and deadlines.',
        ],
        'seo_keywords' => 'real estate IT support, property management technology, wire fraud prevention, Orange County real estate IT',
        'seo_description' => 'IT support for real estate and property management firms in Orange County. Mobile device management, wire fraud prevention, and transaction-ready technology.',
    ],
];

class PagesController
{
    // ─── Service profile generation (rich default data) ─────────────

    private static function default_service_profile(array $service): array
    {
        $is_professional = strtolower(trim($service['service_type'] ?? '')) === 'professional';
        $description = mb_substr($service['description'] ?? '', 0, 220);
        if (!$description)
            $description = $service['title'] . ' service support for Orange County businesses.';

        if ($is_professional) {
            $process = [
                ['title' => 'Discovery', 'detail' => 'Map requirements, risks, and success criteria.', 'icon' => 'fa-solid fa-clipboard-check'],
                ['title' => 'Architecture', 'detail' => 'Design secure workflows, integrations, and standards.', 'icon' => 'fa-solid fa-diagram-project'],
                ['title' => 'Implementation', 'detail' => 'Deliver in milestones with validation at each stage.', 'icon' => 'fa-solid fa-gears'],
                ['title' => 'Optimization', 'detail' => 'Refine performance and outcomes with measurable reporting.', 'icon' => 'fa-solid fa-chart-line'],
            ];
            $tools = [
                ['name' => 'Microsoft 365', 'icon' => 'fa-brands fa-microsoft', 'desc' => 'Identity, productivity, and endpoint workflows'],
                ['name' => 'Cloudflare', 'icon' => 'fa-solid fa-cloud', 'desc' => 'Edge networking, security, and performance controls'],
                ['name' => 'Endpoint Monitoring', 'icon' => 'fa-solid fa-desktop', 'desc' => 'Visibility into uptime, incidents, and drift'],
                ['name' => 'Secure Access', 'icon' => 'fa-solid fa-shield-halved', 'desc' => 'Policy-based authentication and access control'],
            ];
            $deliverables = [
                ['label' => 'Coverage', 'value' => 'Strategic delivery aligned to business goals', 'icon' => 'fa-solid fa-layer-group'],
                ['label' => 'Security', 'value' => 'Risk-aware controls and compliance alignment', 'icon' => 'fa-solid fa-shield-halved'],
                ['label' => 'Performance', 'value' => 'Stable operations with optimization visibility', 'icon' => 'fa-solid fa-gauge-high'],
                ['label' => 'Support', 'value' => 'Structured escalation and accountable communication', 'icon' => 'fa-solid fa-headset'],
            ];
            $hero_badges = [
                ['icon' => 'fa-solid fa-layer-group', 'label' => 'Strategic Discovery and Planning'],
                ['icon' => 'fa-solid fa-gears', 'label' => 'Milestone-Based Implementation'],
                ['icon' => 'fa-solid fa-chart-line', 'label' => 'Continuous Performance Optimization'],
            ];
        } else {
            $process = [
                ['title' => 'Intake & Diagnostics', 'detail' => 'Capture symptoms and run root-cause tests.', 'icon' => 'fa-solid fa-stethoscope'],
                ['title' => 'Repair Plan', 'detail' => 'Confirm scope, parts, and expected turnaround.', 'icon' => 'fa-solid fa-screwdriver-wrench'],
                ['title' => 'Repair Execution', 'detail' => 'Apply component-level fixes with QA checkpoints.', 'icon' => 'fa-solid fa-microchip'],
                ['title' => 'Validation', 'detail' => 'Stress test and verify full functional readiness.', 'icon' => 'fa-solid fa-circle-check'],
            ];
            $tools = [
                ['name' => 'Bench Diagnostics', 'icon' => 'fa-solid fa-laptop-medical', 'desc' => 'Hardware and subsystem verification workflows'],
                ['name' => 'Data-Safe Handling', 'icon' => 'fa-solid fa-user-lock', 'desc' => 'Minimized risk during repair and recovery handling'],
                ['name' => 'Thermal + Power Tests', 'icon' => 'fa-solid fa-temperature-half', 'desc' => 'Performance and stability validation under load'],
                ['name' => 'Post-Repair QA', 'icon' => 'fa-solid fa-list-check', 'desc' => 'Final checklist before customer handoff'],
            ];
            $deliverables = [
                ['label' => 'Diagnostics', 'value' => 'Root-cause confirmation before repairs', 'icon' => 'fa-solid fa-stethoscope'],
                ['label' => 'Turnaround', 'value' => 'Clear checkpoints and status visibility', 'icon' => 'fa-solid fa-stopwatch'],
                ['label' => 'Parts Quality', 'value' => 'Verified components and repair standards', 'icon' => 'fa-solid fa-microchip'],
                ['label' => 'Validation', 'value' => 'Functional and stress testing complete', 'icon' => 'fa-solid fa-circle-check'],
            ];
            $hero_badges = [
                ['icon' => 'fa-solid fa-stethoscope', 'label' => 'Diagnostics-First Workflow'],
                ['icon' => 'fa-solid fa-screwdriver-wrench', 'label' => 'Component-Level Repair Paths'],
                ['icon' => 'fa-solid fa-circle-check', 'label' => 'Validation Before Handoff'],
            ];
        }

        $service_modules = array_map(fn($p) => ['title' => $p['title'], 'detail' => $p['detail'], 'icon' => $p['icon']], array_slice($process, 0, 4));
        $issue_solution_map = array_map(fn($p) => [
            'issue' => $p['title'] . ' gaps creating inconsistent outcomes',
            'solution' => $p['detail'],
            'icon' => $p['icon'],
        ], array_slice($process, 0, 4));
        $lead_time_diagram = array_map(fn($p) => [
            'phase' => $p['title'],
            'eta' => '1-3 business days',
            'detail' => $p['detail'],
            'icon' => $p['icon'],
        ], array_slice($process, 0, 4));

        $profile = [
            'meta_description' => $description,
            'meta_title' => $service['title'] . ' in Orange County | Right On Repair',
            'keywords' => [$service['title'] . ' Orange County', $service['title'] . ' services', 'business IT support', 'Right On Repair'],
            'intro_kicker' => 'Solutions',
            'positioning_badge' => 'Service Delivery Program',
            'board_title' => 'Service Workflow',
            'modules_title' => 'Specialized Service Programs',
            'narrative_title' => 'Service Scope and Delivery Standards',
            'process' => $process,
            'tools' => $tools,
            'deliverables' => $deliverables,
            'hero_badges' => $hero_badges,
            'service_modules' => $service_modules,
            'issue_solution_map' => $issue_solution_map,
            'lead_time_diagram' => $lead_time_diagram,
            'faqs' => [
                ['q' => 'What is included in ' . strtolower($service['title']) . '?', 'a' => 'We scope your requirements, deliver with clear milestones, and provide post-delivery support and optimization guidance.'],
                ['q' => 'Can this be tailored to our environment?', 'a' => 'Yes. Every engagement is adapted to your business workflows, constraints, and growth goals.'],
                ['q' => 'Do you provide post-delivery support?', 'a' => 'Yes. We offer ongoing support, reporting, and improvement cycles after implementation.'],
            ],
            'seo_content_blocks' => [],
            'service_area_cities' => ORANGE_COUNTY_CA_CITIES,
            'compliance_frameworks' => ['NIST-aligned controls', 'Least-privilege access principles', 'Routine security review cadences'],
            'proof_points' => [
                ['label' => 'Scope', 'value' => 'Clear objectives and accountable ownership'],
                ['label' => 'Reliability', 'value' => 'Stability-first implementation and testing'],
                ['label' => 'Visibility', 'value' => 'Actionable reporting and communication cadence'],
            ],
            'related_technologies' => array_column($tools, 'name'),
            'supported_brands' => [],
            'brand_services' => [],
        ];

        // Merge profile_json overrides if available
        $incoming = json_decode($service['profile_json'] ?? '{}', true);
        if (is_array($incoming) && !empty($incoming)) {
            foreach (['meta_description', 'meta_title', 'intro_kicker', 'positioning_badge', 'board_title', 'modules_title', 'narrative_title'] as $key) {
                if (!empty($incoming[$key]))
                    $profile[$key] = $incoming[$key];
            }
            foreach (['keywords', 'related_technologies', 'service_area_cities', 'compliance_frameworks', 'supported_brands'] as $key) {
                if (!empty($incoming[$key]) && is_array($incoming[$key]))
                    $profile[$key] = $incoming[$key];
            }
            if (!empty($incoming['seo_content_blocks']) && is_array($incoming['seo_content_blocks'])) {
                $profile['seo_content_blocks'] = array_filter(array_map(fn($b) => trim($b), $incoming['seo_content_blocks']));
            }
            foreach (['process', 'tools', 'deliverables', 'hero_badges', 'service_modules', 'issue_solution_map', 'lead_time_diagram'] as $key) {
                if (!empty($incoming[$key]) && is_array($incoming[$key]))
                    $profile[$key] = $incoming[$key];
            }
            if (!empty($incoming['faqs']) && is_array($incoming['faqs']))
                $profile['faqs'] = $incoming['faqs'];
            if (!empty($incoming['proof_points']) && is_array($incoming['proof_points']))
                $profile['proof_points'] = $incoming['proof_points'];
            if (!empty($incoming['brand_services']) && is_array($incoming['brand_services']))
                $profile['brand_services'] = $incoming['brand_services'];
        }

        // Always use full OC cities
        $profile['service_area_cities'] = ORANGE_COUNTY_CA_CITIES;
        if (empty($profile['related_technologies'])) {
            $profile['related_technologies'] = array_column($profile['tools'] ?? [], 'name');
        }

        return $profile;
    }

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

        $service_profile = self::default_service_profile($service);

        render_with_layout('service_detail', [
            'slug' => $slug,
            'service' => $service,
            'service_profile' => $service_profile,
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
        if (!$hero_desc)
            $hero_desc = trim($industry['description'] ?? '');
        $industry['hero_description'] = $hero_desc;

        $industry['challenges'] = trim($industry['challenges'] ?? 'Downtime pressure|Security and compliance requirements|Scalability constraints');
        $industry['solutions'] = trim($industry['solutions'] ?? 'Proactive monitoring and escalation|Security-first architecture and controls|Roadmap-based technology modernization');
        $industry['stats'] = trim($industry['stats'] ?? 'Response SLA:24/7|Coverage:Orange County|Support Model:Onsite + Remote|Focus:Security + Uptime');

        // Rich content details per industry slug
        $content_details = INDUSTRY_CONTENT_DETAILS[$slug] ?? [];

        render_with_layout('industry_detail', [
            'slug' => $slug,
            'industry' => $industry,
            'services' => $services,
            'other_industries' => $other_industries,
            'challenge_descriptions' => $content_details['challenge_descriptions'] ?? [],
            'solution_descriptions' => $content_details['solution_descriptions'] ?? [],
            'seo_keywords' => $content_details['seo_keywords'] ?? '',
            'seo_description' => $content_details['seo_description'] ?? '',
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
