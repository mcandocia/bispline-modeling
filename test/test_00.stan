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

