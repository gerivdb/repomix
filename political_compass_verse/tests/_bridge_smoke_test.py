import sys, json
sys.path.insert(0, r"D:\DO\WEB\TOOLS\L4-TOOLS\VERSUS")

from political_compass_verse import (
    TritQuadruplet, TritPoliticalNarrate, TritPoliticalEncode
)

narrate = TritPoliticalNarrate()

q = TritQuadruplet(0,2,0,2)
arc = narrate.narrate(q, label="La Cite de Verre")
print("static arc:", arc.arc_id, arc.label, arc.mode)

q1 = TritQuadruplet(0,2,0,2)
q2 = TritQuadruplet(2,0,2,1)
arc2 = narrate.narrate_transition(q1, q2, label="La Grande Bifurcation")
print("transition arc:", arc2.arc_id, arc2.label, arc2.mode)

from pathlib import Path
yaml_path = Path(r"D:\DO\WEB\TOOLS\L4-TOOLS\VERSUS\political_compass_verse\scenarios\hypotheses\scenario_post_AGI.yaml")
arc3 = narrate.narrate_counterfactual(yaml_path)
print("counterfactual arc:", arc3.arc_id, arc3.label, arc3.mode)

# Test export
import tempfile
tmp = Path(tempfile.gettempdir()) / "test_batverse_arc.json"
narrate.export_arc(arc3, tmp)
data = json.loads(tmp.read_text(encoding="utf-8"))
print("export OK:", data["arc_id"], data["label"])
print("BRIDGE ALL OK")
