ingest_daily_to_time_series <- function(directory, file_extensions = c('.csv'), name_date_format = 'MM-DD-YYY'){
  
  # Get a list of all files that match the extensions (will be in correct date order by default based on naming convention)
  file_list = c()
  for(extension in file_extensions){
    file_list = c(file_list, list.files(directory, extension, full.names = TRUE))
  }
  
  # Initialize data frames to hold Confirmed, Recovered, and Deaths
  Confirmed = data.frame('Province.State' = c('temp'), 'Country.Region' = c('temp'), stringsAsFactors = FALSE)
  Deaths = data.frame('Province.State' = c('temp'), 'Country.Region' = c('temp'), stringsAsFactors = FALSE)
  Recovered = data.frame('Province.State' = c('temp'), 'Country.Region' = c('temp'), stringsAsFactors = FALSE)
  
  # Add the key column used to summarize data
  key_columns = c('Country.Region', 'Province.State')
  Confirmed$Key = paste(Confirmed[,key_columns], collapse = '@')
  Deaths$Key = paste(Deaths[,key_columns], collapse = '@')
  Recovered$Key = paste(Recovered[,key_columns], collapse = '@')
  
  colname_vec = c()
  date_col_start = ncol(Confirmed) + 1
  
  for(csv_file in file_list){
    
    # Read the file as a csv
    temp_data = read.csv(csv_file, stringsAsFactors = FALSE)
    
    # Add the file date name to the column name vector
    colname_vec = c(colname_vec, tools::file_path_sans_ext(basename(csv_file)))
    
    # Find the columns corresponding to the State and Country
    state_col = grep(pattern = 'State', colnames(temp_data))
    country_col = grep(pattern = 'Country', colnames(temp_data))
    
    # Get the next column number to use for this data
    new_col = ncol(Confirmed) + 1
    new_row = nrow(Confirmed) + 1
    add_rows = c(new_row:(new_row + nrow(temp_data) - 1))
    
    # Add the country and state names to the tables
    Confirmed[add_rows, c(1,2)] = temp_data[,c(state_col, country_col)]
    Deaths[add_rows, c(1,2)] = temp_data[,c(state_col, country_col)]
    Recovered[add_rows, c(1,2)] = temp_data[,c(state_col, country_col)]
    
    # Add the data for this date table to the last column
    Confirmed[add_rows, new_col] = temp_data$Confirmed
    Deaths[add_rows, new_col] = temp_data$Deaths
    Recovered[add_rows, new_col] = temp_data$Recovered
    
  }
  
  # Name the columns
  colnames(Confirmed)[date_col_start:ncol(Confirmed)] = colname_vec
  colnames(Deaths)[date_col_start:ncol(Deaths)] = colname_vec
  colnames(Recovered)[date_col_start:ncol(Recovered)] = colname_vec
  
  # Reconstruct the key value column
  Confirmed$Key = apply(Confirmed[,key_columns], MARGIN = 1, paste, collapse = '@')
  Deaths$Key = apply(Deaths[,key_columns], MARGIN = 1, paste, collapse = '@')
  Recovered$Key = apply(Recovered[,key_columns], MARGIN = 1, paste, collapse = '@')
  
  # Remove the temporary row used to create columns
  Confirmed = Confirmed[-c(1),]
  Deaths = Deaths[-c(1),]
  Recovered = Recovered[-c(1),]
  
  # Construct a lookup table with unique values for the province/country/key and sort by key
  key_table = Confirmed[,c(key_columns, 'Key')]
  key_table = unique.array(key_table)
  key_table = key_table[order(key_table$Key), ]
  
  # Summarize the data columns by key and sort by key
  Confirmed = rowsum(Confirmed[,date_col_start:ncol(Confirmed)], Confirmed$Key, na.rm = TRUE)
  Deaths = rowsum(Deaths[,date_col_start:ncol(Deaths)], Deaths$Key, na.rm = TRUE)
  Recovered = rowsum(Recovered[,date_col_start:ncol(Recovered)], Recovered$Key, na.rm = TRUE)
  
  # Add the key table back to the summarized data
  Confirmed = cbind.data.frame(key_table, Confirmed)
  Deaths = cbind.data.frame(key_table, Deaths)
  Recovered = cbind.data.frame(key_table, Recovered)
  
  
  return(list('Confirmed' = Confirmed,
              'Deaths' = Deaths,
              'Recovered' = Recovered,
              'DateColumns' = c((ncol(key_table) + 1):ncol(Confirmed))))
}


