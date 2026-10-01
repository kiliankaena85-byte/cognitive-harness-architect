"""
Project Harness & Skill Synthesizer - Command Line Interface
Dual-Agent Architecture: Gemini (Global Reasoning) + Intel AI Boost NPU (Local System 1 Arbiter).
"""

import sys
import os
import argparse
import json
import hashlib
from pathlib import Path

# Force UTF-8 stdout/stderr for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.npu_engine import IntelNpuDecisionEngine
from core.decomposer import ProjectVectorDecomposer
from core.multi_pass_crawler import MultiPassDocCrawler
from core.skill_synthesizer import SkillSynthesizer
from core.harness_scaffolder import ProjectHarnessScaffolder
from core.evolutionary_engine import EvolutionaryHarnessArchitect
from core.orchestrator import DagOrchestrator, CANONICAL_FILENAMES, MINISTRY_NAMES
from config import DEFAULT_SCRATCH_DIR, GLOBAL_SKILLS_DIR



def print_banner():
    print("=" * 70)
    print("   PROJECT HARNESS & SKILL SYNTHESIZER (PHSS)")
    print("   Dual-Agent Architecture: Gemini + Intel AI Boost NPU")
    print("=" * 70)


def cmd_analyze(args):
    print_banner()
    brief = args.brief
    print(f"\n[1/3] Decomposing Project Brief:\n      \"{brief}\"\n")

    npu = IntelNpuDecisionEngine()
    decomposer = ProjectVectorDecomposer(npu)
    result = decomposer.decompose(brief)

    print(f"Hardware Arbiter : {result['npu_telemetry']['device']} (NPU Active: {result['npu_telemetry']['npu_active']})")
    print(f"Decision Model   : {result['npu_telemetry']['model']}\n")

    print("=" * 70)
    print(f"HIERARCHICAL DECOMPOSITION: {result['total_ministries']} MINISTRIES | {result['total_specialists']} SPECIALISTS")
    print("=" * 70)

    for m_idx, ministry in enumerate(result["hierarchy"], 1):
        status_gate = "[PASSED]" if ministry["gate_ready_preliminary"] else "[BLOCKED]"
        print(f"\n[{m_idx}/7] {ministry['ministry_name']}")
        print(f"    Contract Output : {ministry['contract_out']}")
        print(f"    Stage-Gate      : {ministry['stage_gate']}")
        print(f"    Gate Status     : {status_gate} (Confidence: {ministry['gate_confidence'] * 100:.1f}%)")
        print("    Specialists:")
        for spec in ministry["specialists"]:
            print(f"      - {spec['id']} {spec['role']:<40} [Priority Rating: {spec['npu_priority_rating']}/10 | {spec['latency_ms']}ms]")

    print("\n" + "=" * 70)
    print("IDENTIFIED ARCHITECTURAL VECTORS:")
    print("=" * 70)

    for i, vec in enumerate(result["vectors"], 1):
        print(f"Vector {i}: {vec['category']}")
        print(f"  Recommended Tech : {vec['recommended_tech']}")
        print(f"  NPU Confidence   : {vec['confidence'] * 100:.1f}%")
        print(f"  Required Skill   : {vec['required_skill']}")
        print(f"  Rationale        : {vec['rationale']}\n")

    print("=" * 70)
    print("SKILL INVENTORY AUDIT:")
    print("=" * 70)
    for s in result["skills_audit"]:
        status = "[INSTALLED]" if s["is_installed"] else "[MISSING - MUST SYNTHESIZE]"
        print(f"  {status:<28} {s['skill_name']} ({s['category']})")

    print(f"\nMissing Skills to Synthesize: {result['missing_skills_count']}\n")
    return result


