"""Run DEEPCYPs' published checkpoints on our constituents.

Kept OUTSIDE the cloned repo on purpose. The repo is third-party code we did not write.

torch 2.6 changed torch.load's default to weights_only=True, which the 2022 checkpoints
trip over because they pickle an argparse.Namespace of training arguments. We allowlist
exactly that class rather than setting weights_only=False, which would re-enable
arbitrary code execution during unpickling.
"""

import argparse
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
INPUT = Path(sys.argv[2]).resolve()
OUTDIR = Path(sys.argv[3]).resolve()

sys.path.insert(0, str(REPO))

import torch

# Allowlist only what these checkpoints legitimately contain.
SAFE = [argparse.Namespace]
try:
    import numpy
    SAFE += [numpy.core.multiarray.scalar, numpy.dtype]
except Exception:
    pass
torch.serialization.add_safe_globals(SAFE)

from fpgnn.data import MoleDataSet          # noqa: E402
from fpgnn.tool import get_scaler, load_args, load_data, load_model  # noqa: E402
from fpgnn.train import predict             # noqa: E402

MODELS = {
    "CYP1A2": "model_save/CYP_single-task/singletask_cyp1a2.pt",
    "CYP2C9": "model_save/CYP_single-task/singletask_cyp2c9.pt",
    "CYP2C19": "model_save/CYP_single-task/singletask_cyp2c19.pt",
    "CYP2D6": "model_save/CYP_single-task/singletask_cyp2d6.pt",
    "CYP3A4": "model_save/CYP_single-task/singletask_cyp3a4.pt",
}

OUTDIR.mkdir(parents=True, exist_ok=True)

for enzyme, relative in MODELS.items():
    checkpoint = REPO / relative
    print(f"\n=== {enzyme} ===", flush=True)
    try:
        args = argparse.Namespace(
            predict_path=str(INPUT), model_path=str(checkpoint),
            result_path=str(OUTDIR / f"{enzyme}.csv"), cuda=False, batch_size=50,
        )
        train_args = load_args(str(checkpoint))
        for key, value in vars(train_args).items():
            if not hasattr(args, key):
                setattr(args, key, value)
        args.cuda = False

        scaler = get_scaler(str(checkpoint))
        data = load_data(str(INPUT), args)
        model = load_model(str(checkpoint), False)

        # These checkpoints were trained on GPU, so the saved args carry cuda=True and
        # the rebuilt submodules shadow nn.Module.cuda with a boolean set to True.
        # Flip them to False so the forward pass stays on CPU.
        for module in model.modules():
            if isinstance(getattr(module, "cuda", None), bool):
                module.cuda = False

        values = predict(model, data, args.batch_size, scaler)

        smiles = data.smile()
        with open(OUTDIR / f"{enzyme}.csv", "w") as handle:
            handle.write("Smiles,prediction\n")
            for smile, value in zip(smiles, values):
                score = value[0] if isinstance(value, (list, tuple)) else value
                handle.write(f"{smile},{score}\n")
        print(f"  OK — wrote {len(smiles)} predictions", flush=True)
    except Exception as error:
        print(f"  FAILED: {type(error).__name__}: {error}", flush=True)