summarize_dataset <- function(full_dataset, provinces = c(), countries = c(), text_string = '', count_columns = c(5:ncol(full_dataset)), text_split_term = '; '){
  
  
  selected_regions = c()
  row_subset = c()
  
  # Get matching entries
  if(length(provinces) > 0){
    
    row_subset = c(row_subset, which(full_dataset$Province.State %in% provinces))
    selected_regions = c(selected_regions, provinces)
    
  }
  
  if(length(countries) > 0){
    
    row_subset = c(row_subset, which(full_dataset$Country.Region %in% countries))
    selected_regions = c(selected_regions, countries)
    
  }
  
  if(nchar(text_string) > 0){
    
    # Split string by separating term
    search_text_vec = strsplit(text_string, text_split_term, fixed = TRUE)
    
    for(search_term in search_text_vec[[1]]){
     
      row_subset = c(row_subset, union(grep(search_term, full_dataset$Province.State),
                         grep(search_term, full_dataset$Country.Region)))
      
      selected_regions = c(selected_regions, paste(full_dataset$Province.State[row_subset]))
      selected_regions = c(selected_regions, paste(full_dataset$Country.Region[row_subset]))
      
    }
    
  }
  
  row_subset = unique(row_subset)
  selected_regions = unique(selected_regions)
  
  case_counts = colSums(full_dataset[row_subset, count_columns])
  
  # formatted_dates = as.Date(gsub('X', '', names(case_counts)), format = "%m.%d.%y")
  formatted_dates = as.Date(names(case_counts), format = "%m-%d-%y")
  
  return(list('case_counts' = case_counts,
              'formatted_dates' = formatted_dates,
              'selected_regions' = selected_regions))
  
}


create_log_model <- function(plot_dat, predict_days = 0, withhold_days = 0){
  
  # Restrict data to values > 0
  valid_values = which(plot_dat > 0)
  
  X = valid_values
  Y = plot_dat[valid_values]
  
  mod = lm(log(Y) ~ X)
  
  # Get 95% prediction intervals
  fitted_values = predict(mod, interval = 'confidence')
  fitted_values = exp(fitted_values)
  
  # Create prediction interval for requested number of days ahead
  predictions = NULL
  if(predict_days > 0){
    
    # Generate new values for prediction for requested number of days
    new_data = mod$model[rep(nrow(mod$model), 1 + predict_days), ]
    new_data$X = new_data$X + c(0:predict_days)
    
    # Generate predictions with prediction interval
    predictions = predict(mod, interval = 'prediction', newdata = new_data)
    predictions = exp(predictions)
    
  }
  
  
  return(list('date_names' = names(Y),
              'X' = X,
              'Y' = Y,
              'model' = mod,
              'fitted_values' = fitted_values,
              'predictions' = predictions))
  
}


resolution_simulation <- function(cumulative_confirmed_vec, end_point = NULL, distribution_func, ...){
  
  # Initialize output vector
  resolution_date_vec = c()
  
  # Simulate resolution time (recovery or death) for each new case in cumulative case vector
  for(i in 1:length(cumulative_confirmed_vec)){
    
    # resolution_time_vec = rexp(cumulative_confirmed_vec[i] - cumulative_confirmed_vec[i - 1], 1/mean)
    resolution_time_vec = distribution_func(cumulative_confirmed_vec[i] - cumulative_confirmed_vec[i - 1], ...)
    #resolution_time_vec = do.call(distribution_func, append( cumulative_confirmed_vec[i] - cumulative_confirmed_vec[i - 1])
    
    resolution_date = ceiling(resolution_time_vec) + i
    
    resolution_date_vec = c(resolution_date_vec, resolution_date)
    
  }
  
  # resolution_date_vec = resolution_date_vec[order(resolution_date_vec)]
  # Set the resolution date vector to the maximum of the simulated dataset if one was not provided
  if(is.null(end_point)){
    
    end_point = max(resolution_date_vec)
    
  }
  
  # Convert simulation results to cumulative resolution count
  resolution_ecdf = ecdf(resolution_date_vec)
  cumulative_resolution_vec = resolution_ecdf(c(1:end_point)) * length(resolution_date_vec)
  
  return(cumulative_resolution_vec)
  
}


resolution_predict <- function(cumulative_confirmed_vec, end_point = NULL, distribution_cdf_func, ...){
  
  # Calculate difference vectors for the cumulative confirmed vector and resolved case vector
  daily_new_cases = diff(cumulative_confirmed_vec)
  diff_length = length(daily_new_cases)
  
  # Initialize a probability density matrix to store the pdf for new cases created on each day
  resolution_matrix = matrix(data = 0, nrow=length(daily_new_cases), ncol = length(daily_new_cases))
  
  # Calculate the pdf for each day that has new confirmed cases and store it in the matrix (assuming the resolution would be reported on the next day)
  for(i in 1:diff_length){
    
    # If there are new cases, calculate the pdf for recovery date through the end of the dataset and enter it into the matrix
    if(daily_new_cases[i] > 0){
      
      # Calculate the resolution estimated dates for the new cases on this day
      resolution_matrix[i, i:diff_length] = daily_new_cases[i] * diff(distribution_cdf_func(c(0:(diff_length + 1 - i)), ...))
      
    }
    
  }
  
  # Sum the density matrix by column to create a prediction for cumulative resolved cases
  cumulative_resolution_vec = colSums(resolution_matrix)

  return(cumulative_resolution_vec)
  
}


