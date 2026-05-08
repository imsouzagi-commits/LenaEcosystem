from __future__ import annotations


class IntentionalModulator:

    @classmethod
    def apply(
        cls,
        cognitive_state,
        intentional_frame,
        recent_topic_windows,
        session_semantic_hits,
    ) -> None:

        frame_type = intentional_frame.type

        if frame_type == "displacement":

            recent_topic_windows.clear()

            session_semantic_hits.clear()

            cognitive_state.semantic_inertia *= 0.05
            cognitive_state.continuity_residue *= 0.08
            cognitive_state.emotional_residue *= 0.35

            return

        if frame_type in {
            "worldly",
            "exploratory",
        }:

            cognitive_state.semantic_inertia *= 0.55
            cognitive_state.continuity_residue *= 0.45
            cognitive_state.emotional_residue *= 0.72

            return

        if frame_type == "relational":

            cognitive_state.emotional_residue *= 0.90