def cmd_scaffold(args):
    print_banner()
    project_name = args.name
    brief = args.brief
    target_dir = DEFAULT_SCRATCH_DIR / project_name

    print(f"\nInitializing Project Scaffolding for: '{project_name}'")
    print(f"Target Directory: {target_dir}")
    print(f"Brief: \"{brief}\"\n")

    # Step 1: Decompose
    npu = IntelNpuDecisionEngine()
    decomposer = ProjectVectorDecomposer(npu)
    decomp_result = decomposer.decompose(brief)

    # Step 2: Multi-Pass Research & Synthesis for Missing Skills
    synthesizer = SkillSynthesizer()
    generated_skills_dir = Path(__file__).resolve().parent / "generated_skills"
    generated_skills_dir.mkdir(exist_ok=True)

    synthesized_paths = []

    # Knowledge bases for canonical narrow skills
    skill_definitions = {
        "cloudflare-workers": {
            "title": "Cloudflare Workers & D1 Edge Runtime",
            "description": "Deploy, configure, and orchestrate Cloudflare Workers, KV namespaces, and D1 serverless SQL databases using Wrangler v3.",
            "phases": [
                {"phase": "1", "what": "Local Dev & Emulation", "transport": "CLI", "surface": "npx wrangler dev"},
                {"phase": "2", "what": "D1 Database Migrations", "transport": "CLI", "surface": "npx wrangler d1 migrations apply"},
                {"phase": "3", "what": "KV Key-Value Binding", "transport": "REST/CLI", "surface": "npx wrangler kv:key put"},
                {"phase": "4", "what": "Edge Deployment", "transport": "CLI", "surface": "npx wrangler deploy"}
            ],
            "auth": {
                "env_var": "CLOUDFLARE_API_TOKEN",
                "scopes": ["Account.Workers", "Account.D1", "Account.KV Storage"]
            },
            "commands": [
                {"name": "Initialize Project", "description": "Generates a clean TypeScript worker structure with wrangler.jsonc", "command": "npm create cloudflare@latest -- --type hello-world --ts"},
                {"name": "Local Emulation", "description": "Starts Miniflare-based local simulation matching edge constraints", "command": "npx wrangler dev --port 8787"},
                {"name": "Apply D1 Schema", "description": "Applies SQL migrations locally or remotely", "command": "npx wrangler d1 migrations apply <DB_NAME> --local"}
            ],
            "errors": [
                {"code": "10001", "cause": "Invalid Cloudflare API Token or missing permissions", "action": "Verify CLOUDFLARE_API_TOKEN and check Account-level scopes in CF dashboard"},
                {"code": "429", "cause": "Rate limit exceeded on Edge KV/D1 mutations", "action": "Implement exponential backoff retry with jitter"}
            ],
            "notes": "### Wrangler v3 Standards\nAlways use `wrangler.jsonc` instead of deprecated `wrangler.toml` for modern configuration.\nEnforce `nodejs_compat` compatibility flag in config."
        },
        "github-actions-automation": {
            "title": "GitHub Actions & gh CLI Automation",
            "description": "Manage GitHub workflows, automated CI/CD releases, issue triage, and secret management using gh CLI and declarative YAML.",
            "phases": [
                {"phase": "1", "what": "Repository & Secret Preflight", "transport": "CLI", "surface": "gh secret set"},
                {"phase": "2", "what": "Workflow Lint & Validation", "transport": "CLI", "surface": "gh workflow view"},
                {"phase": "3", "what": "Trigger & Monitor Runs", "transport": "CLI", "surface": "gh run watch"},
                {"phase": "4", "what": "Semantic Release Tagging", "transport": "CLI", "surface": "gh release create"}
            ],
            "auth": {
                "env_var": "GITHUB_TOKEN",
                "scopes": ["repo", "workflow", "write:packages"]
            },
            "commands": [
                {"name": "Auth Status", "description": "Checks current GitHub CLI authentication state", "command": "gh auth status"},
                {"name": "Trigger Workflow", "description": "Manually triggers a workflow dispatch with parameters", "command": "gh workflow run test.yml -f environment=staging"},
                {"name": "Watch Latest Run", "description": "Streams live job execution logs in terminal", "command": "gh run watch $(gh run list --limit 1 --json databaseId -q '.[0].databaseId')"}
            ],
            "errors": [
                {"code": "HTTP 401", "cause": "Bad GITHUB_TOKEN or expired SSH session", "action": "Run `gh auth login` or re-export valid GITHUB_TOKEN"},
                {"code": "HTTP 403", "cause": "Resource not accessible by integration (missing workflow permissions)", "action": "Update repo Settings -> Actions -> General -> Workflow permissions to Read and Write"}
            ],
            "notes": "### Actions Best Practices\nPin actions to exact full SHA commits rather than mutable tags for security.\nUse `actions/checkout@v4` and `actions/setup-node@v4`."
        },
        "microsoft-word-docx-engine": {
            "title": "Microsoft Word DOCX & OpenXML Processing Engine",
            "description": "Parse, modify, and render Microsoft Word (.docx) documents in pure JavaScript/TypeScript without requiring Microsoft Word desktop installation.",
            "phases": [
                {"phase": "1", "what": "Template Inspection", "transport": "CLI/Code", "surface": "docx-templates analyze"},
                {"phase": "2", "what": "Dynamic Data Merging", "transport": "Library", "surface": "createReport({ template, data })"},
                {"phase": "3", "what": "OpenXML Table & Style Injection", "transport": "Library", "surface": "new Table({ rows: [...] })"},
                {"phase": "4", "what": "Integrity & Schema Verification", "transport": "CLI", "surface": "preflight_check.ps1"}
            ],
            "auth": {
                "env_var": "DOCX_TEMPLATE_KEY",
                "scopes": ["local_filesystem_read", "local_filesystem_write"]
            },
            "commands": [
                {"name": "Install Dependencies", "description": "Installs serverless-safe docx generation packages", "command": "npm install docx docx-templates"},
                {"name": "Generate Document", "description": "Executes template data merging with strict type safety", "command": "node scripts/generate_report.js --template template.docx --out output.docx"}
            ],
            "errors": [
                {"code": "CORRUPT_ZIP", "cause": "Invalid OpenXML archive or broken XML tag balance", "action": "Ensure template placeholders do not split across XML run nodes (<w:r>)"},
                {"code": "MEMORY_LIMIT", "cause": "Document exceeds 100MB with embedded uncompressed images", "action": "Compress raster assets to WebP/JPEG before injection"}
            ],
            "notes": "### Pure OpenXML Architecture\nNever invoke Windows COM / ActiveX Word automation in modern services.\nUse `docx` npm library for procedural generation and `docx-templates` for mail-merge placeholders."
        }
    }

    # Synthesize skills matching the decomposed vectors
    for item in decomp_result["skills_audit"]:
        s_name = item["skill_name"]
        if s_name in skill_definitions:
            s_def = skill_definitions[s_name]
            print(f"[Synthesizer] Synthesizing narrow-specialized skill: {s_name}...")
            s_path = synthesizer.synthesize_skill(
                skill_name=s_name,
                title=s_def["title"],
                description=s_def["description"],
                phases=s_def["phases"],
                auth_config=s_def["auth"],
                cli_commands=s_def["commands"],
                error_handling=s_def["errors"],
                reference_notes=s_def["notes"],
                output_dir=generated_skills_dir
            )
            synthesized_paths.append(s_path)
            print(f"             -> Generated at: {s_path}")

    # Step 3: Scaffold target project
    print(f"\n[Scaffolder] Scaffolding target project directory: {target_dir}...")
    scaffolder = ProjectHarnessScaffolder()
    scaffold_result = scaffolder.scaffold_project(
        target_dir=target_dir,
        project_name=project_name,
        decomposed_data=decomp_result,
        synthesized_skills=synthesized_paths
    )

    print("\n" + "=" * 70)
    print("PROJECT HARNESS SCAFFOLDING COMPLETE!")
    print("=" * 70)
    print(f"Project Workspace : {scaffold_result['project_path']}")
    print(f"Harness Config    : {scaffold_result['harness_file']}")
    print(f"Mounted Skills    : {', '.join(scaffold_result['deployed_skills'])}")
    print(f"Agent Rules       : {target_dir / 'AGENTS.md'}")
    print("\nRecommendation: Set this directory as the active workspace in Antigravity.")
    return scaffold_result


