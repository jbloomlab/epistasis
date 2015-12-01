__doc__ = """ Submodule of linear epistasis models. Includes full local and global epistasis models and regression model for low order models."""

# ------------------------------------------------------------
# Imports
# ------------------------------------------------------------

import numpy as np

# ------------------------------------------------------------
# seqspace imports
# ------------------------------------------------------------

from seqspace.utils import list_binary, enumerate_space, encode_mutations, construct_genotypes

# ------------------------------------------------------------
# Local imports
# ------------------------------------------------------------

from epistasis.decomposition import generate_dv_matrix
from epistasis.utils import epistatic_order_indices, build_model_params
from epistasis.models.base import BaseModel

# ------------------------------------------------------------
# Unique Epistasis Functions
# ------------------------------------------------------------

def hadamard_weight_vector(genotypes):
    """ Build the hadamard weigth vector. """
    l = len(genotypes)
    n = len(genotypes[0])
    weights = np.zeros((l, l), dtype=float)
    for g in range(l):
        epistasis = float(genotypes[g].count("1"))
        weights[g][g] = ((-1)**epistasis)/(2**(n-epistasis))
    return weights

def cut_interaction_labels(labels, order):
    """ Cut off interaction labels at certain order of interactions. """
    return [l for l in labels if len(l) <= order]

# ------------------------------------------------------------
# Epistasis Mapping Classes
# ------------------------------------------------------------

class LocalEpistasisModel(BaseModel):

    def __init__(self, wildtype, genotypes, phenotypes, errors=None, log_transform=False, mutations=None):
        """ Create a map of the local epistatic effects using expanded mutant
            cycle approach.

            i.e.
            Phenotype = K_0 + sum(K_i) + sum(K_ij) + sum(K_ijk) + ...

            __Arguments__:

            `wildtype` [str] : Wildtype genotype. Wildtype phenotype will be used as reference state.

            `genotypes` [array-like, dtype=str] : Genotypes in map. Can be binary strings, or not.

            `phenotypes` [array-like] : Quantitative phenotype values

            `errors` [array-like] : List of phenotype errors.

            `log_transform` [bool] : If True, log transform the phenotypes.
        """
        # Populate Epistasis Map
        super(LocalEpistasisModel, self).__init__(wildtype, genotypes, phenotypes, errors=errors, log_transform=log_transform, mutations=mutations)
        self.order = self.length

        # Construct the Interactions mapping -- Interactions Subclass is added to model
        self._construct_interactions()

        # Generate basis matrix for mutant cycle approach to epistasis.
        self.X = generate_dv_matrix(self.Binary.genotypes, self.Interactions.labels, encoding={"1": 1, "0": 0})
        self.X_inv = np.linalg.inv(self.X)

    def fit(self):
        """ Estimate the values of all epistatic interactions using the expanded
            mutant cycle method to order=number_of_mutations.
        """
        self.Interactions.values = np.dot(self.X_inv, self.Binary.phenotypes)

    def fit_error(self):
        """ Estimate the error of each epistatic interaction by standard error
            propagation of the phenotypes through the model.
        """
        # Errorbars are symmetric, so only one column for errors is necessary
        self.Interactions.errors = np.sqrt(np.dot(self.X, self.Binary.errors**2))


class GlobalEpistasisModel(BaseModel):

    def __init__(self, wildtype, genotypes, phenotypes, errors=None, log_transform=False, mutations=None):
        """ Create a map of the global epistatic effects using Hadamard approach (defined by XX)

            This is the related to LocalEpistasisMap by the discrete Fourier
            transform of mutant cycle approach.

            __Arguments__:

            `wildtype` [str] : Wildtype genotype. Wildtype phenotype will be used as reference state.

            `genotypes` [array-like, dtype=str] : Genotypes in map. Can be binary strings, or not.

            `phenotypes` [array-like] : Quantitative phenotype values

            `errors` [array-like] : List of phenotype errors.

            `log_transform` [bool] : If True, log transform the phenotypes.
        """
        # Populate Epistasis Map
        super(GlobalEpistasisModel, self).__init__(wildtype, genotypes, phenotypes, errors, log_transform, mutations=mutations)
        self.order = self.length

        # Construct the Interactions mapping -- Interactions Subclass is added to model
        self._construct_interactions()

        # Generate basis matrix for mutant cycle approach to epistasis.
        #self.weight_vector = hadamard_weight_vector(self.Binary.genotypes)
        self.X = generate_dv_matrix(self.Binary.genotypes, self.Interactions.labels, encoding={"1": 1, "0": -1})
        self.X_inv = np.linalg.inv(self.X)

    def fit(self):
        """ Estimate the values of all epistatic interactions using the hadamard
        matrix transformation.
        """
        self.Interactions.values = 1/(self.n) * np.dot(self.X_inv, self.Binary.phenotypes)
        #self.Interactions.values = np.dot(self.weight_vector,np.dot(self.X_inv, self.Binary.phenotypes))

    def fit_error(self):
        """ Estimate the error of each epistatic interaction by standard error
            propagation of the phenotypes through the model.
        """
        self.Interactions.errors = np.sqrt( np.dot( (1/self.n)**2 * abs(self.X), self.Binary.errors**2) )