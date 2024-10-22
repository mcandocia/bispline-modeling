functions {{
  // these should be close enough
  real sign(int x){{
     return x/(abs(x) + machine_precision());
  }}

  real sign(real x){{
     return x/(abs(x) + machine_precision());
  }}

  // for xy drift boundary-limiting
  real exp_limit(real x, real l2){{
    return -l2 + 2 * l2 * 1./(1. + exp((x+l2)/(2*l2)));
  }};

  vector exp_limit(vector x, real l2){{
    return -l2 + 2 * l2 * 1./(1. + exp((x+l2)/(2*l2)));
  }};

  row_vector exp_limit(row_vector x, real l2){{
    return -l2 + 2 * l2 * 1./(1. + exp((x+l2)/(2*l2)));
  }};
  
}}

data {{
{data_template}
}}

transformed data {{
{transformed_data_template}    
}}

parameters {{
{parameters_template}
}}

transformed parameters {{
{transformed_parameters_template}
}}

model {{
{model_template}
}}

generated quantities {{
{generated_quantities_template}
}}

