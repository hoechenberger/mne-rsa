import pytest
import numpy as np
from numpy.testing import assert_equal
from scipy import sparse

from mne_rsa import searchlight


class TestSearchLight:
    """Test the searchlight generator class"""

    def test_iter_spatio_temporal(self):
        """Test generating spatio-temporal searchlight patches."""
        dist = np.array([[0, 1, 2],
                         [1, 0, 1],
                         [2, 1, 0]])
        s = searchlight((10, 3, 4), dist, spatial_radius=2, temporal_radius=1)
        assert len(s) == 6
        assert s.shape == (3, 2)
        assert_equal(list(s), [
            (slice(None), np.array([0, 1]), slice(0, 3)),
            (slice(None), np.array([0, 1]), slice(1, 4)),
            (slice(None), np.array([0, 1, 2]), slice(0, 3)),
            (slice(None), np.array([0, 1, 2]), slice(1, 4)),
            (slice(None), np.array([1, 2]), slice(0, 3)),
            (slice(None), np.array([1, 2]), slice(1, 4)),
        ])

        # Test using a sparse matrix
        dist_sparse = sparse.csr_matrix(dist)
        s = searchlight((10, 3, 4), dist_sparse,
                        spatial_radius=2, temporal_radius=1)
        assert len(s) == 6
        assert s.shape == (3, 2)
        assert_equal(list(s), [
            (slice(None), np.array([0, 1]), slice(0, 3)),
            (slice(None), np.array([0, 1]), slice(1, 4)),
            (slice(None), np.array([0, 1, 2]), slice(0, 3)),
            (slice(None), np.array([0, 1, 2]), slice(1, 4)),
            (slice(None), np.array([1, 2]), slice(0, 3)),
            (slice(None), np.array([1, 2]), slice(1, 4)),
        ])

        # Test using subsets of series and samples
        s = searchlight((10, 3, 4), dist, spatial_radius=2, temporal_radius=1,
                        sel_series=[1, 2], sel_samples=[2, 3])
        assert len(s) == 2
        assert s.shape == (2, 1)
        assert_equal(list(s), [
            (slice(None), np.array([0, 1, 2]), slice(1, 4)),
            (slice(None), np.array([1, 2]), slice(1, 4)),
        ])

    def test_iter_spatial(self):
        """Test generating spatial searchlight patches."""
        dist = np.array([[0, 1, 2],
                         [1, 0, 1],
                         [2, 1, 0]])

        s = searchlight((5, 10, 3, 4), dist, spatial_radius=2)
        assert len(s) == 3
        assert s.shape == (3,)
        assert_equal(list(s), [
            (slice(None), slice(None), np.array([0, 1]), slice(None)),
            (slice(None), slice(None), np.array([0, 1, 2]), slice(None)),
            (slice(None), slice(None), np.array([1, 2]), slice(None)),
        ])

        s = searchlight((10, 3, 4), dist, spatial_radius=2)
        assert len(s) == 3
        assert s.shape == (3,)
        assert_equal(list(s), [
            (slice(None), np.array([0, 1]), slice(None)),
            (slice(None), np.array([0, 1, 2]), slice(None)),
            (slice(None), np.array([1, 2]), slice(None)),
        ])

        s = searchlight((10, 3), dist, spatial_radius=2)
        assert len(s) == 3
        assert s.shape == (3,)
        assert_equal(list(s), [
            (slice(None), np.array([0, 1])),
            (slice(None), np.array([0, 1, 2])),
            (slice(None), np.array([1, 2])),
        ])

        # Test using a sparse matrix
        dist_sparse = sparse.csr_matrix(dist)
        s = searchlight((10, 3), dist_sparse, spatial_radius=2)
        assert len(s) == 3
        assert s.shape == (3,)
        assert_equal(list(s), [
            (slice(None), np.array([0, 1])),
            (slice(None), np.array([0, 1, 2])),
            (slice(None), np.array([1, 2])),
        ])

    def test_iter_temporal(self):
        """Test generating temporal searchlight patches."""
        s = searchlight((10, 3, 4), temporal_radius=1)
        assert len(s) == 2
        assert s.shape == (2,)
        assert_equal(list(s), [
            (slice(None), slice(None), slice(0, 3)),
            (slice(None), slice(None), slice(1, 4)),
        ])

        s = searchlight((10, 4), temporal_radius=1)
        assert len(s) == 2
        assert s.shape == (2,)
        assert_equal(list(s), [
            (slice(None), slice(0, 3)),
            (slice(None), slice(1, 4)),
        ])

    def test_iter_single(self):
        """Test generating a single searchlight patch."""
        s = searchlight((5, 10, 3, 4))
        assert len(s) == 1
        assert s.shape == tuple()
        assert_equal(next(s), tuple([slice(None)] * 4))

        s = searchlight((10, 3, 4))
        assert len(s) == 1
        assert s.shape == tuple()
        assert_equal(next(s), tuple([slice(None)] * 3))

        s = searchlight((10, 3))
        assert len(s) == 1
        assert s.shape == tuple()
        assert_equal(next(s), tuple([slice(None)] * 2))

        s = searchlight((10,))
        assert len(s) == 1
        assert s.shape == tuple()
        assert_equal(next(s), (slice(None),))

        # Test using subsets of series and samples
        s = searchlight((10, 3, 4), sel_series=[1, 2], sel_samples=[2, 3])
        assert len(s) == 1
        assert s.shape == tuple()
        assert_equal(next(s), (slice(None), [1, 2], [2, 3]))

    def test_invalid_input(self):
        """Test giving invalid input to searchlight generator."""
        dist = np.array([[0, 1, 2],
                         [1, 0, 1],
                         [2, 1, 0]])

        # Spatio-temporal case
        with pytest.raises(ValueError, match='no spatial dimension'):
            searchlight((10,), dist=dist, spatial_radius=1, temporal_radius=1)
        with pytest.raises(ValueError, match='no temporal dimension'):
            searchlight((10, 3), dist=dist,
                        spatial_radius=1, temporal_radius=1)
        with pytest.raises(ValueError, match='no distance information'):
            searchlight((10, 3, 4), spatial_radius=1, temporal_radius=1)

        # Spatial case
        with pytest.raises(ValueError, match='no spatial dimension'):
            searchlight((10,), dist=dist, spatial_radius=1)
        with pytest.raises(ValueError, match='no distance information'):
            searchlight((10, 5), spatial_radius=1)
        with pytest.raises(ValueError, match='no spatial dimension'):
            searchlight((10,), sel_series=[1, 2])

        # Temporal case
        with pytest.raises(ValueError, match='no temporal dimension'):
            searchlight((10,), dist=dist, temporal_radius=1)
        with pytest.raises(ValueError, match='no temporal dimension'):
            searchlight((10,), dist=dist, sel_samples=[1, 2])
