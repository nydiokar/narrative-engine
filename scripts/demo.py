"""Pipeline demo — seed a premise, run through checkpoints, inspect state.

Usage:
    python scripts/demo.py                             # full pipeline (mock LLM)
    python scripts/demo.py --to scenes                 # stop after scenes checkpoint
    python scripts/demo.py --premise "..."             # custom premise
    python scripts/demo.py --real-llm                  # use real LLM (Ollama by default)
    python scripts/demo.py --model qwen3-coder         # specific model (implies --real-llm)

Checkpoints (in order): brief, premise, structure, episodes, scenes, draft, editorial, final

Mediums:
    --medium book        Novel-style prose (default)
    --medium movie       Cinematic screenplay
    --medium animation   Visual scene descriptions + dialogue
    --medium series      Episodic TV teleplay
    --medium game        Interactive narrative
    --medium audio_drama Audio description + dialogue

Save/Load:
    --save <path>   Save pipeline state to JSON file after run
    --load <path>   Load pipeline state from JSON file before run

Tree / Branching (narrative workbench):
    --branch                    Enter branching mode
    --from <checkpoint>         Checkpoint to branch from (default: premise)
    --vary <field>              What to vary: genre, premise, tone, seed
    --values <list>             Comma-separated values to try
    --labels <list>             Optional labels (default: same as values)
    --compare <labels>          Compare siblings by label (comma-separated)
    --promote <label>           Mark a branch as active
    --tree-save <path>          Save tree state to file
    --tree-load <path>          Load tree state from file

Environment variables for real LLM:
    LLM_BASE_URL    — API base URL (default: http://localhost:11434/v1)
    LLM_API_KEY     — API key (default: ollama)
    LLM_MODEL       — Model name (default: llama3.2)
"""

from __future__ import annotations

import json
import os
import sys

# Ensure project root is on sys.path when run as a script
_proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

from src.agents.director import Director
from src.agents.llm import MockLLMProvider, OpenAILLMProvider, set_llm, reset_llm
from src.agents.store import get_store, reset_store
from src.contracts.models import Medium, StoryContract
from src.pipeline.checkpoints import CHECKPOINT_ORDER, run_to_checkpoint
from src.pipeline.orchestrator import default_agent_registry
from src.tree.executor import BranchConfig, TreeExecutor
from src.tree.node import TreeNode, TreeStore


PREMISE = (
    "A disgraced mage, stripped of her powers after a catastrophic experiment, "
    "must retrieve three scattered fragments of an ancient crystal before a "
    "rival cabal assembles them to unleash a world-ending blight. She has only "
    "the whispered guidance of a long-dead archivist and a stolen map that "
    "might be a trap."
)

