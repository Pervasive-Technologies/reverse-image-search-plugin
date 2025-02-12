"""Reverse Image Search plugin.

| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|  PERVASIVE CUSTOMISED VERSION

fiftyone plugins list

fiftyone plugins download https://github.com/jacobmarks/reverse-image-search-plugin

fiftyone plugins delete @jacobmarks/reverse_image_search

fiftyone plugins download https://github.com/Pervasive-Technologies/reverse-image-search-plugin

fiftyone plugins delete @jacobmarks/reverse_image_search

"""

from io import BytesIO
from PIL import Image

import fiftyone.operators as foo
import fiftyone.operators.types as types

import fiftyone.zoo as foz
import fiftyone.brain as fob
import numpy as np


import os
print("plugin running",os.getcwd())

MODEL_GITHUB_URL = "https://github.com/Pervasive-Technologies/pt-cpg-google-vit-large-patch16-224/"  # Replace with your actual URL

foz.register_zoo_model_source(MODEL_GITHUB_URL)

# Load dataset
#dataset = fo.load_dataset("your-dataset")

# Load the model
#model = foz.load_zoo_model("pt-cpg-google-vit-large-patch16-224")



def handle_request(payload):
    if 'url' in payload:
        url = payload['url']
        import requests
        response = requests.get(url)
        image_file_like = BytesIO(response.content)
    else:
        import base64
        base64_image = payload['file_data']
        if ';base64,' in base64_image:
            base64_image = base64_image.split(';base64,')[1]
        image_data = base64.b64decode(base64_image)
        image_file_like = BytesIO(image_data)

    image = Image.open(image_file_like).convert("RGB")
    return image


def get_valid_indexes(dataset):
    valid_indexes = []
    for br in dataset.list_brain_runs():
        bri = dataset.get_brain_info(br).config
        if "Similarity" in bri.cls:
            valid_indexes.append(br)
    return valid_indexes


def run_reverse_image_search(ctx):
    dataset = ctx.dataset
    index_name = ctx.params.get("index")
    index = dataset.load_brain_results(index_name)
    model = index.get_model()
    #model = model
    
    k = ctx.params.get("num_results")

    query_image = handle_request(ctx.params)

    if hasattr(model, "embed"):
        query_embedding = model.embed(query_image)
    else:
        query_embedding = model.embed_image(query_image)

    view = dataset.sort_by_similarity(query_embedding, brain_key=index_name, k=k)
    return view


class OpenReverseImageSearchPanel(foo.Operator):
    @property
    def config(self):
        return foo.OperatorConfig(
            name="open_reverse_image_search_panel",
            label="Reverse Image Search: open reverse image search panel",
            icon="/assets/icon.svg",
        )

    def resolve_placement(self, ctx):
        return types.Placement(
            types.Places.SAMPLES_GRID_SECONDARY_ACTIONS,
            types.Button(
                label="Reverse Image Search",
                icon="/assets/icon.svg",
                prompt=False,
            ),
        )

    def execute(self, ctx):
        ctx.trigger(
            "open_panel",
            params=dict(
                name="ReverseImageSearchPanel",
                isActive=True,
                layout="horizontal"
            ),
        )


class RunReverseImageSearch(foo.Operator):
    @property
    def config(self):
        return foo.OperatorConfig(
            name="reverse_search_image",
            label="Reverse Image Search",
            unlisted=True,
        )

    def resolve_input(self, ctx):
        inputs = types.Object()
        inputs.int("num_results", label="Number of Results", required=True)
        inputs.str("index", label="Brain Key", required=True)

        inputs.str("url", label="Image URL", required=False)
        inputs.str("file_data", label="Image File", required=False)
        return types.Property(inputs)

    def execute(self, ctx):
        view = run_reverse_image_search(ctx)
        ctx.ops.set_view(view=view)


def register(p):
    p.register(RunReverseImageSearch)
    p.register(OpenReverseImageSearchPanel)
