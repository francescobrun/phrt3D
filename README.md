# Post-reconstruction 3D phase retrieval (PHRT3D)
Sample data and Python code for the article: F. Brun et al., [Post-reconstruction 3D single-distance phase retrieval for multi-stage phase-contrast tomography with photon-counting detectors](https://doi.org/10.1107/S1600577519000237), *Journal of Synchrotron Radiation*, Vol. 26, Issue 2, pp. 510-516 (2019).

**Note**: The code is not optimized for memory occupation. When used with the provided 4GB test dataset (256 slices of 2048x2048 pixels), it requires a machine with at least 64GB of RAM and the execution time should be less than a minute. 

## Input

Code requires as input a stack of propagation-based phase-contrast X-ray CT (Computed Tomography) reconstructed slices and the experimental conditions (i.e, energy, propagation distance and pixel size). Given the refractive index of the homogeneous material (i.e., delta and beta parameters), the output is the phase retrieved volume (written to disk as a stack of slices) according to a 3D version of the TIE algorithm (Paganin's). 

In other words, the input is the dataset as reconstructed via a conventional "absoprtion" computing pipeline and the output is the phase map, as depicted in the following figure (an axial slice is reported but the process operates over the whole 3D volume):

![](/doc/figure1.jpg)

**Note**: This approach does not require projection images and/or flat/dark images. It can be applied to past archived reconstructed data for which tomographic projections are no more available.
