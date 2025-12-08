"""Test Suite for geometry affinity measures."""

import pytest

from soundevent import data
from soundevent.geometry import affinity


class TestComputeTemporalCloseness:
    """Tests for compute_temporal_closeness."""

    def test_temporal_closeness_exact_match(self):
        """Test closeness is 1.0 for identical time points."""
        geom1 = data.TimeStamp(coordinates=1.0)
        geom2 = data.TimeStamp(coordinates=1.0)
        assert affinity.compute_temporal_closeness(geom1, geom2) == 1.0

    def test_temporal_closeness_no_match(self):
        """Test closeness is 0.0 when distance exceeds max_distance."""
        geom1 = data.TimeStamp(coordinates=1.0)
        geom2 = data.TimeStamp(coordinates=2.0)
        assert affinity.compute_temporal_closeness(geom1, geom2) == 0.0

    def test_temporal_closeness_partial_match(self):
        """Test linear decay of closeness score."""
        geom1 = data.TimeStamp(coordinates=1.0)
        geom2 = data.TimeStamp(coordinates=1.05)
        assert affinity.compute_temporal_closeness(
            geom1, geom2
        ) == pytest.approx(0.5)

    def test_temporal_closeness_custom_max_distance(self):
        """Test closeness with custom max_distance."""
        geom1 = data.TimeStamp(coordinates=1.0)
        geom2 = data.TimeStamp(coordinates=2.0)
        assert (
            affinity.compute_temporal_closeness(geom1, geom2, max_distance=2.0)
            == 0.5
        )

    def test_temporal_closeness_ratio_start(self):
        """Test comparing start times."""
        geom1 = data.TimeInterval(coordinates=[0.0, 2.0])
        geom2 = data.TimeInterval(coordinates=[0.1, 3.0])
        assert (
            affinity.compute_temporal_closeness(
                geom1, geom2, ratio=0, max_distance=0.2
            )
            == 0.5
        )

    def test_temporal_closeness_ratio_center(self):
        """Test comparing center times."""
        geom1 = data.TimeInterval(coordinates=[0.0, 2.0])
        geom2 = data.TimeInterval(coordinates=[1.0, 3.0])
        assert (
            affinity.compute_temporal_closeness(
                geom1, geom2, ratio=0.5, max_distance=2.0
            )
            == 0.5
        )


class TestComputeSpectralCloseness:
    """Tests for compute_spectral_closeness."""

    def test_spectral_closeness_exact_match(self):
        """Test closeness is 1.0 for identical frequency points."""
        geom1 = data.Point(coordinates=[0, 1000])
        geom2 = data.Point(coordinates=[1, 1000])
        assert affinity.compute_spectral_closeness(geom1, geom2) == 1.0

    def test_spectral_closeness_no_match(self):
        """Test closeness is 0.0 when distance exceeds max_distance."""
        geom1 = data.Point(coordinates=[0, 1000])
        geom2 = data.Point(coordinates=[0, 3000])
        assert affinity.compute_spectral_closeness(geom1, geom2) == 0.0

    def test_spectral_closeness_partial_match(self):
        """Test linear decay of closeness score."""
        geom1 = data.Point(coordinates=[0, 1000])
        geom2 = data.Point(coordinates=[0, 1500])
        assert affinity.compute_spectral_closeness(geom1, geom2) == 0.5

    def test_spectral_closeness_ratio_center(self):
        """Test comparing center frequencies."""
        geom1 = data.BoundingBox(coordinates=[0, 1000, 1, 2000])
        geom2 = data.BoundingBox(coordinates=[0, 2000, 1, 3000])
        assert (
            affinity.compute_spectral_closeness(
                geom1,
                geom2,
                ratio=0.5,
                max_distance=2000,
            )
            == 0.5
        )


class TestComputeTemporalIoU:
    """Tests for compute_temporal_iou."""

    def test_temporal_iou_no_overlap(self):
        """Test IoU is 0 for disjoint intervals."""
        geom1 = data.TimeInterval(coordinates=[0, 1])
        geom2 = data.TimeInterval(coordinates=[2, 3])
        assert affinity.compute_temporal_iou(geom1, geom2) == 0.0

    def test_temporal_iou_full_overlap(self):
        """Test IoU is 1 for identical intervals."""
        geom1 = data.TimeInterval(coordinates=[0, 1])
        geom2 = data.TimeInterval(coordinates=[0, 1])
        assert affinity.compute_temporal_iou(geom1, geom2) == 1.0

    def test_temporal_iou_partial_overlap(self):
        """Test IoU for partially overlapping intervals."""
        geom1 = data.TimeInterval(coordinates=[0, 2])
        geom2 = data.TimeInterval(coordinates=[1, 3])
        assert abs(affinity.compute_temporal_iou(geom1, geom2) - 1 / 3) < 1e-6

    def test_temporal_iou_ignores_frequency(self):
        """Test that frequency differences do not affect Temporal IoU."""
        geom1 = data.BoundingBox(coordinates=[0, 100, 1, 200])
        geom2 = data.BoundingBox(coordinates=[0, 300, 1, 400])
        assert affinity.compute_temporal_iou(geom1, geom2) == 1.0


