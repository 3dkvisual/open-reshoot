# Open Reshoot

**Reshoot footage you already have — as a ComfyUI app.** Upload a clip, pick a scene (snow, fire, anime,
futuristic…), check the new first frame, and generate the whole shot again in the new world: same camera
move, same framing, same buildings and lettering. Open weights only, core ComfyUI nodes only, no custom
nodes, no paid API.

**Demo video:** [YouTube](https://youtu.be/45RNtBm2SVk) · [demo/open_reshoot_demo.mp4](demo/open_reshoot_demo.mp4)

## The app (one workflow, two steps)

`app/open_reshoot_app.json` — open it in ComfyUI and switch to **App mode**.

1. **Load your video** and choose a **scene** from the selector (optional: add free text).
2. **Step 1 — frame 0.** Run. The app takes the first frame of *your* clip at its original resolution and
   rebuilds it in the chosen scene with Qwen-Image-Edit-2511 (4-step Lightning). If you don't like it,
   change the seed or the text and run again — it takes a few minutes.
3. **Step 2 — video.** Pick the frame 0 you liked, turn on **Generate video** and run. LTX-2.5 22B
   (full dev model, never the distilled one) animates it image-to-video while an IC-LoRA follows the
   **canny edges of your original clip**, frame by frame. Frame 0 sets the look; the edges lock camera,
   geometry and motion. Two stages: 960×512, then latent upscale ×2 to 1920×1024. Audio comes from stage 1.

**Free zones (optional).** Type up to 3 object names (e.g. `sky` or `bus, road`). SAM 3 (core node) tracks
them through your clip and the edge guide is switched off there, so new elements the scene adds in those
areas (flying ships in the sky, a different vehicle) are kept instead of being redrawn from the original edges.

**Any aspect ratio.** The app reads your clip's orientation: landscape clips render at 960×512 → 1920×1024,
vertical clips at 512×960 → 1024×1920. Nothing to set.

Step 2 only runs when the switch is on (lazy `ComfySwitchNode`), so iterating on frame 0 never pays for
the video.

### Scenes

| Scene | What changes |
|---|---|
| `nieve` / snow | snow on every surface, falling snow (known issue: moving vehicles can smear) |
| `fuego` / fire | the buildings burn (guide strength 0.7 so the fire can move) |
| `abandonada` / abandoned | decades of decay, empty streets |
| `inundada` / flooded | the street under water |
| `cyberpunk` | neon night |
| `golden hour` | light only |
| `futurista` / futuristic | the same place in a far future: every structure kept, restyled |
| `anime` | redrawn as a 2D anime film background |

Every scene keeps every structure of the source in place: frame 0 restyles the place, it never removes
parts of it (if frame 0 drops a building, the edge guide would draw it back in the video).

## Requirements

- ComfyUI ≥ 0.40 (core nodes only), NVIDIA GPU.
- Models: run the installer, it does everything.

  1. Install ComfyUI (portable build recommended).
  2. Put this repo folder inside your ComfyUI folder and double-click **`install.bat`** (or run
     `python install.py "C:\path\to\ComfyUI"`). It downloads the 11 model files (~33 GB) straight into the
     right `models/` folders with the exact names, resumes if the download is cut, skips what you already
     have, and adds the app to ComfyUI's workflow list.
  3. It asks once for a Hugging Face token: the LTX 2.5 files are gated. Log in, press "Agree and access
     repository" on https://huggingface.co/Lightricks/LTX-2.5, and create a Read token on
     https://huggingface.co/settings/tokens. The token is not stored.

  Manual install, if you prefer (the app also lists missing models with a Download button when you press
  Run; on the portable build that downloads through the browser, so move each file into its folder and
  keep the exact name):

  | Folder | File |
  |---|---|
  | `diffusion_models` | [`qwen_image_edit_2511_fp8mixed.safetensors`](https://huggingface.co/Comfy-Org/Qwen-Image-Edit/resolve/main/split_files/diffusion_models/qwen_image_edit_2511_fp8mixed.safetensors) |
  | `loras` | [`Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors`](https://huggingface.co/lightx2v/Qwen-Image-Edit-2511-Lightning/resolve/main/Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors) |
  | `text_encoders` | [`qwen_2.5_vl_7b_fp8_scaled.safetensors`](https://huggingface.co/Comfy-Org/Qwen-Image/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors) |
  | `vae` | [`qwen_image_vae.safetensors`](https://huggingface.co/Comfy-Org/Qwen-Image/resolve/main/split_files/vae/qwen_image_vae.safetensors) |
  | `diffusion_models` | [`ltx-2.5-22b-dev-transformer-comfy-int8-convrot.safetensors`](https://huggingface.co/Lightricks/LTX-2.5/resolve/main/diffusion_models/ltx-2.5-22b-dev-transformer-comfy-int8-convrot.safetensors) |
  | `loras` | [`ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors`](https://huggingface.co/Lightricks/LTX-2.3-22b-IC-LoRA-Union-Control/resolve/main/ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors) |
  | `text_encoders` | [`gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors`](https://huggingface.co/Lightricks/LTX-2.5/resolve/main/text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors) |
  | `vae` | [`ltx-2.5-video-vae-bf16.safetensors`](https://huggingface.co/Lightricks/LTX-2.5/resolve/main/vae/ltx-2.5-video-vae-bf16.safetensors) |
  | `vae` | [`ltx-2.5-audio-vae-bf16.safetensors`](https://huggingface.co/Lightricks/LTX-2.5/resolve/main/vae/ltx-2.5-audio-vae-bf16.safetensors) |
  | `checkpoints` | [`sam3.1_multiplex_fp16.safetensors`](https://huggingface.co/Comfy-Org/sam3/resolve/main/checkpoints/sam3.1_multiplex_fp16.safetensors) |
  | `latent_upscale_models` | [`ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors`](https://huggingface.co/Lightricks/LTX-2.5/resolve/main/latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors) |

### Tested hardware (honest numbers)

Tested on an **RTX 4060 Laptop, 8 GB VRAM, 32 GB RAM** — the floor, not the target:

- Frame 0: ~3 min.
- Video, 8 s (193 frames) at 1920×1024: several hours, because the 22B model does not fit in 8 GB and
  streams from RAM every step. A 24 GB card is much faster.
- On 8 GB cards: upload the clip at **1280 px or less** (step 2 decodes every frame), and free memory
  between step 1 and step 2 (ComfyUI → *Unload models*). The canny guide is computed in batches of 32
  frames so it fits.
- An RTX 2060 (8 GB) runs out of memory in step 2.

## License

Code: MIT (see `LICENSE`). Model weights keep their own licenses: Qwen-Image-Edit (Apache-2.0), LTX-2.5
(Lightricks LTX license), Gemma (Gemma terms). Check them before commercial use.
