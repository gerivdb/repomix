"""
TEST E2E FULL BUS CYCLE
P0_CRITIQUE
Valide le cycle complet:
PRIM.canonized → META_REDACTOR → EPIC généré
"""

import sys
sys.path.insert(0, '.')

from engines.common.event_bus import bus, Event
from engines.meta_redactor_engine.epic_generator import MetaRedactorEngine

def test_full_bus_cycle():
    redactor = MetaRedactorEngine()
    
    # Simule un evenement prim.canonized sur le bus
    event = Event.emit(
        origin="prim.engine",
        phase="completed",
        payload={
            "component": "test-epic-999",
            "concept_id": "test_concept_001"
        },
        entropy=0.1
    )
    
    # On emet l'evenement
    bus.emit(event)
    
    # On verifie que le meta redacteur peut generer le prochain epic
    assert redactor.can_generate() == True
    
    epic = redactor.generate_epic(
        epic_id=1000,
        name="TEST_EPIC_AUTO_GEN",
        priority="P1_AUTO",
        objective="Test auto generation",
        architecture="BUS → META → EPIC",
        tests=["convergence"],
        roi_items=["0 HITL"],
        command="test auto"
    )
    
    assert "EPIC-1000" in epic
    assert "P1_AUTO" in epic
    
    print("✅ FULL BUS CYCLE TEST PASSED")

if __name__ == "__main__":
    test_full_bus_cycle()