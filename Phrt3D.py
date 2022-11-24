import numpy as np
import tifffile 
import time
import os
import glob

# Numpy can be of course used instead:
from pyfftw.interfaces.numpy_fft import rfftn, irfftn



def phase_retrieval(im, b, d, e, z, px, padding=(0,0,0.25), nr_threads=4):
	"""Execute phase_retrieval with TIE (Paganin's) algorithm.

	Parameters
	----------
	im : array_like
		Volume data as 3D numpy array. 

	b : double
		Beta: immaginary part of the complex X-ray refraction index.

	d : double
		Delta: decrement from unity of the real part of the complex X-ray refraction index.

	e [KeV]: double
		Energy in KeV of the incident X-ray beam.

	z [mm]: double
		Sample-to-detector propagation distance in mm.

	px [mm]: double
		Side in mm of the detector element.

	padding : 3-item list such as (0,0,1)
		Apply image padding by adding the specified factor * dimension size.
	
	"""
	

	# Save original dims:	
	dim0 = im.shape[0]
	dim1 = im.shape[1]
	dim2 = im.shape[2]

	# Prepare pad dims:
	pad0 = int(padding[0]*dim0) // 2
	pad1 = int(padding[1]*dim1) // 2
	pad2 = int(padding[2]*dim2) // 2

	# Pad image (if required):	
	im = np.pad(im, ((pad0,pad0), (pad1,pad1), (pad2,pad2)),'edge')
	
	# Get new dimensions:
	rows = im.shape[0]
	cols = im.shape[1]
	plns = im.shape[2]

	# Use PyFFTW:
	im = rfftn(im, threads=nr_threads)		

	# Get additional values:
	lam = (12.398424 * 10 ** (-7)) / e # in mm
	mu = 4 * np.pi * b / lam

	# Prepare frequencies:
	ulim = np.arange(-(cols) // 2, (cols) // 2, dtype=np.float32) * (2 * np.pi / (cols * px))
	vlim = np.arange(-(rows) // 2, (rows) // 2, dtype=np.float32) * (2 * np.pi / (rows * px))
	wlim = np.arange(-(plns) // 2, (plns) // 2, dtype=np.float32) * (2 * np.pi / (plns * px))
	u,v,w = np.meshgrid(ulim, vlim, wlim)

	# Prepare filter according to TIE formula:
	w = 1 + z*d/mu * (u*u + v*v + w*w)
	
	# Shift and get only half of the frequencies because of rfftn:
	w = np.fft.fftshift(w)	
	w = w[:,:,0:w.shape[2] // 2 + 1] 

	# Perform actual filtering:
	im = im / (w + np.finfo(np.float32).eps) # Avoids division by zero
		
	# Use PyFFTW:
	im = irfftn(im, threads=nr_threads)
		
	# Return cropped output:
	im = im[pad0:pad0+dim0, pad1:pad1+dim1, pad2:pad2+dim2] 
			
	# Conclude formula and return:
	return -1 / mu * np.log(im + np.finfo(np.float32).eps) 


if __name__ == '__main__':
	
	## Parameters:
	IN_PATH = "test_dataset_input"  
	OUT_PATH = "test_dataset_output"

	DELTA = 1.8E-7
	BETA  = 1E-10
	ENERGY = 22  # [KeV]
	DISTANCE = 150 # [mm]
	PIXEL = 0.0022 # [mm]



	## Read input volume (sequence of axial slices):
	print("Loading volume from disk...")
	
	# Get list of files:
	files = sorted(glob.glob(os.path.join(IN_PATH,"*.tif*")))
		
	# Read first image to understand sizes and prepare dataset:
	im = tifffile.imread(files[0])
	dset = np.empty( (im.shape[0],im.shape[1],len(files)), dtype=np.float32)
	dset[:,:,0] = im

	# Load volume:
	for i in range(1,len(files)):
		im = tifffile.imread(files[i]).astype(np.float32)
		dset[:,:,i] = im



	## Filter:
	print("Filtering...")
	t0 = time.time()
	
	dset = np.exp(-dset) # To process common absorption reconstructed data

	dset = phase_retrieval(dset, BETA, DELTA, ENERGY, DISTANCE, PIXEL)
	
	t1 = time.time()
	print("Filtering performed in ", format(t1 - t0,'.3f'), " s.")
	

	
	## Write filtered volume as sequence of axial slices:
	print("Writing processed slices to disk...")
	for i in np.arange(dset.shape[2]):
		tifffile.imwrite(os.path.join(OUT_PATH, "slice_" + "{:04d}".format(i) + ".tif"), dset[:,:,i])

	print("Post-reconstruction 3D phase retrieval completed!")