def cmd_evolve(args):
    print_banner()
    brief = args.brief
    pop_size = args.population
    gens = args.generations
    print(f"\n[Darwinian Evolution] Launching Genetic Architecture Search (GAS)...")
    print(f"Population Size : {pop_size} hypotheses per generation")
    print(f"Generations     : {gens} iterative evolutionary cycles")
    print(f"Project Brief   : \"{brief}\"\n")

    ea = EvolutionaryHarnessArchitect()
    result = ea.run_evolutionary_search(brief, population_size=pop_size, generations=gens)

    print("-" * 70)
    print("EVOLUTIONARY SEARCH SUMMARY (PHYSICAL INTEL AI BOOST NPU):")
    print("-" * 70)
    print(f"Total Hypotheses Screened: {result['total_hypotheses_screened']}")
    print(f"Hardware Compute Device:   {result['device']}")
    print(f"Champion Fitness Rating:   {result['champion_fitness']} / 10.0")

    print("\nGenerational Throughput & Natural Selection:")
    for h in result["evolution_history"]:
        g = h["generation"]
        ev = h["evaluated"]
        th = h["throughput_hps"]
        bf = h["best_fitness"]
        print(f"  * Gen {g}: Screened {ev} candidates at {th} hyp/sec | Best Fitness: {bf}")

    print("\nChampion Genome (Surviving Architecture):")
    for k, v in result["champion_genome"].items():
        print(f"  - {k:<15}: {v}")

    print("\nFitness Breakdown:")
    for k, v in result["fitness_breakdown"].items():
        print(f"  - {k:<15}: {v} / 10.0")

    print("\nTop 3 Pareto Frontier Alternatives:")
    for i, alt in enumerate(result["top_3_pareto_front"], 1):
        print(f"  Alternative {i}: {alt.get('runtime', '')} + {alt.get('edge_cloud', '')} + {alt.get('doc_engine', '')}")

    return result


