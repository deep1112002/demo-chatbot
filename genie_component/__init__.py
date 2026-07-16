import os
import streamlit.components.v1 as components

_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

_component_func = components.declare_component(
    "genie_avatar",
    path=_FRONTEND_DIR,
)


def genie_avatar(reply_text: str = "", reply_nonce: int = 0, muted: bool = False, key: str = None):
    """
    Renders Genie's 3D avatar with voice input/output.

    Args:
        reply_text: the latest assistant reply to speak aloud (empty = say nothing).
        reply_nonce: bump this any time reply_text is a *new* reply, so the component
            knows to speak it again even if the text happens to repeat.
        muted: if True, suppress spoken output.
        key: optional Streamlit widget key.

    Returns:
        A dict like {"transcript": str, "nonce": int} sent from the browser whenever
        the user finishes a voice utterance, or None if nothing has been captured yet.
    """
    return _component_func(
        reply_text=reply_text,
        reply_nonce=reply_nonce,
        muted=muted,
        key=key,
        default=None,
    )
