# bispline modeling

This repository is a WIP.

The script `build_bcs_stan.py` generates a .stan file that models a 2-dimensional spline with an odd degree.

The following features will be present when completed:

* Ability to set degree of spline (e.g., bilinear, bicubic, biquintic, etc.)

* Initializing any combination of the 4 edges of the spline. This could allow you to fit splines to subsections of a much larger grid without having to fit all the data into a model at once.

* Use either a pre-defined grid of values (pretty simple) or $(y,x)$ coordinate data.

* If using $(y,x)$ coordinate data, a $\phi$ value and a $\sigma$ value can be used to describe AR(1) drift in model error.

* If using $(y,x)$ coordinate data, a drift parameter can be specified estimating possible error in the $(y,x)$ coorrdinates themselves. A tile radius is specified, which should be low, since Stan doesn't like dealing with indices (a 1-tile radius, for example, would have to search through 9 tiles rather than 1; 2 tiles would be 25, which I don't recommend)

* Eventually additional variates will be allowed. This might be useful to indicate different biases with different devices used to make measurements.

* Kernels that speed up how many tiles get updated in a correlated manner can be used. Currently square pyramid shapes with uniform spacing are present, and they only affect the raw values and the first derivatives of their included tiles. I have two other shapes (diamond and circle) planned, but they are not a priority.

* The output of splines can be specified with a particular resolution called "granularity". This allows one to retrieve data to create visually smooth surfaces (you can also just do that with the spline coefficients themselves)

See https://maxcandocia.com/article/2024/Oct/14/sampled-bicubic-spline-fitting/ and https://maxcandocia.com/article/2024/Sep/21/modeling-time-dependent-error-and-burgers/ for examples on how the underlying algorithms independently work. I will be creating a final write-up once the code is complete and I have run it with data I collected myself.