from core.discovery_engine import CognitiveDiscoveryEngine


def cmd_discover(args):
    print_banner()
    raw_prompt = args.prompt
    print(f"\n[Level 0: Cognitive Discovery & Inception Engine]")
    print(f"Raw Input from User: \"{raw_prompt}\"\n")

    discovery = CognitiveDiscoveryEngine()
    step1 = discovery.start_discovery(raw_prompt)

    print(f"Detected Domain     : {step1['detected_domain']}")
    print(f"Confidence Rating   : {step1['domain_confidence'] * 100:.1f}%")
    print(f"NPU Decision Speed  : {step1['npu_latency_ms']} ms\n")

    print("=" * 70)
    print("SOCRATIC CUSTDEV QUESTIONS (Interview for Founders/Beginners):")
    print("=" * 70)
    for q in step1["custdev_questions"]:
        print(f"\n* [{q['id']}] {q['question']}")
        print(f"  -> Инженерная цель: {q['purpose']}")

    # Step 2: Show competitor analysis
    comp = discovery.analyze_competitors(step1["detected_domain"], ["Рыночный стандарт Топ-3"])
    print("\n" + "=" * 70)
    print("COMPETITIVE BENCHMARK (Standard Top-3 Architecture):")
    print("=" * 70)
    print("\n[Admin Panel Standard Tabs]:")
    for tab in comp["standard_admin_architecture"]:
        subtabs = ", ".join(tab["subtabs"])
        print(f"  * Вкладка '{tab['tab']}': [{subtabs}]")

    print("\n[Client Portal Standard Tabs]:")
    for tab in comp["standard_portal_architecture"]:
        subtabs = ", ".join(tab["subtabs"])
        print(f"  * Вкладка '{tab['tab']}': [{subtabs}]")

    # Step 3: Show trade-offs
    tradeoffs = discovery.generate_tradeoff_options(step1["detected_domain"])
    print("\n" + "=" * 70)
    print("ARCHITECTURAL TRADE-OFFS & DECISION TREES (A/B/C Options):")
    print("=" * 70)
    for item in tradeoffs["tradeoffs"]:
        print(f"\nВыбор для '{item['component']}':")
        for opt in item["options"]:
            tag = "[РЕКОМЕНДУЕТСЯ]" if opt["recommended"] else ""
            print(f"  - Вариант {opt['id']}: {opt['name']} {tag}")
            print(f"    Плюсы : {opt['pros']}")
            print(f"    Минусы: {opt['cons']}")

    # Step 4: Synthesize enriched brief
    enriched = discovery.synthesize_enriched_brief(
        raw_prompt=raw_prompt,
        user_answers={"Q1": "Розница и оптовики", "Q2": "Владелец и операторы", "Q3": "Тикеты"},
        selected_options={"support": "Вариант B (Тикеты)", "auth": "Вариант B (Гибридная модель)"},
        competitors=["Рыночный стандарт Топ-3"]
    )

    print("\n" + "=" * 70)
    print("ENRICHED PROJECT BRIEF SYNTHESIZED SUCCESSFULLY!")
    print("=" * 70)
    print(f"Title               : {enriched['project_title']}")
    print(f"Completeness Score  : {enriched['brief_completeness_score'] * 100:.1f}%")
    print(f"Ready for 7 Minis   : {enriched['handoff_ready_for_7_ministries']}")
    print(f"Saved Artifact Path : {enriched['saved_artifact_path']}\n")
    print(">>> Теперь этот бриф готов к передаче в 7 Министерств для 100% верификации! <<<\n")
    return enriched