resolution_dist_fit <- function(cumulative_confirmed_vec, cumulative_resolved_vec, distribution = 'lognormal'){
  
  # Calculate difference vectors for the cumulative confirmed vector and resolved case vector
  daily_new_cases = diff(cumulative_confirmed_vec)
  daily_resolved_cases = diff(cumulative_resolved_vec)
  diff_length = length(daily_new_cases)
  
  # Create function to calculate negative log likelihood of observed resolution data under the specified distribution
  log_lik_func = function(x){
      
      # Initialize a probability density matrix to store the pdf for new cases created on each day
      density_matrix = matrix(data = 0, nrow=length(daily_new_cases), ncol = length(daily_new_cases))
      
      # Calculate the pdf for each day that has new confirmed cases and store it in the matrix (assuming the resolution would be reported on the next day)
      for(i in 1:diff_length){
        
        # If there are new cases, calculate the pdf for recovery date through the end of the dataset and enter it into the matrix
        if(daily_new_cases[i] > 0){
          
          # Calculate the probabiliy (cannot use exatly zero probability of recovery on the day of diagnosis due to returning Inf negative log likelihood, even though this would be consistent with model used in simulation section)
          
          if(distribution == 'Lognormal'){
            density_matrix[i, i:diff_length] = daily_new_cases[i] * diff(plnorm(c(0:(diff_length + 1 - i)), meanlog = x[1], sdlog = x[2]))
          } else if(distribution == 'Exponential'){
            density_matrix[i, i:diff_length] = daily_new_cases[i] * diff(pexp(c(0:(diff_length + 1 - i)), rate = x[1]))
          } else if(distribution == 'Poisson'){
            density_matrix[i, i:diff_length] = daily_new_cases[i] * diff(ppois(c(0:(diff_length + 1 - i)), lambda = x[1]))
          } else if(distribution == 'Weibull'){
            density_matrix[i, i:diff_length] = daily_new_cases[i] * diff(pweibull(c(0:(diff_length + 1 - i)), shape = x[1], scale = x[2]))
          } else if(distribution == 'Negative Binomial'){
            density_matrix[i, i:diff_length] = daily_new_cases[i] * diff(pnbinom(c(0:(diff_length + 1 - i)), size = x[1], mu = x[2]))
          }
          
        }
        
      }
      
      # Sum the density matrix by column and normalize by number of observations to create a pdf vector over the observed dataset
      pdf_vec = colSums(density_matrix) / sum(daily_new_cases)
      
      # Account for the probability associated with all remaining unresolved cases
      tail_prob = 1 - sum(pdf_vec)
      
      # Calculate log likelihood of recovery vector
      # return( -sum(daily_resolved_cases * log(pdf_vec), na.rm = TRUE))
      return( -sum(daily_resolved_cases * log(pdf_vec), na.rm = TRUE) - log(tail_prob) * (sum(daily_new_cases) - sum(daily_resolved_cases)))
    }
  
  # Set initial parameters for optimizer based on initial distribution
  if(distribution == 'Lognormal'){
    initial_params = c(log(14), 1)
    names(initial_params) = c('meanlog', 'sdlog')
    # optim_lower_bound = c(-Inf, 0.01)
    # optim_upper_bound = c(Inf, Inf)
    
  }else if(distribution == 'Exponential'){
    initial_params = c(1/21)
    names(initial_params) = c('rate')
    # optim_lower_bound = 0
    # optim_upper_bound = Inf
  }else if(distribution == 'Poisson'){
    initial_params = c(14)
    names(initial_params) = c('lambda')
    # optim_lower_bound = 0
    # optim_upper_bound = Inf
  }else if(distribution == 'Weibull'){
    initial_params = c(2, 23)
    names(initial_params) = c('shape', 'scale')
    # optim_lower_bound = 0
    # optim_upper_bound = Inf
  }else if(distribution == 'Negative Binomial'){
    initial_params = c(5, 21)
    names(initial_params) = c('size', 'mu')
    # optim_lower_bound = 0
    # optim_upper_bound = Inf
  }
  
  # Minimize the negative log-likelihood of the distribution
  optim_fit = optim(initial_params, log_lik_func)
  # optim_fit = optim(initial_params, log_lik_func, lower = optim_lower_bound, upper = optim_upper_bound, control = list(trace = 6))
  
  # Return fitted distribution parameters
  return(optim_fit)
  
}