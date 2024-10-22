functions {
  // these should be close enough
  real sign(int x){
     return x/(abs(x) + machine_precision());
  }

  real sign(real x){
     return x/(abs(x) + machine_precision());
  }

  // for xy drift boundary-limiting
  real exp_limit(real x, real l2){
    return -l2 + 2 * l2 * 1./(1. + exp((x+l2)/(2*l2)));
  };

  vector exp_limit(vector x, real l2){
    return -l2 + 2 * l2 * 1./(1. + exp((x+l2)/(2*l2)));
  };

  row_vector exp_limit(row_vector x, real l2){
    return -l2 + 2 * l2 * 1./(1. + exp((x+l2)/(2*l2)));
  };
  
}

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
   
   // if phi will be defined
   // TODO: add parameter counterpart in parameters section
   

   // derivative penalties (if defined)
   // TODO: add parameter counterparts
   W_d1

   // various edge inputs
   

   // drift
   
   

   // granularity
   int<lower=1> granularity;


}

transformed data {




    // 
    step_size = 1./granularity;
    n_y_tiles = 1 + granularity * (ydim-1);
    n_x_tiles = 1 + granularity * (xdim-1);

    

    

    
}

parameters {

// parameter grid w/necessary truncations for each derivative
// if kernels used, rename this with `_raw` 
matrix[ydim-0,xdim-0] map_y0x0;
matrix[ydim-0,xdim-0] map_y0x1;
matrix[ydim-0,xdim-0] map_y1x1;

// kernel matrices


//  if z-drift is being used, define the errors and the sigmas
//  (also allow sigmas to be defined)


//  if xy-drift is being used, define matrix of drifts
//  sigma should be defined in `data` block, not here


// future: define additional variates used in model


}

transformed parameters {
None
}

model {
[PLACEHOLDER]
}

generated quantities {
[PLACEHOLDER]
}