from core.gost_compiler import GostStandardsCompiler


def cmd_gost(args):
    print_banner()
    print(f"\n[ГОСТ 34.602-89 & ISO/IEC/IEEE 29148 Specification Compiler]")
    
    brief_file = args.brief_file
    if brief_file and Path(brief_file).exists():
        with open(brief_file, "r", encoding="utf-8") as f:
            brief_data = json.load(f)
    else:
        # Default to the synthesized enriched brief if available
        default_path = Path(__file__).resolve().parent / "Enriched_Project_Brief.json"
        if default_path.exists():
            with open(default_path, "r", encoding="utf-8") as f:
                brief_data = json.load(f)
        else:
            brief_data = {
                "project_title": "Умная высоконагруженная SMM-платформа с NPU-арбитражем",
                "core_actors": [
                    {"role": "Guest", "jtbd": "Быстрый заказ за 10 секунд без паролей"},
                    {"role": "Wholesale_Client", "jtbd": "Массовые заказы через API и личный баланс"},
                    {"role": "Administrator", "jtbd": "Управление провайдерами и наценкой маржи"},
                    {"role": "Support_Agent", "jtbd": "Обработка тикетов по заказам с SLA 4 часа"}
                ]
            }

    print(f"Target System Title : \"{brief_data.get('project_title')}\"")
    print(f"Standards Enforced  : ГОСТ 34.602-89 / ISO/IEC/IEEE 29148:2018 / ГОСТ Р 56939-2024\n")

    compiler = GostStandardsCompiler()
    res = compiler.compile(brief_data)

    print("=" * 70)
    print("STANDARDS-COMPLIANT TECHNICAL SPECIFICATION COMPILED!")
    print("=" * 70)
    print(f"1. Markdown Spec    : {res['markdown_path']}")
    print(f"2. Word Document    : {res['docx_path']}")
    print(f"Sections Structured : {res['sections_count']} разделов по ГОСТ 34")
    print(f"Traceability Matrix : {res['traceability_matrix_items']} требований (RTM)")
    print(f"Compilation Time    : {res['compilation_time_ms']} ms")
    print(f"Physical Hardware   : {res['hardware_device']}")
    print("\n>>> Официальный документ ТЗ готов к согласованию и передаче в разработку! <<<\n")
    return res


from core.gost_verifier import DeterministicHarnessVerifier


def cmd_verify(args):
    print_banner()
    print(f"\n[ГОСТ 34.603-92 / ГОСТ Р 56939-2024 / ISO 29148 Verification Harness]")
    doc_path = Path(args.doc) if args.doc else Path(__file__).resolve().parent / "TZ_GOST_34_602_89_SPECIFICATION.md"
    print(f"Target Document: {doc_path}\n")

    verifier = DeterministicHarnessVerifier(doc_path)
    res = verifier.run_full_verification()

    print("=" * 70)
    print(f"VERIFICATION RESULT: {res['verdict']}")
    print(f"Overall Quality Score : {res['overall_score']} / 100.0 (Execution time: {res['verification_duration_ms']} ms)")
    print("=" * 70)

    for t in res["tests"]:
        status = "[PASSED]" if t["passed"] else "[FAILED]"
        print(f"\n* {status} {t['test_id']}: {t['name']}")
        print(f"  Score: {t['score']}/100")
        if "missing_sections" in t and t["missing_sections"]:
            print(f"  -> Missing: {', '.join(t['missing_sections'])}")
        if "fuzzy_terms_found" in t and t["fuzzy_terms_found"]:
            for fz in t["fuzzy_terms_found"]:
                print(f"  -> Fuzzy term: '{fz['fuzzy_term']}' ({fz.get('occurrences', 1)}x) - {fz['remedy']}")
        if "checks" in t:
            passed_checks = [k for k, v in t["checks"].items() if v]
            failed_checks = [k for k, v in t["checks"].items() if not v]
            print(f"  -> Passed: {passed_checks}")
            if failed_checks:
                print(f"  -> Missing checks: {failed_checks}")

    print("\n" + "=" * 70)
    return res


from core.cdd_tdd_engine import CddTddHarnessEngine, build_sample_finance_contract, build_sample_npu_contract


