"""Quick test: generate scenes for one episode only."""
import json, sys, logging
from src.agents.scene_writer import SceneWriter
from src.agents.store import ContractStore
from src.agents.llm import SubprocessLLMProvider
from src.agents.base import AgentContext

logging.basicConfig(level=logging.INFO)
store = ContractStore()
store.load("state_episodes.json")

episodes = store.list_by_type("episode")
ep0 = episodes[0]
chapters = [c for c in store.list_by_type("chapter") if getattr(c, "episode_id", None) and str(c.episode_id) == str(ep0.id)]
chapters.sort(key=lambda c: c.sequence_number)

print(f"Episode: {ep0.title} ({len(chapters)} chapters)")
for ch in chapters:
    print(f"  Chapter: {ch.title} (id={ch.id})")

llm = SubprocessLLMProvider(cmd_template="opencode run --dir {run_dir} --format json --dangerously-skip-permissions {prompt}")
writer = SceneWriter(llm=llm, store=store)

ctx = AgentContext(
    workflow_id="04-episodes-to-scenes",
    step_id="render_prose",
    metadata={"medium": "book"},
)

result = writer._render_episode_chapters(ctx, str(ep0.id), chapters)
cd = result.get("contracts_data", [])
print(f"\nSuccess: {result.get('success', '?')}")
print(f"Message: {result.get('message', '')}")
print(f"Errors: {result.get('errors', [])}")
print(f"Scenes returned: {len(cd)}")
if cd:
    for s in cd[:3]:
        content = s.get('content', '')[:200]
        print(f"  Scene: type={s.get('scene_type')}, loc={s.get('setting_location')}")
        print(f"    content[:200] = {content!r}")
        print(f"    content len = {len(s.get('content', ''))}")
