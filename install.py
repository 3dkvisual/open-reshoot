"""Open Reshoot installer: downloads every model the app needs straight into your ComfyUI folders
(exact file names, resumes if interrupted) and adds the app to ComfyUI's workflow list.

Usage:  python install.py [path\\to\\ComfyUI]      (install.bat does this for you)
Only the Python standard library is used, so ComfyUI's own embedded Python is enough."""
import os, sys, shutil, urllib.request, urllib.error, getpass

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, "app", "open_reshoot_app.json")
LTX = "https://huggingface.co/Lightricks/LTX-2.5/resolve/main/"
MODELS = [  # (folder, file, url, gated)
    ("diffusion_models", "qwen_image_edit_2511_fp8mixed.safetensors",
     "https://huggingface.co/Comfy-Org/Qwen-Image-Edit/resolve/main/split_files/diffusion_models/qwen_image_edit_2511_fp8mixed.safetensors", False),
    ("loras", "Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors",
     "https://huggingface.co/lightx2v/Qwen-Image-Edit-2511-Lightning/resolve/main/Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors", False),
    ("text_encoders", "qwen_2.5_vl_7b_fp8_scaled.safetensors",
     "https://huggingface.co/Comfy-Org/Qwen-Image/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors", False),
    ("checkpoints", "sam3.1_multiplex_fp16.safetensors",
     "https://huggingface.co/Comfy-Org/sam3/resolve/main/checkpoints/sam3.1_multiplex_fp16.safetensors", False),
    ("vae", "qwen_image_vae.safetensors",
     "https://huggingface.co/Comfy-Org/Qwen-Image/resolve/main/split_files/vae/qwen_image_vae.safetensors", False),
    ("loras", "ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors",
     "https://huggingface.co/Lightricks/LTX-2.3-22b-IC-LoRA-Union-Control/resolve/main/ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors", False),
    ("diffusion_models", "ltx-2.5-22b-dev-transformer-comfy-int8-convrot.safetensors",
     LTX + "diffusion_models/ltx-2.5-22b-dev-transformer-comfy-int8-convrot.safetensors", True),
    ("text_encoders", "gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors",
     LTX + "text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors", True),
    ("vae", "ltx-2.5-video-vae-bf16.safetensors", LTX + "vae/ltx-2.5-video-vae-bf16.safetensors", True),
    ("vae", "ltx-2.5-audio-vae-bf16.safetensors", LTX + "vae/ltx-2.5-audio-vae-bf16.safetensors", True),
    ("latent_upscale_models", "ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors",
     LTX + "latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors", True),
]
GATED_HELP = """
The LTX 2.5 files need a free Hugging Face account (license terms of Lightricks):
  1. Log in and press "Agree and access repository" on https://huggingface.co/Lightricks/LTX-2.5
  2. Create a token (type: Read) on https://huggingface.co/settings/tokens
The token is only used for these downloads and is not saved anywhere."""


def find_comfy(arg):
    cands = [arg] if arg else [os.getcwd(), os.path.dirname(HERE), os.path.dirname(os.path.dirname(HERE))]
    for c in cands:
        for p in (c, os.path.join(c, "ComfyUI")):
            if p and os.path.isfile(os.path.join(p, "main.py")) and os.path.isdir(os.path.join(p, "models")):
                return os.path.abspath(p)
    return None


def size_of(url, token):
    req = urllib.request.Request(url, method="HEAD", headers={"Authorization": f"Bearer {token}"} if token else {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return int(r.headers.get("Content-Length", 0))


def download(url, dest, token):
    part = dest + ".part"
    total = size_of(url, token)
    have = os.path.getsize(part) if os.path.exists(part) else 0
    if total and have >= total:
        os.replace(part, dest); return
    h = {"Authorization": f"Bearer {token}"} if token else {}
    if have:
        h["Range"] = f"bytes={have}-"
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120) as r, open(part, "ab" if have else "wb") as f:
        if have and r.status != 206:  # server ignored the range: start over
            f.seek(0); f.truncate(); have = 0
        done, step = have, 0
        while True:
            b = r.read(8 << 20)
            if not b:
                break
            f.write(b); done += len(b); step += 1
            if total and step % 8 == 0:
                print(f"    {done / 2**30:5.1f} / {total / 2**30:.1f} GB", flush=True)
    if total and os.path.getsize(part) != total:
        raise IOError(f"incomplete download ({os.path.getsize(part)} of {total} bytes), run the installer again to resume")
    os.replace(part, dest)


def main():
    comfy = find_comfy(sys.argv[1] if len(sys.argv) > 1 else None)
    while not comfy:
        comfy = find_comfy(input("Path to your ComfyUI folder (the one with main.py): ").strip().strip('"'))
    print(f"ComfyUI: {comfy}")
    todo = [m for m in MODELS if not os.path.isfile(os.path.join(comfy, "models", m[0], m[1]))]
    token = os.environ.get("HF_TOKEN", "")
    if any(m[3] for m in todo) and not token:
        print(GATED_HELP)
        token = getpass.getpass("Hugging Face token (input hidden): ").strip()
    failed = []
    for i, (folder, name, url, gated) in enumerate(MODELS, 1):
        dest = os.path.join(comfy, "models", folder, name)
        if os.path.isfile(dest):
            print(f"[{i}/{len(MODELS)}] {name}: already there"); continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        print(f"[{i}/{len(MODELS)}] {name} -> models/{folder}")
        try:
            download(url, dest, token if gated else "")
        except urllib.error.HTTPError as e:
            msg = "no access: accept the license and check the token (see above)" if e.code in (401, 403) else f"HTTP {e.code}"
            print(f"    FAILED: {msg}"); failed.append(name)
        except Exception as e:
            print(f"    FAILED: {e}"); failed.append(name)
    wf = os.path.join(comfy, "user", "default", "workflows")
    os.makedirs(wf, exist_ok=True)
    shutil.copyfile(APP, os.path.join(wf, "open_reshoot_app.json"))
    print("\nApp added: in ComfyUI open Workflows > open_reshoot_app (it opens in App mode).")
    if failed:
        print(f"{len(failed)} file(s) failed: {', '.join(failed)}\nRun the installer again: it resumes and skips what is already there.")
        sys.exit(1)
    print("All models in place. Restart ComfyUI if it was open.")


if __name__ == "__main__":
    main()
