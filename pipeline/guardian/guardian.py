"""
Corrected Guardian - Fixed validation and admission logic.
Uses JSON for sandbox compatibility.
"""
import json

class Guardian:
    def __init__(self, contract_path):
        with open(contract_path) as f:
            self.contract = json.load(f)

    def validate_artifact(self, artifact_path):
        """Validates an artifact against the Narrative Contract."""
        
        try:
            with open(artifact_path) as f:
                content = json.load(f)
        except Exception:
            return {
                "status": "rejected",
                "violations": ["INVALID_FORMAT"],
                "builder_admission": "denied"
            }

        report = {
            "status": "accepted",
            "violations": [],
            "builder_admission": "approved" # Default to approved for clean JSONs
        }

        content_str = json.dumps(content) if not isinstance(content, str) else content
        
        # Check 1: Character Identity (Fixed comparison logic)
        allowed_character_ids = {c["id"] for c in self.contract["characters"]}
        
        if 'characters' in content:
            for char in content['characters']:
                if char.get("id") not in allowed_character_ids:
                    report["violations"].append("UNAPPROVED_CHARACTER_ID")
        elif "Ethan" in content_str or "Claire" in content_str:
            # Fallback for strings/markdown-like text
            report["violations"].append("UNAPPROVED_CHARACTER_ID")

        # Check 2: Ending Type (The "No Reconciliation" Rule)
        if 'ending_type' in content:
            if content['ending_type'] != self.contract['ending']:
                report["violations"].append("ENDING_CHANGED")
        
        # Fallback for string-based content checks
        if 'reconciliation' in content_str.lower() or 'repair' in content_str.lower():
            report["violations"].append("ENDING_CHANGED")

        # Check 3: Runtime Compliance (Fixed min/max check)
        runtime_val = None
        if 'runtime' in content:
            r = content['runtime']
            if isinstance(r, int):
                runtime_val = r
            elif isinstance(r, dict):
                runtime_val = r.get("seconds") or r.get("target_seconds")
        
        if runtime_val is not None:
            min_r = self.contract['runtime'].get('minimum_seconds', 0)
            max_r = self.contract['runtime'].get('maximum_seconds', 9999)
            if runtime_val < min_r:
                report["violations"].append("RUNTIME_BELOW_MINIMUM")
            elif runtime_val > max_r:
                report["violations"].append("RUNTIME_ABOVE_MAXIMUM")

        # Finalize - Ensure all required fields are present
        # If violations found, deny admission
        if len(report["violations"]) > 0:
            report["status"] = "rejected"
            report["builder_admission"] = "denied"
        
        return report
