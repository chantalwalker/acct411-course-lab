"""Register the local card component from an importable module for multipage apps."""
from pathlib import Path
import streamlit.components.v1 as components


def sliding_hand(**kwargs):
    component = components.declare_component(
        'velvet_hand', path=str(Path(__file__).parent / 'hand_component'))
    return component(**kwargs)