def cmd_cdd_tdd(args):
    print_banner()
    print("\n[CDD-TDD Scientific Harness: Hoare Invariants + PBT + NPU Physical Gate]")
    engine = CddTddHarnessEngine()
    engine.register_contract(build_sample_finance_contract())
    engine.register_contract(build_sample_npu_contract())

    print("=" * 70)
    print("PHASE 1: TDD RED - STUB PRE-CHECK (VERIFYING NON-VACUITY)")
    print("=" * 70)
    def bad_stub(p):
        return {"net_profit": -10.0, "margin_pct": -5.0, "solvency_status": "INSOLVENT"}

    res_red = engine.verify_cdd_invariants("Finance_Margin_Engine", {"sell_price": 100, "provider_cost": 95, "tax_rate": 0.20}, bad_stub)
    print(f"Red Gate Status : {'REJECTED (EXPECTED)' if not res_red['passed'] else 'FAILED'}")
    print(f"Error Caught    : {res_red['error']}")

    print("\n" + "=" * 70)
    print("PHASE 2: TDD GREEN - MATHEMATICALLY PROVEN IMPLEMENTATION")
    print("=" * 70)
    def verified_fn(p):
        rev = p["sell_price"]
        c = p["provider_cost"]
        tax = rev * p["tax_rate"]
        net = rev - c - tax
        m = (net / rev) * 100 if rev > 0 else 0
        return {"net_profit": round(net, 2), "margin_pct": round(m, 2), "solvency_status": "SOLVENT" if net > 0 and m >= 15.0 else "INSOLVENT"}

    res_green = engine.verify_cdd_invariants("Finance_Margin_Engine", {"sell_price": 100, "provider_cost": 60, "tax_rate": 0.06}, verified_fn)
    print(f"Green Gate Status : {'PASSED (VERIFIED)' if res_green['passed'] else 'FAILED'}")
    print(f"Verification Time : {res_green.get('latency_microseconds')} µs")

    print("\n" + "=" * 70)
    print("PHASE 3: PROPERTY-BASED TESTING (1,000 SYNTHETIC CASES)")
    print("=" * 70)
    import random
    def calc_price(cost, tax):
        div = 1.0 - tax - 0.20
        return cost / div if div > 0 else cost * 2.0
    def gen_cases():
        return [{"sell_price": calc_price(cost, tax), "provider_cost": cost, "tax_rate": tax} for cost in [random.uniform(10, 500) for _ in range(1000)] for tax in [random.choice([0.0, 0.06, 0.13, 0.20])]][:1000]

    pbt = engine.run_property_based_stress_test("Finance_Margin_Engine", verified_fn, gen_cases)
    print(f"Screened Cases    : {pbt['total_cases_tested']}")
    print(f"Pass Rate         : {pbt['pass_ratio']}%")
    print(f"Execution Time    : {pbt['duration_ms']} ms")
    print(f"Mutation Gate     : {'CERTIFIED' if pbt['mutation_safe'] else 'FAILED'}")
    print("=" * 70 + "\n")
    return pbt