MOCK_RESPONSES: dict[str, str] = {
    "showrunner.review_brief": json.dumps({
        "success": True,
        "message": "Brief reviewed — premise viable, genre and themes align.",
        "errors": [],
        "artifacts": [],
    }),
    "showrunner.approve_brief": json.dumps({
        "success": True,
        "message": "Brief approved — theme, genre, world axes, and character layers coherent.",
        "errors": [],
        "artifacts": [],
    }),
    "structuralist.analyze_premise": json.dumps({
        "success": True,
        "message": "Premise analyzed — actantial configuration extracted.",
        "errors": [],
        "contract_data": {
            "subject_id": "",
            "object_of_value_id": "",
            "object_of_value_description": "The mage's redemption and the safety of the realm",
            "sender_id": "archivist_whisper",
            "receiver_id": "mage",
        },
    }),
    "structuralist.select_backbone": json.dumps({
        "success": True,
        "message": "Backbone grammar: Greimas canonical schema with Propp morphology.",
        "errors": [],
    }),
    "structuralist.build_fabula": json.dumps({
        "success": True,
        "message": "Fabula chain constructed — 12 events across 3 acts.",
        "errors": [],
    }),
    "character_architect.draft_protagonists": json.dumps({
        "success": True,
        "message": "Protagonist drafted with full psychological profile.",
        "errors": [],
        "contract_data": {
            "name": "Elara Veyn",
            "description": "A brilliant but reckless mage, disgraced by her ambition, now seeking atonement.",
            "actant_roles": ["subject", "hero"],
            "personality": {"openness": 8, "conscientiousness": 4, "extraversion": 3, "agreeableness": 5, "neuroticism": 7},
            "values": {"primary": "redemption", "secondary": ["knowledge", "protection"], "priorities": {}},
            "social_mode_default": "authority_ranking",
            "attachment_pattern": "fearful_avoidant",
            "core_desires": ["redemption", "belonging", "knowledge"],
            "core_fears": ["irrelevance", "condemnation", "losing control"],
            "wound_types": ["betrayal_self", "failure"],
            "need_types": ["atonement", "connection"],
            "goal_polarity": "attain",
            "emotional_baseline_emotion": "sadness",
            "emotional_baseline_intensity": "medium",
        },
    }),
    "showrunner.approve_premise": json.dumps({
        "success": True,
        "message": "Premise approved — subject, object, sender, receiver all valid.",
        "errors": [],
    }),
    "showrunner.approve_structure": json.dumps({
        "success": True,
        "message": "Structure approved — fabula chain is sound.",
        "errors": [],
    }),
    "outline_planner.segment_fabula": json.dumps({
        "success": True,
        "message": "Fabula segmented into 3 episodes.",
        "errors": [],
        "contracts_data": [
            {
                "sequence_number": 0,
                "title": "The Shattered Seal",
                "summary": "Elara learns the crystal fragments exist and begins her reluctant quest.",
                "canonical_phase": "manipulation",
                "dominant_conflict": "interpersonal",
                "greimas_tracking": {
                    "subject": "Elara Veyn",
                    "object_of_value": "redemption",
                    "current_state": "powerless and disgraced",
                    "desired_transformation": "to recover power and prove worth",
                    "opponent": "rival cabal",
                    "opponent_value_logic": "they seek control through destruction",
                    "helper": "archivist's whispers",
                    "action_type": "quest initiation",
                    "resulting_state": "committed to the quest",
                    "sanction_or_judgment": "",
                    "contribution_to_whole_fabula": "establishes the stakes and sets the protagonist in motion",
                },
            },
            {
                "sequence_number": 1,
                "title": "The Fragment Hunt",
                "summary": "Elara tracks each fragment through dangerous territories, gaining allies and enemies.",
                "canonical_phase": "competence",
                "dominant_conflict": "environmental",
                "greimas_tracking": {
                    "subject": "Elara Veyn",
                    "object_of_value": "knowledge and power",
                    "current_state": "committed but under-equipped",
                    "desired_transformation": "to acquire the three fragments",
                    "opponent": "rival cabal agents",
                    "opponent_value_logic": "they want the fragments for destruction",
                    "helper": "a reluctant thief and the archivist's map",
                    "action_type": "acquisition and combat",
                    "resulting_state": "possesses two fragments, one remains",
                    "sanction_or_judgment": "",
                    "contribution_to_whole_fabula": "builds competence and tests resolve",
                },
            },
            {
                "sequence_number": 2,
                "title": "The Reckoning",
                "summary": "Elara confronts the cabal, assembles the crystal, and faces the final choice.",
                "canonical_phase": "performance",
                "dominant_conflict": "internal",
                "greimas_tracking": {
                    "subject": "Elara Veyn",
                    "object_of_value": "redemption or destruction",
                    "current_state": "bears all three fragments",
                    "desired_transformation": "to seal the blight without losing herself",
                    "opponent": "cabal leader",
                    "opponent_value_logic": "power through annihilation",
                    "helper": "allies she gathered",
                    "action_type": "final confrontation",
                    "resulting_state": "blight sealed, atonement found",
                    "sanction_or_judgment": "the archivist's final whisper grants peace",
                    "contribution_to_whole_fabula": "resolves the central conflict and completes the arc",
                },
            },
        ],
    }),
    "showrunner.approve_episodes": json.dumps({
        "success": True,
        "message": "Episode structure approved — 3 acts, coherent progression.",
        "errors": [],
    }),
    "scene_writer.render_prose": json.dumps({
        "success": True,
        "message": "Scenes rendered with full Greimas diagnostics.",
        "errors": [],
        "contracts_data": [
            {
                "chapter_id": None,
                "sequence_number": 0,
                "setting_location": "The Ruined Spire, Elara's sanctuary",
                "setting_time": "dusk",
                "setting_atmosphere": "melancholic and tense",
                "scene_type": "inciting",
                "content": "Elara traces faded runes in the dust, the archivist's voice a whisper in her mind. The first fragment lies in the Sunken Cathedral, guarded by memories she helped create.",
                "greimas_diagnostic": {
                    "state_before": "Elara in stasis, avoiding her past",
                    "action_occurs": "The archivist reveals the crystal's location",
                    "state_after": "Elara has a purpose but fears the journey",
                    "value_object_change": "ignorance_to_knowledge",
                    "future_action_possible_or_blocked": "quest initiated",
                    "diagnostic_pass": True,
                },
                "characters_present": [{"id": "elara", "emotion": "fear", "intensity": "high"}],
                "emotional_tone": "anticipation",
                "canonical_phase": "manipulation",
            },
            {
                "chapter_id": None,
                "sequence_number": 1,
                "setting_location": "The Sunken Cathedral",
                "setting_time": "midnight",
                "setting_atmosphere": "oppressive and wet",
                "scene_type": "confrontation",
                "content": "Elara fights through water-logged corridors, evading the cabal's scouts. She reaches the altar but the fragment is guarded by a spectral warden — a former friend she failed to save.",
                "greimas_diagnostic": {
                    "state_before": "Elara seeks the first fragment",
                    "action_occurs": "She confronts the spectral warden and earns the fragment",
                    "state_after": "She has the first fragment but bears fresh guilt",
                    "value_object_change": "acquired_fragment_one",
                    "future_action_possible_or_blocked": "next fragment location revealed",
                    "diagnostic_pass": True,
                },
                "characters_present": [{"id": "elara", "emotion": "sadness", "intensity": "high"}, {"id": "warden", "emotion": "anger", "intensity": "medium"}],
                "emotional_tone": "sadness",
                "canonical_phase": "competence",
            },
        ],
    }),
    "scene_writer.run_greimas_diagnostic": json.dumps({
        "success": True,
        "message": "All scenes pass the 5-question Greimas diagnostic.",
        "errors": [],
    }),
    "continuity_editor.check_consistency": json.dumps({
        "success": True,
        "message": "Continuity check passed — 2 scenes verified.",
        "errors": [],
    }),
    "showrunner.assemble_draft": json.dumps({
        "success": True,
        "message": "Draft assembled from 2 rendered scenes.",
        "errors": [],
    }),
    "developmental_editor.evaluate_draft": json.dumps({
        "success": True,
        "message": "Developmental edit complete — pacing solid, genre delivery strong.",
        "errors": [],
    }),
    "revision_agent.apply_structural_changes": json.dumps({
        "success": True,
        "message": "Structural changes applied successfully.",
        "errors": [],
        "contract_data": {
            "changes": [{"type": "scene", "contract_id": "00000000-0000-0000-0000-000000000001", "field": "status", "new_value": "revised"}]
        },
    }),
    "line_editor.refine_prose": json.dumps({
        "success": True,
        "message": "Line edit complete — sentence rhythm and diction improved.",
        "errors": [],
    }),
    "revision_agent.apply_line_changes": json.dumps({
        "success": True,
        "message": "Line edit changes applied.",
        "errors": [],
        "contract_data": {
            "changes": [{"type": "scene", "contract_id": "00000000-0000-0000-0000-000000000001", "field": "content", "new_value": "Elara traced faded runes in the dust, the archivist\u2019s voice a whisper in her mind. The first fragment lay in the Sunken Cathedral, guarded by memories she had helped create."}]
        },
    }),
    "copy_editor.check_consistency": json.dumps({
        "success": True,
        "message": "Copy edit complete — grammar and terminology verified.",
        "errors": [],
    }),
    "revision_agent.apply_copy_changes": json.dumps({
        "success": True,
        "message": "Copy edit changes applied.",
        "errors": [],
        "contract_data": {
            "changes": []
        },
    }),
    "proofreader.final_check": json.dumps({
        "success": True,
        "message": "Proofread complete — clearance certificate issued.",
        "errors": [],
    }),
    "critic.run_hard_gate": json.dumps({
        "success": True,
        "message": "Hard gate: PASS — all 8 structural checks clear.",
        "errors": [],
    }),
    "critic.run_soft_gate": json.dumps({
        "success": True,
        "message": "Soft gate: PASS (6.8/5.0) — quality threshold cleared.",
        "errors": [],
        "contract_data": {
            "dimension_scores": {
                "genre_fit": 7, "thematic_clarity": 6, "conflict_density": 6,
                "relationship_tension": 5, "scene_level_purpose": 8, "suspense_curiosity_surprise": 6,
                "emotional_transport": 6, "novelty": 5, "prose_distinctiveness": 5
            },
            "dimension_notes": {
                "genre_fit": "Strong genre delivery with clear fantasy tropes",
                "thematic_clarity": "Redemption theme is well-instantiated",
                "scene_level_purpose": "All scenes pass Greimas 5-question diagnostic"
            }
        },
    }),
    "critic.run_greimas_diagnostics": json.dumps({
        "success": True,
        "message": "Greimas diagnostics complete. Cliché score: 2/14 — low cliché risk.",
        "errors": [],
        "contract_data": {
            "cliche_signals": [
                {"name": "default_genre_setting", "severity": 1},
                {"name": "mentor_dies_only_to_motivate", "severity": 1}
            ]
        },
    }),
    "revision_agent.apply_revisions": json.dumps({
        "success": True,
        "message": "All revisions applied — no remaining hard gate failures.",
        "errors": [],
        "contract_data": {
            "changes": []
        },
    }),
    "showrunner.approve_final": json.dumps({
        "success": True,
        "message": "Final version approved — ready for release package.",
        "errors": [],
    }),
    "showrunner.approve_structure": json.dumps({
        "success": True,
        "message": "Structure approved — fabula chain is sound.",
        "errors": [],
    }),
    "showrunner.approve_episodes": json.dumps({
        "success": True,
        "message": "Episode structure approved — 3 acts, coherent progression.",
        "errors": [],
    }),
    "scene_writer.render_visual_scene": json.dumps({
        "success": True,
        "message": "Visual scenes rendered with blocking and dialogue.",
        "errors": [],
        "contracts_data": [
            {
                "chapter_id": None,
                "sequence_number": 0,
                "setting_location": "The Ruined Spire, Elara's sanctuary",
                "setting_time": "dusk",
                "setting_atmosphere": "melancholic and tense",
                "scene_type": "inciting",
                "content": "Visual: Elara traces faded runes in the dust. The archivist's voice whispers. Cut to: The Sunken Cathedral, submerged in darkness. Dialogue: Archivist V.O. — 'The first fragment waits where your greatest failure lives.'",
                "greimas_diagnostic": {
                    "state_before": "Elara in stasis, avoiding her past",
                    "action_occurs": "The archivist reveals the crystal's location",
                    "state_after": "Elara has a purpose but fears the journey",
                    "value_object_change": "ignorance_to_knowledge",
                    "future_action_possible_or_blocked": "quest initiated",
                    "diagnostic_pass": True,
                },
                "characters_present": [{"id": "elara", "emotion": "fear", "intensity": "high"}],
                "emotional_tone": "anticipation",
                "canonical_phase": "manipulation",
            },
        ],
    }),
    "scene_writer.finalize_prose": json.dumps({
        "success": True,
        "message": "Prose finalized.",
        "errors": [],
    }),
    "scene_writer.finalize_script": json.dumps({
        "success": True,
        "message": "Script finalized — scene numbering and formatting complete.",
        "errors": [],
    }),
    "scene_writer.finalize_screenplay": json.dumps({
        "success": True,
        "message": "Screenplay finalized — sluglines, action, dialogue formatted.",
        "errors": [],
    }),
    "scene_writer.finalize_teleplay": json.dumps({
        "success": True,
        "message": "Teleplay finalized — act breaks, scene headings, dialogue.",
        "errors": [],
    }),
    "script_editor.refine_script": json.dumps({
        "success": True,
        "message": "Script refined — pacing, formatting, dialogue flow improved.",
        "errors": [],
    }),
    "showrunner.assemble_script": json.dumps({
        "success": True,
        "message": "Script assembled from rendered visual scenes.",
        "errors": [],
    }),
    "showrunner.assemble_screenplay": json.dumps({
        "success": True,
        "message": "Screenplay assembled.",
        "errors": [],
    }),
    "showrunner.assemble_teleplay": json.dumps({
        "success": True,
        "message": "Teleplay assembled with act breaks.",
        "errors": [],
    }),
    "continuity_editor.final_check": json.dumps({
        "success": True,
        "message": "Final continuity check passed.",
        "errors": [],
    }),
}


