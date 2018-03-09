# Externel imports
import pytest

import numpy as np
from gpmap import GenotypePhenotypeMap

# Module to test
from ..nonlinear import *

import warnings

# Ignore fitting warnings
warnings.simplefilter("ignore", RuntimeWarning)


@pytest.fixture
def gpm():
    """Create a genotype-phenotype map"""
    wildtype = "000"
    genotypes = ["000", "001", "010", "100", "011", "101", "110", "111"]
    phenotypes = [0.1,   0.1,   0.5,   0.4,   0.2,   0.8,   0.5,   1.0]
    stdeviations = 0.1
    return GenotypePhenotypeMap(wildtype, genotypes, phenotypes,
                                stdeviations=stdeviations)


def function(x, A, B):
    return A * x + B


def reverse(y, A, B):
    return (y - B) / A


class TestEpistasisNonlinearRegression(object):

    model_type = "local"

    def test_init(self, gpm):
        m = EpistasisNonlinearRegression(function=function,
                                         reverse=reverse,
                                         model_type=self.model_type)
        m.add_gpm(gpm)

        # Checks
        assert hasattr(m, 'parameters') is True
        assert hasattr(m, 'function') is True
        assert hasattr(m, 'reverse') is True

        parameters = m.parameters

        # Checks
        assert 'A' in parameters
        assert 'B' in parameters

    def test_fit(self, gpm):

        m = EpistasisNonlinearRegression(function=function,
                                         reverse=reverse,
                                         model_type=self.model_type)
        m.add_gpm(gpm)
        m.fit(A=1, B=0)

        assert True

    def test_score(self, gpm):
        m = EpistasisNonlinearRegression(function=function,
                                         reverse=reverse,
                                         model_type=self.model_type)
        m.add_gpm(gpm)

        m.fit(A=1, B=0)
        score = m.score()
        assert 0 <= score <= 1

    def test_predict(self, gpm):
        m = EpistasisNonlinearRegression(function=function,
                                         reverse=reverse,
                                         model_type=self.model_type)
        m.add_gpm(gpm)

        m.fit(A=1, B=0)
        y = m.predict(X='obs')

        # Tests
        assert True

    def test_thetas(self, gpm):
        m = EpistasisNonlinearRegression(function=function,
                                         reverse=reverse,
                                         model_type=self.model_type)
        m.add_gpm(gpm)
        m.fit(A=1, B=0)
        coefs = m.thetas
        # Tests
        assert len(coefs) == 6

    def test_hypothesis(self, gpm):

        m = EpistasisNonlinearRegression(function=function,
                                         reverse=reverse,
                                         model_type=self.model_type)
        m.add_gpm(gpm)

        m.fit(A=1, B=0)
        predictions = m.hypothesis()
        # Tests
        assert True


    def test_lnlikelihood(self, gpm):
        m = EpistasisNonlinearRegression(function=function,
                                         reverse=reverse,
                                         model_type=self.model_type)
        m.add_gpm(gpm)

        m.fit(A=1, B=0)

        # Calculate lnlikelihood
        lnlike = m.lnlikelihood()
        assert lnlike.dtype == float
