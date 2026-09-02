import json

class Builder:
    def __init__(self, package_path):
        self.package_path = package_path
        self.package = None
        manifest_path = f"{self.package_path}/manifest.json"
        try:
            with open(manifest_path) as f:
                self.package = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Manifest not found at {manifest_path}")

    def is_sealed(self):
        if not self.package:
            return False
        return (self.package.get("package_sealed") == True and 
                self.package.get("builder_admission") == "approved")

    def get_artifacts(self, artifact_name):
        path = f"{self.package_path}/{artifact_name}"
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Artifact {artifact_name} not found in package.")
            return None