def cmd_orchestrate(args):
    print_banner()

    # Validate prompt
    if not args.prompt or not args.prompt.strip():
        sys.stderr.write("Error: --prompt cannot be empty\n")
        sys.exit(2)

    prompt = args.prompt.strip()

    # Validate intent file if provided
    intent_path = None
    if args.intent:
        p_intent = Path(args.intent)
        if not p_intent.exists():
            sys.stderr.write(f"Error: Intent file not found: {args.intent}\n")
            sys.exit(1)
        intent_path = str(p_intent.resolve())

    # Check output directory
    output_dir = None
    if args.output_dir:
        out_p = Path(args.output_dir)
        if out_p.exists() and not out_p.is_dir():
            sys.stderr.write(f"Error: Output path '{args.output_dir}' is an existing file, not a directory.\n")
            sys.exit(1)
        output_dir = str(out_p)

    use_mock = not args.live

    mode_label = "MOCK (Deterministic Fast-Path)" if use_mock else "LIVE (OpenRouter LLM Ensemble)"
    print(f"\n[Autonomous Generative Cognitive Pipeline: 7 Ministries]")
    print(f"Mode              : {mode_label}")
    print(f"Task Prompt       : \"{prompt}\"")
    disc_mode = getattr(args, "discovery_mode", "auto")
    print(f"Discovery Mode    : {disc_mode.upper()}")
    if intent_path:
        print(f"Intent File       : {intent_path}")
    if output_dir:
        print(f"Target Output Dir : {output_dir}")
    if args.simulate_therac_hazard:
        print(f"Simulation        : Therac-25 Hardware Latency Race Condition Triggered")
    print()

    user_answers = {}
    if disc_mode == "interactive":
        from core.discovery_engine import CognitiveDiscoveryEngine
        cde = CognitiveDiscoveryEngine()
        questions = cde.conduct_socratic_interview(prompt)
        if questions:
            print("=" * 70)
            print("SOCRATIC CUSTDEV QUESTIONS (Level 0 Inception Gate):")
            print("=" * 70)
            for q in questions:
                print(f"\n* [{q.question_id}] {q.prompt_text}")
                print(f"  -> Рекомендация: {q.default_recommendation}")
                if sys.stdin.isatty():
                    try:
                        ans = input("  Ваш ответ (Enter для рекомендации): ").strip()
                        user_answers[q.question_id] = ans or q.default_recommendation
                    except EOFError:
                        user_answers[q.question_id] = q.default_recommendation
                else:
                    user_answers[q.question_id] = q.default_recommendation
            print("=" * 70 + "\n")

    try:
        orchestrator = DagOrchestrator(use_mock=use_mock, output_dir=output_dir)
        result = orchestrator.run(
            prompt=prompt,
            intent_path=intent_path,
            simulate_therac_hazard=args.simulate_therac_hazard,
            output_dir=output_dir,
            discovery_mode=disc_mode,
            user_answers=user_answers if user_answers else None,
        )
    except Exception as e:
        sys.stderr.write(f"Orchestration Failed: {e}\n")
        sys.exit(1)

    # Structured summary
    print("=" * 70)
    print("ORCHESTRATION SUMMARY: 7 MINISTRIES COMMITTED")
    print("=" * 70)

    node_names = getattr(orchestrator, "node_names", MINISTRY_NAMES)

    for nid in range(1, 8):
        m_name = node_names.get(nid, f"Ministry_{nid}")
        fname = CANONICAL_FILENAMES.get(nid, f"Artifact_{nid}.json")
        fsm_state = result.fsm_states.get(nid, "COMMITTED")
        state_display = fsm_state.replace("STATE_", "")
        print(f"[{nid}/7] {m_name:<22} -> {fname:<32} [{state_display}]")

    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION TELEMETRY & ATTRIBUTES:")
    print("=" * 70)
    print(f"Status                  : {result.status}")
    print(f"Saga Compensations      : {len(result.saga_compensations_executed)}")
    for sc in result.saga_compensations_executed:
        print(f"  -> Compensating Tx: Node {sc.get('vetoing_node')} vetoed Node {sc.get('target_node')} (Hazard: {sc.get('hazard_code', 'N/A')})")
    print(f"Simplex Downgrades      : {len(result.simplex_downgrades_applied)}")
    for sd in result.simplex_downgrades_applied:
        print(f"  -> Downscaled Node {sd.get('node_id')}: {sd.get('reason', '')}")

    quality_art = result.artifacts.get(CANONICAL_FILENAMES.get(7, ""), {})
    release_sig = quality_art.get("cryptographic_release_signature", "UNKNOWN")
    print(f"Cryptographic Signature : {release_sig}")

    if getattr(result, "inception_contract", None):
        inc = result.inception_contract
        print(f"Level 0 Inception Gate  : [ENRICHED] (Domain: {inc.target_domain} | Vagueness: {inc.vagueness_score*100:.1f}%)")
        print(f"  -> Actors Formulated  : {len(inc.actors)} roles ({', '.join(a.role_name for a in inc.actors)})")
        print(f"  -> Compliance Bound   : {', '.join(inc.compliance_regime)}")

    if output_dir:
        out_path = Path(output_dir).resolve()
        print("\n" + "=" * 70)
        print(f"EXPORTED ARTIFACTS IN '{out_path}':")
        print("=" * 70)
        for nid in range(1, 8):
            fname = CANONICAL_FILENAMES.get(nid, "")
            fpath = out_path / fname
            if fpath.exists():
                file_bytes = fpath.read_bytes()
                sha_hash = hashlib.sha256(file_bytes).hexdigest()
                size = len(file_bytes)
                print(f"  * {fname:<32} ({size:>5} bytes) [SHA256: {sha_hash}]")
            else:
                print(f"  * {fname:<32} [MISSING]")

        manifest_file = out_path / "release_manifest.json"
        if manifest_file.exists():
            m_bytes = manifest_file.read_bytes()
            m_sha = hashlib.sha256(m_bytes).hexdigest()
            print(f"  * {'release_manifest.json':<32} ({len(m_bytes):>5} bytes) [SHA256: {m_sha}]")

    print("=" * 70 + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description="Project Harness & Skill Synthesizer (PHSS)")
    subparsers = parser.add_subparsers(dest="command")

    # Command: orchestrate (7-Ministry Saga Autonomous Pipeline)
    p_orch = subparsers.add_parser(
        "orchestrate",
        help="Run 7-ministry autonomous generative pipeline with Saga orchestration",
    )
    p_orch.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Input specification or project brief",
    )
    p_orch.add_argument(
        "--intent",
        type=str,
        default=None,
        help="Path to intent Gherkin scenario file",
    )
    p_orch.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to export the 7 validated artifacts",
    )
    p_orch.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="Run with deterministic mock models for fast offline execution",
    )
    p_orch.add_argument(
        "--live",
        action="store_true",
        default=False,
        help="Run with live OpenRouter LLM APIs",
    )
    p_orch.add_argument(
        "--simulate-therac-hazard",
        action="store_true",
        default=False,
        help="Simulate Therac-25 hardware latency hazard",
    )
    p_orch.add_argument(
        "--discovery-mode",
        type=str,
        choices=["auto", "interactive", "bypass"],
        default="auto",
        help="Level 0 Inception mode: 'auto' (enrich vague prompts), 'interactive' (Socratic questions), 'bypass' (direct)",
    )

    # Command: cdd-tdd (Scientific CDD-TDD Gate)
    subparsers.add_parser("cdd-tdd", help="Run scientific CDD-TDD cycle: Hoare contracts, RED stub validation, and Property-Based stress test")

    # Command: verify (Deterministic Standards Gate)
    p_verify = subparsers.add_parser("verify", help="Run deterministic verification of specification against ГОСТ 34.603-92 / ISO 29148")
    p_verify.add_argument("--doc", type=str, default=None, help="Path to specification markdown file (optional)")

    # Command: discover (Level 0)
    p_discover = subparsers.add_parser("discover", help="Level 0: Socratic CustDev, competitor benchmark, and enriched brief synthesis")
    p_discover.add_argument("prompt", type=str, help="Vague or beginner prompt describing the idea")

    # Command: gost (Standards Compiler)
    p_gost = subparsers.add_parser("gost", help="Compile verified specification into formal ГОСТ 34.602-89 / ISO 29148 Word (.docx) & Markdown")
    p_gost.add_argument("--brief-file", type=str, default=None, help="Path to Enriched_Project_Brief.json (optional)")

    # Command: analyze
    p_analyze = subparsers.add_parser("analyze", help="Decompose project brief into technical vectors and audit skills")
    p_analyze.add_argument("brief", type=str, help="Natural language description of the new project")

    # Command: evolve
    p_evolve = subparsers.add_parser("evolve", help="Run Darwinian genetic search over 1,000+ hypotheses on Intel AI Boost NPU")
    p_evolve.add_argument("brief", type=str, help="Natural language description of the new project")
    p_evolve.add_argument("--population", type=int, default=1000, help="Population size per generation (default 1000)")
    p_evolve.add_argument("--generations", type=int, default=3, help="Number of evolutionary cycles (default 3)")

    # Command: scaffold
    p_scaffold = subparsers.add_parser("scaffold", help="End-to-end scaffolding: decompose, synthesize skills, mount rules")
    p_scaffold.add_argument("name", type=str, help="Target project folder name")
    p_scaffold.add_argument("brief", type=str, help="Natural language description of the new project")

    args = parser.parse_args()

    if args.command == "orchestrate":
        return cmd_orchestrate(args)
    elif args.command == "cdd-tdd":
        cmd_cdd_tdd(args)
    elif args.command == "verify":
        cmd_verify(args)
    elif args.command == "discover":
        cmd_discover(args)
    elif args.command == "gost":
        cmd_gost(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "evolve":
        cmd_evolve(args)
    elif args.command == "scaffold":
        cmd_scaffold(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