class TestComputeFrequencyIoU:
    """Tests for compute_frequency_iou."""

    def test_frequency_iou_no_overlap(self):
        """Test IoU is 0 for disjoint frequency bands."""
        geom1 = data.BoundingBox(coordinates=[0, 100, 1, 200])
        geom2 = data.BoundingBox(coordinates=[0, 300, 1, 400])
        assert affinity.compute_frequency_iou(geom1, geom2) == 0.0

    def test_frequency_iou_full_overlap(self):
        """Test IoU is 1 for identical frequency bands."""
        geom1 = data.BoundingBox(coordinates=[0, 100, 1, 200])
        geom2 = data.BoundingBox(coordinates=[5, 100, 6, 200])
        assert affinity.compute_frequency_iou(geom1, geom2) == 1.0

    def test_frequency_iou_partial_overlap(self):
        """Test IoU for partially overlapping frequency bands."""
        geom1 = data.BoundingBox(coordinates=[0, 100, 1, 300])
        geom2 = data.BoundingBox(coordinates=[0, 200, 1, 400])
        assert abs(affinity.compute_frequency_iou(geom1, geom2) - 1 / 3) < 1e-6

    def test_frequency_iou_ignores_time(self):
        """Test that time differences do not affect Frequency IoU."""
        geom1 = data.BoundingBox(coordinates=[0, 100, 1, 200])
        geom2 = data.BoundingBox(coordinates=[2, 100, 3, 200])
        assert affinity.compute_frequency_iou(geom1, geom2) == 1.0


class TestComputeBBoxIoU:
    """Tests for compute_bbox_iou."""

    def test_bbox_iou_no_overlap(self):
        """Test IoU is 0 for disjoint boxes."""
        geom1 = data.BoundingBox(coordinates=[0, 0, 1, 100])
        geom2 = data.BoundingBox(coordinates=[2, 200, 3, 300])
        assert affinity.compute_bbox_iou(geom1, geom2) == 0.0

    def test_bbox_iou_single_axis_overlap(self):
        """Test IoU is 0 if overlap is only on one axis."""
        geom1 = data.BoundingBox(coordinates=[0, 0, 1, 100])
        geom2 = data.BoundingBox(coordinates=[0, 200, 1, 300])
        # Overlap in time, but not freq
        assert affinity.compute_bbox_iou(geom1, geom2) == 0.0

    def test_bbox_iou_full_overlap(self):
        """Test IoU is 1 for identical boxes."""
        geom1 = data.BoundingBox(coordinates=[0, 0, 1, 100])
        geom2 = data.BoundingBox(coordinates=[0, 0, 1, 100])
        assert affinity.compute_bbox_iou(geom1, geom2) == 1.0

    def test_bbox_iou_partial_overlap(self):
        """Test IoU for partially overlapping boxes."""
        geom1 = data.BoundingBox(coordinates=[0, 0, 2, 200])
        geom2 = data.BoundingBox(coordinates=[1, 100, 3, 300])
        assert affinity.compute_bbox_iou(geom1, geom2) == pytest.approx(1 / 7)


class TestComputeGeometricIoU:
    """Tests for compute_geometric_iou."""

    def test_geometric_iou_rectangles(self):
        """Test geometric IoU matches BBox IoU for rectangles."""
        geom1 = data.BoundingBox(coordinates=[0, 0, 2, 200])
        geom2 = data.BoundingBox(coordinates=[1, 100, 3, 300])
        bbox_iou = affinity.compute_bbox_iou(geom1, geom2)
        geom_iou = affinity.compute_geometric_iou(geom1, geom2)
        assert abs(geom_iou - bbox_iou) < 1e-6

    def test_geometric_iou_disjoint(self):
        """Test IoU is 0 for disjoint geometries."""
        geom1 = data.BoundingBox(coordinates=[0, 0, 1, 100])
        geom2 = data.BoundingBox(coordinates=[2, 200, 3, 300])
        assert affinity.compute_geometric_iou(geom1, geom2) == 0.0

    def test_geometric_iou_polygons(self):
        """Test IoU for polygons."""
        geom1 = data.Polygon(coordinates=[[[0, 0], [2, 0], [1, 2], [0, 0]]])
        geom2 = data.Polygon(coordinates=[[[1, 0], [3, 0], [2, 2], [1, 0]]])
        assert affinity.compute_geometric_iou(geom1, geom2) == pytest.approx(
            1 / 7
        )
