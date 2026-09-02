"""
Corrected Context Manager - Loads actual parent content into capsules.
Uses JSON for sandbox compatibility.
"""
import json

class ContextManager:
    def __init__(self, contract_path):
        with open(contract_path) as f:
            self.contract = json.load(f)

    def get_capsule(self, task_type, parent_artifact=None):
        """Builds a specific context block for the current generator."""
        
        # 1. Include the "Truth" (Immutable Production Memory)
        capsule = {
            "production_id": self.contract["production_id"],
            "contract_id": self.contract["contract_id"],
            "contract_version": self.contract.get("contract_version", "1.0"),
            "immutable_constraints": {
                "characters": [c["id"] for c in self.contract["characters"]],
                "ending_type": self.contract["ending"],
                # Use specific mechanism field, not just the last trajectory stage
                "mechanism": self.contract.get("core_conflict", {}).get("withdrawal_mechanism"),
                "tone_tags": self.contract["tone"]
            }
        }

        # 2. Load actual parent artifact data (Genuine Context)
        if parent_artifact:
            capsule["parent_memory"] = {
                "story_id": self.contract.get("story_id"),
                "scene_data": parent_artifact # Injects full scene content here
            }

        # 3. Add specific constraints for the current task
        if task_type == "generate_dialogue":
            capsule["constraints"] = {
                "max_words": 28,
                "new_characters_forbidden": True,
                "reconciliation_forbidden": True,
                "forbidden_exposition": True
            }

        return capsule