def print_store_state(store):
    """Pretty-print the current contract store contents."""
    all_items = store.list_all()
    for type_key, contracts in sorted(all_items.items()):
        print(f"\n  -- {type_key.upper()} ({len(contracts)} contract(s)) --")
        for c in contracts:
            d = c.model_dump(mode="json") if hasattr(c, "model_dump") else {}
            title = d.get("title") or d.get("name") or str(d.get("id", "?"))[:8]
            print(f"    [{type_key}] {title}")
            if type_key == "story":
                premise = d.get("premise", "")
                short_premise = premise[:60] + "..." if len(premise) > 60 else premise
                print(f"      premise: {short_premise}")
                if d.get("genre", {}).get("primary_bisac"):
                    print(f"      genre BISAC: {d['genre']['primary_bisac']}")
                if d.get("subject_id"):
                    print(f"      subject_id: {d['subject_id'][:8]}...")
            elif type_key == "character":
                print(f"      role: {d.get('actant_roles', [])}")
                desires = d.get("core_desires", [])
                if desires:
                    print(f"      desires: {desires}")
            elif type_key == "episode":
                print(f"      phase: {d.get('canonical_phase', '?')}")
                print(f"      summary: {(d.get('summary', '') or '')[:80]}")
            elif type_key == "chapter":
                print(f"      scenes: {len(d.get('scenes', []))}")
            elif type_key == "scene":
                diag = d.get("greimas_diagnostic", {})
                if diag:
                    print(f"      diagnostic: {'PASS' if diag.get('diagnostic_pass') else 'FAIL'}")
            elif type_key == "critique":
                print(f"      verdict: {d.get('verdict', '?')}")
                print(f"      summary: {(d.get('summary', '') or '')[:80]}")


