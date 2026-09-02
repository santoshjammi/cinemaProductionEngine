"""
Generates a ComfyUI Workflow JSON for Scene 4 (Lost Emotional Safety).
This script prepares the 'truth' as a prompt and constructs the FLUX graph.
"""
import json
import os

# Scene 4 Data from Truth Package
scene_data = {
    "prompt": "Medium close-up — warm indoor light turning cold. SARAH's hand reaching out to MARK's shoulder. MARK is rigid, pulling his body into the shadows on the right. Tension between them.",
    "negative_prompt": "reconciliation, happy_ending, blurry, low_quality, text, watermark",
    "width": 1024,
    "height": 576,
    "steps": 28,
    "cfg": 3.5,
    "seed": 1987
}

workflow = {
    "7": {
        "inputs": {"text": scene_data["prompt"], "clip": "CLIP_L"},
        "class_type": "CLIPSetLastLayer"
    },
    "8": {
        "inputs": {"text": scene_data["negative_prompt"], "clip": "CLIP_L"},
        "class_type": "CLIPSetLastLayer"
    },
    "10": {
        "inputs": {"t5xxl": "T5_XXL_FP8", "text": scene_data["prompt"]},
        "class_type": "ConditioningT5XL"
    },
    "11": {
        "inputs": {"t5xxl": "T5_XXL_FP8", "text": scene_data["negative_prompt"]},
        "class_type": "ConditioningT5XL"
    },
    "12": {
        "inputs": {"unet": "FLUX_BF16", "seed": scene_data["seed"], "steps": scene_data["steps"], 
                    "cfg": scene_data["cfg"], "sampler_name": "euler"},
        "class_type": "KSampler"
    },
    "13": {
        "inputs": {"samples": ["12", 0], "vae": "FLUX_VAE"},
        "class_type": "VAEDecode"
    },
    "14": {
        "inputs": {"images": ["13", 0]},
        "class_type": "PreviewImage"
    },
    "15": {
        "inputs": {"filename_prefix": "scene_4_stranded_hand/", "images": ["13", 0]},
        "class_type": "SaveImage"
    }
}

# Save to a file that can be loaded into ComfyUI (ComfyUI-Manager or API)
output_dir = "/Users/santosh/Desktop/projects/videoGen/pipeline/architect/comfyui_workflows/"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "scene_4_stranded_hand_workflow.json")

with open(output_path, 'w') as f:
    json.dump(workflow, f, indent=2)

print(f"Workflow JSON generated at: {output_path}")
