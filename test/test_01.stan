data {


   // edges will overlay the parameter grid, but keep data, even perfect grids,
   // intact
   int<lower=1> ydim;
   int<lower=1> xdim;

   // if use_perfect_grid
   
   
   // if NOT use_perfect_grid
   int N;
   vector[N]<lower=0> ycoords;
   vector[N]<lower=0> xcoords;

   // if using time drift
   vector[N] td;
   // if phi will be defined
   // TODO: add parameter counterpart in parameters section
   real phi;

   // derivative penalties (if defined)
   // TODO: add parameter counterparts
   W_d1

   // various edge inputs
   

   // drift
   real<lower=0> drift_sd;
   

   // granularity
   int<lower=1> granularity;


}

transformed data {




    // 
    step_size = 1./granularity;
    n_y_tiles = 1 + granularity * (ydim-1);
    n_x_tiles = 1 + granularity * (xdim-1);

    

    
// this defines how many iterations the kernel goes through
// and assigns the initial parameters
// note that while a denominator is still calculated for edge segments,
// they will not be evaluated for them
int<lower=1> ky_0;
int<lower=1> kx_0;
ky_0 = ydim %/% 7+1;;
kx_0 = xdim %/% 7+1;;
matrix<lower=0>[ydim,xdim] kernel_dy0x0_0;

    for (yi in 1:ydim){
      for (xi in 1:xdim){
        kernel_dy0x0_0[yi,xi] = 0;
      }
    }
    


// template for squares
for (yi in 1:ky_0){
  for (xi in 1:kx_0){
    // for each specific subkernel
    // loop over max distance in each direction
     
    for (y in max(1, 1+(yi - 1) * 7 - 14):min(ydim,1+(yi - 1) * 7 + 14)){
      for (x in max(1, 1+(xi - 1) * 7 - 14):min(xdim,1+(xi - 1) * 7 + 14)){
        // note the center is (1+(yi-1)*7,(1+(xi-1)*7)
        kernel_dy0x0_0[y,x] += (1.0-0.5 * max(abs(y-(1+yi-1)*7),abs(x-(1+(xi-1)*7))));
      }
    }
  }
}


// this defines how many iterations the kernel goes through
// and assigns the initial parameters
// note that while a denominator is still calculated for edge segments,
// they will not be evaluated for them




matrix<lower=0>[ydim,xdim] kernel_dy0x1_0;

    for (yi in 1:ydim){
      for (xi in 1:xdim){
        kernel_dy0x1_0[yi,xi] = 0;
      }
    }
    


// template for squares
// first derivative, so just do a flat count 
for (yi in 1:ky_0){
  for (xi in 1:kx_0){
    // for each specific subkernel
    // loop over max distance in each direction
     
    for (y in max(1, 1+(yi - 1) * 7 - 14):min(ydim,1+(yi - 1) * 7 + 14)){
      for (x in max(1, 1+(xi - 1) * 7 - 14):min(xdim,1+(xi - 1) * 7 + 14)){
        // note the center is (1+(yi-1)*7,(1+(xi-1)*7)
        kernel_dy0x1_0[y,x] += 1;
      }
    }
  }
}






    
}

parameters {
[PLACEHOLDER]
}

transformed parameters {
[PLACEHOLDER]
}

model {
[PLACEHOLDER]
}

generated quantities {
[PLACEHOLDER]
}