def _run_tree_mode(
    agents,
    medium: Medium,
    target_checkpoint: str | None = None,
):
    """Execute tree operations: branch, compare, promote."""
    import os

    args = sys.argv[1:]

    # Parse tree-specific args (--to already parsed in main())
    tree_load_path = None
    tree_save_path = None
    branch_from = "premise"
    branch_to = target_checkpoint or "final"
    vary_field = "genre"
    values_str = None
    labels_str = None
    compare_labels = None
    promote_label = None

    for i, arg in enumerate(args):
        if arg == "--tree-load" and i + 1 < len(args):
            tree_load_path = args[i + 1]
        if arg == "--tree-save" and i + 1 < len(args):
            tree_save_path = args[i + 1]
        if arg == "--from" and i + 1 < len(args):
            branch_from = args[i + 1]
        if arg == "--vary" and i + 1 < len(args):
            vary_field = args[i + 1]
        if arg == "--values" and i + 1 < len(args):
            values_str = args[i + 1]
        if arg == "--labels" and i + 1 < len(args):
            labels_str = args[i + 1]
        if arg == "--compare" and i + 1 < len(args):
            compare_labels = args[i + 1]
        if arg == "--promote" and i + 1 < len(args):
            promote_label = args[i + 1]

    # Load or create tree
    tree = TreeStore()
    if tree_load_path and os.path.exists(tree_load_path):
        tree.load(tree_load_path)
        print(f"\nLoaded tree from {tree_load_path}")
        print(f"  Nodes: {tree.size()}")
    else:
        # Create root from current store state — only seed contracts
        store = get_store()
        story_contracts = store.list_by_type("story")
        if not story_contracts:
            print("No story in store. Run pipeline to a checkpoint first.")
            sys.exit(1)

        # Root snapshot = seed only (story contract, no pipeline artifacts)
        full_snapshot = store.snapshot()
        seed_keys = {"story"}
        contracts_data = full_snapshot.get("contracts", {})
        seed_contracts = {k: v for k, v in contracts_data.items() if k in seed_keys}
        seed_snapshot = {"contracts": seed_contracts, "field_locks": {}}

        root = TreeNode(
            label="root",
            checkpoint="",
            store_snapshot=seed_snapshot,
            active=True,
        )
        tree.root = root
        seed_count = len(seed_snapshot.get("contracts", {}).get("story", []))
        print(f"\nCreated root node (seed state: {seed_count} story)")
        print(f"  Branch from: {branch_from}")

    # Handle --compare
    if compare_labels:
        labels = [l.strip() for l in compare_labels.split(",")]
        nodes = []
        for label in labels:
            node = tree.get_by_label(label)
            if node:
                nodes.append(node)
            else:
                print(f"  Node '{label}' not found in tree")
        if nodes:
            executor = TreeExecutor(tree, agents)
            executor.compare(nodes)
        return

    # Handle --promote
    if promote_label:
        node = tree.get_by_label(promote_label)
        if node:
            executor = TreeExecutor(tree, agents)
            executor.promote(node)
            print(f"\nPromoted '{promote_label}' to active path")
            active = tree.get_active()
            print(f"  Active: {active.label if active else 'none'}")
            print(f"  Path to root:")
            for p in tree.path_to_root(node.id):
                print(f"    [{p.label}] {p.checkpoint} {p.variant_params}")
        else:
            print(f"  Node '{promote_label}' not found")
        if tree_save_path:
            tree.save(tree_save_path)
            print(f"Saved tree to {tree_save_path}")
        return

    # Handle --branch
    if values_str:
        values = [v.strip() for v in values_str.split(",")]
        labels_list = None
        if labels_str:
            labels_list = [l.strip() for l in labels_str.split(",")]

        # Get parent node
        active = tree.get_active()
        parent = active or tree.root
        if not parent:
            print("No parent node found")
            sys.exit(1)

        print(f"\n{'#'*60}")
        print(f"#  BRANCHING FROM: [{parent.label}] @ {parent.checkpoint}")
        print(f"#  Vary: {vary_field}")
        print(f"#  Values: {values}")
        print(f"{'#'*60}\n")

        config = BranchConfig(
            checkpoint=branch_from,
            vary_field=vary_field,
            values=values,
            medium=medium,
            labels=labels_list,
            target_checkpoint=branch_to,
        )

        executor = TreeExecutor(tree, agents)
        children = executor.branch(parent, config)

        print(f"\nCreated {len(children)} child variants:")
        for child in children:
            score_str = ""
            if child.scores.get("verdict"):
                score_str = f" [verdict: {child.scores['verdict']}]"
            print(f"  [{child.label}] depth={child.depth}{score_str}")

        # Deactivate parent, activate first child
        executor.promote(children[0])
        print(f"\nPromoted '{children[0].label}' as active path")

    else:
        print("No --values specified for branching. Use --values genre1,genre2,...")
        print("Or use --compare or --promote for tree operations.")

    if tree_save_path:
        tree.save(tree_save_path)
        print(f"Saved tree ({tree.size()} nodes) to {tree_save_path}")


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    args = sys.argv[1:]
    target_checkpoint = None
    premise = PREMISE
    use_real_llm = False
    model_name = None
    medium = Medium.BOOK

    save_path = None
    load_path = None
    tree_mode = False

    for i, arg in enumerate(args):
        if arg == "--to" and i + 1 < len(args):
            target_checkpoint = args[i + 1]
        if arg == "--premise" and i + 1 < len(args):
            premise = args[i + 1]
        if arg == "--real-llm":
            use_real_llm = True
        if arg == "--model" and i + 1 < len(args):
            use_real_llm = True
            model_name = args[i + 1]
        if arg == "--medium" and i + 1 < len(args):
            medium = Medium(args[i + 1])
        if arg == "--save" and i + 1 < len(args):
            save_path = args[i + 1]
        if arg == "--load" and i + 1 < len(args):
            load_path = args[i + 1]
        if arg == "--branch":
            tree_mode = True
        if arg == "--compare":
            tree_mode = True
        if arg == "--promote":
            tree_mode = True

    if target_checkpoint and target_checkpoint not in CHECKPOINT_ORDER:
        print(f"Unknown checkpoint '{target_checkpoint}'")
        print(f"Available: {', '.join(CHECKPOINT_ORDER)}")
        sys.exit(1)

    # Reset everything
    reset_store()
    reset_llm()
    store = get_store()

    # Set up LLM provider
    if use_real_llm:
        provider = OpenAILLMProvider(model=model_name)
        print(f"\nReal LLM: {provider.model} @ {provider.client.base_url}\n")
        set_llm(provider)
    else:
        mock_llm = MockLLMProvider()
        for trigger, response in MOCK_RESPONSES.items():
            mock_llm.add_rule(trigger, response)
        set_llm(mock_llm)

    # Load from saved state if requested (must be before tree mode check)
    if load_path:
        import os
        if os.path.exists(load_path):
            store.load(load_path)
            print(f"\nLoaded pipeline state from {load_path}")

    # Build agent registry once (shared across pipeline + tree)
    agents = default_agent_registry(store=store)

    # Tree mode short-circuits the pipeline run
    if tree_mode:
        _run_tree_mode(agents, medium=medium, target_checkpoint=target_checkpoint)
        return

    # Seed the story (only if not loaded from save)
    if not load_path:
        story = StoryContract(
            title="The Crystal Key",
            premise=premise,
            logline="A disgraced mage races to assemble an ancient crystal before her rivals weaponize it.",
        )
        store.put("story", story)

    print(f"\n{'#'*60}")
    print(f"#  NARRATIVE ENGINE — PIPELINE DEMO")
    print(f"#  Story: The Crystal Key ({medium.value})")
    target_str = f" -> to '{target_checkpoint}'" if target_checkpoint else " -> full pipeline"
    print(f"#{target_str}")
    print(f"{'#'*60}\n")

    print("SEED PREMISE:")
    print(f"  {premise[:120]}...\n")

    # Run the pipeline
    director = Director(agents, store=store, medium=medium)

    reports = run_to_checkpoint(director, target_checkpoint or "final", verbose=True)

    # Save pipeline state if requested
    if save_path:
        store.save(save_path)
        print(f"\nSaved pipeline state to {save_path}")

    # Final summary
    print(f"\n{'='*60}")
    print("FINAL STORE STATE:")
    print_store_state(store)

    all_passed = all(r.passed for r in reports)
    print(f"\n{'='*60}")
    print(f"PIPELINE RESULT: {'PASS ALL CHECKPOINTS PASSED' if all_passed else 'FAIL SOME CHECKPOINTS FAILED'}")
    print(f"  Checkpoints verified: {len(reports)}")
    for r in reports:
        status = "PASS" if r.passed else "FAIL"
        print(f"  {status} {r.stage}")

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
