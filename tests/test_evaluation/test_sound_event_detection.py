from dataclasses import dataclass
from typing import Sequence
from uuid import UUID

import pytest

from soundevent import data
from soundevent.evaluation.tasks.sound_event_detection import (
    evaluate_sound_event_detection,
)
from soundevent.geometry.affinity import compute_temporal_closeness


@dataclass
class MockDetection:
    uuid: UUID
    geometry: data.Geometry
    score: float

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __hash__(self):
        return hash(self.uuid)


@dataclass
class MockClipPrediction:
    clip: data.Clip
    detections: Sequence[MockDetection] = ()


def mock_affinity_fn(
    det: MockDetection, ann: data.SoundEventAnnotation
) -> float:
    if det.geometry is None or ann.sound_event.geometry is None:
        return 0.0
    return compute_temporal_closeness(
        geometry1=det.geometry,
        geometry2=ann.sound_event.geometry,
        max_distance=0.1,
    )


def mock_score_fn(det: MockDetection) -> float:
    return det.score


class TestEvaluateSoundEventDetection:
    def test_input_mismatch_validation_lengths(self, random_clips):
        clips = random_clips(n=2)
        clip1, clip2 = clips[0], clips[1]

        pred1 = MockClipPrediction(clip=clip1)
        pred2 = MockClipPrediction(clip=clip2)
        ann1 = data.ClipAnnotation(clip=clip1, sound_events=[])

        with pytest.raises(
            ValueError,
            match="The number of clip predictions and annotations must match",
        ):
            list(
                evaluate_sound_event_detection(
                    clip_predictions=[pred1, pred2],
                    clip_annotations=[ann1],
                    affinity=mock_affinity_fn,
                    score=mock_score_fn,
                )
            )

    def test_input_mismatch_validation_uuids(self, random_clips):
        clips = random_clips(n=2)
        clipA, clipB = clips[0], clips[1]

        pred_A = MockClipPrediction(clip=clipA)
        ann_B = data.ClipAnnotation(clip=clipB, sound_events=[])

        with pytest.raises(
            ValueError,
            match="The clip predictions and annotations must be mapped to the same clips",
        ):
            list(
                evaluate_sound_event_detection(
                    clip_predictions=[pred_A],
                    clip_annotations=[ann_B],
                    affinity=mock_affinity_fn,
                    score=mock_score_fn,
                )
            )

    def test_order_independence(self, random_clips):
        clips = random_clips(n=2)
        clipA, clipB = clips[0], clips[1]

        geoA = data.TimeInterval(coordinates=[0.1, 0.2])
        geoB = data.TimeInterval(coordinates=[0.5, 0.6])

        detA = MockDetection(uuid=clipA.uuid, geometry=geoA, score=1.0)
        detB = MockDetection(uuid=clipB.uuid, geometry=geoB, score=1.0)

        seA = data.SoundEvent(geometry=geoA, recording=clipA.recording)
        annA = data.SoundEventAnnotation(sound_event=seA)

        seB = data.SoundEvent(geometry=geoB, recording=clipB.recording)
        annB = data.SoundEventAnnotation(sound_event=seB)

        predA_clip = MockClipPrediction(clip=clipA, detections=[detA])
        annA_clip = data.ClipAnnotation(clip=clipA, sound_events=[annA])

        predB_clip = MockClipPrediction(clip=clipB, detections=[detB])
        annB_clip = data.ClipAnnotation(clip=clipB, sound_events=[annB])

        results = list(
            evaluate_sound_event_detection(
                clip_predictions=[predB_clip, predA_clip],
                clip_annotations=[annA_clip, annB_clip],
                affinity=mock_affinity_fn,
                score=mock_score_fn,
            )
        )

        assert len(results) == 2

        matchA = next(m for c, m in results if c == clipA)
        assert matchA.prediction == detA
        assert matchA.annotation == annA

        matchB = next(m for c, m in results if c == clipB)
        assert matchB.prediction == detB
        assert matchB.annotation == annB

    def test_integration_happy_path(self, clip):
        geo = data.TimeInterval(coordinates=[0.0, 0.0])

        det = MockDetection(uuid=clip.uuid, geometry=geo, score=0.9)

        se = data.SoundEvent(geometry=geo, recording=clip.recording)
        ann = data.SoundEventAnnotation(sound_event=se)

        pred_clip = MockClipPrediction(clip=clip, detections=[det])
        ann_clip = data.ClipAnnotation(clip=clip, sound_events=[ann])

        results = list(
            evaluate_sound_event_detection(
                clip_predictions=[pred_clip],
                clip_annotations=[ann_clip],
                affinity=mock_affinity_fn,
                score=mock_score_fn,
            )
        )

        assert len(results) == 1
        output_clip, match = results[0]

        assert output_clip == clip
        assert match.prediction == det
        assert match.annotation == ann
        assert match.affinity_score == 1.0
        assert match.prediction_score == 0.9

    def test_empty_input_handling(self, clip):
        pred_clip = MockClipPrediction(clip=clip, detections=[])
        ann_clip = data.ClipAnnotation(clip=clip, sound_events=[])

        results_empty_lists = list(
            evaluate_sound_event_detection(
                clip_predictions=[],
                clip_annotations=[],
                affinity=mock_affinity_fn,
                score=mock_score_fn,
            )
        )
        assert len(results_empty_lists) == 0

        results_empty_events = list(
            evaluate_sound_event_detection(
                clip_predictions=[pred_clip],
                clip_annotations=[ann_clip],
                affinity=mock_affinity_fn,
                score=mock_score_fn,
            )
        )
        assert len(results_empty_events) == 0
